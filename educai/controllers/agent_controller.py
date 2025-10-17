from typing import Any, Dict, List, Optional
from flask import jsonify
from educai.services.app_state import get_agent_system, get_manager_agent
from educai.services.session_store import get_history, append_exchange, reset_if_mode_changed
from educai.agents.rag import get_shared_rag


def home_info() -> Dict[str, Any]:
    return {
        "message": "🎓 World-Class Medical Learning AI - NEET Preparation Platform",
        "version": "3.0.0",
        "features": [
            "Multi-Agent Specialist System",
            "RAG-Enhanced Knowledge Base",
            "AI-Powered Question Routing",
            "Advanced Teaching Modes",
            "Socratic Method Learning",
            "Clinical Case Training",
            "NEET-Focused Preparation",
            "Adaptive Study Plans"
        ],
        "endpoints": {
            "basic": {
                "/ask": "POST - Ask a question (auto-routes to best agent)",
                "/collaborate": "POST - Get collaborative response from multiple agents",
                "/agents": "GET - List available agents",
                "/health": "GET - Health check"
            },
            "knowledge": {
                "/rag/context": "POST - Get RAG context for a question",
                "/knowledge/stats": "GET - Get knowledge base statistics",
                "/search": "POST - Search knowledge base with optional topic filter"
            },
            "teaching": {
                "/teach": "POST - World-class teaching with multiple pedagogical modes",
                "/teach/modes": "GET - List all available teaching modes",
                "/study-plan": "POST - Generate personalized study plan",
                "/mnemonic": "POST - Generate powerful mnemonics and memory aids",
                "/clinical-case": "POST - Generate realistic clinical cases",
                "/quiz": "POST - Generate NEET-style practice questions",
                "/differential": "POST - Train differential diagnosis thinking",
                "/analogy": "POST - Explain with powerful analogies",
                "/learning-recommendation": "POST - Get personalized learning recommendations"
            }
        },
        "teaching_modes": [
            "explain - Comprehensive explanation with clinical correlations",
            "socratic - Guided learning through thoughtful questions",
            "clinical_case - Learn through realistic patient scenarios",
            "mnemonic - Memory aids and recall techniques",
            "quiz - NEET-style practice questions with explanations",
            "differential - Differential diagnosis training",
            "step_by_step - Break complex topics into simple steps",
            "neet_focused - NEET exam-specific strategies and high-yield facts"
        ]
    }


def health() -> Dict[str, Any]:
    agent_system = get_agent_system()
    return {
        "status": "healthy",
        "agents_loaded": len(agent_system.agents),
        "rag_enabled": True,
        "knowledge_base": agent_system.get_knowledge_stats()
    }


def list_agents() -> Dict[str, Any]:
    agent_system = get_agent_system()
    agents_info: List[Dict[str, Any]] = []
    for agent_id, agent in agent_system.agents.items():
        agents_info.append({
            "id": agent_id,
            "name": agent.name,
            "specialization": agent.specialization,
            "description": agent.description
        })
    return {"agents": agents_info}


def ask(question: str, preferred_agent: Optional[str], mode: str, context: Optional[Dict[str, Any]], session_id: Optional[str] = None) -> Dict[str, Any]:
    agent_system = get_agent_system()
    manager = get_manager_agent()
    ctx = context.copy() if context else {}
    ctx["mode"] = mode
    # Session management
    reset_if_mode_changed(session_id or "", mode)
    history_msgs = get_history(session_id or "", mode)
    if history_msgs:
        ctx["conversation_history"] = history_msgs
    manager_result = manager.handle(question, mode, ctx)
    if manager_result.get("handled"):
        response_text = manager_result["response"]
        # append to session history
        append_exchange(session_id or "", mode, question, response_text)
        return {
            "question": question,
            "response": response_text,
            "agent_used": "manager",
            "routing_info": {"auto_routed": False, "manager": True, "reason": manager_result.get("reason")},
            "mode": mode,
            "rag_enabled": True
        }
    result = agent_system.ask_question(question, preferred_agent, ctx)
    if "error" in result:
        return result
    # append to session history
    append_exchange(session_id or "", mode, question, result.get("response", ""))
    return {
        "question": question,
        "response": result["response"],
        "agent_used": result["agent_used"],
        "routing_info": result["routing_info"],
        "mode": mode,
        "rag_enabled": True
    }


def collaborate(question: str, context: Optional[Dict[str, Any]], session_id: Optional[str] = None) -> Dict[str, Any]:
    agent_system = get_agent_system()
    manager = get_manager_agent()
    ctx = context.copy() if context else {}
    mode = ctx.get("mode")
    # Session management
    reset_if_mode_changed(session_id or "", mode)
    history_msgs = get_history(session_id or "", mode)
    if history_msgs:
        ctx["conversation_history"] = history_msgs
    manager_result = manager.handle(question, mode, ctx)
    if manager_result.get("handled"):
        handled = {
            "coordinated_response": manager_result["response"],
            "individual_responses": {},
            "agents_consulted": [],
            "handled_by": "manager",
            "reason": manager_result.get("reason")
        }
        append_exchange(session_id or "", mode, question, handled["coordinated_response"]) 
        return {
            "question": question,
            "collaborative_response": handled
        }
    response = agent_system.collaborative_response(question, ctx)
    # best-effort assistant text
    assistant_text = response.get("coordinated_response") if isinstance(response, dict) else None
    if isinstance(assistant_text, str):
        append_exchange(session_id or "", mode, question, assistant_text)
    return {
        "question": question,
        "collaborative_response": response
    }


def rag_context(question: str, max_tokens: int) -> Dict[str, Any]:
    agent_system = get_agent_system()
    context = agent_system.get_rag_context(question, max_tokens)
    if context:
        return {
            "question": question,
            "context": context,
            "context_length": len(context.split())
        }
    else:
        return {
            "question": question,
            "context": "No relevant context found in knowledge base",
            "context_length": 0
        }


def knowledge_stats() -> Dict[str, Any]:
    agent_system = get_agent_system()
    return {
        "knowledge_base_statistics": agent_system.get_knowledge_stats(),
        "status": "success"
    }


def search(query: str, topic: Optional[str], limit: int) -> Dict[str, Any]:
    agent_system = get_agent_system()
    context = agent_system.get_rag_context(query, max_tokens=1500)

    topic_results: List[Dict[str, Any]] = []
    if topic:
        rag = get_shared_rag()
        topic_results = rag.search_by_topic(topic, limit)

    return {
        "query": query,
        "topic": topic,
        "context": context,
        "topic_specific_results": topic_results,
        "total_results": len(topic_results)
    }
