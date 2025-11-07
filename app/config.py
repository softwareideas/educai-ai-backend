import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Google Generative AI
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Application Settings
CONTROLLER_GATE_ENABLED = os.getenv("CONTROLLER_GATE_ENABLED", "false").lower() == "true"
