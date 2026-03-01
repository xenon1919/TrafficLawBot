from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict
from loguru import logger
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.agents.traffic_agent import TrafficLawAgent
from config.settings import settings

app = FastAPI(
    title="TrafficLawBot API",
    description="Agentic RAG for Indian Traffic Rules",
    version="1.0.0"
)

# Initialize agent (singleton)
agent = None

@app.on_event("startup")
async def startup():
    global agent
    logger.info("Starting TrafficLawBot API...")
    agent = TrafficLawAgent()
    logger.info("✅ API ready")

class QueryRequest(BaseModel):
    question: str = Field(..., max_length=500, description="Traffic law question")

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict]
    confidence: str

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """Ask a traffic law question."""
    try:
        result = agent.answer(request.question)
        return QueryResponse(**result)
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "model": settings.llm_model}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
