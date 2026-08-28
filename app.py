import logging
import os
from typing import Literal, Optional

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pydantic import BaseModel, Field

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("bandhu")

DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

app = Flask(__name__)

# --- CORS ---
# Allow Firebase, Vercel, Localhost, or custom production domains seamlessly
_default_origins = "http://localhost:5173,http://127.0.0.1:5173,https://bandhu-ai-566ed.web.app,https://bandhu-ai-566ed.firebaseapp.com"
frontend_origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_URL", _default_origins).split(",")
    if origin.strip()
]
# If FRONTEND_URL is set to "*", allow all origins
if "*" in frontend_origins:
    CORS(app, resources={r"/*": {"origins": "*"}})
else:
    CORS(app, resources={r"/*": {"origins": frontend_origins}}, supports_credentials=True)

# --- Rate limiting ---
limiter = Limiter(get_remote_address, app=app, default_limits=[])

# --- LangChain / LLM Setup (Groq & Gemini) ---
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

llm = None
structured_llm = None
active_provider = "mock"
active_model = None
init_error = None


class ContentItem(BaseModel):
    label: str
    desc: str


class RichData(BaseModel):
    """Structured payload the frontend renders as a card. Omit fields that don't apply."""

    type: Literal["education", "farming", "health"]
    title: str
    content: Optional[list[ContentItem]] = Field(
        default=None, description="Education only: labeled concept breakdown."
    )
    formula: Optional[str] = Field(default=None, description="Education only: the formula, if any.")
    points: Optional[list[str]] = Field(
        default=None, description="Farming/health only: concise actionable bullet points."
    )


class ChatOutput(BaseModel):
    response: str = Field(description="The conversational reply, in Marathi.")
    rich_data: Optional[RichData] = Field(
        default=None,
        description=(
            "Only include when the answer benefits from a structured card "
            "(a formula/diagram, or a checklist of steps/points). Omit for simple conversational replies."
        ),
    )


# 1. Try Groq provider if selected or key is present
if LLM_PROVIDER == "groq" or (LLM_PROVIDER == "auto" and GROQ_API_KEY):
    from langchain_groq import ChatGroq
    groq_models_to_try = [GROQ_MODEL, "llama-3.1-8b-instant", "llama-3.2-3b-preview", "llama-3.3-70b-versatile", "mixtral-8x7b-32768"]
    # remove duplicates
    groq_models_to_try = list(dict.fromkeys(groq_models_to_try))

    for model_candidate in groq_models_to_try:
        try:
            llm = ChatGroq(
                model=model_candidate,
                groq_api_key=GROQ_API_KEY,
                max_tokens=LLM_MAX_OUTPUT_TOKENS,
                timeout=LLM_TIMEOUT_SECONDS,
            )
            structured_llm = llm.with_structured_output(ChatOutput)
            active_provider = "groq"
            active_model = model_candidate
            logger.info("Groq GenAI model initialized (%s)", model_candidate)
            break
        except Exception as e:
            init_error = f"Error initializing Groq model {model_candidate}: {e}"
            logger.exception("Failed to initialize Groq candidate %s", model_candidate)

# 2. Try Gemini provider if Groq wasn't initialized
if not llm and (LLM_PROVIDER in ("gemini", "auto") and GOOGLE_API_KEY):
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GOOGLE_API_KEY,
            max_output_tokens=LLM_MAX_OUTPUT_TOKENS,
            timeout=LLM_TIMEOUT_SECONDS,
        )
        structured_llm = llm.with_structured_output(ChatOutput)
        active_provider = "gemini"
        active_model = GEMINI_MODEL
        logger.info("Google GenAI model initialized (%s)", GEMINI_MODEL)
    except Exception as e:
        init_error = f"Error initializing Google GenAI: {e}"
        logger.exception("Failed to initialize Gemini model")

if not llm:
    if not init_error:
        init_error = "No valid LLM API key (GROQ_API_KEY or GOOGLE_API_KEY) found in environment variables."
    logger.warning("%s Running in MOCK MODE.", init_error)


