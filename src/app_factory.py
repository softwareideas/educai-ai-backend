from flask import Flask
from flask_cors import CORS

from src.routes.core import core_bp
from src.routes.qa import qa_bp
from src.routes.knowledge import knowledge_bp
from src.routes.teaching import teaching_bp


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    # Register blueprints (keep existing paths unchanged)
    app.register_blueprint(core_bp)
    app.register_blueprint(qa_bp)
    app.register_blueprint(knowledge_bp)
    app.register_blueprint(teaching_bp)

    return app
