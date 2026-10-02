"""
Bandhu AI - Daily Weather & Advisory Routes
===========================================

Flask Blueprint endpoint for:
- GET /api/daily-info: Returns live weather forecast, agricultural advisory, and news articles.
"""

from flask import Blueprint, jsonify, request
from services.weather_service import get_daily_info_payload

daily_info_bp = Blueprint("daily_info", __name__)


# ==============================================================================
# ROUTE: GET /api/daily-info (Live Weather & Agricultural Advisory)
# ==============================================================================
@daily_info_bp.route("/api/daily-info", methods=["GET", "OPTIONS"])
def daily_info():
    """Returns live 5-day weather forecast from Open-Meteo API and agricultural advisories."""
    if request.method == "OPTIONS":
        return jsonify({}), 200

    payload = get_daily_info_payload()
    return jsonify(payload), 200
