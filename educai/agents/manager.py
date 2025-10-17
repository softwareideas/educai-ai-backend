import re
from typing import Any, Dict, Optional
from educai.agents.rag import get_shared_rag

class ManagerAgent:
    def __init__(self):
        self.rag = get_shared_rag()
        self.agent_id: str = "manager"
        self.name: str = "Medical Manager Agent"
        self.description: str = "Conversation controller and medical domain gatekeeper"
        self.system_prompt: str = (
            "You are the Medical Manager Agent, responsible for classifying and routing user queries within a medical assistant system. "
            "Your job is to identify whether a message is related to the medical domain or not. "
            "If the question is general medical (for example, about health, fitness, nutrition, or wellness), forward it to the General Medical Agent. "
            "If the question is specific to symptoms, diseases, medications, treatments, or diagnostics, forward it to the Medical Expert Agent. "
            "If the question is unrelated to medicine (for example, about Google, Facebook, education, history, technology, or any non-medical topic), do not forward it. "
            "Instead, reply briefly and politely that you are designed only for medical-related discussions. "
            "Never answer non-medical questions yourself and never forward them. "
            "If the message is unclear or irrelevant, ask the user to clarify their medical question. "
            "Keep responses short (2–3 sentences) and maintain a professional, health-focused tone."
        )


    def _mode_scope(self, mode: Optional[str]) -> str:
        if mode in ("neet", "neet_focused"):
            return "NEET preparation"
        if mode in ("exam", "semester", "class_exam"):
            return "Semester and Class Exam preparation"
        return "medical studies"

    def _is_greeting_or_smalltalk(self, text: str) -> bool:
        q = (text or "").strip().lower()
        if not q:
            return False
        greetings = [
            "hi", "hello", "hey", "yo", "hola", "namaste", "greetings", "good day",
            "good morning", "good afternoon", "good evening",
            "how are you", "what's up", "whats up", "sup",
            "who are you", "what can you do", "introduce yourself",
            "what topics", "what are the topics", "which topics", "suggest topics", "recommend topics",
            "which subject", "what subject", "best subject", "in which subject you're best",
            "what can you teach", "what do you cover", "can you help", "help me", "pls help", "please help",
            "what is your name", "whats your name", "what's your name", "your name", "may i know your name"
        ]
        return any(q == g or q.startswith(g + " ") for g in greetings)

    def _is_ack(self, text: str) -> bool:
        q = (text or "").strip().lower()
        if not q:
            return False
        norm = re.sub(r"[^a-z\s]", "", q).strip()
        if not norm:
            return False
        if any(phrase in norm for phrase in ["good morning", "good afternoon", "good evening"]):
            return False
        ack_exact = {
            "thanks", "thank you", "thank u", "thx", "tnx", "ty", "great", "awesome", "cool", "nice", "ok", "okay", "k",
            "got it", "understood", "yup", "yeah", "yep", "alright", "sure", "perfect", "wonderful",
            "good", "fine", "excellent", "amazing", "hmm", "oh", "ohh", "ohhh", "aha",
            "bye", "good night", "goodnight", "see you"
        }
        if norm in ack_exact:
            return True
        ack_prefixes = [
            "thanks", "thank you", "thank u", "thx", "tnx", "great", "awesome", "cool", "nice", "ok", "okay", "alright",
            "perfect", "wonderful", "amazing", "good", "fine", "excellent", "got it", "understood",
            "yup", "yeah", "yep", "sure", "hmm", "oh", "ohh", "ohhh", "aha", "bye", "good night", "see you"
        ]
        return any(norm.startswith(p) for p in ack_prefixes)

    def _is_capability_query(self, text: str) -> bool:
        q = (text or "").strip().lower()
        if not q:
            return False
        norm = re.sub(r"[^a-z\s]", "", q).strip()
        if not norm:
            return False
        patterns = [
            "what can you do", "what do you do", "your capability", "your capabilities",
            "what are you capable", "what are your capabilities", "capabilities", "capability", "capable"
        ]
        if any(p in norm for p in patterns):
            return True
        # Also catch short forms like "what's your capable"
        return "capab" in norm

    def _is_name_query(self, text: str) -> bool:
        q = (text or "").strip().lower()
        if not q:
            return False
        norm = re.sub(r"[^a-z\s]", "", q).strip()
        if not norm:
            return False
        patterns = [
            "what is your name", "whats your name", "what's your name", "your name",
            "may i know your name", "tell me your name"
        ]
        return any(p in norm for p in patterns)

    def _is_personal_info_query(self, text: str) -> bool:
        q = (text or "").strip().lower()
        if not q:
            return False
        norm = re.sub(r"[^a-z\s]", "", q).strip()
        if not norm:
            return False
        patterns = [
            "where are you from", "where do you live", "your location", "where are you located",
            "what is your age", "how old are you", "who created you", "who built you", "who made you"
        ]
        return any(p in norm for p in patterns)

    def _is_unclear(self, text: str) -> bool:
        q = (text or "").strip()
        if not q:
            return True
        # Normalize (keep letters/numbers/spaces)
        norm = re.sub(r"[^a-z0-9\s]", "", q.lower()).strip()
        if not norm:
            return True
        # Very short tokens or punctuation-only variants
        if norm in {"?", "??", "???", ".", "..", "..."}:
            return True
        # Check for long repeated characters (e.g., "aaaaaa")
        compact = norm.replace(" ", "")
        if re.fullmatch(r"(.)\1{4,}", compact):
            return True
        # Require at least one alphabetic word of length >= 3
        words = norm.split()
        has_meaningful = any(len(w) >= 3 and re.search(r"[a-z]", w) for w in words)
        return not has_meaningful

    def _is_medical(self, text: str, mode: Optional[str] = None) -> bool:
        q = (text or "").strip().lower()
        if not q:
            return False
        core = [
            "neet", "mbbs", "medical", "medicine", "clinical", "patient", "case",
            "symptom", "sign", "diagnosis", "treatment", "management", "pathogenesis",
            "mechanism of action", "side effect", "contraindication", "dose", "dosage",
            "anatomy", "physiology", "biochemistry", "pathology", "pharmacology",
            "organ", "tissue", "bone", "muscle", "nerve", "blood vessel", "histology",
            "embryology", "enzyme", "metabolism", "hormone", "vitamin", "dna", "rna",
            "disease", "infection", "tumor", "lesion", "inflammation",
            "mcq", "quiz", "mnemonic", "study plan",
            "brain", "heart", "lung", "kidney", "liver", "spleen", "pancreas", "stomach",
            "intestine", "neuron", "artery", "vein", "capillary", "blood", "cell", "skull",
            "health", "wellness", "nutrition", "fitness", "doctor", "hospital", "clinic",
            "pharmacokinetics", "pharmacodynamics", "anatomical", "neurology", "cardiology",
            "dermatology", "endocrinology", "gastroenterology", "hematology", "immunology"
        ]
        if any(k in q for k in core):
            return True
        # Include NEET Biology plant/ecology only in NEET modes
        if mode in ("neet", "neet_focused"):
            neet_bio = [
                "photosynthesis", "respiration in plants", "plant physiology", "plant growth",
                "transport in plants", "xylem", "phloem", "stomata", "chlorophyll",
                "calvin cycle", "c3", "c4", "cam plants", "transpiration",
                "ecosystem", "biodiversity", "conservation", "organisms and populations",
                "cell cycle", "cell division", "biomolecules", "enzymes",
                "genetics", "evolution", "reproduction in organisms", "reproductive health",
                "sexual reproduction in flowering plants"
            ]
            if any(k in q for k in neet_bio):
                return True
        return False

    def handle(self, question: str, mode: Optional[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if self._is_ack(question):
            scope = self._mode_scope(mode)
            if scope == "NEET preparation":
                resp = "You're welcome! If you need anything else for NEET prep, just ask."
            elif scope == "Semester and Class Exam preparation":
                resp = "You're welcome! If you need anything else for Semester or Class Exams, just ask."
            else:
                resp = "You're welcome! If you need anything else for your medical studies, just ask."
            return {"handled": True, "response": resp, "reason": "acknowledgment"}

        if self._is_name_query(question):
            return {"handled": True, "response": "I'm your Medical Study Manager.", "reason": "name_query"}

        if self._is_personal_info_query(question):
            return {"handled": True, "response": "I'm a virtual medical study assistant. Let's focus on medical and health-related questions.", "reason": "personal_info"}


        # Greetings/small talk should take precedence over unclear/gibberish
        if self._is_greeting_or_smalltalk(question):
            scope = self._mode_scope(mode)
            if scope == "NEET preparation":
                base = "Hello! I'm your medical learning assistant for NEET preparation. "
                hint = "For example, ask: 'Explain RAAS mechanism' or 'Quiz me on ECG basics.'"
            elif scope == "Semester and Class Exam preparation":
                base = "Hello! I'm your medical learning assistant for Semester and Class Exam preparation. "
                hint = "For example, ask: 'Short note on CSF circulation' or '2-mark question on types of shock.'"
            else:
                base = "Hello! I can help to prepare your medical studies. "
                hint = "For example, ask: 'What is the cerebellum?' or 'Make a mnemonic for cranial nerves.'"
            return {"handled": True, "response": base + "Ask me a medical question to begin. " + hint, "reason": "greeting_smalltalk"}

        # Capability summary
        if self._is_capability_query(question):
            scope = self._mode_scope(mode)
            subjects_text = "Anatomy, Physiology, Biochemistry, Pathology, Pharmacology"
            if scope == "NEET preparation":
                resp = (
                    f"I help with NEET prep: explain concepts, generate quizzes, mnemonics, clinical cases, and study tips across {subjects_text}."
                )
            elif scope == "Semester and Class Exam preparation":
                resp = (
                    f"I help with Semester/Class exam prep: concise explanations, short-notes, 2/5-mark style Q&A, mnemonics, and practice questions across {subjects_text}."
                )
            else:
                resp = (
                    f"I help with medical studies: explain concepts, mnemonics, quizzes, clinical cases, and study guidance across {subjects_text}."
                )
            return {"handled": True, "response": resp, "reason": "capabilities"}

        # Generic help requests for prep (concise, mode-aware next-step prompt)
        norm = re.sub(r"[^a-z\s]", "", (question or "").lower()).strip()
        if norm and ("prepare" in norm or "prep" in norm or "help" in norm or "explain me" in norm) and ("neet" in norm or "exam" in norm or "semester" in norm or "class" in norm or "study" in norm):
            scope = self._mode_scope(mode)
            if scope == "NEET preparation":
                resp = (
                    "Sure—let's focus your NEET prep. Tell me a subject and topic to begin (e.g., Anatomy: cranial nerves; Physiology: cardiac cycle; Pharmacology: beta blockers; Pathology: inflammation; Biochemistry: glycolysis)."
                )
            elif scope == "Semester and Class Exam preparation":
                resp = (
                    "Sure—let's focus your Semester/Class exam prep. Share subject and topic (e.g., short note on CSF circulation; 2-mark types of shock; glycolysis steps)."
                )
            else:
                resp = (
                    "Sure—tell me a medical subject and topic to begin (e.g., Anatomy: cranial nerves; Physiology: cardiac cycle)."
                )
            return {"handled": True, "response": resp, "reason": "generic_help"}

        # Unclear/gibberish handling (after greeting/capabilities/help)
        if self._is_unclear(question):
            return {"handled": True, "response": "I didn’t quite understand that. Could you please rephrase your medical question?", "reason": "unclear"}

        if not self._is_medical(question, mode):
            return {"handled": True, "response": "I’m here to help with medical and health-related questions. Could you please ask me something in that area?", "reason": "non_medical"}

        return {"handled": False}
