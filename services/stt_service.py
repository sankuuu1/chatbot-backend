"""
Bandhu AI - Speech-To-Text (STT) Service
=========================================

Provides high-accuracy voice transcription using Groq Whisper API (`whisper-large-v3-turbo`).
Optimized for Marathi and Indian regional accents.
"""

import logging
import requests
from config import GROQ_API_KEY

logger = logging.getLogger("bandhu.stt")


def transcribe_audio_file(file_bytes: bytes, filename: str = "audio.webm") -> str:
    """Transcribes audio recording using Groq Whisper API.

    Args:
        file_bytes (bytes): Raw audio binary data.
        filename (str): Name of the audio file (default: "audio.webm").

    Returns:
        str: Transcribed text string.

    Raises:
        ValueError: If GROQ_API_KEY is missing.
        HTTPError: If Groq API request fails.
    """
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
