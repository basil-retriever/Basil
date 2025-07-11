import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    SCRAPED_PAGES_DIR = DATA_DIR / "scraped_pages"
    PROCESSED_DIR = DATA_DIR / "processed"
    CHROMA_DB_DIR = PROJECT_ROOT / "chroma_db"
    
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
    
    DEFAULT_MAX_PAGES = 50
    REQUEST_TIMEOUT = 10
    RATE_LIMIT_DELAY = 1
    
    CHROMA_COLLECTION_NAME = "website_content"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    
    OVERVIEW_FILE = "website_content_overview.md"
    SEARCH_SENTENCES_FILE = "search_sentences.md"
    
    @classmethod
    def validate(cls) -> bool:
        if not cls.GROQ_API_KEY:
            print("Warning: GROQ_API_KEY not set in environment variables")
            return False
        return True
    
    @classmethod
    def setup_directories(cls) -> None:
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.SCRAPED_PAGES_DIR.mkdir(exist_ok=True)
        cls.PROCESSED_DIR.mkdir(exist_ok=True)
        cls.CHROMA_DB_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def get_output_paths(cls):
        return {
            'overview': cls.PROCESSED_DIR / cls.OVERVIEW_FILE,
            'search_sentences': cls.PROCESSED_DIR / cls.SEARCH_SENTENCES_FILE
        }