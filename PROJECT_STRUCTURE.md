# Project Structure

Clean, minimal structure with only essential files.

```
traffic-law-bot/
│
├── 📁 src/                          # Source code
│   ├── 📁 agents/                   # Agentic workflow
│   │   └── traffic_agent.py         # Main agent with guardrails & generation
│   │
│   ├── 📁 api/                      # REST API
│   │   └── main.py                  # FastAPI server with /ask endpoint
│   │
│   ├── 📁 ingestion/                # Document processing
│   │   ├── ingest.py                # Main ingestion script
│   │   └── document_processor.py    # PDF parsing & chunking
│   │
│   ├── 📁 retrieval/                # Vector search
│   │   └── retriever.py             # ChromaDB semantic search
│   │
│   └── 📁 ui/                       # User interface
│       └── app.py                   # Streamlit chat interface
│
├── 📁 config/                       # Configuration
│   └── settings.py                  # Environment settings & validation
│
├── 📁 data/                         # PDF documents (user-provided)
│   ├── mv_act_1988.pdf             # Motor Vehicles Act
│   ├── mv_amendment_2019.pdf       # 2019 Amendment
│   ├── cmvr_2026.pdf               # Central Motor Vehicles Rules
│   └── telangana_transport_rules.pdf
│
├── 📁 eval/                         # (Empty - for future testing)
│
├── 📁 chroma_db/                    # Vector store (auto-generated)
│   └── [ChromaDB files]             # Embeddings & metadata
│
├── 📄 .env                          # Environment variables (API keys)
├── 📄 .env.example                  # Environment template
├── 📄 .gitignore                    # Git ignore rules
│
├── 📄 README.md                     # GitHub README (main entry point)
├── 📄 DOCUMENTATION.md              # Complete technical documentation
├── 📄 PROJECT_STRUCTURE.md          # This file - project overview
│
└── 📄 requirements.txt              # Python dependencies

```

## File Descriptions

### Core Application Files

| File | Purpose | Lines |
|------|---------|-------|
| `src/agents/traffic_agent.py` | Orchestrates RAG workflow: guardrails → retrieve → generate → cite | ~100 |
| `src/retrieval/retriever.py` | Semantic search using ChromaDB vector store | ~50 |
| `src/ingestion/ingest.py` | Main script to load PDFs and build vector index | ~60 |
| `src/ingestion/document_processor.py` | PDF parsing, metadata extraction, chunking | ~100 |
| `src/api/main.py` | FastAPI REST API with /ask endpoint | ~50 |
| `src/ui/app.py` | Streamlit chat interface with source display | ~100 |
| `config/settings.py` | Pydantic settings with environment validation | ~40 |

### Documentation Files

| File | Purpose | Audience |
|------|---------|----------|
| `README.md` | GitHub landing page with quick start | Everyone |
| `DOCUMENTATION.md` | Complete technical deep-dive | Developers |
| `PROJECT_STRUCTURE.md` | Project organization overview | Contributors |

### Configuration Files

| File | Purpose |
|------|---------|
| `.env` | Your API keys and settings (not in git) |
| `.env.example` | Template for environment variables |
| `requirements.txt` | Python package dependencies |
| `.gitignore` | Files to exclude from git |

## Total Lines of Code

- **Application Code**: ~500 lines
- **Documentation**: ~1,500 lines
- **Configuration**: ~50 lines

**Total**: ~2,000 lines (very lightweight!)

## Dependencies

Only 10 packages in `requirements.txt`:
1. `google-generativeai` - Gemini API client
2. `sentence-transformers` - Embeddings
3. `chromadb` - Vector store
4. `pypdf` - PDF parsing
5. `python-magic-bin` - File type detection
6. `fastapi` - API framework
7. `uvicorn` - ASGI server
8. `streamlit` - UI framework
9. `python-dotenv` - Environment variables
10. `pydantic` + `pydantic-settings` - Configuration
11. `httpx` - HTTP client
12. `loguru` - Logging

## What's NOT Included

❌ No Docker files (removed for simplicity)
❌ No Ollama setup (using cloud API)
❌ No LlamaIndex/LangChain (direct implementation)
❌ No evaluation framework (kept minimal)
❌ No empty `__init__.py` files (modern Python doesn't need them)
❌ No complex build tools (just pip)

## Running the System

```bash
# 1. Ingest documents (one-time)
python -m src.ingestion.ingest

# 2. Start API server
python -m src.api.main

# 3. Start UI (in another terminal)
streamlit run src/ui/app.py
```

That's it! 🚀
