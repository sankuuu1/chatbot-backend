"""
Bandhu AI - User Settings Management Routes
============================================

Flask Blueprint endpoints for:
- GET /api/settings: Fetch user preferences from SQLite DB.
- POST /api/settings: Update user preferences in SQLite DB.
- POST /api/settings/reset: Reset user preferences back to default profile.
"""

from flask import Blueprint, jsonify, request
from services.db_service import get_settings, update_settings, reset_settings

settings_bp = Blueprint("settings", __name__)


# ==============================================================================
# ROUTE: GET & POST /api/settings (User Preferences Profile)
# ==============================================================================
@settings_bp.route("/api/settings", methods=["GET", "POST", "OPTIONS"])
def handle_settings():
    """Retrieves or updates user preference profile settings."""
    if request.method == "OPTIONS":
        return jsonify({}), 200

    if request.method == "GET":
        return jsonify(get_settings()), 200

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        updated = update_settings(data)
        return jsonify({"status": "success", "settings": updated}), 200


# ==============================================================================
# ROUTE: POST /api/settings/reset (Reset Settings Profile)
# ==============================================================================
@settings_bp.route("/api/settings/reset", methods=["POST", "OPTIONS"])
def reset_user_settings():
    """Resets user preference profile settings back to default values."""
    if request.method == "OPTIONS":
        return jsonify({}), 200

    res = reset_settings()
    return jsonify({"status": "success", "settings": res}), 200
