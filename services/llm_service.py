import logging
import config
from models import ChatOutput
from services.mock_service import get_mock_response

logger = logging.getLogger("bandhu.llm")

llm = None
structured_llm = None
active_provider = "mock"
active_model = None
init_error = None

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


def init_llm_providers():
    global llm, structured_llm, active_provider, active_model, init_error

    if config.LLM_PROVIDER == "groq" or (config.LLM_PROVIDER == "auto" and config.GROQ_API_KEY):
        try:
            from langchain_groq import ChatGroq
            groq_models = [config.GROQ_MODEL, "llama-3.3-70b-versatile", "llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"]
            groq_models = list(dict.fromkeys([m for m in groq_models if m]))

            for model_candidate in groq_models:
                try:
                    llm = ChatGroq(
                        model=model_candidate,
                        groq_api_key=config.GROQ_API_KEY,
                        max_tokens=config.LLM_MAX_OUTPUT_TOKENS,
                        timeout=config.LLM_TIMEOUT_SECONDS,
                    )
                    structured_llm = llm.with_structured_output(ChatOutput)
                    active_provider = "groq"
                    active_model = model_candidate
                    logger.info("Groq GenAI model initialized (%s)", model_candidate)
                    break
                except Exception as e:
                    init_error = f"Error initializing Groq model {model_candidate}: {e}"
                    logger.exception("Failed Groq candidate %s", model_candidate)
        except Exception as e:
            init_error = f"Groq package error: {e}"

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

    if not llm:
        if not init_error:
            init_error = "No valid LLM API key (GROQ_API_KEY or GOOGLE_API_KEY) found."
        logger.warning("%s Running in MOCK MODE.", init_error)


def build_messages(user_message: str, category: str, history: list[dict]) -> list[tuple[str, str]]:
    messages = [("system", SYSTEM_PROMPT)]
    for turn in (history or [])[-config.MAX_HISTORY_TURNS:]:
        sender = turn.get("sender")
        text = turn.get("text")
        if not text or sender not in ("user", "ai"):
            continue
        role = "human" if sender == "user" else "ai"
        messages.append((role, str(text)[:config.MAX_MESSAGE_LENGTH]))
    messages.append(("human", f"Category: {category}. Question: {user_message}"))
    return messages


def generate_chat_response(user_message: str, category: str, history: list[dict]):
    clean_msg = user_message.strip().lower()

    greetings = {"hi", "hello", "hey", "namaskar", "नमस्कार", "हाय", "हेल्प", "help", "बंधू", "bandhu"}
    if clean_msg in greetings or clean_msg.startswith(("hi ", "hello ", "hey ", "नमस्कार", "हाय ")):
        return {
            "response": "नमस्कार! मी बंधू. 🙏\nसांगा, आज मी तुम्हाला कशी मदत करू शकतो? तुम्ही मला शेती, कीड, हवामान, बाजारभाव किंवा अभ्यासाविषयी काहीही विचारू शकता.",
            "rich_data": None
        }, 200

    if active_provider == "groq" and llm:
        messages = build_messages(user_message.strip(), category, history)
        success_result = None
        try:
            success_result = llm.invoke(messages)
        except Exception as e1:
            logger.warning("Primary Groq model failed: %s. Trying fallback llama-3.3-70b-versatile...", e1)
            try:
                from langchain_groq import ChatGroq
                fallback_client = ChatGroq(
                    model="llama-3.3-70b-versatile",
                    groq_api_key=config.GROQ_API_KEY,
                    max_tokens=config.LLM_MAX_OUTPUT_TOKENS,
                    timeout=config.LLM_TIMEOUT_SECONDS,
                )
                success_result = fallback_client.invoke(messages)
            except Exception as e2:
                logger.exception("Fallback Groq model also failed: %s", e2)
                mock_text, mock_rich = get_mock_response(user_message, category)
                return {"response": mock_text, "rich_data": mock_rich, "groq_error": str(e2)}, 200

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

    elif structured_llm:
        try:
            messages = build_messages(user_message.strip(), category, history)
            result: ChatOutput = structured_llm.invoke(messages)
            rich_data = result.rich_data.model_dump(exclude_none=True) if result.rich_data else None
            return {"response": result.response, "rich_data": rich_data}, 200
        except Exception:
            logger.exception("GenAI invocation failed")
            return {"error": "सध्या उत्तर देता येत नाही, कृपया थोड्या वेळाने पुन्हा प्रयत्न करा."}, 502
    else:
        text_response, rich_data = get_mock_response(user_message, category)
        return {"response": text_response, "rich_data": rich_data}, 200


def get_health_status():
    return {
        "status": "active",
        "provider": active_provider,
        "model": active_model,
        "mode": active_provider,
        "error": init_error,
        "groq_key_present": bool(config.GROQ_API_KEY),
        "google_key_present": bool(config.GOOGLE_API_KEY),
    }
