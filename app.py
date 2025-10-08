from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import google.generativeai as genai
from agents.medical_agents import MedicalAgentSystem
from agents.enhanced_teaching_agent import WorldClassMedicalTeachingSystem
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Initialize the medical agent systems
agent_system = MedicalAgentSystem()
teaching_system = WorldClassMedicalTeachingSystem()

@app.route('/')
def home():
    return jsonify({
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
    })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "agents_loaded": len(agent_system.agents),
        "rag_enabled": True,
        "knowledge_base": agent_system.get_knowledge_stats()
    })

@app.route('/agents')
def get_agents():
    agents_info = []
    for agent_id, agent in agent_system.agents.items():
        agents_info.append({
            "id": agent_id,
            "name": agent.name,
            "specialization": agent.specialization,
            "description": agent.description
        })
    return jsonify({"agents": agents_info})

@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()

        if not data or 'question' not in data:
            return jsonify({"error": "Question is required"}), 400

        question = data['question']
        preferred_agent = data.get('agent')  # None if not provided (will trigger auto-routing)
        mode = data.get('mode', 'general')  # general, neet, or exam
        context = data.get('context', {})
        
        # Add mode to context for NCERT-focused responses
        context['mode'] = mode

        # Get response from agents (with intelligent routing or direct)
        result = agent_system.ask_question(question, preferred_agent, context)
        
        # Check for errors
        if 'error' in result:
            return jsonify(result), 400

        return jsonify({
            "question": question,
            "response": result['response'],
            "agent_used": result['agent_used'],
            "routing_info": result['routing_info'],
            "mode": mode,
            "rag_enabled": True
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/collaborate', methods=['POST'])
def collaborate():
    try:
        data = request.get_json()

        if not data or 'question' not in data:
            return jsonify({"error": "Question is required"}), 400

        question = data['question']
        context = data.get('context', {})

        # Get collaborative response from multiple agents
        response = agent_system.collaborative_response(question, context)

        return jsonify({
            "question": question,
            "collaborative_response": response
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/rag/context', methods=['POST'])
def get_rag_context():
    try:
        data = request.get_json()

        if not data or 'question' not in data:
            return jsonify({"error": "Question is required"}), 400

        question = data['question']
        max_tokens = data.get('max_tokens', 1000)

        # Get RAG context
        context = agent_system.get_rag_context(question, max_tokens)

        if context:
            return jsonify({
                "question": question,
                "context": context,
                "context_length": len(context.split())
            })
        else:
            return jsonify({
                "question": question,
                "context": "No relevant context found in knowledge base",
                "context_length": 0
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/knowledge/stats')
def get_knowledge_stats():
    try:
        stats = agent_system.get_knowledge_stats()
        return jsonify({
            "knowledge_base_statistics": stats,
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search', methods=['POST'])
def search_knowledge():
    try:
        data = request.get_json()

        if not data or 'query' not in data:
            return jsonify({"error": "Query is required"}), 400

        query = data['query']
        topic = data.get('topic')  # Optional topic filter
        limit = data.get('limit', 5)

        # Get RAG context
        context = agent_system.get_rag_context(query, max_tokens=1500)

        # If topic specified, also search by topic
        topic_results = []
        if topic:
            from agents.rag_system import MedicalRAG
            rag = MedicalRAG()
            topic_results = rag.search_by_topic(topic, limit)

        return jsonify({
            "query": query,
            "topic": topic,
            "context": context,
            "topic_specific_results": topic_results,
            "total_results": len(topic_results)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/teach', methods=['POST'])
def teach():
    """World-class teaching with multiple pedagogical modes"""
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({"error": "Question is required"}), 400
        
        question = data['question']
        mode = data.get('mode', 'explain')  # Default to explain mode
        agent = data.get('agent')  # Optional: specify agent
        difficulty = data.get('difficulty', 'intermediate')  # beginner/intermediate/advanced
        
        # Validate mode
        valid_modes = ['explain', 'socratic', 'clinical_case', 'mnemonic', 'quiz', 
                       'differential', 'step_by_step', 'neet_focused']
        if mode not in valid_modes:
            return jsonify({
                "error": f"Invalid mode. Valid modes: {', '.join(valid_modes)}"
            }), 400
        
        # Get teaching response
        result = teaching_system.teach(question, mode, agent, difficulty)
        
        return jsonify({
            "success": True,
            "question": question,
            "mode": mode,
            "difficulty": difficulty,
            **result
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/teach/modes', methods=['GET'])
def get_teaching_modes():
    """List all available teaching modes with descriptions"""
    return jsonify({
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
    })


@app.route('/study-plan', methods=['POST'])
def generate_study_plan():
    """Generate personalized study plan"""
    try:
        data = request.get_json()
        
        if not data or 'topic' not in data:
            return jsonify({"error": "Topic is required"}), 400
        
        topic = data['topic']
        time_available = data.get('time_available', '1 week')
        current_level = data.get('current_level', 'beginner')
        agent = data.get('agent')
        
        # Get the appropriate teaching agent
        if agent and agent in teaching_system.teaching_agents:
            teaching_agent = teaching_system.teaching_agents[agent]
        else:
            agent = teaching_system._smart_route(topic)
            teaching_agent = teaching_system.teaching_agents[agent]
        
        result = teaching_agent.generate_study_plan(topic, time_available, current_level)
        result['agent_used'] = agent
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/mnemonic', methods=['POST'])
def generate_mnemonic():
    """Generate powerful mnemonics and memory aids"""
    try:
        data = request.get_json()
        
        if not data or 'topic' not in data:
            return jsonify({"error": "Topic is required"}), 400
        
        topic = data['topic']
        agent = data.get('agent')
        
        result = teaching_system.teach(topic, mode='mnemonic', agent=agent)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/clinical-case', methods=['POST'])
def generate_clinical_case():
    """Generate realistic clinical case"""
    try:
        data = request.get_json()
        
        if not data or 'topic' not in data:
            return jsonify({"error": "Topic is required"}), 400
        
        topic = data['topic']
        agent = data.get('agent')
        
        result = teaching_system.teach(topic, mode='clinical_case', agent=agent)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/quiz', methods=['POST'])
def generate_quiz():
    """Generate NEET-style practice questions"""
    try:
        data = request.get_json()
        
        if not data or 'topic' not in data:
            return jsonify({"error": "Topic is required"}), 400
        
        topic = data['topic']
        difficulty = data.get('difficulty', 'intermediate')
        agent = data.get('agent')
        
        result = teaching_system.teach(topic, mode='quiz', agent=agent, difficulty=difficulty)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/differential', methods=['POST'])
def differential_diagnosis():
    """Train differential diagnosis thinking"""
    try:
        data = request.get_json()
        
        if not data or 'scenario' not in data:
            return jsonify({"error": "Clinical scenario is required"}), 400
        
        scenario = data['scenario']
        agent = data.get('agent', 'pathology')  # Default to pathology for clinical reasoning
        
        result = teaching_system.teach(scenario, mode='differential', agent=agent)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/analogy', methods=['POST'])
def explain_with_analogy():
    """Explain complex topics using analogies"""
    try:
        data = request.get_json()
        
        if not data or 'topic' not in data:
            return jsonify({"error": "Topic is required"}), 400
        
        topic = data['topic']
        agent = data.get('agent')
        
        # Get the appropriate teaching agent
        if agent and agent in teaching_system.teaching_agents:
            teaching_agent = teaching_system.teaching_agents[agent]
        else:
            agent = teaching_system._smart_route(topic)
            teaching_agent = teaching_system.teaching_agents[agent]
        
        result = teaching_agent.explain_with_analogy(topic)
        result['agent_used'] = agent
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/learning-recommendation', methods=['POST'])
def get_learning_recommendation():
    """Get personalized learning recommendations"""
    try:
        data = request.get_json()
        
        if not data or 'topic' not in data:
            return jsonify({"error": "Topic is required"}), 400
        
        topic = data['topic']
        user_level = data.get('user_level', 'beginner')
        
        result = teaching_system.get_learning_recommendation(topic, user_level)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Get port from environment variable (for Cloud Run) or default to 8080
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
