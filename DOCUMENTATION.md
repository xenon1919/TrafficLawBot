# TrafficLawBot - Complete Technical Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [How It Works](#how-it-works)
4. [Components Explained](#components-explained)
5. [Data Flow](#data-flow)
6. [Setup & Configuration](#setup--configuration)
7. [Usage Guide](#usage-guide)
8. [Troubleshooting](#troubleshooting)

---

## System Overview

TrafficLawBot is an **Agentic RAG (Retrieval-Augmented Generation)** system that answers questions about Indian traffic laws, fines, and regulations. It's specifically focused on Telangana/Hyderabad compliance with 2026 updates.

### What is RAG?

RAG combines two powerful AI techniques:
1. **Retrieval**: Finding relevant information from a knowledge base (your PDFs)
2. **Generation**: Using an LLM to create natural language answers based on retrieved information

### Why "Agentic"?

The system acts like an intelligent agent with:
- **Guardrails**: Refuses non-traffic questions
- **Grounding**: Only answers from retrieved documents (no hallucination)
- **Citations**: Shows sources for every claim
- **Confidence scoring**: Tells you how reliable the answer is

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                        │
│                    (Streamlit Web App)                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                       FastAPI Server                         │
│                    (REST API Endpoint)                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    TrafficLawAgent                           │
│              (Agentic Workflow Orchestrator)                 │
│                                                              │
│  1. Guardrails Check → 2. Retrieve → 3. Generate → 4. Cite  │
└──────────┬──────────────────────────────────┬───────────────┘
           │                                  │
           ▼                                  ▼
┌──────────────────────┐          ┌──────────────────────────┐
│  SimpleRetriever     │          │   Gemini 1.5 Flash       │
│  (ChromaDB Search)   │          │   (Google AI API)        │
└──────────┬───────────┘          └──────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│                      ChromaDB Vector Store                    │
│              (Embedded PDF Chunks + Metadata)                 │
└──────────────────────────────────────────────────────────────┘
```

---

## How It Works

### Phase 1: Document Ingestion (One-Time Setup)

When you run `python -m src.ingestion.ingest`:

1. **Load PDFs**: Reads all PDF files from `data/` folder
   - Motor Vehicles Act 1988
   - MV Amendment Act 2019
   - Telangana Transport rules
   - Fine summaries

2. **Extract Text**: Uses `pypdf` to extract text page by page

3. **Extract Metadata**: Intelligently detects:
   - Section numbers (e.g., "Section 185")
   - Rule numbers (e.g., "Rule 138")
   - Fine amounts (e.g., "₹1,000")
   - Year/amendment info
   - State (Telangana/Hyderabad)
   - Document type (act, amendment, rules)

4. **Chunk Documents**: Breaks text into 512-word chunks with 50-word overlap
   - Why chunk? LLMs have token limits, and smaller chunks = better retrieval
   - Why overlap? Ensures context isn't lost at chunk boundaries

5. **Create Embeddings**: ChromaDB automatically converts text to vectors
   - Uses `all-MiniLM-L6-v2` model (384-dimensional vectors)
   - Embeddings capture semantic meaning (similar concepts = similar vectors)

6. **Store in ChromaDB**: Saves everything to `chroma_db/` folder
   - Text chunks
   - Embeddings (vectors)
   - Metadata (section, page, source, etc.)

### Phase 2: Query Processing (Every Question)

When a user asks: "What is the fine for riding without helmet in Hyderabad?"

#### Step 1: Guardrails Check
```python
# In TrafficLawAgent._is_valid_query()
allowed_topics = ["traffic", "challan", "fine", "helmet", "drunk driving", ...]
if any(topic in query.lower() for topic in allowed_topics):
    proceed()
else:
    reject("I specialize in traffic laws only")
```

**Why?** Prevents the system from answering off-topic questions.

#### Step 2: Retrieval
```python
# In SimpleRetriever.retrieve()
1. Convert query to embedding vector (same model as ingestion)
2. Search ChromaDB for top 5 most similar chunks (cosine similarity)
3. Return chunks with metadata and similarity scores
```

**Example Retrieved Chunks:**
```
[Source 1] Section 129: Wearing of protective headgear...
Penalty: ₹1,000 fine and/or disqualification of licence
Metadata: {section: "129", state: "TG", is_fine_table: true}

[Source 2] Telangana enforcement: Helmet violations...
Metadata: {source: "telangana_rules.pdf", page: 15}
```

**Why top 5?** Balance between context richness and token limits.

#### Step 3: Generate Answer
```python
# In TrafficLawAgent._generate_answer()
prompt = f"""
You are an expert on Indian traffic laws.
Answer using ONLY the provided context.

RULES:
- Cite sources using [Source N]
- If not in context, say "I don't have information"
- Mention year/amendment if available

Context:
{retrieved_chunks}

Question: {user_query}

Answer:
"""

response = gemini_model.generate_content(prompt)
```

**Gemini 1.5 Flash processes this and generates:**
```
In Hyderabad (Telangana), riding without a helmet carries a fine of ₹1,000 
under Section 129 of the Motor Vehicles Act [Source 1]. This is enforced 
strictly by Telangana traffic police [Source 2].
```

#### Step 4: Format Response
```python
return {
    "answer": generated_text,
    "sources": [
        {
            "id": 1,
            "text": "Section 129: Wearing of protective...",
            "metadata": {"section": "129", "state": "TG"},
            "score": 0.89
        },
        ...
    ],
    "confidence": "high"  # Based on number of sources found
}
```

---

## Components Explained

### 1. Document Processor (`src/ingestion/document_processor.py`)

**Purpose**: Converts raw PDFs into structured, searchable chunks.

**Key Functions:**

```python
load_pdf(pdf_path)
# - Opens PDF with pypdf
# - Extracts text page by page
# - Adds metadata (source, page number)
# Returns: List of Document objects

_extract_metadata(text, filename)
# - Uses regex to find section numbers: r'Section\s+(\d+)'
# - Detects fines: r'₹\s*\d+'
# - Identifies state: "telangana" or "hyderabad" in text
# Returns: Dictionary of metadata

chunk_documents(documents)
# - Splits text into 512-word chunks
# - Adds 50-word overlap between chunks
# - Preserves metadata for each chunk
# Returns: List of smaller Document chunks
```

**Why This Matters:**
- Good chunking = better retrieval accuracy
- Metadata enables filtering (e.g., "only Telangana rules")
- Section numbers help with precise citations

### 2. Simple Retriever (`src/retrieval/retriever.py`)

**Purpose**: Finds relevant document chunks for a query.

**How It Works:**

```python
class SimpleRetriever:
    def __init__(self):
        # Load embedding model (converts text → vectors)
        self.embed_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Connect to ChromaDB
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_collection("traffic_laws")
    
    def retrieve(self, query, top_k=5):
        # ChromaDB automatically:
        # 1. Converts query to embedding
        # 2. Computes cosine similarity with all stored embeddings
        # 3. Returns top_k most similar chunks
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        return formatted_results
```

**Similarity Calculation:**
```
Query: "helmet fine hyderabad"
Query Vector: [0.23, -0.45, 0.67, ...]  (384 dimensions)

Chunk 1: "Section 129 helmet penalty"
Chunk 1 Vector: [0.25, -0.43, 0.69, ...]
Similarity: 0.89 (very similar!)

Chunk 2: "Parking rules in Delhi"
Chunk 2 Vector: [-0.12, 0.78, -0.34, ...]
Similarity: 0.23 (not similar)
```

### 3. Traffic Law Agent (`src/agents/traffic_agent.py`)

**Purpose**: Orchestrates the entire RAG workflow.

**Workflow:**

```python
def answer(self, query):
    # Step 1: Guardrails
    if not self._is_valid_query(query):
        return rejection_message
    
    # Step 2: Retrieve
    results = self.retriever.retrieve(query, top_k=5)
    
    if not results:
        return "No information found"
    
    # Step 3: Generate
    answer = self._generate_answer(query, results)
    
    # Step 4: Format
    return {
        "answer": answer,
        "sources": formatted_sources,
        "confidence": calculate_confidence(results)
    }
```

**Confidence Scoring:**
```python
if len(results) >= 3 and avg_score > 0.8:
    confidence = "high"
elif len(results) >= 2:
    confidence = "medium"
else:
    confidence = "low"
```

### 4. FastAPI Server (`src/api/main.py`)

**Purpose**: Provides HTTP API for the agent.

```python
@app.post("/ask")
async def ask_question(request: QueryRequest):
    # Validates input (max 500 chars)
    # Calls agent.answer()
    # Returns JSON response
    
    return {
        "answer": "...",
        "sources": [...],
        "confidence": "high"
    }
```

**Why FastAPI?**
- Fast, modern Python web framework
- Automatic API documentation (visit `/docs`)
- Type validation with Pydantic
- Async support for concurrent requests

### 5. Streamlit UI (`src/ui/app.py`)

**Purpose**: User-friendly chat interface.

**Features:**
- Chat history (session state)
- Source expansion (click to see full context)
- Feedback buttons (👍/👎)
- Example questions sidebar
- Confidence indicators (🟢🟡🔴)

**How It Works:**
```python
if user_input:
    # Send to API
    response = httpx.post("http://localhost:8000/ask", 
                         json={"question": user_input})
    
    # Display answer
    st.markdown(response["answer"])
    
    # Show sources
    with st.expander("Sources"):
        for source in response["sources"]:
            st.text(source["text"])
            st.json(source["metadata"])
```

---

## Data Flow

### Complete Request Flow

```
1. USER TYPES QUESTION
   ↓
   "What is drunk driving penalty in Telangana?"
   
2. STREAMLIT UI
   ↓
   Sends HTTP POST to http://localhost:8000/ask
   
3. FASTAPI SERVER
   ↓
   Validates input, calls agent.answer()
   
4. TRAFFIC LAW AGENT
   ↓
   Checks guardrails: ✓ (traffic-related)
   
5. SIMPLE RETRIEVER
   ↓
   Query ChromaDB with "drunk driving penalty telangana"
   ↓
   Returns 5 most similar chunks:
   - Section 185 (score: 0.92)
   - Telangana enforcement (score: 0.87)
   - 2019 Amendment (score: 0.85)
   - Fine table (score: 0.81)
   - Repeat offence (score: 0.78)
   
6. GEMINI 1.5 FLASH
   ↓
   Receives prompt with context + question
   ↓
   Generates grounded answer with citations
   
7. AGENT FORMATS RESPONSE
   ↓
   {
     "answer": "Under Section 185...",
     "sources": [...],
     "confidence": "high"
   }
   
8. FASTAPI RETURNS JSON
   ↓
   
9. STREAMLIT DISPLAYS
   ↓
   Shows answer + expandable sources + confidence
```

---

## Setup & Configuration

### Environment Variables (`.env`)

```bash
# Your Gemini API key from https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=AIzaSy...

# Model selection
LLM_MODEL=gemini-1.5-flash-latest
# Options: gemini-1.5-flash-latest, gemini-1.5-pro-latest

# Embedding model (for vector search)
EMBEDDING_MODEL=all-MiniLM-L6-v2
# Lightweight, fast, good quality (384 dimensions)

# Retrieval settings
TOP_K_RETRIEVAL=5
# How many chunks to retrieve per query
# More = better context but slower + more tokens

CHUNK_SIZE=512
# Words per chunk
# Smaller = more precise, Larger = more context

CHUNK_OVERLAP=50
# Overlap between chunks to preserve context
```

### Why These Defaults?

**Gemini 1.5 Flash:**
- Free tier: 1,500 requests/day
- Fast: ~2-3 seconds
- Smart: Good at following instructions
- Cost-effective for production

**all-MiniLM-L6-v2:**
- Small model (80MB)
- Fast inference (CPU-friendly)
- Good quality for semantic search
- 384 dimensions (vs 768+ for larger models)

**TOP_K=5:**
- Balance between context and token usage
- 5 chunks ≈ 2,500 words ≈ 3,000 tokens
- Leaves room for question + answer in context window

**CHUNK_SIZE=512:**
- Typical paragraph length
- Not too small (loses context)
- Not too large (dilutes relevance)

---

## Usage Guide

### 1. Initial Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Add your API key to .env
# Edit .env and replace "your_gemini_api_key_here"

# Add PDF documents to data/ folder
# See data/README.md for recommended sources
```

### 2. Ingest Documents

```bash
python -m src.ingestion.ingest
```

**What happens:**
```
Loading PDF: data/mv_act_1988.pdf
Loaded 245 pages from mv_act_1988.pdf
Loading PDF: data/telangana_rules.pdf
Loaded 87 pages from telangana_rules.pdf
Created 1,847 chunks from 332 documents
Processing 1,847 chunks...
✅ Ingestion complete! Indexed 1,847 chunks.
Collection size: 1847
```

**To rebuild index:**
```bash
python -m src.ingestion.ingest --force
```

### 3. Start API Server

```bash
python -m src.api.main
```

**Output:**
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Test API:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is helmet fine?"}'
```

### 4. Start UI

```bash
streamlit run src/ui/app.py
```

**Opens browser at:** http://localhost:8501

### 5. Ask Questions

**Good Questions:**
- "What is the fine for riding without helmet in Hyderabad?"
- "Drunk driving penalty in Telangana 2026?"
- "What is Section 185 of Motor Vehicles Act?"
- "How to pay traffic challan online?"
- "What happens if I get 5 violations in a year?"

**Bad Questions (Will be rejected):**
- "What is the weather today?" (not traffic-related)
- "How to cook biryani?" (off-topic)
- "Tell me a joke" (not in scope)

---

## Troubleshooting

### Issue: "API key not valid"

**Cause:** Invalid or missing Gemini API key

**Solution:**
1. Get key from https://aistudio.google.com/app/apikey
2. Edit `.env` file
3. Replace `GOOGLE_API_KEY=your_key_here` with actual key
4. Restart API server

### Issue: "Collection not found"

**Cause:** ChromaDB index not created

**Solution:**
```bash
python -m src.ingestion.ingest
```

### Issue: "No PDFs found"

**Cause:** No PDF files in `data/` folder

**Solution:**
1. Download PDFs (see `data/README.md`)
2. Place in `data/` folder
3. Run ingestion

### Issue: "ModuleNotFoundError: No module named 'config'"

**Cause:** Python path issue

**Solution:** Already fixed in code with:
```python
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
```

### Issue: Slow responses

**Causes & Solutions:**

1. **Too many chunks retrieved**
   - Reduce `TOP_K_RETRIEVAL` in `.env` (try 3)

2. **Large chunk size**
   - Reduce `CHUNK_SIZE` to 256
   - Re-run ingestion

3. **Gemini API latency**
   - Normal: 2-3 seconds
   - Check internet connection
   - Try `gemini-1.5-flash-latest` (fastest)

### Issue: Poor answer quality

**Causes & Solutions:**

1. **Not enough context**
   - Increase `TOP_K_RETRIEVAL` to 7-10
   - Increase `CHUNK_SIZE` to 768

2. **Missing documents**
   - Add more PDFs to `data/`
   - Re-run ingestion

3. **Wrong model**
   - Try `gemini-1.5-pro-latest` (smarter but slower)

---

## Performance Metrics

### Typical Response Times

- **Retrieval**: 50-100ms (ChromaDB search)
- **LLM Generation**: 2-3 seconds (Gemini API)
- **Total**: 2-3 seconds per query

### Token Usage (per query)

- **Input**: ~3,000 tokens (context + question)
- **Output**: ~200-500 tokens (answer)
- **Total**: ~3,500 tokens per query

### Cost Estimates (Gemini 1.5 Flash)

**Free Tier:**
- 1,500 requests/day
- 1M tokens/minute
- Perfect for development + moderate use

**Paid Tier (if needed):**
- Input: $0.075 per 1M tokens
- Output: $0.30 per 1M tokens
- ~$0.0003 per query (very cheap!)

---

## Future Enhancements

### Planned Features

1. **Hybrid Search**: Add BM25 (keyword search) + reranking
2. **Query Decomposition**: Break complex questions into sub-queries
3. **Self-Critique**: LLM validates its own answers
4. **Feedback Loop**: Learn from 👍/👎 to improve retrieval
5. **Multilingual**: Support Telugu language queries
6. **Image Support**: Extract text from traffic sign images
7. **Evaluation**: RAGAS metrics for quality monitoring

### Scalability

**Current Setup:**
- Single server
- Local ChromaDB
- Good for: 10-100 users

**Production Setup:**
- Load balancer
- Hosted ChromaDB (Chroma Cloud)
- Redis caching
- Good for: 1,000+ users

---

## Conclusion

TrafficLawBot demonstrates a production-ready RAG system with:

✅ **Lightweight**: No heavy dependencies, runs on CPU
✅ **Accurate**: Grounded answers with citations
✅ **Fast**: 2-3 second responses
✅ **Cost-effective**: Free tier sufficient for most use
✅ **Maintainable**: Clean architecture, well-documented

The system can be adapted for any domain by:
1. Changing the PDFs in `data/`
2. Updating guardrails in `allowed_topics`
3. Customizing prompts in `traffic_agent.py`

**Questions?** Check the code comments or raise an issue!
