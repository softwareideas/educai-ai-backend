from flask import Blueprint, request, jsonify
from educai.controllers import agent_controller as ctrl

qa_bp = Blueprint("qa", __name__)


@qa_bp.route("/ask", methods=["POST"])
def ask_question():
    data = request.get_json(silent=True) or {}
    if "question" not in data:
        return jsonify({"error": "Question is required"}), 400

    question = data["question"]
    preferred_agent = data.get("agent")
    mode = data.get("mode", "general")
    context = data.get("context", {})

    session_id = data.get("session_id")
    result = ctrl.ask(question, preferred_agent, mode, context, session_id=session_id)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


@qa_bp.route("/collaborate", methods=["POST"])
def collaborate():
    data = request.get_json(silent=True) or {}
    if "question" not in data:
        return jsonify({"error": "Question is required"}), 400

    question = data["question"]
    context = data.get("context", {})
    mode = data.get("mode")
    if mode is not None:
        context["mode"] = mode

    session_id = data.get("session_id")
    result = ctrl.collaborate(question, context, session_id=session_id)
    return jsonify(result)
