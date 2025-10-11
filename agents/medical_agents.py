import google.generativeai as genai
import json
import logging
from typing import Dict, List, Optional, Any
from .rag_system import get_shared_rag
from src.config import GEMINI_DEFAULT_MODEL
from agents.base_agent import MedicalAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MedicalAgentSystem:
    def __init__(self):
        self.agents: Dict[str, MedicalAgent] = {}
        self.rag_system = get_shared_rag()  # Use shared RAG system
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize all medical agents using the registry"""
        from agents.agent_registry import load_all_agents
        self.agents = load_all_agents()

    def _route_question(self, question: str) -> Dict[str, Any]:
        """Use AI to intelligently route the question to the most appropriate agent"""
        try:
            model = genai.GenerativeModel(GEMINI_DEFAULT_MODEL)
            
            routing_prompt = f"""You are an intelligent medical question router. Analyze the following question and determine which medical specialist should answer it.

Available Specialists:
1. **anatomy** - Human body structure, organs, tissues, bones, muscles, nerves, blood vessels, histology, embryology
2. **physiology** - Body functions, mechanisms, processes, homeostasis, organ systems functioning
3. **biochemistry** - Metabolic pathways, enzymes, proteins, DNA, RNA, hormones, vitamins, chemical processes
4. **pathology** - Diseases, disorders, abnormalities, cellular injury, inflammation, tumors, infections
5. **pharmacology** - Drugs, medications, treatments, dosages, side effects, drug interactions, mechanisms of action
6. **general** - General medical questions, integrated multi-system questions, or unclear specialty

Question: {question}

Analyze this question and respond ONLY with a JSON object in this exact format:
{{
  "agent": "agent_name",
  "confidence": "high/medium/low",
  "reasoning": "Brief explanation why this agent was selected"
}}

