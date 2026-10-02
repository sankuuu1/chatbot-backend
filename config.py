import os
from dotenv import load_dotenv

load_dotenv()

# Environment settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
PORT = int(os.getenv("PORT", 5000))

# CORS Origins
_default_origins = "http://localhost:5173,http://127.0.0.1:5173,https://bandhu-ai-566ed.web.app,https://bandhu-ai-566ed.firebaseapp.com,https://bandhuai.vercel.app"
FRONTEND_ORIGINS = [
    origin.strip()
    for origin in os.getenv("FRONTEND_URL", _default_origins).split(",")
    if origin.strip()
]

# AI Credentials & Models
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("GROQ-API-KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "auto").lower()

LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "20"))
LLM_MAX_OUTPUT_TOKENS = int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "1024"))
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "2000"))
MAX_HISTORY_TURNS = int(os.getenv("MAX_HISTORY_TURNS", "10"))
ALLOWED_CATEGORIES = {"education", "farming", "health", "help", "general"}
