# 💊 Pharma Agentic AI

A Multi-Agent Intelligence Platform for Pharmaceutical Strategy using CrewAI, Groq (Llama 3 70B), and Streamlit.

## 🎯 Overview

This system orchestrates 8 specialized AI agents to answer complex pharmaceutical strategy questions:

| Agent | Role | Capabilities |
|-------|------|-------------|
| 📊 **IQVIA Agent** | Market Data Specialist | Market size, CAGR, competition levels, whitespace |
| 📜 **Patent Agent** | IP Legal Analyst | Patent expiry, FTO assessment, generic entry |
| 🚢 **EXIM Agent** | Supply Chain Analyst | Import/export volumes, pricing, sourcing |
| 🔬 **Clinical Agent** | R&D Pipeline Analyst | Trial landscape, repurposing opportunities |
| 💬 **Social Agent** | Patient Voice Analyst | Sentiment, complaints, innovation insights |
| ⚔️ **Competitor Agent** | Strategic War Gamer | Competitor prediction, threat assessment |
| 📁 **Internal Agent** | Corporate Strategist | RAG-based document search |
| 🌐 **Web Agent** | External Researcher | News, approvals, market developments |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                        │
│                  (Chat Interface + Reports)                  │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Master Orchestrator                       │
│              (CrewAI Hierarchical Process)                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
    ┌─────────┬─────────┬─┴───────┬─────────┬─────────┐
    ▼         ▼         ▼         ▼         ▼         ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
│ IQVIA │ │Patent │ │Clinical│ │Social │ │Compet.│ │  ...  │
│ Agent │ │ Agent │ │ Agent │ │ Agent │ │ Agent │ │       │
└───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘ └───────┘
    │         │         │         │         │
    ▼         ▼         ▼         ▼         ▼
┌───────────────────────────────────────────────────────────┐
│                     Mock Data Layer                        │
│  (JSON files simulating IQVIA, USPTO, ClinicalTrials...)   │
└───────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd a:\Projects\Pharma
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=llama3-70b-8192
TAVILY_API_KEY=your-tavily-api-key-here
```

Get your API keys from:
- **Groq API**: https://console.groq.com/keys
- **Tavily API**: https://tavily.com/

### 3. Run Tests

```bash
python test_golden_tasks.py
```

### 4. Launch Streamlit App

```bash
streamlit run app.py
```

### 5. (Optional) Launch API Server

```bash
uvicorn src.api.main:app --reload --port 8000
```

Then visit: http://localhost:8000/docs

## 🎯 Golden Tasks (Test Scenarios)

| # | Task | Example Query |
|---|------|---------------|
| 1 | **Whitespace Analysis** | "Which respiratory diseases show low competition but high patient burden in India?" |
| 2 | **Repurposing** | "Identify potential repurposing opportunities for Pembrolizumab." |
| 3 | **FTO Check** | "Check patent expiry for Sitagliptin in the US." |
| 4 | **Patient Voice** | "What are patients complaining about regarding Diabetes injectables?" |
| 5 | **War Game** | "Simulate a launch of generic Rivaroxaban in 2025." |

## 📁 Project Structure

```
Pharma/
├── app.py                      # Streamlit frontend
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration
├── test_golden_tasks.py        # Validation test suite
│
├── src/
│   ├── agents/
│   │   ├── worker_agents.py    # 8 specialized agents
│   │   └── master_agent.py     # Orchestrator with CrewAI
│   │
│   ├── tools/
│   │   ├── iqvia_tool.py       # Market data queries
│   │   ├── patent_tool.py      # Patent/FTO analysis
│   │   ├── exim_tool.py        # Trade data queries
│   │   ├── clinical_tool.py    # Clinical trials queries
│   │   ├── social_tool.py      # Social media/sentiment
│   │   ├── competitor_tool.py  # War gaming tools
│   │   ├── internal_tool.py    # Internal docs RAG
│   │   └── web_tool.py         # Web search
│   │
│   ├── services/
│   │   ├── rag_service.py      # ChromaDB vector store
│   │   └── report_generator.py # PDF/Excel generation
│   │
│   ├── api/
│   │   └── main.py             # FastAPI REST API
│   │
│   └── config/
│       └── settings.py         # Configuration management
│
├── mock_data/
│   ├── iqvia_market_data.json
│   ├── clinical_trials.json
│   ├── uspto_patents.json
│   ├── exim_trade_data.json
│   ├── social_media_posts.json
│   ├── competitor_strategies.json
│   ├── internal_docs_metadata.json
│   └── web_search_results.json
│
└── reports/                    # Generated PDF/Excel reports
```

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/query` | Run multi-agent query |
| POST | `/tools/{tool_name}` | Call specific tool directly |
| GET | `/agents` | List available agents |
| GET | `/examples` | Get example queries |
| GET | `/health` | Health check |

### Example API Call

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Which respiratory diseases show low competition in India?",
    "generate_pdf": true
  }'
```

## 📊 Mock Data Coverage

| Data Source | Molecules Covered |
|-------------|-------------------|
| IQVIA Market | Pembrolizumab, Sitagliptin, Rivaroxaban, Pirfenidone, Roflumilast, Fluticasone, Omalizumab, Tiotropium |
| Patents | All above molecules with expiry dates |
| Clinical Trials | NSCLC, Diabetes, IPF, COPD, Asthma, PAH, Melanoma, TNBC |
| EXIM Trade | Import volumes and pricing for all molecules |
| Social Media | Diabetes, Respiratory, Oncology patient voices |
| Competitor Intel | Sitagliptin, Pembrolizumab, Rivaroxaban, Pirfenidone, Tiotropium |

## 🧪 Technology Stack

- **LLM**: Groq Llama 3 70B (sub-second latency)
- **Agent Framework**: CrewAI with Hierarchical Process
- **Vector DB**: ChromaDB for RAG
- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Reports**: fpdf2, openpyxl

## 📄 License

Internal use only - Proprietary

---

Built with ❤️ for Pharmaceutical Innovation
