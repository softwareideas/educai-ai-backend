"""
Enhanced Medical Teaching Agent with World-Class Learning Features
Includes: Socratic method, clinical cases, mnemonics, adaptive learning, NEET preparation
"""

import google.generativeai as genai
import json
import logging
from typing import Dict, List, Optional, Any
from .rag_system import MedicalRAG
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedMedicalTeachingAgent:
    """World-class medical teaching agent with advanced pedagogical features"""
    
    def __init__(self, agent_id: str, name: str, specialization: str):
        self.agent_id = agent_id
        self.name = name
        self.specialization = specialization
        self.rag_system = MedicalRAG()
        self.teaching_modes = [
            'explain', 'socratic', 'clinical_case', 'mnemonic', 
            'quiz', 'differential', 'step_by_step', 'neet_focused'
        ]
        
    def teach(self, question: str, mode: str = 'explain', difficulty: str = 'intermediate', 
              context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main teaching method with multiple pedagogical approaches
        
        Args:
            question: Student's question
            mode: Teaching mode (explain, socratic, clinical_case, mnemonic, quiz, etc.)
            difficulty: beginner, intermediate, advanced
            context: Additional context (user history, preferences)
        """
        
        # Get RAG context
        rag_context = self.rag_system.get_relevant_context(question, max_tokens=2000)
        
        # Route to appropriate teaching method
        if mode == 'explain':
            return self._explain_mode(question, rag_context, difficulty)
        elif mode == 'socratic':
            return self._socratic_mode(question, rag_context, difficulty)
        elif mode == 'clinical_case':
            return self._clinical_case_mode(question, rag_context)
        elif mode == 'mnemonic':
            return self._mnemonic_mode(question, rag_context)
        elif mode == 'quiz':
            return self._quiz_mode(question, rag_context, difficulty)
        elif mode == 'differential':
            return self._differential_diagnosis_mode(question, rag_context)
        elif mode == 'step_by_step':
            return self._step_by_step_mode(question, rag_context)
        elif mode == 'neet_focused':
            return self._neet_focused_mode(question, rag_context, difficulty)
        else:
            return self._explain_mode(question, rag_context, difficulty)
    
    def _explain_mode(self, question: str, rag_context: str, difficulty: str) -> Dict[str, Any]:
        """Comprehensive explanation with clinical correlations"""
        
        prompt = f"""You are a world-class medical educator specializing in {self.specialization}.

**VERIFIED MEDICAL KNOWLEDGE:**
{rag_context}

**STUDENT QUESTION:** {question}
**DIFFICULTY LEVEL:** {difficulty}

Provide a comprehensive, pedagogically effective explanation following this structure:

📚 **CORE CONCEPT**
- Clear definition with key terminology
- Why this concept is important

🔬 **DETAILED EXPLANATION**
- Break down complex concepts into simple parts
- Use analogies when helpful
- Explain mechanisms step-by-step

🏥 **CLINICAL RELEVANCE**
- Real-world applications
- Common clinical scenarios
- Diagnostic/therapeutic implications

💡 **KEY TAKEAWAYS**
- 3-5 bullet points of most important facts
- What NEET commonly tests

🎯 **MEMORY AIDS**
- Mnemonic if applicable
- Visual cues or patterns

📖 **RELATED CONCEPTS**
- What to study next
- How this connects to other topics

Keep the tone encouraging and student-friendly. Make complex topics feel approachable."""

        return self._generate_response(prompt, 'explain')
    
    def _socratic_mode(self, question: str, rag_context: str, difficulty: str) -> Dict[str, Any]:
        """Socratic method - teach through guided questioning"""
        
        prompt = f"""You are a Socratic medical educator. Instead of directly answering, guide the student to discover the answer through thoughtful questions.

**VERIFIED MEDICAL KNOWLEDGE:**
{rag_context}

**STUDENT QUESTION:** {question}

Use the Socratic method:

🤔 **GUIDING QUESTIONS** (Ask 3-4 progressive questions that lead to understanding)
1. Start with foundational understanding
2. Build to mechanism/process
3. Lead to clinical application
4. End with synthesis

💭 **THINK ABOUT**
- Prompts to activate prior knowledge
- Connections to make

🎓 **LEARNING PATH**
After the student thinks through these questions, provide:
- Confirmation of correct reasoning
- Gentle correction of misconceptions
- Complete answer with reinforcement

This develops critical thinking and deeper understanding."""

        return self._generate_response(prompt, 'socratic')
    
    def _clinical_case_mode(self, question: str, rag_context: str) -> Dict[str, Any]:
        """Generate realistic clinical case scenarios"""
        
        prompt = f"""You are a clinical educator creating realistic case scenarios based on {self.specialization}.

**VERIFIED MEDICAL KNOWLEDGE:**
{rag_context}

**TOPIC:** {question}

Create an engaging clinical case that teaches this concept:

👤 **PATIENT PRESENTATION**
- Age, sex, chief complaint
- History of present illness
- Relevant past medical history
- Physical examination findings

🔍 **CLINICAL REASONING GUIDE**
- What's your differential diagnosis?
- What key findings support/refute each diagnosis?
- What tests would you order? Why?

📊 **INVESTIGATION RESULTS**
- Lab values (with normal ranges)
- Imaging findings
- Special tests

💊 **DIAGNOSIS & MANAGEMENT**
- Final diagnosis with reasoning
- Treatment approach
- Expected outcomes
- What could go wrong?

🎯 **TEACHING POINTS**
- Key concepts demonstrated
- Common pitfalls to avoid
- NEET relevance

Make it realistic and memorable. Use this case to cement understanding."""

        return self._generate_response(prompt, 'clinical_case')
    
    def _mnemonic_mode(self, question: str, rag_context: str) -> Dict[str, Any]:
        """Generate powerful mnemonics and memory aids"""
        
        prompt = f"""You are a master of medical mnemonics and memory techniques.

**VERIFIED MEDICAL KNOWLEDGE:**
{rag_context}

**TOPIC:** {question}

Create powerful memory aids:

🧠 **PRIMARY MNEMONIC**
- Catchy, memorable acronym or phrase
- What each letter/word represents
- How to remember the mnemonic itself

🎨 **VISUAL MEMORY AID**
- Describe a vivid mental image
- Use exaggeration or humor
- Make it unforgettable

🔗 **ASSOCIATION CHAINS**
- Link concepts together
- Use stories or scenarios
- Create logical connections

📝 **PATTERN RECOGNITION**
- Identify patterns in the information
- Group related items
- Use number patterns, rhymes

✅ **QUICK RECALL TEST**
- Provide a one-line trigger
- Student should be able to recall all key points

🎯 **NEET TIP**
- How this is commonly tested
- Most likely incorrect options

Make memorization easy and fun!"""

        return self._generate_response(prompt, 'mnemonic')
    
    def _quiz_mode(self, question: str, rag_context: str, difficulty: str) -> Dict[str, Any]:
        """Generate practice questions with detailed explanations"""
        
        prompt = f"""You are a NEET question paper expert creating high-quality practice questions.

**VERIFIED MEDICAL KNOWLEDGE:**
{rag_context}

**TOPIC:** {question}
**DIFFICULTY:** {difficulty}

Create 5 NEET-style MCQs:

For each question:

**Q[N]. [QUESTION STEM]**
(A) Option 1
(B) Option 2
(C) Option 3
(D) Option 4

---

**ANSWERS & EXPLANATIONS:**

**Q1 Answer: (X) [Correct option]**
✅ **Why this is correct:** [Detailed reasoning]
❌ **Why others are incorrect:**
- (A): [Reason]
- (B): [Reason]
- (C): [Reason]
- (D): [Reason]

💡 **Concept tested:** [Key concept]
🎯 **NEET Pearl:** [Important tip]
📚 **Related topic:** [What else to review]

---

[Repeat for all 5 questions]

**PERFORMANCE ANALYSIS:**
- Questions 1-2: Foundation level
- Questions 3-4: Application level  
- Question 5: Advanced/Clinical reasoning

Make questions realistic, tricky, and educational!"""

        return self._generate_response(prompt, 'quiz')
    
    def _differential_diagnosis_mode(self, question: str, rag_context: str) -> Dict[str, Any]:
        """Train differential diagnosis thinking"""
        
        prompt = f"""You are teaching clinical reasoning and differential diagnosis for {self.specialization}.

**VERIFIED MEDICAL KNOWLEDGE:**
{rag_context}

**CLINICAL SCENARIO/TOPIC:** {question}

Teach systematic differential diagnosis:

🎯 **CHIEF COMPLAINT/FINDING**
- What are we evaluating?

🔍 **DIFFERENTIAL DIAGNOSIS** (Use VINDICATE or other framework)
V - Vascular
I - Infectious/Inflammatory  
N - Neoplastic
D - Degenerative/Developmental
I - Idiopathic/Iatrogenic
C - Congenital
A - Autoimmune/Allergic
T - Traumatic
E - Endocrine/Metabolic

📋 **SYSTEMATIC APPROACH**
For each possibility:
- Key supporting features
- Key refuting features
- Must-rule-out conditions
- Most likely diagnosis

🔬 **DIAGNOSTIC WORKUP**
- First-line investigations
- Second-line tests
- Confirmatory tests
- When to order what

⚠️ **RED FLAGS**
- Emergency situations
- Don't miss diagnoses
- When to escalate

🎓 **CLINICAL PEARLS**
- Epidemiology clues
- Classical presentations
- Atypical presentations

Teach them to think like a clinician!"""

        return self._generate_response(prompt, 'differential')
    
    def _step_by_step_mode(self, question: str, rag_context: str) -> Dict[str, Any]:
        """Break down complex topics into simple steps"""
        
        prompt = f"""You are an expert at breaking complex medical concepts into simple, digestible steps.

**VERIFIED MEDICAL KNOWLEDGE:**
{rag_context}

**COMPLEX TOPIC:** {question}

Break this down systematically:

📖 **PREREQUISITE KNOWLEDGE**
- What you need to know first
- Quick review of basics

🪜 **STEP-BY-STEP BREAKDOWN**

**STEP 1: [Foundation]**
- Simplest concept first
- Build confidence
- ✅ Check understanding: [Quick question]

**STEP 2: [Building Up]**
- Next layer of complexity
- Connect to Step 1
- ✅ Check understanding: [Quick question]

**STEP 3: [Integration]**
- How it all fits together
- Complete picture
- ✅ Check understanding: [Quick question]

**STEP 4: [Application]**
- Use it in context
- Clinical examples
- ✅ Check understanding: [Quick question]

🎯 **COMMON CONFUSION POINTS**
- Where students typically struggle
- How to avoid misunderstandings

📊 **VISUAL SUMMARY**
- Flowchart description
- Concept map outline

✨ **YOU NOW UNDERSTAND**
- Summary of what was learned
- How to remember it
- What comes next

Use simple language, analogies, and encouragement!"""

        return self._generate_response(prompt, 'step_by_step')
    
    def _neet_focused_mode(self, question: str, rag_context: str, difficulty: str) -> Dict[str, Any]:
        """NEET-specific preparation with exam strategies"""
        
        prompt = f"""You are a NEET expert trainer with deep knowledge of exam patterns and high-yield topics.

**VERIFIED MEDICAL KNOWLEDGE:**
{rag_context}

**TOPIC:** {question}
**TARGET SCORE:** {difficulty}

Provide NEET-focused guidance:

⭐ **NEET IMPORTANCE** (Rate: High/Medium/Low)
- How frequently tested
- Typical marks allocated
- Recent trend analysis

📊 **COMMON QUESTION PATTERNS**
- How NEET typically tests this
- Question styles (direct/indirect/clinical/image)
- Common traps and distractors

🎯 **HIGH-YIELD FACTS**
List 10-15 most testable points:
1. [Fact] → [Why NEET loves this]
2. [Fact] → [Why NEET loves this]
[Continue...]

💡 **MUST-KNOW FOR EXAM**
- Formula/values to memorize
- Can't-afford-to-forget points
- Instant recall triggers

⚡ **QUICK REVISION STRATEGY**
- 5-minute review technique
- Last-day before exam focus
- What to revise first

❌ **COMMON MISTAKES**
- What students get wrong
- How to avoid these errors
- Negative marking traps

🔗 **LINKED TOPICS**
- Often asked together
- Cross-subject connections
- Integrated questions possible

📝 **PREVIOUS YEAR INSIGHTS**
- Pattern observed in last 5 years
- Difficulty level evolution
- Weightage distribution

⏱️ **TIME MANAGEMENT**
- Average time per question
- When to skip vs attempt
- Difficulty assessment

🎯 **SCORING STRATEGY**
- Safe questions (must get)
- Moderate (calculated risk)
- Tough (skip if unsure)

Make every minute of study count for maximum marks!"""

        return self._generate_response(prompt, 'neet_focused')
    
    def _generate_response(self, prompt: str, mode: str) -> Dict[str, Any]:
        """Generate AI response with error handling"""
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            
            if response.text:
                return {
                    "success": True,
                    "mode": mode,
                    "content": response.text.strip(),
                    "timestamp": datetime.now().isoformat(),
                    "specialization": self.specialization
                }
            else:
                raise Exception("Empty response from AI")
                
        except Exception as e:
            logger.error(f"Error in {mode} mode: {str(e)}")
            return {
                "success": False,
                "mode": mode,
                "error": str(e),
                "fallback_content": "I encountered an error. Please try again or rephrase your question."
            }
    
    def generate_study_plan(self, topic: str, time_available: str, current_level: str) -> Dict[str, Any]:
        """Generate personalized study plan"""
        
        rag_context = self.rag_system.get_relevant_context(topic, max_tokens=1500)
        
        prompt = f"""Create a personalized study plan for NEET preparation.

**VERIFIED MEDICAL KNOWLEDGE:**
{rag_context}

**TOPIC:** {topic}
**TIME AVAILABLE:** {time_available}
**CURRENT LEVEL:** {current_level}
**SPECIALIZATION:** {self.specialization}

Create a structured study plan:

📅 **STUDY TIMELINE**
Break down into phases (daily/weekly based on time available)

**Phase 1: Foundation** (X% of time)
- Core concepts to master
- Resources to use
- Success criteria

**Phase 2: Deep Dive** (X% of time)
- Advanced topics
- Clinical correlations
- Practice problems

**Phase 3: Application** (X% of time)
- Clinical cases
- Previous year questions
- Mock tests

**Phase 4: Revision** (X% of time)
- Quick revision techniques
- High-yield focus
- Last-minute strategies

🎯 **DAILY ROUTINE**
- Active learning session
- Practice questions
- Revision slot
- Sleep & breaks

📚 **RESOURCES**
- Textbook chapters
- Video lectures
- Question banks
- Flashcards

✅ **MILESTONES & CHECKPOINTS**
- Weekly goals
- Self-assessment tests
- Progress tracking

🔄 **SPACED REPETITION SCHEDULE**
- Day 1, 3, 7, 14, 30 review
- What to review when

💪 **MOTIVATION BOOSTERS**
- Track progress
- Celebrate small wins
- Stay consistent

Make it realistic, actionable, and effective!"""

        return self._generate_response(prompt, 'study_plan')
    
    def explain_with_analogy(self, complex_topic: str) -> Dict[str, Any]:
        """Explain complex topics using analogies"""
        
        rag_context = self.rag_system.get_relevant_context(complex_topic, max_tokens=1500)
        
        prompt = f"""You are a master of medical analogies and metaphors.

**VERIFIED MEDICAL KNOWLEDGE:**
{rag_context}

**COMPLEX TOPIC:** {complex_topic}

Explain this using powerful analogies:

🌟 **THE ANALOGY**
- Choose a relatable real-world system
- Map medical concept to everyday experience
- Make it vivid and memorable

🔗 **THE MAPPING**
Medical Concept ↔ Real-World Analogy
- [Concept 1] ↔ [Analogy 1]
- [Concept 2] ↔ [Analogy 2]
- [Process] ↔ [Similar process]

📖 **THE STORY**
Narrate the analogy:
- Beginning: Set the scene
- Middle: Show the process
- End: Complete the cycle

💡 **LIMITATIONS OF THE ANALOGY**
- Where it breaks down
- What it doesn't capture
- Transition back to medical reality

✨ **THE ACTUAL MEDICAL CONCEPT**
Now explain accurately with proper terminology

🎯 **TAKEAWAY**
- Remember: [Simple trigger]
- Associates with: [Analogy]
- Means: [Medical fact]

Make it impossible to forget!"""

        return self._generate_response(prompt, 'analogy')


class WorldClassMedicalTeachingSystem:
    """Orchestrates world-class medical education experience"""
    
    def __init__(self):
        self.teaching_agents = self._initialize_teaching_agents()
        self.rag_system = MedicalRAG()
        
    def _initialize_teaching_agents(self) -> Dict[str, EnhancedMedicalTeachingAgent]:
        """Initialize specialized teaching agents"""
        agents = {}
        
        specializations = {
            'anatomy': 'Human Anatomy',
            'physiology': 'Human Physiology',
            'biochemistry': 'Medical Biochemistry',
            'pathology': 'Medical Pathology',
            'pharmacology': 'Medical Pharmacology',
            'general': 'General Medicine'
        }
        
        for agent_id, specialization in specializations.items():
            agents[agent_id] = EnhancedMedicalTeachingAgent(
                agent_id=agent_id,
                name=f"Dr. {specialization} Expert",
                specialization=specialization
            )
        
        return agents
    
    def teach(self, question: str, mode: str = 'explain', agent: str = None, 
              difficulty: str = 'intermediate') -> Dict[str, Any]:
        """Main teaching interface"""
        
        # Auto-route if no agent specified
        if agent is None or agent not in self.teaching_agents:
            agent = self._smart_route(question)
        
        teaching_agent = self.teaching_agents[agent]
        result = teaching_agent.teach(question, mode, difficulty)
        
        result['agent_used'] = agent
        result['available_modes'] = teaching_agent.teaching_modes
        
        return result
    
    def _smart_route(self, question: str) -> str:
        """Intelligently route to best teaching agent"""
        # Simple keyword-based routing (can be enhanced with AI)
        question_lower = question.lower()
        
        keywords = {
            'anatomy': ['anatomy', 'structure', 'muscle', 'bone', 'nerve', 'artery', 'vein'],
            'physiology': ['physiology', 'function', 'mechanism', 'homeostasis', 'regulation'],
            'biochemistry': ['biochemistry', 'metabolism', 'enzyme', 'protein', 'pathway'],
            'pathology': ['pathology', 'disease', 'disorder', 'cancer', 'infection'],
            'pharmacology': ['drug', 'medication', 'pharmacology', 'treatment', 'therapy']
        }
        
        for agent, kw_list in keywords.items():
            if any(kw in question_lower for kw in kw_list):
                return agent
        
        return 'general'
    
    def get_learning_recommendation(self, topic: str, user_level: str) -> Dict[str, Any]:
        """Recommend best learning approach for a topic"""
        
        recommendations = {
            "beginner": {
                "primary_mode": "step_by_step",
                "supplementary": ["mnemonic", "explain"],
                "practice": "quiz with beginner difficulty"
            },
            "intermediate": {
                "primary_mode": "explain",
                "supplementary": ["clinical_case", "socratic"],
                "practice": "quiz with intermediate difficulty"
            },
            "advanced": {
                "primary_mode": "clinical_case",
                "supplementary": ["differential", "neet_focused"],
                "practice": "quiz with advanced difficulty"
            }
        }
        
        return {
            "topic": topic,
            "user_level": user_level,
            "recommendations": recommendations.get(user_level, recommendations["intermediate"]),
            "learning_path": [
                "1. Start with foundational explanation",
                "2. Practice with quiz questions",
                "3. Apply to clinical cases",
                "4. Reinforce with mnemonics",
                "5. Test with differential diagnosis",
                "6. Prepare for NEET-style questions"
            ]
        }
