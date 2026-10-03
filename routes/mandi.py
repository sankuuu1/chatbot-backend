"""
Bandhu AI - Agmarknet Mandi Rates Route
=======================================

Flask Blueprint endpoint:
- GET /api/mandi-rates: Returns latest APMC mandi rates for major crops in Maharashtra.
"""

from flask import Blueprint, jsonify, request
from services.mandi_service import get_latest_mandi_rates

mandi_bp = Blueprint("mandi", __name__)


@mandi_bp.route("/api/mandi-rates", methods=["GET", "OPTIONS"])
def mandi_rates():
    """Returns live and recent APMC Mandi rates for Maharashtra commodities."""
    if request.method == "OPTIONS":
        return jsonify({}), 200

    force_refresh = request.args.get("refresh", "false").lower() == "true"
    lang = request.args.get("lang", "mr")

    try:
        data = get_latest_mandi_rates(force_refresh=force_refresh)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve mandi rates: {str(e)}"}), 500