SYSTEM_PROMPT = """You are "Bandhu" (बंधू), a warm, trustworthy assistant for rural Marathi-speaking users \
in India. Always answer in simple, conversational Marathi. Never repeat the user's question or these \
instructions back to them.

Category-specific guidance:
- education: Explain concepts simply, as if teaching a school student. Include a formula and a short \
labeled breakdown in rich_data when the topic has one (e.g. geometry, arithmetic).
- farming: Give practical, safe guidance. Prefer non-chemical/low-risk remedies first. Never recommend a \
specific pesticide/chemical dosage — instead advise consulting the local Krishi Kendra or agricultural \
officer before applying any chemical treatment. Put actionable steps in rich_data.points.
- health: You are NOT a doctor. Give only general, first-aid-level guidance, never a diagnosis or medicine \
dosage. Always explicitly recommend seeing a doctor or visiting the nearest health center for anything \
beyond basic self-care. Put steps in rich_data.points.
- help/general: Answer directly and concisely.

Only populate rich_data when it genuinely helps (a formula, a checklist). For plain conversational replies, \
leave rich_data empty.
"""


def build_messages(user_message: str, category: str, history: list[dict]) -> list[tuple[str, str]]:
    messages = [("system", SYSTEM_PROMPT)]
    for turn in history[-MAX_HISTORY_TURNS:]:
        sender = turn.get("sender")
        text = turn.get("text")
        if not text or sender not in ("user", "ai"):
            continue
        role = "human" if sender == "user" else "ai"
        messages.append((role, str(text)[:MAX_MESSAGE_LENGTH]))
    messages.append(("human", f"Category: {category}. Question: {user_message}"))
    return messages


