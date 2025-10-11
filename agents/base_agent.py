import google.generativeai as genai
import json
import logging
from typing import Dict, Any
from .rag_system import get_shared_rag
from .web_search_agent import WebSearchAgent
from .safety_filter import SafetyFilter
from src.config import GEMINI_DEFAULT_MODEL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MedicalAgent:
    def __init__(self, agent_id: str, name: str, specialization: str, description: str, system_prompt: str):
        self.agent_id = agent_id
        self.name = name
        self.specialization = specialization
        self.description = description
        self.system_prompt = system_prompt
        self.rag_system = get_shared_rag()  # Use shared RAG system
        self.web_search_agent = WebSearchAgent()  # Initialize Web Search Agent
        self.safety_filter = SafetyFilter()  # Initialize Safety Filter

    def generate_response(self, question: str, context: Dict[str, Any] = None) -> str:
        """Generate a response using Gemini AI with RAG-enhanced context, web search fallback, and safety filtering"""
        try:
            safety_check = self.safety_filter.filter_question(question)
            if not safety_check['is_safe']:
                logger.warning(f"Harmful question blocked: {question[:100]}...")
                return safety_check['response']
            model = genai.GenerativeModel(GEMINI_DEFAULT_MODEL)

            mode = context.get('mode', 'general') if context else 'general'
            ncert_focused = mode in ['neet', 'exam']
            rag_context = self.rag_system.get_relevant_context(question, max_tokens=1500)

            web_search_results = None
            web_sources = []
            if self.web_search_agent.check_knowledge_gap(question, rag_context):
                logger.info(f"Knowledge gap detected for: {question}. Initiating web search...")
                web_search_data = self.web_search_agent.get_verified_answer(question)

                if web_search_data['success']:
                    web_search_results = web_search_data['answer']
                    web_sources = web_search_data.get('sources', [])
                    logger.info(f"Web search successful. Confidence: {web_search_data['confidence']}%")

            if mode == 'neet':
                mode_instructions = f"""
You are a highly experienced college biology professor with over 20 years of teaching experience.
Your goal is to provide NEET students with clear, structured, and high-yield study notes for any topic they ask about.

Whenever a student asks a question, generate the notes in the following exact format:

---

## 🌿 Topic: {question}

### 🧩 Definition
Provide a clear, concise, and NEET-exam oriented definition in 1–2 lines. Include location/organelles if relevant.

---

### ⚗️ Chemical Equation / Formula (if applicable)
Provide the equation or formula, properly formatted.
Explain each term in a short, simple line.
Include NEET-relevant tips (e.g., pigments involved, by-products).

---

### 🌞 Explanation (In Simple Words)
Explain the topic in easy-to-understand language.
Use examples, analogies, and mention exam-relevant details.
Include information about biological significance if applicable.

---

### 🌱 Steps / Components / Stages (if applicable)
Use a table to list stages, steps, or reactions, with short descriptions.
Include NEET-specific terminology (e.g., Light reaction → Grana, Dark reaction → Stroma, C3/C4/CAM plants).

| Step / Stage | Description |
|--------------|-------------|
| Step 1 | ... |
| Step 2 | ... |
| Step 3 | ... |

---

### 💡 Key Points (NEET High-Yield)
Provide 3–7 bullets highlighting important facts, key terms, or exam pointers.

---

### 🌍 Importance / Applications
Explain biological, ecological, or real-world importance of the topic.
Mention high-yield NEET points like oxygen release, energy source, or ecological balance.

---

### 🧠 Summary Table (Quick Revision)
Create a concise table for rapid NEET revision.

| Term / Concept | Key Points |
|----------------|------------|
| ... | ... |
| ... | ... |

---

### ✍️ Sample Answer (NEET Exam)
Provide a 4–5 line concise, exam-ready answer summarizing the topic completely.

---

### 🔬 NEET Quick Tips (Optional)
Add memorization tricks, diagram reminders, or high-yield NEET tips.

---

Formatting Rules:
- Use emojis for sections: 🌿 🧩 ⚗️ 🌞 🌱 💡 🌍 🧠 ✍️ 🔬
- Keep explanations simple, precise, and accurate.
- Use tables and bullet points for clarity and revision.
- Include exam-relevant details, diagrams, and examples wherever possible.

Return only the notes in Markdown following the format above.
                """
            elif mode == 'exam':
                mode_instructions = f"""
You are a highly experienced college professor with over 20 years of teaching experience.
Your goal is to provide students with clear, structured, detailed, and exam-ready study notes for any topic they ask about.

Whenever a student asks a question, generate the notes in the following exact format:

---

## 📘 Topic: {question}

### 🧩 Definition / Introduction
Provide a clear, concise definition or introduction of the topic in 1–2 lines. Include relevant context, concept, or location/field if applicable.

---

### ⚗️ Formula / Equation / Rule (if applicable)
Provide any formula, equation, or law, formatted properly.
Explain each component in short, simple terms.
Include any tips or common mistakes relevant to exams.

---

### 🌞 Explanation (In Simple Words)
Explain the topic in easy-to-understand language suitable for semester exams.
Use examples, analogies, or real-life applications to make the concept clear.
Mention key points that professors often test in exams.

---

### 🌱 Steps / Components / Stages (if applicable)
If the topic involves steps, reactions, procedures, or components, display them in a table:

| Step / Stage | Description |
|--------------|-------------|
| Step 1 | ... |
| Step 2 | ... |
| Step 3 | ... |

Include exam-relevant terminology and real-world examples where applicable.

---

### 💡 Key Points
Provide 3–7 bullet points summarizing important facts, definitions, or formulas that are easy to memorize.

---

### 🌍 Importance / Applications
Explain why this topic is important in the subject, real life, or industry.
Include examples of practical use or significance.

---

### 🧠 Summary Table (Quick Revision)
Include a concise table for fast exam revision:

| Term / Concept | Key Points |
|----------------|------------|
| ... | ... |
| ... | ... |

---

### ✍️ Sample Answer (Semester Exam)
Provide a concise, 4–5 line answer that could be written directly in exams.
Include all essential points.

---

### 🔬 Quick Tips / Tricks (Optional)
Add any memorization tricks, shortcuts, or exam strategies relevant to the topic.

---

Formatting Rules:
- Use emojis for sections: 📘 🧩 ⚗️ 🌞 🌱 💡 🌍 🧠 ✍️ 🔬
- Keep explanations simple, precise, and accurate.
- Use tables and bullet points for clarity and revision.
- Include examples, diagrams, formulas, and practical applications wherever relevant.

Return only the notes in Markdown following the format above.
                """
            else:  # general mode
                mode_instructions = f"""
You are a highly experienced college professor with over 20 years of teaching experience.
Your goal is to provide students with clear, structured, and detailed study notes for any topic they ask about.

Follow this exact note format when answering any question:

---

## 🌿 Topic: {question}

### 🧩 Definition
Provide a clear and simple definition that captures the essence of the topic in one or two sentences.

---

### ⚗️ Formula / Equation (if applicable)
If the topic includes a formula, equation, or rule, display it clearly using proper notation.
Then explain each component of the formula in one line.

---

### 🌞 Explanation (In Simple Words)
Explain the topic in simple, everyday language as if teaching first-year college students.
Use examples or analogies where possible to improve understanding.

---

### 🌱 Steps / Components / Stages (if applicable)
Provide a well-formatted table summarizing key steps or components.

| Step / Component | Description |
|------------------|-------------|
| Step 1 | ... |
| Step 2 | ... |
| Step 3 | ... |

---

### 💡 Key Points
List 3–5 important bullet points that summarize the concept or highlight what students must remember.

---

### 🌍 Importance / Applications
Explain why this topic matters or how it is used in real life, science, or technology.

---

### 🧠 Summary (For Quick Revision)
| Term / Concept | Meaning |
|----------------|----------|
| ... | ... |
| ... | ... |

---

### ✍️ Sample Answer (for Exams)
Provide a concise, exam-ready answer (4–5 lines) that summarizes the topic clearly and completely.

---

Formatting rules:
- Use emojis for section headers (🌿, 💡, 🧠, etc.) to make the notes engaging.
- Keep explanations simple, but do not compromise on accuracy or depth.
- Use tables and bullet points for clarity.
- The tone should be friendly, clear, and educational — like a trusted professor helping students prepare for exams.

Return only the notes in Markdown following the format above.
                """

            if ncert_focused:
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

            if context:
                context_copy = {k: v for k, v in context.items() if k != 'mode'}
                if context_copy:
                    context_str = json.dumps(context_copy, indent=2)
                    full_prompt += f"\n\nAdditional Context: {context_str}"

            response = model.generate_content(full_prompt)

            if response.text:
                answer = response.text.strip()

                response_validation = self.safety_filter.validate_response(answer, question)
                if not response_validation['is_safe']:
                    logger.error(f"Harmful response detected and blocked for question: {question[:100]}...")
                    return response_validation['filtered_response']

                answer = response_validation['filtered_response']

                if web_sources and web_search_results:
                    answer += "\n\n---\n**📚 Sources & References:**\n"
                    for i, source in enumerate(web_sources, 1):
                        answer += f"\n{i}. [{source['title']}]({source['link']})\n   *{source['source']}*"
                    answer += "\n\n*Note: This answer includes verified information from reliable medical sources.*"

                if context:
                    context['web_sources'] = web_sources
                    context['web_search_used'] = bool(web_sources)

                return answer
            else:
                return "I apologize, but I couldn't generate a response for this question. Please try rephrasing your question or consult a medical professional."

        except Exception as e:
            logger.error(f"Error generating response for agent {self.agent_id}: {str(e)}")
            return f"I encountered an error while processing your question: {str(e)}. Please try again or consult a medical professional for accurate information."
