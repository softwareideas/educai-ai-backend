from typing import Any, Dict, List, Optional
from flask import jsonify
from src.services.app_state import get_agent_system
from agents.rag_system import get_shared_rag


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


def ask(question: str, preferred_agent: Optional[str], mode: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    agent_system = get_agent_system()
    ctx = context.copy() if context else {}
    ctx["mode"] = mode
    result = agent_system.ask_question(question, preferred_agent, ctx)
    if "error" in result:
        return result
    return {
        "question": question,
        "response": result["response"],
        "agent_used": result["agent_used"],
        "routing_info": result["routing_info"],
        "mode": mode,
        "rag_enabled": True
    }


def collaborate(question: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    agent_system = get_agent_system()
    response = agent_system.collaborative_response(question, context or {})
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
