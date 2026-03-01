from typing import Dict, List
import google.generativeai as genai
from loguru import logger
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from src.retrieval.retriever import SimpleRetriever

class TrafficLawAgent:
    """Lightweight agentic RAG with Gemini 2.5 Flash."""
    
    def __init__(self):
        # Initialize Gemini
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel(
            model_name=settings.llm_model,
            generation_config={
                "temperature": settings.llm_temperature,
                "max_output_tokens": settings.llm_max_tokens,
            }
        )
        self.retriever = SimpleRetriever()
        logger.info(f"✅ Initialized with {settings.llm_model}")
    
    def answer(self, query: str) -> Dict:
        """Main agentic workflow."""
        logger.info(f"Processing query: {query}")
        
        # Step 1: Guardrails
        if not self._is_valid_query(query):
            return {
                "answer": "I specialize in Indian traffic laws and fines. Please ask about traffic rules, challans, or penalties.",
                "sources": [],
                "confidence": "low"
            }
        
        # Step 2: Retrieve context
        results = self.retriever.retrieve(query, top_k=settings.top_k_retrieval)
        
        if not results:
            return {
                "answer": "I couldn't find relevant information. Please rephrase or check official sources like parivahan.gov.in",
                "sources": [],
                "confidence": "low"
            }
        
        # Step 3: Generate answer
        answer = self._generate_answer(query, results)
        
        # Step 4: Format response
        return {
            "answer": answer,
            "sources": self._format_sources(results),
            "confidence": "high" if len(results) >= 3 else "medium"
        }
    
    def _is_valid_query(self, query: str) -> bool:
        """Guardrail: check if query is traffic-related."""
        query_lower = query.lower()
        return any(topic in query_lower for topic in settings.allowed_topics)
    
    def _generate_answer(self, query: str, results: List[Dict]) -> str:
        """Generate grounded answer with citations using Gemini."""
        context = "\n\n".join([
            f"[Source {i+1}] {r['text']}\nMetadata: {r['metadata']}"
            for i, r in enumerate(results)
        ])
        
        prompt = f"""You are an expert on Indian traffic laws. Answer the question using ONLY the provided context.

CRITICAL RULES:
- Cite sources using [Source N] format
- If information is not in context, say "I don't have information about this"
- For fines, always mention the year/amendment if available
- Warn if data might be outdated (pre-2026)
- Be specific about Telangana/Hyderabad rules when mentioned

Context:
{context}

Question: {query}

Answer (with citations):"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return f"Error generating response: {str(e)}"
    
    def _format_sources(self, results: List[Dict]) -> List[Dict]:
        """Format sources for UI display."""
        sources = []
        for i, r in enumerate(results, 1):
            sources.append({
                "id": i,
                "text": r["text"][:200] + "...",
                "metadata": r["metadata"],
                "score": r.get("score", 0.0)
            })
        return sources
