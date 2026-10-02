import os
import logging
import requests
from config import GROQ_API_KEY

logger = logging.getLogger("bandhu.stt")


def transcribe_audio_file(file_bytes: bytes, filename: str = "audio.webm") -> str:
    """Transcribes Marathi voice recording using Groq Whisper API."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not configured on server")

    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
    }
    files = {
        "file": (filename, file_bytes, "audio/webm"),
    }
    data = {
        "model": "whisper-large-v3-turbo",
        "language": "mr",
        "response_format": "json",
    }

    response = requests.post(url, headers=headers, files=files, data=data, timeout=15)
    response.raise_for_status()
    result = response.json()
    return result.get("text", "").strip()
