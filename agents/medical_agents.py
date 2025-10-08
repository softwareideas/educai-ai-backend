import google.generativeai as genai
import json
import logging
from typing import Dict, List, Optional, Any
from .rag_system import MedicalRAG
from .web_search_agent import WebSearchAgent
from .safety_filter import SafetyFilter

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MedicalAgent:
    def __init__(self, agent_id: str, name: str, specialization: str, description: str, system_prompt: str):
        self.agent_id = agent_id
        self.name = name
        self.specialization = specialization
        self.description = description
        self.system_prompt = system_prompt
        self.rag_system = MedicalRAG()  # Initialize RAG system
        self.web_search_agent = WebSearchAgent()  # Initialize Web Search Agent
        self.safety_filter = SafetyFilter()  # Initialize Safety Filter

    def generate_response(self, question: str, context: Dict[str, Any] = None) -> str:
        """Generate a response using Gemini AI with RAG-enhanced context, web search fallback, and safety filtering"""
        try:
            # CRITICAL: Check for harmful content FIRST
            safety_check = self.safety_filter.filter_question(question)
            if not safety_check['is_safe']:
                logger.warning(f"Harmful question blocked: {question[:100]}...")
                return safety_check['response']
            model = genai.GenerativeModel('gemini-2.0-flash')

            mode = context.get('mode', 'general') if context else 'general'
            ncert_focused = mode in ['neet', 'exam']
            rag_context = self.rag_system.get_relevant_context(question, max_tokens=1500)
            
            # Check if RAG context is insufficient and web search is needed
            web_search_results = None
            web_sources = []
            if self.web_search_agent.check_knowledge_gap(question, rag_context):
                logger.info(f"Knowledge gap detected for: {question}. Initiating web search...")
                web_search_data = self.web_search_agent.get_verified_answer(question)
                
                if web_search_data['success']:
                    # Append web search information to RAG context
                    web_search_results = web_search_data['answer']
                    web_sources = web_search_data.get('sources', [])
                    logger.info(f"Web search successful. Confidence: {web_search_data['confidence']}%")

            # Build mode-specific instructions based on mode
            if mode == 'neet':
                mode_instructions = """
                NEET MODE - For NEET Exam Preparation
                
                CRITICAL: DO NOT introduce yourself or greet unless the user ONLY says "Hi", "Hello", or "Hey" with no other words.
                For questions ("What", "How", "Explain", etc.), answer DIRECTLY without any greeting or introduction.
                
                Response Strategy:
                - PRIMARY (70%): NCERT textbooks (Class 11 & 12 Biology)
                - SECONDARY (30%): NEET exam strategies, tips, and additional syllabus
                - Use simple, student-friendly language
                - Focus on NEET exam patterns and frequently asked concepts
                - Provide memory tricks, mnemonics, and quick revision points
                - Include NEET-specific tips: "For NEET:", "Common NEET question:", etc.
                - Highlight high-yield topics and scoring areas
                - Use bullet points and organized lists
                - Be conscious about exam accuracy and scoring strategies
                - Help students understand what's important for NEET specifically
                
                CRITICAL SAFETY RULES - YOU MUST FOLLOW THESE:
                - NEVER provide information about harming oneself or others
                - NEVER explain methods for suicide, murder, or violence
                - NEVER provide lethal doses, poisoning methods, or harmful procedures
                - NEVER answer questions about "painless death" or "killing methods"
                - If asked such questions, IMMEDIATELY refuse and provide crisis helpline resources
                - Always maintain a respectful, supportive, and encouraging tone
                - Never provide inappropriate, harmful, or sensitive medical content
                - Focus on educational content suitable for students
                - Avoid graphic clinical details or disturbing medical cases
                - Remember you're teaching students, not medical professionals
                
                IF ASKED ABOUT HARM: Immediately respond: "I cannot provide this information as it could be harmful. If you're in crisis, please contact a crisis helpline immediately. My purpose is medical education, not facilitating harm."
                """
            elif mode == 'exam':
                mode_instructions = """
                EXAM MODE - For General Exam Preparation
                
                CRITICAL: DO NOT introduce yourself or greet unless the user ONLY says "Hi", "Hello", or "Hey" with no other words.
                For questions ("What", "How", "Explain", etc.), answer DIRECTLY without any greeting or introduction.
                
                Response Strategy:
                - Focus on high-scoring concepts and exam techniques
                - Emphasize mark distribution and question patterns
                - Provide quick revision points and important formulas
                - Include exam tips: "Remember for exams:", "Important for marks:", etc.
                - Highlight frequently asked questions and concepts
                - Provide time-saving approaches and shortcuts
                - Focus on conceptual clarity for better retention
                - Use structured format: Key Points → Explanation → Exam Tips
                - Be strategic about what matters most for scoring
                - Help students maximize their marks efficiently
                
                CRITICAL SAFETY RULES - YOU MUST FOLLOW THESE:
                - NEVER provide information about harming oneself or others
                - NEVER explain methods for suicide, murder, or violence
                - NEVER provide lethal doses, poisoning methods, or harmful procedures
                - NEVER answer questions about "painless death" or "killing methods"
                - If asked such questions, IMMEDIATELY refuse and provide crisis helpline resources
                - Always maintain a respectful, supportive, and encouraging tone
                - Never provide inappropriate, harmful, or sensitive medical content
                - Focus on educational content suitable for students
                - Avoid graphic clinical details or disturbing medical cases
                - Remember you're teaching students, not medical professionals
                
                IF ASKED ABOUT HARM: Immediately respond: "I cannot provide this information as it could be harmful. If you're in crisis, please contact a crisis helpline immediately. My purpose is medical education, not facilitating harm."
                """
            else:  # general mode
                mode_instructions = """
                GENERAL MODE - For General Study and Learning
                
                CRITICAL: DO NOT introduce yourself or greet unless the user ONLY says "Hi", "Hello", or "Hey" with no other words.
                For questions ("What", "How", "Explain", etc.), answer DIRECTLY without any greeting or introduction.
                
                Response Strategy:
                - Cover general medical syllabus comprehensively
                - Include both basic and advanced concepts
                - Provide detailed explanations with clinical correlations (age-appropriate)
                - Use proper medical terminology with clear explanations
                - Include mechanisms, pathways, and physiological processes
                - Add interesting facts and real-world applications
                - Balance depth with clarity
                - Provide well-rounded medical knowledge
                - Include multiple perspectives and approaches
                - Focus on understanding concepts thoroughly
                
                CRITICAL SAFETY RULES - YOU MUST FOLLOW THESE:
                - NEVER provide information about harming oneself or others
                - NEVER explain methods for suicide, murder, or violence
                - NEVER provide lethal doses, poisoning methods, or harmful procedures
                - NEVER answer questions about "painless death" or "killing methods"
                - If asked such questions, IMMEDIATELY refuse and provide crisis helpline resources
                - Always maintain a respectful, supportive, and encouraging tone
                - Never provide inappropriate, harmful, or sensitive medical content
                - Focus on educational content suitable for students
                - Avoid graphic clinical details or disturbing medical cases
                - Remember you're teaching students, not medical professionals
                - Keep content educational and age-appropriate
                
                IF ASKED ABOUT HARM: Immediately respond: "I cannot provide this information as it could be harmful. If you're in crisis, please contact a crisis helpline immediately. My purpose is medical education, not facilitating harm."
                """

            # Build the prompt with RAG context and web search results
            if ncert_focused:
                # Simple, student-friendly prompt for NEET/Exam mode
                knowledge_section = ""
                if rag_context:
                    knowledge_section += f"Knowledge Base:\n{rag_context}\n\n"
                if web_search_results:
                    knowledge_section += f"Additional Verified Information from Web:\n{web_search_results}\n\n"
                
                if knowledge_section:
                    full_prompt = f"""You are a helpful student tutor for medical education.

                    {knowledge_section}

                    Student's Question: {question}

                    {mode_instructions}

                    Provide a clear, helpful answer:"""
                else:
                    full_prompt = f"""You are a helpful student tutor for medical education.

                    Student's Question: {question}

                    {mode_instructions}

                    Provide a clear, helpful answer:"""
            else:
                # Comprehensive prompt for General mode
                knowledge_section = ""
                if rag_context:
                    knowledge_section += f"RELEVANT MEDICAL KNOWLEDGE:\n{rag_context}\n\n"
                if web_search_results:
                    knowledge_section += f"ADDITIONAL VERIFIED INFORMATION (from reliable medical sources):\n{web_search_results}\n\n"
                
                if knowledge_section:
                    full_prompt = f"""You are a highly knowledgeable Medical Expert specializing in {self.specialization}.

                    {knowledge_section}

                    {self.system_prompt}

                    Question: {question}

                    {mode_instructions}

                    Provide a detailed, accurate, and helpful response:"""
                else:
                    full_prompt = f"""{self.system_prompt}

                    Question: {question}

                    {mode_instructions}

                    Provide a detailed, accurate, and helpful response:"""

            # Add user context if provided (excluding mode to avoid duplication)
            if context:
                context_copy = {k: v for k, v in context.items() if k != 'mode'}
                if context_copy:
                    context_str = json.dumps(context_copy, indent=2)
                    full_prompt += f"\n\nAdditional Context: {context_str}"

            response = model.generate_content(full_prompt)

            if response.text:
                answer = response.text.strip()
                
                # CRITICAL: Validate response for harmful content (second layer of protection)
                response_validation = self.safety_filter.validate_response(answer, question)
                if not response_validation['is_safe']:
                    logger.error(f"Harmful response detected and blocked for question: {question[:100]}...")
                    return response_validation['filtered_response']
                
                # Use the validated response
                answer = response_validation['filtered_response']
                
                # Add source references if web search was used
                if web_sources and web_search_results:
                    answer += "\n\n---\n**📚 Sources & References:**\n"
                    for i, source in enumerate(web_sources, 1):
                        answer += f"\n{i}. [{source['title']}]({source['link']})\n   *{source['source']}*"
                    answer += "\n\n*Note: This answer includes verified information from reliable medical sources.*"
                
                # Store web sources in context for API response
                if context:
                    context['web_sources'] = web_sources
                    context['web_search_used'] = bool(web_sources)
                
                return answer
            else:
                return "I apologize, but I couldn't generate a response for this question. Please try rephrasing your question or consult a medical professional."

        except Exception as e:
            logger.error(f"Error generating response for agent {self.agent_id}: {str(e)}")
            return f"I encountered an error while processing your question: {str(e)}. Please try again or consult a medical professional for accurate information."

