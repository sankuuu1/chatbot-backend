import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import config
from services.db_service import init_db
from services.llm_service import init_llm_providers, get_health_status
from routes.chat import chat_bp
from routes.daily_info import daily_info_bp
from routes.settings import settings_bp

logging.basicConfig(
    level=config.LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("bandhu")

app = Flask(__name__)

# --- CORS Setup ---
CORS(app, resources={r"/*": {"origins": "*"}})

# --- Rate Limiter ---
limiter = Limiter(get_remote_address, app=app, default_limits=[])
limiter.limit("20 per minute")(chat_bp)

# --- Database & LLM Initialization ---
init_db()
init_llm_providers()

# --- Register Blueprints ---
app.register_blueprint(chat_bp)
app.register_blueprint(daily_info_bp)
app.register_blueprint(settings_bp)


@app.route("/health", methods=["GET"])
def health():
    return jsonify(get_health_status()), 200


if __name__ == "__main__":
    logger.info("Starting Bandhu AI Backend on port %d...", config.PORT)
    app.run(debug=config.DEBUG, host="0.0.0.0", port=config.PORT)
