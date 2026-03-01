from typing import List, Dict
import chromadb
from sentence_transformers import SentenceTransformer
from loguru import logger
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings

class SimpleRetriever:
    """Lightweight retriever using ChromaDB."""
    
    def __init__(self):
        logger.info("Initializing SimpleRetriever...")
        
        # Initialize embedding model (lightweight)
        self.embed_model = SentenceTransformer(settings.embedding_model)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=str(settings.vector_store_path))
        
        try:
            self.collection = self.client.get_collection("traffic_laws")
            logger.info(f"✅ Loaded collection with {self.collection.count()} documents")
        except:
            logger.warning("Collection not found. Run ingestion first.")
            self.collection = None
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve relevant documents."""
        if not self.collection:
            return []
        
        # Query the collection
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        # Format results
        formatted = []
        if results['documents'] and results['documents'][0]:
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                formatted.append({
                    "text": doc,
                    "metadata": metadata,
                    "score": 1 - distance  # Convert distance to similarity
                })
        
        logger.info(f"Retrieved {len(formatted)} documents for query: {query[:50]}...")
        return formatted