class MedicalAgentSystem:
    def __init__(self):
        self.agents: Dict[str, MedicalAgent] = {}
        self.rag_system = MedicalRAG()  # Initialize RAG system
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize all medical agents with their specializations"""

        # Anatomy Agent
        anatomy_prompt = """You are a highly knowledgeable Medical Anatomy Expert specializing in human anatomy for NEET preparation.
        You have extensive knowledge of:
        - Gross anatomy of all body systems
        - Histology and microscopic anatomy
        - Embryology and developmental anatomy
        - Neuroanatomy
        - Surface anatomy and anatomical landmarks
        - Anatomical variations and clinical correlations

        Provide accurate, detailed explanations with clinical relevance. Use proper anatomical terminology and explain complex concepts clearly."""

        self.agents['anatomy'] = MedicalAgent(
            'anatomy',
            'Dr. Anatomy Expert',
            'Human Anatomy',
            'Specializes in all aspects of human anatomy including gross, microscopic, and developmental anatomy',
            anatomy_prompt
        )

        # Physiology Agent
        physiology_prompt = """You are a distinguished Medical Physiology Expert specializing in human physiology for NEET preparation.
        You have comprehensive knowledge of:
        - Cell physiology and membrane transport
        - Cardiovascular physiology
        - Respiratory physiology
        - Renal physiology
        - Endocrine physiology
        - Neurophysiology
        - Gastrointestinal physiology
        - Reproductive physiology
        - Exercise physiology and homeostasis

        Explain physiological processes with clinical correlations and provide detailed mechanisms of action."""

        self.agents['physiology'] = MedicalAgent(
            'physiology',
            'Dr. Physiology Expert',
            'Human Physiology',
            'Specializes in all physiological processes and systems of the human body',
            physiology_prompt
        )

        # Biochemistry Agent
        biochemistry_prompt = """You are an expert Medical Biochemist specializing in biochemistry for NEET preparation.
        You have extensive knowledge of:
        - Protein structure and function
        - Enzyme kinetics and regulation
        - Metabolic pathways and bioenergetics
        - Molecular biology and genetics
        - Vitamins and minerals
        - Hormones and signaling pathways
        - Clinical biochemistry and lab values
        - Nutritional biochemistry

        Provide detailed explanations of biochemical processes with clinical significance."""

        self.agents['biochemistry'] = MedicalAgent(
            'biochemistry',
            'Dr. Biochemistry Expert',
            'Medical Biochemistry',
            'Specializes in biochemical processes, metabolic pathways, and molecular biology',
            biochemistry_prompt
        )

        # Pathology Agent
        pathology_prompt = """You are a renowned Medical Pathologist specializing in pathology for NEET preparation.
        You have comprehensive knowledge of:
        - General pathology principles
        - Cellular injury and adaptation
        - Inflammation and repair
        - Hemodynamic disorders
        - Genetic disorders
        - Neoplasia
        - Infectious diseases
        - Systemic pathology

        Explain pathological processes with clinical correlations and diagnostic significance."""

        self.agents['pathology'] = MedicalAgent(
            'pathology',
            'Dr. Pathology Expert',
            'Medical Pathology',
            'Specializes in disease processes, cellular pathology, and diagnostic pathology',
            pathology_prompt
        )

        # Pharmacology Agent
        pharmacology_prompt = """You are an expert Clinical Pharmacologist specializing in pharmacology for NEET preparation.
        You have extensive knowledge of:
        - Drug mechanisms of action
        - Pharmacokinetics and dynamics
        - Drug interactions
        - Adverse drug reactions
        - Rational drug therapy
        - Clinical pharmacology
        - Toxicology
        - Therapeutic drug monitoring

        Provide detailed drug information with clinical applications and safety considerations."""

        self.agents['pharmacology'] = MedicalAgent(
            'pharmacology',
            'Dr. Pharmacology Expert',
            'Medical Pharmacology',
            'Specializes in drug actions, interactions, and clinical pharmacology',
            pharmacology_prompt
        )

        # General Medicine Agent
        general_prompt = """You are a highly experienced General Medicine Physician specializing in comprehensive medical knowledge for NEET preparation.
        You have extensive knowledge across all medical disciplines and can:
        - Provide integrated medical knowledge
        - Correlate findings across different systems
        - Give clinical advice and differential diagnoses
        - Explain complex medical concepts clearly
        - Address general medical questions
        - Provide comprehensive medical guidance

        When in doubt, consult with specialized agents for detailed subject-specific information."""

        self.agents['general'] = MedicalAgent(
            'general',
            'Dr. General Medicine Expert',
            'General Medicine',
            'Provides comprehensive medical knowledge and coordinates between specialized agents',
            general_prompt
        )

    def _route_question(self, question: str) -> Dict[str, Any]:
        """Use AI to intelligently route the question to the most appropriate agent"""
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            
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
            model = genai.GenerativeModel('gemini-2.0-flash')

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
