from flask import Flask, request, g
from flask_cors import CORS
from dotenv import load_dotenv
import logging
import os

# Load environment from .env if present (GOOGLE_API_KEY, SERPER_API_KEY, ADK_MODEL, PORT, etc.)
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

from app.routes import bp
from app.config import GOOGLE_API_KEY


def create_app() -> Flask:
    app = Flask(__name__)
    # Enforce 10MB max payload globally (mirrors route-level check)
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
    
    # Validate required environment variables
    if not GOOGLE_API_KEY:
        logging.warning("GOOGLE_API_KEY is not set. The application may not work correctly.")
        logging.warning("Please set GOOGLE_API_KEY in your .env file or environment variables.")
    
    # Configure CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(bp)

    # Request ID middleware for traceability
    import uuid

    @app.before_request
    def _assign_request_id():
        rid = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        g.request_id = rid

    @app.after_request
    def _attach_request_id(response):
        rid = getattr(g, "request_id", None)
        if rid:
            response.headers["X-Request-ID"] = rid
        return response
    
    return app


# Expose module-level app for gunicorn (app:app)
app = create_app()

# Validate agent system initialization on startup (deferred to avoid circular imports)
def _check_agent_init():
    """Check agent system initialization after app is created."""
    try:
        from app.session import _runner
        if _runner is None:
            logging.error("Agent system failed to initialize. Check your GOOGLE_API_KEY and logs.")
        else:
            logging.info("Agent system initialized successfully")
    except Exception as e:
        logging.error("Failed to check agent system initialization: %s", str(e))

# Run check after a short delay to ensure all modules are loaded
import threading
def delayed_check():
    import time
    time.sleep(0.1)  # Small delay to ensure modules are fully loaded
    _check_agent_init()

thread = threading.Thread(target=delayed_check, daemon=True)
thread.start()