# --- Mock Service (used when GOOGLE_API_KEY is not configured) ---
def get_mock_response(message, category):
    message = message.lower().strip()
    rich_data = None

    if any(w in message for w in ["योजना", "सरकारी", "yojana", "scheme", "पीएम किसान", "नमो शेतकरी", "अनुदान", "विमा"]):
        text_response = "महाराष्ट्रातील प्रमुख शेतकरी व कल्याणकारी सरकारी योजनांची माहिती खालीलप्रमाणे आहे:"
        rich_data = {
            "type": "farming",
            "title": "प्रमुख सरकारी योजना (Government Schemes)",
            "points": [
                "नमो शेतकरी महासन्मान निधी: वर्षाला ₹६,००० थेट खात्यात जमा.",
                "१ रुपयात सर्वसमावेशक पीक विमा योजना: नैसर्गिक आपत्तीत नुकसानभरपाई.",
                "मागेल त्याला विहीर / सौर कृषी पंप योजना: ९५% अनुदानावर सौर पंप.",
                "महाडीबीटी (MahaDBT): ट्रॅक्टर व औजारांवर ५०% पर्यंत अनुदान."
            ]
        }

    elif any(w in message for w in ["पाऊस", "weather", "हवामान", "rain"]):
        text_response = "नागपूर व विदर्भ भागात आज ढगाळ वातावरण असून संध्याकाळी पावसाची ७०% शक्यता आहे. शेतकऱ्यांनी फवारणी आज टाळावी."

    elif any(w in message for w in ["कापूस", "बाजारभाव", "bajarbhav", "भाव"]):
        text_response = "आज विदर्भातील मुख्य बाजार समित्यांमध्ये (नागपूर, वर्धा, यवतमाळ) उत्तम प्रतीच्या कापसाचा सरासरी बाजारभाव ₹६,९०० ते ₹७,४५० प्रति क्विंटल आहे."

    elif any(w in message for w in ["सोयाबीन", "soyabean"]):
        text_response = "सोयाबीन पिकासाठी सध्याच्या हवामानात पिवळा मोझॅक रोगापासून संरक्षणासाठी चिकट सापळे वापरावेत. बाजारभाव ₹४,३०० ते ₹४,७५० प्रति क्विंटल आहे."

    elif category == "education" or any(w in message for w in ["ganit", "triangle", "क्षेत्रफळ", "गणित", "शिक्षण"]):
        text_response = "त्रिकोणाचे क्षेत्रफळ काढणे खूप सोपे आहे! खालील सूत्र व माहिती नीट समजून घ्या:"
        rich_data = {
            "type": "education",
            "title": "त्रिकोणाचे क्षेत्रफळ (Area of a Triangle)",
            "diagram_type": "triangle",
            "content": [
                {"label": "पाया (Base)", "desc": "त्रिकोणाची खालची बाजू."},
                {"label": "उंची (Height)", "desc": "खालच्या बाजूपासून वरच्या टोकापर्यंतचे उभे अंतर."},
            ],
            "formula": "१/२ × पाया × उंची",
        }

    elif category == "farming" or any(w in message for w in ["kapus", "kid", "शेती", "कीड", "फवारणी"]):
        text_response = "तुमच्या पिकांवरील कीड नियंत्रणासाठी खालील महत्त्वाच्या टिप्स पाळा:"
        rich_data = {
            "type": "farming",
            "title": "कीड व रोग नियंत्रण मार्गदर्शक",
            "points": [
                "पिवळे व निळे चिकट सापळे एकरी १० लावावेत.",
                "सुरुवातीच्या टप्प्यात सेंद्रिय व निंबोळी अर्काची फवारणी करा.",
                "रासायनिक फवारणीपूर्वी कृषी सेवा केंद्राचा सल्ला घ्या."
            ],
        }

    elif category == "health" or any(w in message for w in ["आरोग्य", "ताप", "डॉक्टर", "आरोग्य सल्ला"]):
        text_response = "तुमची लक्षणे सांगा, मी प्राथमिक आरोग्य मार्गदर्शन करू शकतो."
        rich_data = {
            "type": "health",
            "title": "प्राथमिक आरोग्य सल्ला",
            "points": ["ताप असल्यास पुरेसा आराम करा व स्वच्छ पाणी प्या.", "गंभीर लक्षणे असल्यास जवळच्या शासकीय रुग्णालयात जा."],
        }

    elif any(w in message for w in ["hi", "hello", "hey", "namaskar", "नमस्कार", "हाय", "हेल्प", "help", "बंधू", "bandhu"]):
        text_response = "नमस्कार! मी बंधू. 🙏 सांगा, आज मी तुम्हाला कशी मदत करू शकतो? तुम्ही मला शेती, सरकारी योजना, हवामान किंवा अभ्यासाविषयी विचारू शकता."

    else:
        text_response = f"मी '{message}' या विषयावर तुम्हाला मदत करू शकतो! कृपया शेती, सरकारी योजना, हवामान, बाजारभाव किंवा शिक्षणाबद्दल विचारून पहा."

    return text_response, rich_data

    if category == "education" or "ganit" in message or "triangle" in message:
        text_response = "त्रिकोणाचे क्षेत्रफळ काढणे खूप सोपे आहे! खालील माहिती नीट समजून घ्या:"
        rich_data = {
            "type": "education",
            "title": "त्रिकोणाचे क्षेत्रफळ (Area of a Triangle)",
            "diagram_type": "triangle",
            "content": [
                {"label": "पाया (Base)", "desc": "त्रिकोणाची खालची बाजू."},
                {"label": "उंची (Height)", "desc": "खालच्या बाजूपासून वरच्या टोकापर्यंतचे उभे अंतर."},
            ],
            "formula": "१/२ × पाया × उंची",
        }

    elif category == "farming" or "kapus" in message or "kid" in message:
        text_response = "तुमच्या कपाशीवर 'पांढरी माशी' किंवा 'तुडतुडे' यांचा प्रादुर्भाव दिसतो आहे. यासाठी तुम्ही खालील उपाय करू शकता:"
        rich_data = {
            "type": "farming",
            "title": "कापसावरील कीड नियंत्रण",
            "points": [
                "पिवळे चिकट सापळे एकरी १० याप्रमाणे लावावेत.",
                "प्रादुर्भाव जास्त असल्यास निंबोळी अर्काची फवारणी करावी.",
                "कृषी केंद्रातून सल्ला घेऊनच रासायनिक औषधांचा वापर करा.",
            ],
        }

    elif category == "health":
        text_response = "तुमची लक्षणे सांगा, मी प्राथमिक तपासणी करू शकतो."
        rich_data = {
            "type": "health",
            "title": "आरोग्य सल्ला",
            "points": ["ताप आल्यास पाणी भरपूर प्या.", "विश्रांती घ्या."],
        }

    elif "hello" in message or "namaskar" in message:
        text_response = "नमस्कार! मी तुम्हाला कशी मदत करू शकते?"

    return text_response, rich_data


