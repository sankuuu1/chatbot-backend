"""
Bandhu AI - Chat & Audio Transcription Routes
==============================================

Flask Blueprint endpoints for:
- POST /chat: AI conversation endpoint supporting structured replies & history.
- POST /api/transcribe: Audio transcription endpoint using Groq Whisper.
"""

from flask import Blueprint, jsonify, request
import config
from services.llm_service import generate_chat_response
from services.stt_service import transcribe_audio_file
from services.db_service import log_chat

chat_bp = Blueprint("chat", __name__)


# ==============================================================================
# ROUTE: POST /chat (AI Conversation Endpoint)
# ==============================================================================
@chat_bp.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    """Handles user chat queries and returns AI text responses with optional rich cards."""
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.get_json(silent=True) or {}
    user_message = data.get("message")
    category = data.get("category") or "general"
    history = data.get("history") or []
    language = data.get("language") or "mr"

    # Input Validation
    if not isinstance(user_message, str) or not user_message.strip():
        return jsonify({"error": "Message is required"}), 400
    if len(user_message) > config.MAX_MESSAGE_LENGTH:
        return jsonify({"error": f"Message too long (max {config.MAX_MESSAGE_LENGTH} characters)"}), 400
    if category not in config.ALLOWED_CATEGORIES:
        category = "general"

    # Generate AI Response
    res_payload, status_code = generate_chat_response(user_message, category, history, language)

    # Persist log to SQLite DB
    if status_code == 200 and "response" in res_payload:
        log_chat(user_message, category, res_payload["response"])

    return jsonify(res_payload), status_code


# ==============================================================================
# ROUTE: POST /api/transcribe (Groq Whisper Speech-To-Text Endpoint)
# ==============================================================================
@chat_bp.route("/api/transcribe", methods=["POST", "OPTIONS"])
def transcribe():
    """Transcribes uploaded WebM audio blob into Marathi text using Groq Whisper."""
    if request.method == "OPTIONS":
        return jsonify({}), 200

    if "file" not in request.files:
        return jsonify({"error": "Audio file missing"}), 400

    audio_file = request.files["file"]
    file_bytes = audio_file.read()
    language = request.form.get("language") or "mr"

    try:
        text = transcribe_audio_file(file_bytes, audio_file.filename or "audio.webm", language=language)
        return jsonify({"text": text, "status": "success"}), 200
    except Exception as e:
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500
