from typing import Dict, Any, Tuple
import logging
import re

from app.session import run_agent
from app.config import CONTROLLER_GATE_ENABLED
from flask import g

# Gating functions can be uncommented if needed for direct controller-level checks
# from medical_agent_team.tools.controller_gates import _is_unsafe, _is_medical_relevant, _is_smalltalk

# Allowed modes
VALID_MODES = {"general", "neet", "exam", "beginner", "advanced"}

# Maximum lengths
MAX_QUESTION_LENGTH = 2000
MAX_SESSION_ID_LENGTH = 100
def _is_neet_request(text: str) -> bool:
    if not text or not isinstance(text, str):
        return False
    t = text.strip().lower()
    neet_markers = [
        "neet",
        "neet exam",
        "for neet",
        "neet-style",
        "neet style",
        "neet format",
        "convert to neet",
        "make it neet",
        "neet focused",
    ]
    return any(m in t for m in neet_markers)



def _validate_input(question: str, mode: str, session_id: str) -> Tuple[bool, str]:
    """Validate input parameters."""
    if not question or not isinstance(question, str):
        return False, "Question is required and must be a string"
    
    if len(question.strip()) == 0:
        return False, "Question cannot be empty"
    
    if len(question) > MAX_QUESTION_LENGTH:
        return False, f"Question exceeds maximum length of {MAX_QUESTION_LENGTH} characters"
    
    if mode not in VALID_MODES:
        return False, f"Mode must be one of: {', '.join(VALID_MODES)}"
    
    if not session_id or not isinstance(session_id, str):
        return False, "Session ID must be a string"
    
    if len(session_id) > MAX_SESSION_ID_LENGTH:
        return False, f"Session ID exceeds maximum length of {MAX_SESSION_ID_LENGTH} characters"
    
    # Sanitize session_id - only allow alphanumeric, dash, underscore
    if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
        return False, "Session ID contains invalid characters. Only alphanumeric, dash, and underscore are allowed"
    
    return True, ""


def ask_controller(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Controller for handling ask requests."""
    try:
        # Extract and sanitize inputs
        question = (payload or {}).get("question", "").strip()
        mode = (payload or {}).get("mode", "general").strip().lower()
        session_id = (payload or {}).get("session_id") or "default"
        
        # Validate inputs
        is_valid, error_msg = _validate_input(question, mode, session_id)
        if not is_valid:
            logging.warning("Invalid input: %s", error_msg)
            return {
                "error": "Invalid input",
                "message": error_msg,
                "question": question,
                "response": "",
                "session_id": session_id,
                "request_id": getattr(g, "request_id", None),
            }

        # State delta can carry mode for the agent
        state_delta = {"mode": mode}

        # The controller gate is now disabled by default and delegated to the manager agent.
        # To re-enable, set CONTROLLER_GATE_ENABLED=true in the .env file.
        if CONTROLLER_GATE_ENABLED:
            # The gating functions would need to be imported and called here.
            # This block is for demonstration and is not active by default.
            pass

        # Policy: If user requests NEET formatting but mode is not 'neet', return a polite subscription response
        if mode != "neet" and _is_neet_request(question):
            polite_msg = (
                "NEET mode is available as part of our premium plan with exam‑focused formatting, "
                "mnemonics, exam traps, and practice questions. "
                "Please subscribe to access NEET mode. Meanwhile, I can continue in General mode."
            )
            return {
                "question": question,
                "response": polite_msg,
                "agent_used": "orchestrator_agent",
                "mode": mode,
                "policy": "neet_mode_required",
                "request_id": getattr(g, "request_id", None),
            }

        # Run agent with error handling
        try:
            content, resolved_question, report_sources, generated_by, source_items = run_agent(
                session_id=session_id, 
                question=question, 
                state_delta=state_delta
            )
        except RuntimeError as e:
            error_str = str(e).lower()
            # Check for rate limiting errors
            if 'rate limit' in error_str or '429' in error_str or 'resource_exhausted' in error_str or 'quota' in error_str:
                logging.warning("Rate limit error for session %s: %s", session_id, str(e))
                return {
                    "error": "Rate limit exceeded",
                    "message": (
                        "The API service is temporarily unavailable due to rate limiting. "
                        "Please wait 60-120 seconds before retrying. "
                        "If this persists, you may have reached your API quota limit. "
                        "The system is optimizing to reduce API calls."
                    ),
                    "question": question,
                    "response": "",
                    "session_id": session_id,
                    "agent_used": "manager_pipeline",
                    "mode": mode,
                    "retry_after": "Please wait 30-60 seconds before retrying.",
                    "request_id": getattr(g, "request_id", None),
                }
            else:
                logging.error("RuntimeError in run_agent: %s", str(e), exc_info=True)
                return {
                    "error": "Agent execution failed",
                    "message": "An error occurred while processing your question. Please try again.",
                    "question": question,
                    "response": "",
                    "session_id": session_id,
                    "agent_used": "manager_pipeline",
                    "mode": mode,
                    "request_id": getattr(g, "request_id", None),
                }
        except Exception as e:
            error_str = str(e).lower()
            # Check for rate limiting in generic exceptions too
            if '429' in error_str or 'resource_exhausted' in error_str or 'rate limit' in error_str:
                logging.warning("Rate limit error (generic) for session %s: %s", session_id, str(e))
                return {
                    "error": "Rate limit exceeded",
                    "message": (
                        "The API service is temporarily unavailable due to rate limiting. "
                        "Please wait a few moments and try again."
                    ),
                    "question": question,
                    "response": "",
                    "session_id": session_id,
                    "agent_used": "manager_pipeline",
                    "mode": mode,
                    "retry_after": "Please wait 30-60 seconds before retrying.",
                    "request_id": getattr(g, "request_id", None),
                }
            logging.error("Error in run_agent: %s", str(e), exc_info=True)
            return {
                "error": "Agent execution failed",
                "message": "An error occurred while processing your question. Please try again.",
                "question": question,
                "response": "",
                "session_id": session_id,
                "agent_used": "manager_pipeline",
                "mode": mode,
                "request_id": getattr(g, "request_id", None),
            }

        # The fallback pipeline is now fully delegated to the manager agent.
        logging.info("Route=manager session=%s", session_id)

        return {
            "question": question,
            "response": content or "",
            "agent_used": (generated_by or "manager_pipeline"),
            "routing_info": {"auto_routed": True, "reason": "adk_runner"},
            "mode": mode,
            "rag_enabled": True,
            "session_id": session_id,
            "resolved_question": resolved_question or question,
            "sources": report_sources or [],
            "sources_detailed": source_items or [],
            "request_id": getattr(g, "request_id", None),
        }
    except Exception as e:
        logging.error("Unexpected error in ask_controller: %s", str(e), exc_info=True)
        return {
            "error": "Unexpected error",
            "message": "An unexpected error occurred. Please try again.",
            "question": (payload or {}).get("question", ""),
            "response": "",
            "request_id": getattr(g, "request_id", None),
        }
