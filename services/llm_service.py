"""
Bandhu AI - LLM Orchestration & Prompting Engine
=================================================

Orchestrates AI response generation using Groq (LLaMA-3.3-70b / LLaMA-3.1-8b) 
and Google Gemini GenAI providers, with automatic fallback handling to local mock service.
Supports multilingual prompts for Marathi, Hindi, and English.
"""

import logging
import config
from models import ChatOutput
from services.mock_service import get_mock_response

logger = logging.getLogger("bandhu.llm")

# Global LLM Instances
llm = None
structured_llm = None
active_provider = "mock"
active_model = None
init_error = None

# Multilingual System Prompts for AI Persona "Bandhu"
LANG_PROMPTS = {
    "mr": """You are "Bandhu" (बंधू), a warm, trustworthy assistant for rural Marathi-speaking users in India. \
Always answer in simple, conversational Marathi. Never repeat the user's question back to them.

Category guidance:
- education: Explain concepts simply. Include a formula and a short labeled breakdown in rich_data when applicable.
- farming: Give practical, safe guidance. Prefer non-chemical remedies. Never recommend specific pesticide dosages; advise consulting local Krishi Kendra.
- health: You are NOT a doctor. Give general first-aid guidance only and advise visiting a health center.
- help/general: Answer directly and concisely.

Only populate rich_data when it genuinely helps (a formula, a checklist). Leave rich_data empty for plain chat replies.""",

    "hi": """You are "Bandhu" (बंधु), a warm, trustworthy assistant for Hindi-speaking users in India. \
Always answer in simple, conversational Hindi. Never repeat the user's question back to them.

Category guidance:
- education: Explain concepts simply. Include a formula and a short labeled breakdown in rich_data when applicable.
- farming: Give practical, safe guidance. Prefer non-chemical remedies. Never recommend specific pesticide dosages; advise consulting local Krishi Kendra.
- health: You are NOT a doctor. Give general first-aid guidance only and advise visiting a health center.
- help/general: Answer directly and concisely.

Only populate rich_data when it genuinely helps (a formula, a checklist). Leave rich_data empty for plain chat replies.""",

    "en": """You are "Bandhu", a warm, trustworthy AI assistant for users in India. \
Always answer in clear, conversational English. Never repeat the user's question back to them.

Category guidance:
- education: Explain concepts simply. Include a formula and a short labeled breakdown in rich_data when applicable.
- farming: Give practical, safe guidance. Prefer non-chemical remedies. Never recommend specific pesticide dosages; advise consulting local Krishi Kendra.
- health: You are NOT a doctor. Give general first-aid guidance only and advise visiting a medical professional.
- help/general: Answer directly and concisely.

Only populate rich_data when it genuinely helps (a formula, a checklist). Leave rich_data empty for plain chat replies."""
}


def get_available_groq_models(api_key: str) -> list[str]:
    """Queries Groq API for available models in current organization."""
    try:
        import requests
        res = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=5
        )
        if res.status_code == 200:
            models_data = res.json().get("data", [])
            chat_models = [m["id"] for m in models_data if not m["id"].startswith("whisper") and not m["id"].startswith("meta-llama/llama-prompt-guard")]
            return chat_models
    except Exception as e:
        logger.warning("Could not fetch remote Groq models list: %s", e)
    return []


def init_llm_providers():
    """Initializes Groq and Google GenAI LLM clients with candidate model fallbacks."""
    global llm, structured_llm, active_provider, active_model, init_error

    # --- 1. Try Groq Initialization ---
    if config.LLM_PROVIDER == "groq" or (config.LLM_PROVIDER == "auto" and config.GROQ_API_KEY):
        try:
            from langchain_groq import ChatGroq
            available_remote = get_available_groq_models(config.GROQ_API_KEY)
            
            preferred_order = [
                config.GROQ_MODEL,
                "openai/gpt-oss-120b",
                "openai/gpt-oss-20b",
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "llama3-70b-8192",
                "llama3-8b-8192",
                "mixtral-8x7b-32768"
            ]

            groq_models = []
            # First match available remote models in preferred order
            for pref in preferred_order:
                if pref and pref in available_remote and pref not in groq_models:
                    groq_models.append(pref)
            # Add remaining remote models
            for rem in available_remote:
                if rem not in groq_models:
                    groq_models.append(rem)
            # Fallback to preferred list if remote check was empty
            for pref in preferred_order:
                if pref and pref not in groq_models:
                    groq_models.append(pref)

            for model_candidate in groq_models:
                try:
                    candidate_llm = ChatGroq(
                        model=model_candidate,
                        groq_api_key=config.GROQ_API_KEY,
                        max_tokens=config.LLM_MAX_OUTPUT_TOKENS,
                        timeout=config.LLM_TIMEOUT_SECONDS,
                    )
                    llm = candidate_llm
                    active_provider = "groq"
                    active_model = model_candidate
                    logger.info("Groq GenAI model initialized successfully with candidate (%s)", model_candidate)
                    break
                except Exception as e:
                    init_error = f"Error initializing Groq model {model_candidate}: {e}"
                    logger.warning("Failed Groq candidate %s: %s", model_candidate, e)
        except Exception as e:
            init_error = f"Groq package error: {e}"
            logger.exception("Groq init failed")


    # --- 2. Try Google Gemini Initialization ---
    if not llm and (config.LLM_PROVIDER in ("gemini", "auto") and config.GOOGLE_API_KEY):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            llm = ChatGoogleGenerativeAI(
                model=config.GEMINI_MODEL,
                google_api_key=config.GOOGLE_API_KEY,
                max_output_tokens=config.LLM_MAX_OUTPUT_TOKENS,
                timeout=config.LLM_TIMEOUT_SECONDS,
            )
            structured_llm = llm.with_structured_output(ChatOutput)
            active_provider = "gemini"
            active_model = config.GEMINI_MODEL
            logger.info("Google GenAI model initialized (%s)", config.GEMINI_MODEL)
        except Exception as e:
            init_error = f"Error initializing Google GenAI: {e}"
            logger.exception("Failed to initialize Gemini model")

    # --- 3. Fallback to Mock Mode ---
    if not llm:
        if not init_error:
            init_error = "No valid LLM API key (GROQ_API_KEY or GOOGLE_API_KEY) found."
        logger.warning("%s Running in MOCK MODE.", init_error)