IMPORTANT: Respond ONLY with the JSON object, no other text."""
            
            response = model.generate_content(routing_prompt)
            
            if response.text:
                # Clean response and extract JSON
                response_text = response.text.strip()
                # Remove markdown code blocks if present
                if response_text.startswith('```'):
                    response_text = response_text.split('```')[1]
                    if response_text.startswith('json'):
                        response_text = response_text[4:]
                    response_text = response_text.strip()
                
                # Parse JSON
                routing_decision = json.loads(response_text)
                
                # Validate agent exists
                selected_agent = routing_decision.get('agent', 'general')
                if selected_agent not in self.agents:
                    selected_agent = 'general'
                    routing_decision['agent'] = 'general'
                    routing_decision['fallback'] = True
                
                logger.info(f"Router selected: {selected_agent} (Confidence: {routing_decision.get('confidence', 'unknown')})")
                return routing_decision
            
        except Exception as e:
            logger.error(f"Error in question routing: {str(e)}")
        
        # Fallback to general agent
        return {
            "agent": "general",
            "confidence": "low",
            "reasoning": "Routing failed, using general agent as fallback",
            "error": True
        }

    def ask_question(self, question: str, preferred_agent: str = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Ask a question to a specific agent or auto-route to the best agent"""
        
        # If no agent specified or 'general' specified, use intelligent routing
        if preferred_agent is None or preferred_agent == 'general':
            routing_decision = self._route_question(question)
            selected_agent = routing_decision['agent']
            
            # Get response from selected agent
            agent = self.agents[selected_agent]
            response_text = agent.generate_response(question, context)
            
            return {
                "response": response_text,
                "agent_used": selected_agent,
                "routing_info": {
                    "auto_routed": True,
                    "confidence": routing_decision.get('confidence', 'unknown'),
                    "reasoning": routing_decision.get('reasoning', 'No reasoning provided')
                }
            }
        
        # If specific agent requested, use it directly
        else:
            if preferred_agent not in self.agents:
                return {
                    "error": f"Agent '{preferred_agent}' not found. Available agents: {', '.join(self.agents.keys())}",
                    "agent_used": None,
                    "routing_info": {"auto_routed": False, "error": True}
                }
            
            agent = self.agents[preferred_agent]
            response_text = agent.generate_response(question, context)
            
            return {
                "response": response_text,
                "agent_used": preferred_agent,
                "routing_info": {
                    "auto_routed": False,
                    "user_specified": True
                }
            }

    def collaborative_response(self, question: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get responses from multiple relevant agents with RAG enhancement"""
        responses = {}

        # Determine which agents should respond based on the question
        question_lower = question.lower()

        # Keywords to determine relevant agents
        agent_keywords = {
            'anatomy': ['anatomy', 'structure', 'organ', 'tissue', 'muscle', 'bone', 'nerve', 'blood vessel'],
            'physiology': ['physiology', 'function', 'mechanism', 'process', 'homeostasis', 'regulation'],
            'biochemistry': ['biochemistry', 'metabolism', 'enzyme', 'protein', 'dna', 'rna', 'hormone', 'vitamin'],
            'pathology': ['pathology', 'disease', 'disorder', 'abnormal', 'lesion', 'tumor', 'infection'],
            'pharmacology': ['drug', 'medication', 'treatment', 'therapy', 'dose', 'side effect', 'interaction']
        }

        # Find relevant agents
        relevant_agents = ['general']  # Always include general

        for agent_id, keywords in agent_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                relevant_agents.append(agent_id)

        # Remove duplicates while preserving order
        relevant_agents = list(dict.fromkeys(relevant_agents))

        # Get responses from relevant agents
        for agent_id in relevant_agents:
            if agent_id in self.agents:
                responses[agent_id] = self.agents[agent_id].generate_response(question, context)

        return {
            "coordinated_response": self._coordinate_responses(question, responses, context),
            "individual_responses": responses,
            "agents_consulted": relevant_agents
        }

    def _coordinate_responses(self, question: str, responses: Dict[str, str], context: Dict[str, Any] = None) -> str:
        """Coordinate responses from multiple agents into a cohesive answer with RAG enhancement"""
        if not responses:
            return "No responses available from agents."

        # If only one response, return it
        if len(responses) == 1:
            return list(responses.values())[0]

        # For multiple responses, create a coordinated response
        try:
            model = genai.GenerativeModel(GEMINI_DEFAULT_MODEL)

            # Get RAG context for coordination
            rag_context = self.rag_system.get_relevant_context(question, max_tokens=1000)

            # Create a summary prompt with RAG context
            responses_text = "\n\n".join([
                f"**{agent_name.title()} Agent:** {response}"
                for agent_name, response in responses.items()
            ])

            coordination_prompt = f"""Based on the following responses from different medical experts and the verified medical knowledge provided, please provide a comprehensive, well-coordinated answer to the question: "{question}"

            VERIFIED MEDICAL KNOWLEDGE:
            {rag_context}

            EXPERT RESPONSES:
            {responses_text}

            Please synthesize this information into a single, comprehensive response that:
            1. Integrates insights from all relevant specialties
            2. Uses the verified medical knowledge as the foundation
            3. Resolves any conflicting information based on medical evidence
            4. Provides a complete, accurate answer suitable for NEET preparation
            5. Maintains medical accuracy and clinical relevance
            6. Clearly indicates the level of confidence in the information

            Provide the coordinated response:"""

            coordination_response = model.generate_content(coordination_prompt)

            if coordination_response.text:
                return coordination_response.text.strip()
            else:
                # Fallback to general agent response
                return responses.get('general', "Unable to coordinate responses.")

        except Exception as e:
            logger.error(f"Error coordinating responses: {str(e)}")
            # Fallback to general agent response
            return responses.get('general', "Error coordinating responses.")

    def get_rag_context(self, question: str, max_tokens: int = 1000) -> str:
        """Get RAG context for a question"""
        return self.rag_system.get_relevant_context(question, max_tokens)

    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG knowledge base"""
        return self.rag_system.get_statistics()
