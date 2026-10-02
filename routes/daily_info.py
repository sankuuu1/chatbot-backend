from flask import Blueprint, jsonify, request
from services.weather_service import get_daily_info_payload

daily_info_bp = Blueprint("daily_info", __name__)


@daily_info_bp.route("/api/daily-info", methods=["GET", "OPTIONS"])
def daily_info():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    payload = get_daily_info_payload()
    return jsonify(payload), 200
