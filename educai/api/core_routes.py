from flask import Blueprint, jsonify
from educai.controllers import agent_controller as ctrl

core_bp = Blueprint("core", __name__)


@core_bp.route("/", methods=["GET"])
def home():
    return jsonify(ctrl.home_info())


@core_bp.route("/health", methods=["GET"])
def health():
    return jsonify(ctrl.health())


@core_bp.route("/agents", methods=["GET"])
def get_agents():
    return jsonify(ctrl.list_agents())
