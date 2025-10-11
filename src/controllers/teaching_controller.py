from typing import Any, Dict, Optional
from src.services.app_state import get_teaching_system


def teach(question: str, mode: str, agent: Optional[str], difficulty: str) -> Dict[str, Any]:
    teaching_system = get_teaching_system()
    return teaching_system.teach(question, mode, agent, difficulty)


def teaching_modes() -> Dict[str, Any]:
    return {
        "teaching_modes": {
            "explain": {
                "name": "Comprehensive Explanation",
                "description": "Detailed explanation with core concepts, clinical relevance, and memory aids",
                "best_for": "Understanding new topics thoroughly",
                "icon": "📚"
            },
            "socratic": {
                "name": "Socratic Method",
                "description": "Learn through guided questions that develop critical thinking",
                "best_for": "Deep understanding and active learning",
                "icon": "🤔"
            },
            "clinical_case": {
                "name": "Clinical Case Study",
                "description": "Realistic patient scenarios with diagnosis and management",
                "best_for": "Applying knowledge to real-world situations",
                "icon": "🏥"
            },
            "mnemonic": {
                "name": "Memory Aids",
                "description": "Powerful mnemonics, acronyms, and recall techniques",
                "best_for": "Quick memorization and exam preparation",
                "icon": "🧠"
            },
            "quiz": {
                "name": "Practice Questions",
                "description": "NEET-style MCQs with detailed explanations",
                "best_for": "Testing knowledge and exam practice",
                "icon": "📝"
            },
            "differential": {
                "name": "Differential Diagnosis",
                "description": "Train clinical reasoning and systematic diagnosis",
                "best_for": "Developing diagnostic thinking skills",
                "icon": "🔍"
            },
            "step_by_step": {
                "name": "Step-by-Step Breakdown",
                "description": "Complex topics broken into simple, digestible steps",
                "best_for": "Understanding difficult concepts",
                "icon": "🪜"
            },
            "neet_focused": {
                "name": "NEET Preparation",
                "description": "Exam-specific strategies, high-yield facts, and scoring tips",
                "best_for": "NEET exam preparation and strategy",
                "icon": "🎯"
            }
        }
    }


def study_plan(topic: str, time_available: str, current_level: str, agent: Optional[str]) -> Dict[str, Any]:
    teaching_system = get_teaching_system()
    if agent and agent in teaching_system.teaching_agents:
        teaching_agent = teaching_system.teaching_agents[agent]
    else:
        agent = teaching_system._smart_route(topic)
        teaching_agent = teaching_system.teaching_agents[agent]
    result = teaching_agent.generate_study_plan(topic, time_available, current_level)
    result["agent_used"] = agent
    return result


def mnemonic(topic: str, agent: Optional[str]) -> Dict[str, Any]:
    teaching_system = get_teaching_system()
    return teaching_system.teach(topic, mode="mnemonic", agent=agent)


def clinical_case(topic: str, agent: Optional[str]) -> Dict[str, Any]:
    teaching_system = get_teaching_system()
    return teaching_system.teach(topic, mode="clinical_case", agent=agent)


def quiz(topic: str, difficulty: str, agent: Optional[str]) -> Dict[str, Any]:
    teaching_system = get_teaching_system()
    return teaching_system.teach(topic, mode="quiz", agent=agent, difficulty=difficulty)


def differential(scenario: str, agent: Optional[str]) -> Dict[str, Any]:
    teaching_system = get_teaching_system()
    use_agent = agent if agent else "pathology"
    return teaching_system.teach(scenario, mode="differential", agent=use_agent)


def analogy(topic: str, agent: Optional[str]) -> Dict[str, Any]:
    teaching_system = get_teaching_system()
    if agent and agent in teaching_system.teaching_agents:
        teaching_agent = teaching_system.teaching_agents[agent]
        result = teaching_agent.explain_with_analogy(topic)
        result["agent_used"] = agent
        return result
    agent = teaching_system._smart_route(topic)
    teaching_agent = teaching_system.teaching_agents[agent]
    result = teaching_agent.explain_with_analogy(topic)
    result["agent_used"] = agent
    return result


def learning_recommendation(topic: str, user_level: str) -> Dict[str, Any]:
    teaching_system = get_teaching_system()
    return teaching_system.get_learning_recommendation(topic, user_level)