# --- Routes ---
@app.route("/chat", methods=["POST", "OPTIONS"])
@limiter.limit("20 per minute")
def chat():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.get_json(silent=True) or {}
    user_message = data.get("message")
    category = data.get("category") or "general"
    history = data.get("history") or []

    if not isinstance(user_message, str) or not user_message.strip():
        return jsonify({"error": "Message is required"}), 400
    if len(user_message) > MAX_MESSAGE_LENGTH:
        return jsonify({"error": f"Message too long (max {MAX_MESSAGE_LENGTH} characters)"}), 400
    if category not in ALLOWED_CATEGORIES:
        category = "general"
    if not isinstance(history, list):
        history = []

    logger.info("Chat request: category=%s message_len=%d provider=%s", category, len(user_message), active_provider)

    # Fast-path instant response for greetings (< 5ms response time!)
    clean_msg = user_message.strip().lower()
    greetings = {"hi", "hello", "hey", "namaskar", "नमस्कार", "हाय", "हेल्प", "help", "बंधू", "bandhu"}
    if clean_msg in greetings or clean_msg.startswith(("hi ", "hello ", "hey ", "नमस्कार", "हाय ")):
        return jsonify({
            "response": "नमस्कार! मी बंधू. 🙏\nसांगा, आज मी तुम्हाला कशी मदत करू शकतो? तुम्ही मला शेती, कीड, हवामान, बाजारभाव किंवा अभ्यासाविषयी काहीही विचारू शकता.",
            "rich_data": None
        }), 200

    if active_provider == "groq" and llm:
        try:
            messages = build_messages(user_message.strip(), category, history)
            result = llm.invoke(messages)
            content_str = str(result.content).strip()

            # Strip reasoning model think tags if present
            if "</think>" in content_str:
                content_str = content_str.split("</think>")[-1].strip()

            if content_str.startswith("```"):
                parts = content_str.split("```")
                if len(parts) >= 2:
                    content_str = parts[1]
                    if content_str.startswith("json"):
                        content_str = content_str[4:].strip()

            rich_data = None
            try:
                import json
                parsed = json.loads(content_str)
                if isinstance(parsed, dict):
                    text_response = parsed.get("response") or content_str
                    rich_data = parsed.get("rich_data")
                else:
                    text_response = content_str
            except Exception:
                text_response = content_str

            return jsonify({"response": text_response, "rich_data": rich_data}), 200
        except Exception as e:
            logger.exception("Groq GenAI invocation failed: %s", e)
            return jsonify({
                "response": f"Groq AI Error: {str(e)}. (Please verify your GROQ_API_KEY in Render settings)",
                "groq_error": str(e),
                "rich_data": None
            }), 200

    elif structured_llm:
        try:
            messages = build_messages(user_message.strip(), category, history)
            result: ChatOutput = structured_llm.invoke(messages)
            rich_data = result.rich_data.model_dump(exclude_none=True) if result.rich_data else None
            return jsonify({"response": result.response, "rich_data": rich_data})
        except Exception:
            logger.exception("GenAI invocation failed")
            return jsonify({"error": "सध्या उत्तर देता येत नाही, कृपया थोड्या वेळाने पुन्हा प्रयत्न करा."}), 502
    else:
        text_response, rich_data = get_mock_response(user_message, category)
        return jsonify({"response": text_response, "rich_data": rich_data})


DEFAULT_SETTINGS = {
    "name": "संतोष जाधव",
    "phone": "+919876543210",
    "speech_speed": 1.0,
    "auto_play_speech": True,
    "notifications_enabled": True,
    "crop_alerts_enabled": True,
    "dark_mode": False,
    "save_history": True,
}

user_settings = dict(DEFAULT_SETTINGS)


@app.route("/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "active",
            "provider": active_provider,
            "model": active_model,
            "mode": active_provider,
            "error": init_error,
            "groq_key_present": bool(GROQ_API_KEY),
            "google_key_present": bool(GOOGLE_API_KEY),
        }
    )


@app.route("/api/settings", methods=["GET", "POST", "OPTIONS"])
def handle_settings():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    if request.method == "GET":
        return jsonify(user_settings), 200

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        for key in DEFAULT_SETTINGS.keys():
            if key in data:
                user_settings[key] = data[key]
        logger.info("Settings updated: %s", user_settings)
        return jsonify({"status": "success", "settings": user_settings}), 200


@app.route("/api/settings/reset", methods=["POST", "OPTIONS"])
def reset_settings():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    global user_settings
    user_settings = dict(DEFAULT_SETTINGS)
    logger.info("Settings reset to defaults")
    return jsonify({"status": "success", "settings": user_settings}), 200


