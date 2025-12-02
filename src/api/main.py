"""
Pharma Agentic AI - FastAPI Backend
REST API for programmatic access to the multi-agent system.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

app = FastAPI(
    title="Pharma Agentic AI API",
    description="Multi-Agent Intelligence Platform for Pharmaceutical Strategy",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class QueryRequest(BaseModel):
    """Request model for agent queries."""
    query: str
    generate_pdf: bool = False
    generate_excel: bool = False


class QueryResponse(BaseModel):
    """Response model for agent queries."""
    query: str
    response: str
    agents_used: List[str]
    sources: List[str]
    reports: List[Dict[str, str]]
    timestamp: str
    execution_time_ms: float


class ToolQueryRequest(BaseModel):
    """Request model for direct tool queries."""
    tool_name: str
    parameters: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    version: str


# Endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with health check."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


@app.post("/query", response_model=QueryResponse)
async def run_query(request: QueryRequest):
    """
    Run a multi-agent query.
    
    This endpoint orchestrates multiple specialized agents to answer
    complex pharmaceutical strategy questions.
    """
    import time
    start_time = time.time()
    
    try:
        from src.agents.master_agent import create_master_crew, classify_intent
        
        # Classify intent
        agents_needed = classify_intent(request.query)
        
        # Create and run crew
        crew = create_master_crew(request.query)
        result = crew.kickoff()
        response_text = str(result)
        
        # Determine sources
        sources = []
        source_map = {
            "iqvia": "IQVIA Market Database",
            "patent": "USPTO Patent Database",
            "clinical": "Clinical Trials Registry",
            "social": "Patient Forums & Social Media",
            "competitor": "Competitive Intelligence Reports",
            "internal": "Internal Strategy Documents",
            "exim": "EXIM Trade Database",
            "web": "Web Intelligence"
        }
        for agent in agents_needed:
            if agent in source_map:
                sources.append(source_map[agent])
        
        # Generate reports if requested
        reports = []
        if request.generate_pdf:
            from src.services.report_generator import generate_pdf_report
            pdf_path = generate_pdf_report(
                title="Pharma Strategy Analysis",
                query=request.query,
                content=response_text,
                metadata={"agents_used": agents_needed}
            )
            if not pdf_path.startswith("Error"):
                reports.append({"type": "PDF", "path": pdf_path})
        
        if request.generate_excel:
            from src.services.report_generator import generate_excel_report
            data = {"findings": [], "recommendations": []}
            excel_path = generate_excel_report(
                title="Pharma Strategy Analysis",
                query=request.query,
                data=data,
                metadata={"agents_used": agents_needed}
            )
            if not excel_path.startswith("Error"):
                reports.append({"type": "Excel", "path": excel_path})
        
        execution_time = (time.time() - start_time) * 1000
        
        return QueryResponse(
            query=request.query,
            response=response_text,
            agents_used=agents_needed,
            sources=sources,
            reports=reports,
            timestamp=datetime.now().isoformat(),
            execution_time_ms=round(execution_time, 2)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/{tool_name}")
async def call_tool(tool_name: str, request: ToolQueryRequest):
    """
    Directly call a specific tool.
    
    Available tools:
    - query_iqvia_market
    - query_patents
    - query_exim_trade
    - query_clinical_trials
    - query_social_media
    - query_competitor_intel
    - search_internal_docs
    - web_search
    """
    try:
        # Import tools
        from src.tools import (
            query_iqvia_market,
            query_patents,
            query_exim_trade,
            query_clinical_trials,
            query_social_media,
            query_competitor_intel,
            search_internal_docs
        )
        from src.tools.web_tool import web_search
        
        tools = {
            "query_iqvia_market": query_iqvia_market,
            "query_patents": query_patents,
            "query_exim_trade": query_exim_trade,
            "query_clinical_trials": query_clinical_trials,
            "query_social_media": query_social_media,
            "query_competitor_intel": query_competitor_intel,
            "search_internal_docs": search_internal_docs,
            "web_search": web_search
        }
        
        if tool_name not in tools:
            raise HTTPException(
                status_code=404,
                detail=f"Tool '{tool_name}' not found. Available: {list(tools.keys())}"
            )
        
        tool_func = tools[tool_name]
        result = tool_func._run(**request.parameters)
        
        return {
            "tool": tool_name,
            "parameters": request.parameters,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents")
async def list_agents():
    """List all available agents and their capabilities."""
    return {
        "agents": [
            {
                "id": "iqvia",
                "name": "IQVIA Market Agent",
                "role": "Market Data Specialist",
                "capabilities": ["Market size analysis", "CAGR trends", "Competitor mapping", "Whitespace identification"]
            },
            {
                "id": "patent",
                "name": "Patent Landscape Agent",
                "role": "IP Legal Analyst",
                "capabilities": ["Patent expiry tracking", "FTO assessment", "Generic entry analysis"]
            },
            {
                "id": "exim",
                "name": "EXIM Trade Agent",
                "role": "Supply Chain Analyst",
                "capabilities": ["Import/export volumes", "Pricing trends", "Supply chain risk assessment"]
            },
            {
                "id": "clinical",
                "name": "Clinical Trials Agent",
                "role": "R&D Pipeline Analyst",
                "capabilities": ["Trial landscape analysis", "Repurposing opportunities", "Competition density"]
            },
            {
                "id": "social",
                "name": "Social Listening Agent",
                "role": "Patient Voice Analyst",
                "capabilities": ["Sentiment analysis", "Complaint themes", "Innovation opportunities"]
            },
            {
                "id": "competitor",
                "name": "Competitor Agent",
                "role": "Strategic War Gamer",
                "capabilities": ["Competitor prediction", "War gaming", "Threat assessment"]
            },
            {
                "id": "internal",
                "name": "Internal Knowledge Agent",
                "role": "Corporate Strategist",
                "capabilities": ["Document search", "Strategy alignment", "Institutional knowledge"]
            },
            {
                "id": "web",
                "name": "Web Intelligence Agent",
                "role": "External Researcher",
                "capabilities": ["News monitoring", "FDA approvals", "Market developments"]
            }
        ]
    }


@app.get("/examples")
async def get_examples():
    """Get example queries for testing."""
    return {
        "examples": [
            {
                "name": "Whitespace Analysis",
                "query": "Which respiratory diseases show low competition but high patient burden in India?",
                "expected_agents": ["iqvia", "clinical"]
            },
            {
                "name": "Repurposing Opportunities",
                "query": "Identify potential repurposing opportunities for Pembrolizumab.",
                "expected_agents": ["clinical", "patent"]
            },
            {
                "name": "FTO Check",
                "query": "Check patent expiry for Sitagliptin in the US.",
                "expected_agents": ["patent"]
            },
            {
                "name": "Patient Voice",
                "query": "What are patients complaining about regarding current Diabetes injectables?",
                "expected_agents": ["social"]
            },
            {
                "name": "War Game",
                "query": "Simulate a launch of generic Rivaroxaban in 2025. What will competitors do?",
                "expected_agents": ["competitor", "patent"]
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
