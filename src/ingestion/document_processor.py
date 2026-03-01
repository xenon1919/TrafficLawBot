from pathlib import Path
from typing import List, Dict, NamedTuple
from pypdf import PdfReader
from loguru import logger
import re

class Document(NamedTuple):
    text: str
    metadata: Dict

class DocumentProcessor:
    """Lightweight document processing with metadata extraction."""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def load_pdf(self, pdf_path: Path) -> List[Document]:
        """Load PDF and extract text with metadata."""
        logger.info(f"Loading PDF: {pdf_path}")
        reader = PdfReader(pdf_path)
        documents = []
        
        for page_num, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            if not text.strip():
                continue
            
            # Extract metadata from content
            metadata = self._extract_metadata(text, pdf_path.stem)
            metadata.update({
                "source": pdf_path.name,
                "page": page_num,
                "doc_type": self._infer_doc_type(pdf_path.stem)
            })
            
            documents.append(Document(text=text, metadata=metadata))
        
        logger.info(f"Loaded {len(documents)} pages from {pdf_path.name}")
        return documents
    
    def _extract_metadata(self, text: str, filename: str) -> Dict:
        """Extract structured metadata from text."""
        metadata = {}
        
        # Extract section numbers
        section_match = re.search(r'Section\s+(\d+[A-Z]?)', text, re.IGNORECASE)
        if section_match:
            metadata["section_number"] = section_match.group(1)
        
        rule_match = re.search(r'Rule\s+(\d+)', text, re.IGNORECASE)
        if rule_match:
            metadata["rule_number"] = rule_match.group(1)
        
        # Detect fine/penalty table
        if re.search(r'(fine|penalty|punishment|₹\s*\d+)', text, re.IGNORECASE):
            metadata["is_fine_table"] = "true"
        
        # Extract year
        year_match = re.search(r'(19|20)\d{2}', text)
        if year_match:
            metadata["year"] = year_match.group(0)
        
        # State detection
        if "telangana" in text.lower() or "hyderabad" in text.lower():
            metadata["state"] = "TG"
        
        return metadata
    
    def _infer_doc_type(self, filename: str) -> str:
        """Infer document type from filename."""
        filename_lower = filename.lower()
        if "motor" in filename_lower and "act" in filename_lower:
            return "act"
        elif "amendment" in filename_lower:
            return "amendment"
        elif "rule" in filename_lower or "cmvr" in filename_lower:
            return "rules"
        elif "telangana" in filename_lower or "hyderabad" in filename_lower:
            return "state_rules"
        return "general"
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Simple chunking with overlap."""
        chunks = []
        
        for doc in documents:
            text = doc.text
            words = text.split()
            
            # Simple word-based chunking
            for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
                chunk_words = words[i:i + self.chunk_size]
                chunk_text = " ".join(chunk_words)
                
                if chunk_text.strip():
                    chunks.append(Document(text=chunk_text, metadata=doc.metadata))
        
        logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
        return chunks