@app.route("/api/daily-info", methods=["GET", "OPTIONS"])
def daily_info():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    weather_data = {
        "temperature": 28,
        "condition": "ढगाळ वातावरण",
        "rain_probability": 70,
        "location": "नागपूर, महाराष्ट्र",
    }

    try:
        import urllib.request
        import json

        url = "https://api.open-meteo.com/v1/forecast?latitude=21.1458&longitude=79.0882&current=temperature_2m,relative_humidity_2m,weather_code&hourly=precipitation_probability&forecast_days=5"
        with urllib.request.urlopen(url, timeout=3) as resp:
            raw = json.loads(resp.read().decode())
            curr = raw.get("current", {})
            hourly_rain = raw.get("hourly", {}).get("precipitation_probability", [])
            if curr.get("temperature_2m") is not None:
                weather_data["temperature"] = round(curr.get("temperature_2m"))
            if hourly_rain:
                weather_data["rain_probability"] = max(hourly_rain[:12]) if len(hourly_rain) >= 12 else hourly_rain[0]
    except Exception as e:
        logger.warning("Failed to fetch live weather from Open-Meteo, using cached defaults: %s", e)

    response_payload = {
        "location": weather_data["location"],
        "weather": {
            "temperature": weather_data["temperature"],
            "condition": weather_data["condition"],
            "rain_probability": weather_data["rain_probability"],
            "unit": "अंश सेल्सिअस",
            "time_label": "आज",
        },
        "forecast": [
            {"day": "आज", "high": 31, "low": 23, "icon": "🌧️"},
            {"day": "उद्या", "high": 30, "low": 23, "icon": "🌧️"},
            {"day": "गुरु", "high": 32, "low": 24, "icon": "⛅"},
            {"day": "शुक्र", "high": 30, "low": 22, "icon": "⛅"},
        ],
        "advisory": {
            "title": "शेतकऱ्यांसाठी सूचना",
            "text": "आज पेरणी किंवा खत देण्यासाठी योग्य दिवस नाही.",
        },
        "articles": [
            {
                "id": "1",
                "category": "शेती",
                "category_key": "farming",
                "tag_color": "#E8F5E9",
                "tag_text_color": "#2E7D32",
                "title": "सोयाबीनच्या बाजारभावात वाढ",
                "subtitle": "विदर्भातील बाजारभावात आज बदल",
                "time_ago": "२ तासांपूर्वी",
                "image_url": "https://images.unsplash.com/photo-1599599810694-b5b37304c041?auto=format&fit=crop&w=300&q=80",
            },
            {
                "id": "2",
                "category": "शिक्षण",
                "category_key": "education",
                "tag_color": "#F3E5F5",
                "tag_text_color": "#7B1FA2",
                "title": "शिष्यवृत्ती अर्ज करण्याची अंतिम तारीख वाढली",
                "subtitle": "अर्ज करण्याची नवीन तारीख ३१ जुलै",
                "time_ago": "४ तासांपूर्वी",
                "image_url": "https://images.unsplash.com/photo-1577896851231-70ef18881754?auto=format&fit=crop&w=300&q=80",
            },
            {
                "id": "3",
                "category": "सरकारी योजना",
                "category_key": "schemes",
                "tag_color": "#FFF3E0",
                "tag_text_color": "#E65100",
                "title": "पीएम किसान योजनेचा १६ वा हप्ता लवकरच",
                "subtitle": "लाभार्थ्यांच्या खात्यात थेट जमा",
                "time_ago": "६ तासांपूर्वी",
                "image_url": "https://images.unsplash.com/photo-1592982537447-7440770cbfc9?auto=format&fit=crop&w=300&q=80",
            },
            {
                "id": "4",
                "category": "स्थानिक",
                "category_key": "local",
                "tag_color": "#E3F2FD",
                "tag_text_color": "#1565C0",
                "title": "नागपूर विभागात पुढील ३ दिवस मुसळधार पावसाचा इशारा",
                "subtitle": "हवामान खात्याचा यलो अलर्ट जारी",
                "time_ago": "१ तासापूर्वी",
                "image_url": "https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?auto=format&fit=crop&w=300&q=80",
            },
            {
                "id": "5",
                "category": "रोजगार",
                "category_key": "jobs",
                "tag_color": "#EFEBE9",
                "tag_text_color": "#4E342E",
                "title": "कृषी विभागात ५०० जागांसाठी नोकरभरती जाहीर",
                "subtitle": "ऑनलाइन अर्ज प्रक्रिया सुरू",
                "time_ago": "५ तासांपूर्वी",
                "image_url": "https://images.unsplash.com/photo-1521737711867-e3b97375f902?auto=format&fit=crop&w=300&q=80",
            },
        ],
    }
    return jsonify(response_payload), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=DEBUG, host="0.0.0.0", port=port)
