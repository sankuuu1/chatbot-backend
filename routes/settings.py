from flask import Blueprint, jsonify, request
from services.db_service import get_settings, update_settings, reset_settings

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/api/settings", methods=["GET", "POST", "OPTIONS"])
def handle_settings():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    if request.method == "GET":
        return jsonify(get_settings()), 200

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        updated = update_settings(data)
        return jsonify({"status": "success", "settings": updated}), 200


@settings_bp.route("/api/settings/reset", methods=["POST", "OPTIONS"])
def reset_user_settings():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    res = reset_settings()
    return jsonify({"status": "success", "settings": res}), 200
