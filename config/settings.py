from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Paths
    project_root: Path = Path(__file__).parent.parent
    data_dir: Path = project_root / "data"
    vector_store_path: Path = project_root / "chroma_db"
    
    # LLM API - Gemini
    google_api_key: str = ""
    llm_provider: str = "google"
    llm_model: str = "gemini-1.5-flash-latest"  # Gemini 1.5 Flash (latest stable)
    llm_temperature: float = 0.1
    llm_max_tokens: int = 2048
    
    # Embeddings (lightweight)
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Retrieval
    top_k_retrieval: int = 5
    chunk_size: int = 512
    chunk_overlap: int = 50
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Guardrails
    max_query_length: int = 500
    allowed_topics: list[str] = [
        "traffic", "challan", "fine", "penalty", "licence", "helmet",
        "drunk driving", "overspeeding", "signal", "parking", "rto"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env

settings = Settings()
