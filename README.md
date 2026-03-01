# 🚦 TrafficLawBot - Agentic RAG for Indian Traffic Rules

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Gemini](https://img.shields.io/badge/Powered%20by-Gemini%201.5%20Flash-4285F4?logo=google)](https://ai.google.dev/)

> An intelligent assistant for querying Indian traffic laws, penalties, and Telangana/Hyderabad compliance (2026 Edition). Built with production-grade RAG architecture, grounded answers, and citation tracking.


## ✨ Features

- 🤖 **Agentic RAG**: Intelligent retrieval with guardrails and self-validation
- 📚 **Grounded Answers**: Every response backed by official documents with citations
- ⚡ **Lightning Fast**: 2-3 second responses using Gemini 1.5 Flash
- 🎯 **Domain-Specific**: Specialized in Indian traffic laws (Motor Vehicles Act, CMVR, state rules)
- 💰 **Cost-Effective**: Free tier supports 1,500 requests/day
- 🔍 **Smart Search**: Semantic search with ChromaDB vector store
- 🌐 **Web Interface**: Clean Streamlit UI with source highlighting
- 📊 **Confidence Scoring**: Know how reliable each answer is

## 🎯 Use Cases

- **Citizens**: Understand traffic fines, penalties, and rules
- **Lawyers**: Quick reference for Motor Vehicles Act sections
- **Police**: Verify fine amounts and legal provisions
- **Developers**: Learn production RAG implementation
- **Students**: Study agentic AI systems

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Google Gemini API key ([Get it free](https://aistudio.google.com/app/apikey))
- PDF documents (Motor Vehicles Act, state rules, etc.)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/xenon1919/TrafficLawBot.git
cd TrafficLawBot

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API key
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# 5. Add PDF documents to data/ folder

# 6. Ingest documents (one-time setup)
python -m src.ingestion.ingest

# 7. Start the API server
python -m src.api.main

# 8. In another terminal, start the UI
streamlit run src/ui/app.py
```

Visit http://localhost:8501 and start asking questions! 🎉

See [DOCUMENTATION.md](DOCUMENTATION.md) for detailed technical documentation.

## 💬 Example Queries

```
❓ "What is the fine for riding without helmet in Hyderabad?"
✅ In Hyderabad (Telangana), riding without a helmet carries a fine of ₹1,000 
   under Section 129 of the Motor Vehicles Act [Source 1]...

❓ "Drunk driving penalty in Telangana 2026?"
✅ For first-time drunk driving offence, the penalty is ₹10,000 fine and/or 
   up to 6 months imprisonment under Section 185 [Source 2]...

❓ "What happens if I get 5 violations in a year?"
✅ Under the 2026 CMVR amendment, accumulating 5+ traffic violations in a year 
   may result in licence suspension [Source 3]...
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Web UI                          │
│              (Chat Interface + Source Display)               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI REST API                          │
│                  (/ask endpoint + docs)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  TrafficLawAgent                             │
│   Guardrails → Retrieve → Generate → Cite → Confidence      │
└──────────┬──────────────────────────────────┬───────────────┘
           │                                  │
           ▼                                  ▼
┌──────────────────────┐          ┌──────────────────────────┐
│  ChromaDB Retriever  │          │   Gemini 1.5 Flash       │
│  (Semantic Search)   │          │   (Answer Generation)    │
└──────────┬───────────┘          └──────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│              ChromaDB Vector Store                            │
│        (1,800+ chunks from official documents)                │
└──────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
traffic-law-bot/
├── src/
│   ├── agents/              # Agentic workflow orchestration
│   │   └── traffic_agent.py # Main agent with guardrails
│   ├── retrieval/           # Vector search & retrieval
│   │   └── retriever.py     # ChromaDB semantic search
│   ├── ingestion/           # Document processing pipeline
│   │   ├── ingest.py        # Main ingestion script
│   │   └── document_processor.py  # PDF parsing & chunking
│   ├── api/                 # FastAPI REST endpoints
│   │   └── main.py          # API server
│   └── ui/                  # User interface
│       └── app.py           # Streamlit chat app
├── data/                    # PDF documents (add your files here)
├── config/                  # Configuration management
│   └── settings.py          # Environment settings
├── chroma_db/              # Vector store (auto-generated)
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── DOCUMENTATION.md       # Complete technical docs
├── PROJECT_STRUCTURE.md   # Project organization
└── README.md             # This file
```

## 🛠️ Tech Stack

| Component | Technology | Why? |
|-----------|-----------|------|
| **LLM** | Gemini 1.5 Flash | Fast, free tier, excellent at citations |
| **Embeddings** | all-MiniLM-L6-v2 | Lightweight (80MB), CPU-friendly, good quality |
| **Vector DB** | ChromaDB | Simple, local-first, auto-embeddings |
| **API** | FastAPI | Modern, fast, auto-docs, type-safe |
| **UI** | Streamlit | Rapid prototyping, interactive widgets |
| **PDF Parser** | pypdf | Pure Python, no dependencies |

## 📊 Performance

| Metric | Value |
|--------|-------|
| Response Time | 2-3 seconds |
| Retrieval Speed | 50-100ms |
| Tokens per Query | ~3,500 |
| Cost per Query | ~$0.0003 (paid tier) |
| Free Tier Limit | 1,500 requests/day |
| Accuracy | High (grounded in documents) |

## 🎓 How It Works

### 1. Document Ingestion (One-Time)

```python
# Load PDFs → Extract text → Detect metadata → Chunk → Embed → Store
python -m src.ingestion.ingest
```

- Loads PDFs from `data/` folder
- Extracts metadata (sections, fines, state, year)
- Chunks into 512-word segments with 50-word overlap
- Creates embeddings using sentence-transformers
- Stores in ChromaDB with metadata

### 2. Query Processing (Every Request)

```python
User Question → Guardrails → Retrieve Top 5 Chunks → Generate Answer → Cite Sources
```

1. **Guardrails**: Rejects non-traffic questions
2. **Retrieval**: Semantic search in ChromaDB (cosine similarity)
3. **Generation**: Gemini creates grounded answer with citations
4. **Validation**: Confidence scoring based on source quality

See [DOCUMENTATION.md](DOCUMENTATION.md) for detailed explanation.

## 🔧 Configuration

Edit `.env` to customize:

```bash
# LLM Settings
GOOGLE_API_KEY=your_key_here
LLM_MODEL=gemini-1.5-flash-latest  # or gemini-1.5-pro-latest

# Retrieval Settings
TOP_K_RETRIEVAL=5        # Number of chunks to retrieve
CHUNK_SIZE=512          # Words per chunk
CHUNK_OVERLAP=50        # Overlap between chunks

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
```

## 📚 Data Sources

Add these PDFs to `data/` folder:

1. **Motor Vehicles Act 1988** (consolidated) - [indiacode.nic.in](https://www.indiacode.nic.in/)
2. **Motor Vehicles Amendment Act 2019** - Official gazette
3. **Central Motor Vehicles Rules** - [morth.nic.in](https://morth.nic.in/)
4. **Telangana Transport Rules** - [transport.telangana.gov.in](https://transport.telangana.gov.in/)
5. **Fine Summaries** - Verified from GoDigit, Acko, PolicyBazaar

## 🧪 Testing

```bash
# Test API endpoint
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is helmet fine in Hyderabad?"}'

# Check API docs
open http://localhost:8000/docs
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key not valid" | Get new key from [Google AI Studio](https://aistudio.google.com/app/apikey) |
| "Collection not found" | Run `python -m src.ingestion.ingest` first |
| "No PDFs found" | Add PDF files to `data/` folder |
| Slow responses | Reduce `TOP_K_RETRIEVAL` to 3 in `.env` |
| Poor answers | Add more PDFs or increase `CHUNK_SIZE` |

See [DOCUMENTATION.md](DOCUMENTATION.md#troubleshooting) for more.

## 🚀 Deployment

### Local Development
```bash
python -m src.api.main  # API on :8000
streamlit run src/ui/app.py  # UI on :8501
```

### Cloud Deployment
- **API**: Deploy to Railway, Render, or Fly.io
- **Vector DB**: Use Chroma Cloud for hosted storage
- **UI**: Deploy Streamlit to Streamlit Cloud

## 🤝 Contributing

Contributions welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
pip install -r requirements.txt
pip install black ruff pytest  # Dev tools
black src/  # Format code
ruff check src/  # Lint code
```

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini** for providing excellent free-tier LLM API
- **ChromaDB** for simple, powerful vector search
- **Sentence Transformers** for lightweight embeddings
- **Indian Government** for making traffic laws publicly accessible

## 📧 Contact

- **GitHub**: [@xenon1919](https://github.com/xenon1919)
- **Repository**: [TrafficLawBot](https://github.com/xenon1919/TrafficLawBot)

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=xenon1919/TrafficLawBot&type=Date)](https://star-history.com/#xenon1919/TrafficLawBot&Date)

## 📈 Roadmap

- [x] Basic RAG implementation
- [x] Gemini 1.5 Flash integration
- [x] Streamlit UI
- [x] Citation tracking
- [ ] Hybrid search (BM25 + semantic)
- [ ] Query decomposition for complex questions
- [ ] Self-critique loop
- [ ] Feedback collection & learning
- [ ] Telugu language support
- [ ] Image-based queries (traffic signs)
- [ ] RAGAS evaluation metrics
- [ ] Docker deployment
- [ ] API rate limiting
- [ ] User authentication

## 💡 Related Projects

- [LangChain](https://github.com/langchain-ai/langchain) - LLM application framework
- [LlamaIndex](https://github.com/run-llama/llama_index) - Data framework for LLMs
- [ChromaDB](https://github.com/chroma-core/chroma) - AI-native vector database
- [Streamlit](https://github.com/streamlit/streamlit) - Fast web apps for ML

---

<div align="center">

**Built with ❤️ for safer roads in India**

[Documentation](DOCUMENTATION.md) • [Project Structure](PROJECT_STRUCTURE.md) • [Report Bug](https://github.com/xenon1919/TrafficLawBot/issues) • [Request Feature](https://github.com/xenon1919/TrafficLawBot/issues)

</div>
