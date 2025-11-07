from flask import Blueprint, request, jsonify
import logging
from app.controllers import ask_controller
from app.config import GEMINI_MODEL, GOOGLE_API_KEY
from app.session import _runner

bp = Blueprint("api", __name__)

# Maximum request payload size (10MB)
MAX_CONTENT_LENGTH = 10 * 1024 * 1024


@bp.route("/ask", methods=["POST"])
def ask_route():
    """Handle POST requests to /ask endpoint."""
    try:
        # Check content length
        if request.content_length and request.content_length > MAX_CONTENT_LENGTH:
            return jsonify({
                "error": "Request payload too large",
                "max_size": MAX_CONTENT_LENGTH
            }), 413

        payload = request.get_json(silent=True) or {}
        out = ask_controller(payload)
        return jsonify(out), 200
    except Exception as e:
        logging.error("Error in ask_route: %s", str(e), exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "message": "An error occurred while processing your request"
        }), 500


@bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    ready = _runner is not None and bool(GOOGLE_API_KEY)
    status = "ready" if ready else "initializing"
    return jsonify({
        "status": status,
        "model": GEMINI_MODEL,
        "runner_initialized": _runner is not None,
        "has_api_key": bool(GOOGLE_API_KEY),
    }), 200 if ready else 503
