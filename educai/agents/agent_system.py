import google.generativeai as genai
import json
import logging
import re
from typing import Dict, List, Optional, Any
from educai.agents.rag import get_shared_rag
from educai.config import GEMINI_DEFAULT_MODEL
from educai.agents.base import MedicalAgent

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
        from educai.agents.registry import load_all_agents
        self.agents = load_all_agents()

    def _is_greeting_or_smalltalk(self, question: str) -> bool:
        q = question.strip().lower()
        if not q:
            return False
        greetings = [
            "hi", "hello", "hey", "yo", "hola", "namaste",
            "good morning", "good afternoon", "good evening",
            "how are you", "what's up", "whats up", "sup"
        ]
        smalltalk = [
            "who are you", "what can you do", "help", "introduce yourself",
            "what topics", "what are the topics", "which topics", "suggest topics", "recommend topics",
            "which subject", "what subject", "best subject", "in which subject you're best",
            "what can you teach", "what do you cover"
        ]
        return any(q == g or q.startswith(g + " ") for g in greetings) or any(phrase in q for phrase in smalltalk)

    def _is_acknowledgment(self, question: str) -> bool:
        q = question.strip().lower()
        if not q:
            return False
        # Normalize: remove punctuation/symbols
        norm = re.sub(r"[^a-z\s]", "", q).strip()
        if not norm:
            return False
        # Avoid classifying time-of-day greetings as acknowledgments
        if any(phrase in norm for phrase in ["good morning", "good afternoon", "good evening"]):
            return False
        ack_exact = {
            "thanks", "thank you", "ty", "great", "awesome", "cool", "nice", "ok", "okay", "k",
            "got it", "understood", "yup", "yeah", "yep", "alright", "sure", "perfect", "wonderful",
            "good", "fine", "excellent", "amazing", "hmm"
        }
        if norm in ack_exact:
            return True
        ack_prefixes = [
            "thanks", "thank you", "great", "awesome", "cool", "nice", "ok", "okay", "alright",
            "perfect", "wonderful", "amazing", "good", "fine", "excellent", "got it", "understood",
            "yup", "yeah", "yep", "sure", "hmm"
        ]
        return any(norm.startswith(p) for p in ack_prefixes)

    def _is_medical_topic(self, question: str) -> bool:
        q = question.strip().lower()
        if not q:
            return False
        medical_keywords = [
            "neet", "mbbs", "medical", "medicine", "clinical", "patient", "case",
            "symptom", "sign", "diagnosis", "treatment", "management", "pathogenesis",
            "mechanism of action", "side effect", "contraindication", "dose", "dosage",
            "anatomy", "physiology", "biochemistry", "pathology", "pharmacology",
            "organ", "tissue", "bone", "muscle", "nerve", "blood vessel", "histology",
            "embryology", "enzyme", "metabolism", "hormone", "vitamin", "dna", "rna",
            "disease", "infection", "tumor", "lesion", "inflammation",
            "mcq", "quiz", "mnemonic", "study plan",
            "brain", "heart", "lung", "kidney", "liver", "spleen", "pancreas", "stomach",
            "intestine", "neuron", "artery", "vein", "capillary", "blood", "cell", "skull"
        ]
        if any(k in q for k in medical_keywords):
            return True
        try:
            ctx = self.rag_system.get_relevant_context(question, max_tokens=200)
            if ctx and ctx.strip():
                return True
        except Exception:
            pass
        return False

    def _route_question(self, question: str) -> Dict[str, Any]:
        """Use AI to intelligently route the question to the most appropriate agent"""
        try:
            model = genai.GenerativeModel(GEMINI_DEFAULT_MODEL)

            # Build dynamic list of available specialists with IDs and descriptions
            lines = []
            for agent_key, agent in self.agents.items():
                try:
                    name = getattr(agent, 'name', agent_key)
                    desc = getattr(agent, 'description', getattr(agent, 'specialization', ''))
                except Exception:
                    name, desc = agent_key, ''
                lines.append(f"- \"{agent_key}\": {name} — {desc}")
            specialists = "\n".join(lines)

            routing_prompt = f"""You are an intelligent medical question router. Analyze the question and select the single most appropriate specialist by its KEY from the list below.

Available Specialists (KEY: Name — Description):
{specialists}

Question: {question}

Respond ONLY with a JSON object in this exact format:
{{
  "agent": "<one of the KEYS listed above>",
  "confidence": "high|medium|low",
  "reasoning": "Brief explanation for your selection"
}}
"""

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

        # Keywords to determine relevant agents (grouped architecture)
        agent_keywords = {
            'preclinical': [
                'anatomy', 'physiology', 'biochemistry', 'structure', 'organ', 'tissue', 'muscle', 'bone', 'nerve',
                'function', 'mechanism', 'homeostasis', 'metabolism', 'enzyme', 'protein', 'dna', 'rna', 'hormone', 'vitamin'
            ],
            'paraclinical': [
                'pathology', 'microbiology', 'pharmacology', 'forensic', 'psm', 'community medicine',
                'disease', 'disorder', 'lesion', 'tumor', 'infection', 'bacteria', 'virus', 'fungi', 'parasite',
                'drug', 'medication', 'treatment', 'therapy', 'dose', 'side effect', 'interaction'
            ],
            'clinical': [
                'clinical', 'medicine', 'surgery', 'pediatrics', 'obg', 'obstetrics', 'gynecology', 'orthopedics',
                'ent', 'ophthalmology', 'dermatology', 'psychiatry', 'pulmonology', 'respiratory',
                'history', 'examination', 'diagnosis', 'management', 'differential', 'investigation'
            ],
            'diagnostic': [
                'radiology', 'x-ray', 'ct', 'mri', 'ultrasound', 'usg', 'anesthesiology', 'anesthesia', 'emergency',
                'nuclear medicine', 'lab medicine', 'laboratory', 'interpretation', 'ecg', 'imaging'
            ],
            'superspecialty': [
                'cardiology', 'nephrology', 'gastroenterology', 'neurology', 'oncology', 'endocrinology',
                'rheumatology', 'hematology', 'hepatology', 'critical care', 'pulmonary critical care', 'neonatology'
            ],
            'allied_health': [
                'nursing', 'physiotherapy', 'mlt', 'radiography', 'ott', 'anesthesia technology', 'dialysis technology',
                'optometry', 'occupational therapy', 'dentistry', 'pharmacy', 'nutrition', 'public health', 'him', 'biomedical engineering'
            ],
            'neet_core': [
                'neet biology', 'human biology', 'human anatomy', 'human physiology', 'genetics', 'evolution', 'ecology',
                'biodiversity', 'photosynthesis', 'plant physiology', 'cell', 'biomolecules', 'enzymes', 'cell cycle'
            ]
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
