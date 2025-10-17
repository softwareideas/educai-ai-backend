from flask import Flask
from flask_cors import CORS

from educai.api.core_routes import core_bp
from educai.api.qa_routes import qa_bp
from educai.api.knowledge_routes import knowledge_bp
from educai.api.teaching_routes import teaching_bp


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    # Register blueprints (keep existing paths unchanged)
    app.register_blueprint(core_bp)
    app.register_blueprint(qa_bp)
    app.register_blueprint(knowledge_bp)
    app.register_blueprint(teaching_bp)

    return app