def build_messages(user_message: str, category: str, history: list[dict], language: str = "mr") -> list[tuple[str, str]]:
    """Builds system, conversational history, and current turn prompt tuples for LangChain."""
    sys_prompt = LANG_PROMPTS.get(language, LANG_PROMPTS["mr"])
    messages = [("system", sys_prompt)]

    for turn in (history or [])[-config.MAX_HISTORY_TURNS:]:
        sender = turn.get("sender")
        text = turn.get("text")
        if not text or sender not in ("user", "ai"):
            continue
        role = "human" if sender == "user" else "ai"
        messages.append((role, str(text)[:config.MAX_MESSAGE_LENGTH]))

    messages.append(("human", f"Category: {category}. Question: {user_message}"))
    return messages


def generate_chat_response(user_message: str, category: str, history: list[dict], language: str = "mr") -> tuple[dict, int]:
    """Generates AI chat reply with structured rich_data payload."""
    clean_msg = user_message.strip().lower()

    # Fast path: instant warm greeting matching requested language
    greetings_keywords = {"hi", "hello", "hey", "namaskar", "नमस्कार", "हाय", "हेल्प", "help", "बंधू", "bandhu"}
    if clean_msg in greetings_keywords or clean_msg.startswith(("hi ", "hello ", "hey ", "नमस्कार", "हाय ")):
        if language == "en":
            greeting_resp = "Hello! I am Bandhu. 🙏\nHow can I help you today? You can ask me about farming, crop pests, weather, market rates, or education."
        elif language == "hi":
            greeting_resp = "नमस्ते! मैं बंधु हूँ। 🙏\nबताइए, आज मैं आपकी क्या सहायता कर सकता हूँ? आप मुझसे कृषि, कीट नियंत्रण, मौसम, मंडी भाव या शिक्षा के बारे में पूछ सकते हैं।"
        else:
            greeting_resp = "नमस्कार! मी बंधू. 🙏\nसांगा, आज मी तुम्हाला कशी मदत करू शकतो? तुम्ही मला शेती, कीड, हवामान, बाजारभाव किंवा अभ्यासाविषयी काहीही विचारू शकता."

        return {"response": greeting_resp, "rich_data": None}, 200

    # Execute Groq LLM model call
    if active_provider == "groq" and llm:
        messages = build_messages(user_message.strip(), category, history, language)
        success_result = None
        try:
            success_result = llm.invoke(messages)
        except Exception as e1:
            logger.warning("Primary Groq model failed: %s. Trying candidate fallbacks...", e1)
            candidate_fallbacks = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
            for fb_model in candidate_fallbacks:
                if fb_model == active_model:
                    continue
                try:
                    from langchain_groq import ChatGroq
                    fallback_client = ChatGroq(
                        model=fb_model,
                        groq_api_key=config.GROQ_API_KEY,
                        max_tokens=config.LLM_MAX_OUTPUT_TOKENS,
                        timeout=config.LLM_TIMEOUT_SECONDS,
                    )
                    success_result = fallback_client.invoke(messages)
                    if success_result and success_result.content:
                        break
                except Exception as fb_err:
                    logger.warning("Fallback Groq model %s failed: %s", fb_model, fb_err)

            if not success_result:
                mock_text, mock_rich = get_mock_response(user_message, category, language)
                return {"response": mock_text, "rich_data": mock_rich, "groq_error": str(e1)}, 200

        content_str = str(success_result.content).strip()
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

        return {"response": text_response, "rich_data": rich_data}, 200

    # Structured Output execution for Gemini or other structured LLMs
    elif structured_llm:
        try:
            messages = build_messages(user_message.strip(), category, history, language)
            result: ChatOutput = structured_llm.invoke(messages)
            rich_data = result.rich_data.model_dump(exclude_none=True) if result.rich_data else None
            return {"response": result.response, "rich_data": rich_data}, 200
        except Exception:
            logger.exception("GenAI invocation failed")
            return {"error": "Unable to process response currently."}, 502

    # Offline Mock Fallback
    else:
        text_response, rich_data = get_mock_response(user_message, category, language)
        return {"response": text_response, "rich_data": rich_data}, 200


def get_health_status() -> dict:
    """Returns runtime diagnostic information about active LLM providers."""
    return {
        "status": "active",
        "provider": active_provider,
        "model": active_model,
        "mode": active_provider,
        "error": init_error,
        "groq_key_present": bool(config.GROQ_API_KEY),
        "google_key_present": bool(config.GOOGLE_API_KEY),
    }
