import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Logging level (optional override)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
try:
    logging.getLogger().setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
except Exception:
    pass

# Google Generative AI configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_DEFAULT_MODEL = os.getenv("GEMINI_DEFAULT_MODEL", "gemini-2.0-flash")
GEMINI_FAST_MODEL = os.getenv("GEMINI_FAST_MODEL", GEMINI_DEFAULT_MODEL)

# Configure Gemini once (safe if called multiple times)
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception:
        pass

# RAG/Knowledge base defaults (used by agents/rag_system.py)
KNOWLEDGE_BASE_PATH = os.getenv("KNOWLEDGE_BASE_PATH", "knowledge_base")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
FAISS_INDEX_FILE = os.getenv("FAISS_INDEX_FILE", "medical_index.faiss")
CHUNKS_FILE = os.getenv("CHUNKS_FILE", "medical_chunks.pkl")
