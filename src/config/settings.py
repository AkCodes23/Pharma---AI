"""
Pharma Agentic AI - Configuration Settings
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    MOCK_DATA_DIR: Path = BASE_DIR / "mock_data"
    REPORTS_DIR: Path = BASE_DIR / "reports"
    CHROMA_PERSIST_DIR: Path = BASE_DIR / "data" / "chroma_db"
    
    # Groq Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama3-70b-8192")
    
    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    def __init__(self):
        # Ensure directories exist
        self.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        self.CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> bool:
        """Validate required configuration."""
        if not self.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required. Set it in .env file.")
        return True


# Global settings instance
settings = Settings()
