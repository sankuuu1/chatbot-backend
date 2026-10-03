"""
Bandhu AI - Government Schemes API Route
=======================================

Endpoints:
- GET /api/schemes: Returns list of government welfare schemes.
- POST /api/schemes/check-eligibility: Interactive rule-engine wizard matching eligible schemes.
"""

from flask import Blueprint, jsonify, request
from services.schemes_service import get_all_schemes, check_scheme_eligibility

schemes_bp = Blueprint("schemes", __name__)


@schemes_bp.route("/api/schemes", methods=["GET", "OPTIONS"])
def list_schemes():
    """Returns list of government schemes with optional category filter."""
    if request.method == "OPTIONS":
        return jsonify({}), 200

    category = request.args.get("category")
    try:
        data = get_all_schemes(category)
        return jsonify({"status": "success", "count": len(data), "schemes": data}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve schemes: {str(e)}"}), 500


@schemes_bp.route("/api/schemes/check-eligibility", methods=["POST", "OPTIONS"])
def check_eligibility():
    """Takes user profile parameters and returns matched eligible schemes."""
    if request.method == "OPTIONS":
        return jsonify({}), 200

    profile = request.get_json(silent=True) or {}
    try:
        eligible = check_scheme_eligibility(profile)
        return jsonify({
            "status": "success",
            "matched_count": len(eligible),
            "eligible_schemes": eligible
        }), 200
    except Exception as e:
        return jsonify({"error": f"Eligibility check failed: {str(e)}"}), 500
