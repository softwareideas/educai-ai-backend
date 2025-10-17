from flask import Blueprint, request, jsonify
from educai.controllers import teaching_controller as ctrl

teaching_bp = Blueprint("teaching", __name__)


@teaching_bp.route("/teach", methods=["POST"])
def teach():
    data = request.get_json(silent=True) or {}
    if "question" not in data:
        return jsonify({"error": "Question is required"}), 400

    question = data["question"]
    mode = data.get("mode", "explain")
    agent = data.get("agent")
    difficulty = data.get("difficulty", "intermediate")

    result = ctrl.teach(question, mode, agent, difficulty)
    return jsonify({
        "success": True,
        "question": question,
        "mode": mode,
        "difficulty": difficulty,
        **result
    })


@teaching_bp.route("/teach/modes", methods=["GET"])
def get_teaching_modes():
    return jsonify(ctrl.teaching_modes())


@teaching_bp.route("/study-plan", methods=["POST"])
def generate_study_plan():
    data = request.get_json(silent=True) or {}
    if "topic" not in data:
        return jsonify({"error": "Topic is required"}), 400

    topic = data["topic"]
    time_available = data.get("time_available", "1 week")
    current_level = data.get("current_level", "beginner")
    agent = data.get("agent")

    result = ctrl.study_plan(topic, time_available, current_level, agent)
    return jsonify(result)


@teaching_bp.route("/mnemonic", methods=["POST"])
def generate_mnemonic():
    data = request.get_json(silent=True) or {}
    if "topic" not in data:
        return jsonify({"error": "Topic is required"}), 400

    topic = data["topic"]
    agent = data.get("agent")

    result = ctrl.mnemonic(topic, agent)
    return jsonify(result)


@teaching_bp.route("/clinical-case", methods=["POST"])
def generate_clinical_case():
    data = request.get_json(silent=True) or {}
    if "topic" not in data:
        return jsonify({"error": "Topic is required"}), 400

    topic = data["topic"]
    agent = data.get("agent")

    result = ctrl.clinical_case(topic, agent)
    return jsonify(result)


@teaching_bp.route("/quiz", methods=["POST"])
def generate_quiz():
    data = request.get_json(silent=True) or {}
    if "topic" not in data:
        return jsonify({"error": "Topic is required"}), 400

    topic = data["topic"]
    difficulty = data.get("difficulty", "intermediate")
    agent = data.get("agent")

    result = ctrl.quiz(topic, difficulty, agent)
    return jsonify(result)


@teaching_bp.route("/differential", methods=["POST"])
def differential_diagnosis():
    data = request.get_json(silent=True) or {}
    if "scenario" not in data:
        return jsonify({"error": "Clinical scenario is required"}), 400

    scenario = data["scenario"]
    agent = data.get("agent", "pathology")

    result = ctrl.differential(scenario, agent)
    return jsonify(result)


@teaching_bp.route("/analogy", methods=["POST"])
def explain_with_analogy():
    data = request.get_json(silent=True) or {}
    if "topic" not in data:
        return jsonify({"error": "Topic is required"}), 400

    topic = data["topic"]
    agent = data.get("agent")

    result = ctrl.analogy(topic, agent)
    return jsonify(result)


@teaching_bp.route("/learning-recommendation", methods=["POST"])
def get_learning_recommendation():
    data = request.get_json(silent=True) or {}
    if "topic" not in data:
        return jsonify({"error": "Topic is required"}), 400

    topic = data["topic"]
    user_level = data.get("user_level", "beginner")

    result = ctrl.learning_recommendation(topic, user_level)
    return jsonify(result)
