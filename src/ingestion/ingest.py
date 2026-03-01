import argparse
from pathlib import Path
from loguru import logger
import chromadb
from sentence_transformers import SentenceTransformer
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from src.ingestion.document_processor import DocumentProcessor

def ingest_documents(data_dir: Path, force_rebuild: bool = False):
    """Ingest documents and build vector index."""
    logger.info(f"Starting ingestion from {data_dir}")
    
    # Initialize ChromaDB
    client = chromadb.PersistentClient(path=str(settings.vector_store_path))
    
    # Delete existing collection if force rebuild
    if force_rebuild:
        try:
            client.delete_collection("traffic_laws")
            logger.info("Deleted existing collection")
        except:
            pass
    
    # Create collection
    collection = client.get_or_create_collection(
        name="traffic_laws",
        metadata={"description": "Indian traffic laws and fines"}
    )
    
    # Initialize processor
    processor = DocumentProcessor(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )
    
    # Load all PDFs
    all_documents = []
    pdf_files = list(data_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.error(f"No PDF files found in {data_dir}")
        return
    
    for pdf_path in pdf_files:
        docs = processor.load_pdf(pdf_path)
        all_documents.extend(docs)
    
    # Chunk documents
    chunks = processor.chunk_documents(all_documents)
    
    logger.info(f"Processing {len(chunks)} chunks...")
    
    # Prepare data for ChromaDB
    documents = []
    metadatas = []
    ids = []
    
    for i, chunk in enumerate(chunks):
        documents.append(chunk.text)
        metadatas.append(chunk.metadata)
        ids.append(f"doc_{i}")
    
    # Add to collection (ChromaDB handles embeddings automatically)
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    logger.info(f"✅ Ingestion complete! Indexed {len(chunks)} chunks.")
    logger.info(f"Collection size: {collection.count()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=settings.data_dir)
    parser.add_argument("--force", action="store_true", help="Force rebuild index")
    args = parser.parse_args()
    
    ingest_documents(args.data_dir, args.force)
