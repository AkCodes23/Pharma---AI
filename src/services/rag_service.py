"""
RAG Service using ChromaDB
Vector database for internal document search.
"""
import json
import os
from pathlib import Path
from typing import List, Optional

try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("ChromaDB not installed. Using fallback search.")


class RAGService:
    """RAG service for internal document search using ChromaDB."""
    
    def __init__(self, persist_dir: Optional[str] = None):
        """Initialize the RAG service."""
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.mock_data_path = self.base_dir / "mock_data" / "internal_docs_metadata.json"
        self.persist_dir = persist_dir or str(self.base_dir / "data" / "chroma_db")
        
        self.collection = None
        self.documents = []
        
        if CHROMA_AVAILABLE:
            self._init_chromadb()
        else:
            self._load_documents()
    
    def _init_chromadb(self):
        """Initialize ChromaDB with embeddings."""
        try:
            # Create persist directory
            os.makedirs(self.persist_dir, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(path=self.persist_dir)
            
            # Use default embedding function (all-MiniLM-L6-v2)
            self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="internal_docs",
                embedding_function=self.embedding_function,
                metadata={"description": "Pharma internal documents"}
            )
            
            # Index documents if collection is empty
            if self.collection.count() == 0:
                self._index_documents()
                
        except Exception as e:
            print(f"ChromaDB initialization error: {e}")
            self._load_documents()
    
    def _load_documents(self):
        """Load documents from JSON file."""
        try:
            with open(self.mock_data_path, "r") as f:
                self.documents = json.load(f)
        except Exception as e:
            print(f"Error loading documents: {e}")
            self.documents = []
    
    def _index_documents(self):
        """Index all internal documents into ChromaDB."""
        self._load_documents()
        
        if not self.documents or not self.collection:
            return
        
        ids = []
        documents = []
        metadatas = []
        
        for doc in self.documents:
            doc_id = doc.get("doc_id", "")
            
            # Create searchable text combining all fields
            searchable_text = f"{doc.get('title', '')} {doc.get('summary', '')} {doc.get('content', '')} {' '.join(doc.get('tags', []))}"
            
            ids.append(doc_id)
            documents.append(searchable_text)
            metadatas.append({
                "doc_id": doc_id,
                "title": doc.get("title", ""),
                "tags": ",".join(doc.get("tags", []))
            })
        
        # Add to collection
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
        print(f"Indexed {len(ids)} documents into ChromaDB")
    
    def search(self, query: str, n_results: int = 5) -> List[dict]:
        """
        Search internal documents using semantic similarity.
        
        Args:
            query: Search query
            n_results: Number of results to return
        
        Returns:
            List of matching documents with scores
        """
        if self.collection and CHROMA_AVAILABLE:
            return self._chromadb_search(query, n_results)
        else:
            return self._fallback_search(query, n_results)
    
    def _chromadb_search(self, query: str, n_results: int) -> List[dict]:
        """Search using ChromaDB vector similarity."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, self.collection.count())
            )
            
            # Format results
            formatted = []
            if results and results.get("ids"):
                for i, doc_id in enumerate(results["ids"][0]):
                    # Find original document
                    original = next((d for d in self.documents if d.get("doc_id") == doc_id), {})
                    
                    formatted.append({
                        "doc_id": doc_id,
                        "title": original.get("title", results["metadatas"][0][i].get("title", "")),
                        "summary": original.get("summary", ""),
                        "content": original.get("content", ""),
                        "tags": original.get("tags", []),
                        "distance": results["distances"][0][i] if results.get("distances") else 0
                    })
            
            return formatted
        
        except Exception as e:
            print(f"ChromaDB search error: {e}")
            return self._fallback_search(query, n_results)
    
    def _fallback_search(self, query: str, n_results: int) -> List[dict]:
        """Fallback keyword search when ChromaDB is unavailable."""
        self._load_documents()
        
        query_lower = query.lower()
        scored_docs = []
        
        for doc in self.documents:
            score = 0
            
            # Score based on keyword matches
            searchable = f"{doc.get('title', '')} {doc.get('summary', '')} {doc.get('content', '')}".lower()
            
            for word in query_lower.split():
                if len(word) > 2 and word in searchable:
                    score += searchable.count(word)
            
            # Boost for tag matches
            for tag in doc.get("tags", []):
                if tag.lower() in query_lower:
                    score += 5
            
            if score > 0:
                scored_docs.append((score, doc))
        
        # Sort by score and return top results
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        return [
            {
                "doc_id": doc.get("doc_id"),
                "title": doc.get("title"),
                "summary": doc.get("summary"),
                "content": doc.get("content", ""),
                "tags": doc.get("tags", []),
                "score": score
            }
            for score, doc in scored_docs[:n_results]
        ]
    
    def get_document(self, doc_id: str) -> Optional[dict]:
        """Get a specific document by ID."""
        self._load_documents()
        
        for doc in self.documents:
            if doc.get("doc_id", "").upper() == doc_id.upper():
                return doc
        
        return None
    
    def list_by_tag(self, tag: str) -> List[dict]:
        """List all documents with a specific tag."""
        self._load_documents()
        
        return [
            doc for doc in self.documents
            if tag.lower() in [t.lower() for t in doc.get("tags", [])]
        ]


# Global instance
_rag_service = None


def get_rag_service() -> RAGService:
    """Get or create the global RAG service instance."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
