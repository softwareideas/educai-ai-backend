from flask import Blueprint, request, jsonify
from educai.controllers import agent_controller as ctrl

knowledge_bp = Blueprint("knowledge", __name__)


@knowledge_bp.route("/rag/context", methods=["POST"])
def get_rag_context():
    data = request.get_json(silent=True) or {}
    if "question" not in data:
        return jsonify({"error": "Question is required"}), 400

    question = data["question"]
    max_tokens = data.get("max_tokens", 1000)

    result = ctrl.rag_context(question, max_tokens)
    return jsonify(result)


@knowledge_bp.route("/knowledge/stats", methods=["GET"])
def get_knowledge_stats():
    return jsonify(ctrl.knowledge_stats())


@knowledge_bp.route("/search", methods=["POST"])
def search_knowledge():
    data = request.get_json(silent=True) or {}
    if "query" not in data:
        return jsonify({"error": "Query is required"}), 400

    query = data["query"]
    topic = data.get("topic")
    limit = data.get("limit", 5)

    result = ctrl.search(query, topic, limit)
    return jsonify(result)
