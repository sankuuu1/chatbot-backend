# 🌾 Bandhu AI - Intelligent Rural AI Backend

**Bandhu AI (बंधू AI)** is a multi-lingual, voice-enabled AI assistant backend built for rural Indian users. It delivers real-time agricultural advisories, live weather insights via Open-Meteo, speech-to-text audio transcription via Groq Whisper, educational concept explanations with formula diagrams, and government scheme information in **Marathi (मराठी)**, **Hindi (हिंदी)**, and **English**.

---

## 🏗️ Repository Architecture

The backend is engineered with modular Flask Blueprints, service-oriented architecture, and SQLite data persistence.

```
chatbot-backend/
├── app.py                   # Main Flask application entry point & blueprint registration
├── config.py                # Environment configuration & model settings
├── models.py                # Pydantic schemas for LLM structured output parsing
├── bandhu_data.db           # SQLite database storing settings & chat logs
├── requirements.txt         # Python dependencies manifest
├── Procfile                 # Deployment process file (Render / Heroku)
├── render.yaml              # Render cloud infrastructure specification
│
├── routes/                  # API Endpoint Controllers (Flask Blueprints)
│   ├── __init__.py
│   ├── chat.py              # /chat & /api/transcribe endpoints
│   ├── daily_info.py        # /api/daily-info weather & news endpoint
│   └── settings.py          # /api/settings CRUD endpoints
│
└── services/                # Business Logic & Third-Party Integrations
    ├── __init__.py
    ├── llm_service.py       # LangChain & Groq LLaMA-3.3-70b orchestration engine
    ├── stt_service.py        # Groq Whisper audio transcription engine (STT)
    ├── weather_service.py    # Open-Meteo live weather API & Marathi advisory engine
    ├── db_service.py         # SQLite persistence engine for user profile & logs
    └── mock_service.py       # Local offline fallback provider
```

---

## ✨ Key Features

1. **Groq LLaMA-3.3-70B AI Engine**: Powered by Groq's high-speed inference for conversational responses with Pydantic structured card generation.
2. **Groq Whisper Audio Transcription**: Accepts WebM audio recordings from native voice mic and returns accurate Marathi transcription.
3. **Live Open-Meteo Weather API**: Fetches real-time temperature, humidity, wind speed, precipitation risk, and 5-day forecasts for Nagpur region with localized advisories.
4. **Multilingual System Prompts**: Native prompt engineering in Marathi, Hindi, and English with domain safety rules (e.g. non-chemical farming advice, Krishi Kendra recommendations).
5. **SQLite Persistence**: Automatic DB initialization and thread-safe persistence for user settings and chat logs.

---

## 🔌 API Endpoints Summary

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/health` | `GET` | System diagnostics & active LLM provider health |
| `/chat` | `POST` | AI conversational endpoint with rich card payload |
| `/api/transcribe` | `POST` | Groq Whisper speech-to-text audio transcription |
| `/api/daily-info` | `GET` | Live 5-day weather forecast & agricultural advisories |
| `/api/settings` | `GET / POST` | Fetch or update user profile settings |
| `/api/settings/reset` | `POST` | Reset user settings to default profile |

---

## 🛠️ Environment Variables Setup

Create a `.env` file in the root directory:

```env
FLASK_DEBUG=true
PORT=5000
LOG_LEVEL=INFO

# AI Provider API Keys
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Locally
```bash
python app.py
```
The server will start locally at `http://127.0.0.1:5000`.

---

## 📜 License
Developed for Bandhu AI rural assistant ecosystem.
