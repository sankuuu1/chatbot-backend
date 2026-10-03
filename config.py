"""
Bandhu AI - Backend Configuration Module
========================================

Central configuration management loading environment variables from `.env`.
Defines API keys, CORS origins, model parameters, and application limits.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==============================================================================
# SERVER & ENVIRONMENT SETTINGS
# ==============================================================================
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
DEBUG: bool = os.getenv("FLASK_DEBUG", "false").lower() == "true"
PORT: int = int(os.getenv("PORT", 5000))

# ==============================================================================
# CORS ORIGIN CONFIGURATION
# ==============================================================================
_default_origins = (
    "http://localhost:5173,"
    "http://127.0.0.1:5173,"
    "https://bandhu-ai-566ed.web.app,"
    "https://bandhu-ai-566ed.firebaseapp.com,"
    "https://bandhuai.vercel.app"
)
FRONTEND_ORIGINS: list[str] = [
    origin.strip()
    for origin in os.getenv("FRONTEND_URL", _default_origins).split(",")
    if origin.strip()
]

# ==============================================================================
# AI PROVIDERS & CREDENTIALS
# ==============================================================================
GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY") or os.getenv("GROQ-API-KEY")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
CEDA_API_KEY: str = os.getenv("CEDA_API_KEY", "73efed17e89c0213ceb4c52e97ba4c97ad674b0f62829540ef29f5c53be6c2cc")
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "auto").lower()

# ==============================================================================
# LLM LIMITS & SYSTEM CONSTRAINTS
# ==============================================================================
LLM_TIMEOUT_SECONDS: int = int(os.getenv("LLM_TIMEOUT_SECONDS", "20"))
LLM_MAX_OUTPUT_TOKENS: int = int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "1024"))
MAX_MESSAGE_LENGTH: int = int(os.getenv("MAX_MESSAGE_LENGTH", "2000"))
MAX_HISTORY_TURNS: int = int(os.getenv("MAX_HISTORY_TURNS", "10"))

ALLOWED_CATEGORIES: set[str] = {"education", "farming", "health", "help", "general"}
