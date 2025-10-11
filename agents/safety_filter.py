"""
Safety Filter for Medical AI Agent
Prevents harmful, dangerous, or inappropriate responses
"""

import re
from typing import Dict, Any
try:
    from profanity_check import predict as pf_predict, predict_prob as pf_predict_prob
    _PROFANITY_AVAILABLE = True
except Exception:
    _PROFANITY_AVAILABLE = False

class SafetyFilter:
    """Filter to detect and block harmful or dangerous questions"""
    
    def __init__(self):
        # Harmful keywords and patterns
        self.harmful_patterns = [
            # Violence and harm patterns
            r'\b(kill|murder|harm|hurt|injure|torture|abuse)\s+(someone|people|person|myself|yourself)\b',
            r'\b(how to|ways to|methods to|best way to)\s+(kill|murder|harm|suicide|die|end life)\b',
            r'\bpainless\s+(death|killing|suicide|murder)\b',
            r'\b(suicide|self-harm|self harm|end my life|take my life)\b',
            r'\b(poison|lethal|fatal|deadly)\s+(dose|amount|method|way)\b',
            r'\beuthanasia\s+(method|procedure|way|how)\b',
            r'\b(killing|murder|assassination)\s+(method|technique|way|approach)\b',
            r'\bwhich\s+(drug|substance|poison|method).*(kill|die|fatal|lethal|painless death)\b',
            r'\b(painless|pain-free|without pain).*(killing|death|suicide|murder|die)\b',
            
            # Drug abuse patterns
            r'\bhow to\s+(overdose|OD|get high)\b',
            r'\b(recreational|abuse|misuse)\s+(dose|amount)\s+of\b',
            r'\bwhat\s+(drugs|substances).*(get high|euphoria|trip)\b',
            
            # Illegal/dangerous procedures
            r'\bhow to\s+(perform|do)\s+(abortion|surgery)\s+(at home|myself)\b',
            r'\b(home|DIY|self)\s+(abortion|surgery|amputation)\b',
            
            # Weapons/explosives
            r'\bhow to\s+(make|create|build)\s+(bomb|explosive|weapon|poison)\b',
        ]
        
        # Compile patterns
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.harmful_patterns]

        # Sexual explicit instruction patterns (non-educational)
        self.sexual_explicit_patterns = [
            r'\b(how to|ways to|methods to|best way to)\s+(have\s+sex|do\s+sex|have\s+intercourse|have\s+sexual\s+intercourse)\b',
            r'\b(how to|ways to|methods to|best way to)\s+(use|insert|put)\s+penis\s+(in|into|inside)\s+vagin[ae]\b',
            r'\b(oral\s+sex|anal\s+sex|blowjob|handjob|sex\s+positions?)\b.*\b(how to|guide|tips)\b',
            r'\b(kamasutra|porn|pornography)\b',
        ]
        self.compiled_sexual_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.sexual_explicit_patterns]
        
        # Crisis resources
        self.crisis_resources = """
**If you're experiencing a crisis or having thoughts of self-harm:**

🌍 **International Crisis Resources:**
- **Suicide Prevention Lifeline (USA)**: 988 or 1-800-273-8255
- **Crisis Text Line (USA)**: Text HOME to 741741
- **Samaritans (UK)**: 116 123
- **Lifeline (Australia)**: 13 11 14
- **AASRA (India)**: +91-22-27546669
- **Befrienders Worldwide**: https://www.befrienders.org/

📞 **You are not alone. Please reach out for help.**
"""
    
    def is_harmful(self, question: str) -> bool:
        """Check if question contains harmful patterns"""
        question_lower = question.lower().strip()
        
        # Check against all patterns
        for pattern in self.compiled_patterns:
            if pattern.search(question_lower):
                return True
        # Explicit sexual instruction (non-educational)
        for pattern in self.compiled_sexual_patterns:
            if pattern.search(question_lower):
                return True
        # Profanity check (if available)
        if _PROFANITY_AVAILABLE:
            try:
                score = float(pf_predict_prob([question])[0])
                if score >= 0.7:
                    return True
            except Exception:
                pass
        
        return False
    
    def get_safe_response(self, question: str) -> Dict[str, Any]:
        """
        Generate a safe, helpful response for harmful questions
        Returns dict with safe response and resources
        """
        # Determine the type of harmful question
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['suicide', 'kill myself', 'end my life', 'self harm']):
            response = f"""I'm deeply concerned about what you're going through. Your life has value, and there are people who want to help.

{self.crisis_resources}

**As a medical education AI, I cannot and will not provide information that could be used for self-harm.**

Instead, I encourage you to:
1. **Call a crisis helpline immediately** - They have trained counselors available 24/7
2. **Reach out to a trusted friend, family member, or mental health professional**
3. **Go to your nearest emergency room if you're in immediate danger**

Please know that difficult feelings can pass, and help is available. You deserve support and care."""
            
        elif any(word in question_lower for word in ['kill', 'murder', 'harm someone', 'hurt']):
            response = """I cannot and will not provide information about harming others. This type of information is:

1. **Dangerous and Illegal** - Causing harm to others is a serious crime
2. **Against My Purpose** - I'm designed to help with medical education, not facilitate violence
3. **Unethical** - My role is to promote health and wellbeing

**If you're having thoughts of harming others:**
- Please contact local law enforcement or mental health crisis services immediately
- Speak with a mental health professional

**If you have a legitimate medical education question, please rephrase it appropriately.**"""
        
        elif any(p.search(question_lower) for p in self.compiled_sexual_patterns):
            response = (
                "I can't provide explicit sexual instructions. If you're looking for educational content, I can share age-appropriate, factual information on topics like reproductive anatomy, consent, contraception, and prevention of STIs. "
                "If this is a health concern, please speak with a licensed healthcare professional." 
            )
        else:
            response = """I cannot provide the information you're requesting as it could potentially be harmful or dangerous.

**My purpose is to:**
✅ Help you learn medical concepts for education
✅ Prepare you for medical exams like NEET
✅ Explain anatomy, physiology, and medical science
✅ Support your academic growth

**I cannot provide information about:**
❌ Harming yourself or others
❌ Illegal activities
❌ Dangerous procedures or substances
❌ Misuse of medications

**If you have a genuine medical education question, I'm happy to help! Please ask about:**
- Medical concepts and topics
- NEET preparation
- Anatomy and physiology
- Exam strategies and study tips"""
        
        return {
            'is_safe': False,
            'response': response,
            'blocked': True,
            'reason': 'Potentially harmful or dangerous content detected'
        }
    
    def filter_question(self, question: str) -> Dict[str, Any]:
        """
        Main filtering method
        Returns dict indicating if question is safe and response if blocked
        """
        if self.is_harmful(question):
            return self.get_safe_response(question)
        
        return {
            'is_safe': True,
            'response': None,
            'blocked': False
        }
    
    def validate_response(self, response: str, question: str) -> Dict[str, Any]:
        """
        Validate that the AI response doesn't contain harmful content
        This is a second layer of protection
        """
        response_lower = response.lower()
        
        # Check if response contains dangerous instructions
        dangerous_response_patterns = [
            r'here\'s how to (kill|harm|suicide)',
            r'methods? (to|for) (killing|harming|suicide)',
            r'painless (death|killing|suicide)',
            r'lethal dose',
            r'fatal amount',
        ]
        
        for pattern in dangerous_response_patterns:
            if re.search(pattern, response_lower, re.IGNORECASE):
                return {
                    'is_safe': False,
                    'filtered_response': self.get_safe_response(question)['response'],
                    'reason': 'Response contained potentially harmful content'
                }
        # Explicit sexual instruction in response
        for pattern in self.compiled_sexual_patterns:
            if pattern.search(response_lower):
                return {
                    'is_safe': False,
                    'filtered_response': self.get_safe_response(question)['response'],
                    'reason': 'Response contained explicit sexual content'
                }
        # Profanity check (if available)
        if _PROFANITY_AVAILABLE:
            try:
                score = float(pf_predict_prob([response])[0])
                if score >= 0.7:
                    return {
                        'is_safe': False,
                        'filtered_response': self.get_safe_response(question)['response'],
                        'reason': 'Response contained profanity'
                    }
            except Exception:
                pass
        
        return {
            'is_safe': True,
            'filtered_response': response
        }
