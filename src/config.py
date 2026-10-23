import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables if .env exists
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_DOCS_DIR = DATA_DIR / "knowledge_docs"
CHROMA_PERSIST_DIR = DATA_DIR / "chroma_db"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
KNOWLEDGE_DOCS_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)

# LLM Providers Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
DEFAULT_LLM_PROVIDER = os.getenv("LLM_PROVIDER", "auto")

# Hotel Brand Constants
HOTEL_NAME = "The Grand Azure Resort & Spa"
HOTEL_LOCATION = "Azure Bay, Coastal Riviera"
HOTEL_STARS = 5
HOTEL_PHONE = "+1 (800) 555-AZURE"
HOTEL_EMAIL = "concierge@grandazureresort.com"
HOTEL_CHECK_IN = "3:00 PM"
HOTEL_CHECK_OUT = "11:00 AM"

# Embedding & Vector DB Config
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
CHROMA_COLLECTION_NAME = "hotel_knowledge_base"
DEFAULT_TOP_K = 4
