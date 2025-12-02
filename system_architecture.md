# System Architecture: Pharma Agentic AI

## Overview
The solution utilizes a **Multi-Agent Reference Architecture** (based on industry standards). It features a distinct **Orchestration Layer**, **Knowledge Layer**, **Storage Layer**, and **Agent Layer**. The system is built using **LangGraph** (or CrewAI) for orchestration and **Groq** for high-speed inference.

## Architecture Diagram

```mermaid
graph TD
    User[User / Pharma Planner] -->|Natural Language Query| Gateway[Gateway / User App]
    Gateway -->|Auth & Rate Limits| Orchestrator[Orchestration Layer\n(Master Agent)]
    
    subgraph "Orchestration Layer"
        Orchestrator -->|Intent Classification| Classifier[Classifier / Planner]
        Orchestrator -->|Registry Lookup| Registry[Agent Registry]
    end
    
    subgraph "Storage Layer"
        Orchestrator -->|Read/Write| History[Conversation History]
        Orchestrator -->|Read/Write| State[Agent State]
    end
    
    subgraph "Knowledge Layer"
        InternalAgent -->|RAG| VectorDB[(Vector DB / Internal Docs)]
        Orchestrator -->|Context| SourceBases[(Source Bases)]
    end
    
    subgraph "Agent Layer (Local & Remote)"
        Orchestrator -->|Delegate| Supervisor[Supervisor Agent]
        Supervisor -->|Task| IQVIA[IQVIA Insights Agent]
        Supervisor -->|Task| EXIM[EXIM Trends Agent]
        Supervisor -->|Task| Patent[Patent Landscape Agent]
        Supervisor -->|Task| Trials[Clinical Trials Agent]
        Supervisor -->|Task| InternalAgent[Internal Knowledge Agent]
        Supervisor -->|Task| Web[Web Intelligence Agent]
        Supervisor -->|Task| Social[Social Listening Agent]
        Supervisor -->|Task| Competitor[Competitor Agent]
    end
    
    subgraph "Integration Layer & MCP"
        IQVIA & EXIM & Patent & Trials & Web & Social & Competitor -->|MCP Protocol| Integration[Integration Layer]
        Integration -->|API Call| MockIQVIA[(IQVIA Mock API)]
        Integration -->|API Call| MockEXIM[(EXIM Mock Server)]
        Integration -->|API Call| MockUSPTO[(USPTO API Clone)]
        Integration -->|API Call| MockTrials[(Clinical Trials Stub)]
        Integration -->|Search| WebProxy[(Web Search Proxy)]
        Integration -->|Scrape| MockSocial[(Social Media Mock)]
        Integration -->|Query| MockComp[(Competitor Intel Mock)]
    end
    
    subgraph "Observability & Evals"
        Orchestrator & Supervisor & Integration -->|Traces/Logs| Observability[Observability / LangSmith]
        Observability -->|Feedback| Evaluation[Evaluation / Golden Tests]
    end

    subgraph "Output Layer"
        Orchestrator -->|Synthesized Data| Report[Report Generator Agent]
        Report -->|PDF/Excel| Gateway
        Orchestrator -->|Chat Response| Gateway
    end
```

## Core Layers

### 1. Orchestration Layer
- **Master Agent (Orchestrator)**: The central brain. Uses a "Semantic Kernel" or LangGraph state machine to manage the conversation flow.
- **Classifier**: Determines the intent (Market Analysis vs. Innovation Search).
- **Agent Registry**: Dynamic lookup of available worker agents and their capabilities.

### 2. Agent Layer
- **Supervisor Agent**: Manages the specific execution of sub-tasks, ensuring agents don't hallucinate or loop indefinitely.
- **Worker Agents**: Specialized agents (IQVIA, EXIM, Patent, etc.) that act as "MCP Clients" to fetch data.

### 3. Knowledge Layer
- **Vector DB**: Stores embeddings of internal strategy decks for the Internal Knowledge Agent.
- **Source Bases**: Raw text sources for grounding.

### 4. Storage Layer
- **Conversation History**: Persists the chat context.
- **Agent State**: Tracks the progress of long-running research tasks.

### 5. Integration Layer (MCP)
- **Model Context Protocol (MCP)**: Standardized interface for agents to talk to external tools (Mock APIs).
- **External Tools**: The actual mock data sources (JSON/CSV files wrapped in APIs).

### 6. Observability & Evals
- **Observability**: Tracing agent thought processes (LangSmith/LangFuse).
- **Evaluation**: Running "Golden Tasks" (e.g., "Find whitespace in India") to measure performance against expected outputs.

## Technology Stack
- **Framework**: LangGraph / CrewAI
- **LLM Engine**: Groq (Llama 3 70B / Mixtral) for speed.
- **Vector Store**: ChromaDB / FAISS.
- **Observability**: LangSmith or similar.
- **Protocol**: MCP (Model Context Protocol) for tool integration.
