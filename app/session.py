from typing import Dict, Any, Tuple, List, Optional
import asyncio
import logging
import json
from google.genai.errors import ClientError

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from medical_agent_team.agents import create_manager_and_team
def _is_smalltalk(text: Optional[str]) -> bool:
    if not text or not isinstance(text, str):
        return False
    t = text.strip().lower()
    if not t:
        return False
    greetings = {
        "hi", "hello", "hey", "hola", "howdy", "good morning", "good afternoon", "good evening",
        "thanks", "thank you", "yo", "sup", "hii", "helo", "hai",
    }
    return t in greetings or t.rstrip("!?.") in greetings


def _friendly_greeting_message() -> str:
    return (
        "Hello! I’m here to help with medical learning. Ask me any topic, mechanism, disease, or drug, "
        "and I’ll create a clear, student‑friendly explanation with sources.\n\n"
        "Try: \n"
        "- Explain the cardiac cycle (general).\n"
        "- High‑yield overview of asthma (neet).\n"
        "- MCQ: Which vitamin deficiency causes night blindness?\n"
    )


# Timeout for agent execution (seconds)
AGENT_TIMEOUT = 300  # 5 minutes

# Rate limiting configuration
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 5  # seconds - increased for better rate limit handling
MAX_RETRY_DELAY = 120  # seconds - increased to 2 minutes
RETRY_BACKOFF_MULTIPLIER = 2.5  # More aggressive backoff

# Create a single, long-lived runner instance.
try:
    _team = create_manager_and_team()
    _root_agent = _team["root_agent"]
    _session_service = InMemorySessionService()
    _runner = Runner(app_name="educai-ai-backend", agent=_root_agent, session_service=_session_service)
except Exception as e:
    logging.error("Failed to initialize agent system: %s", str(e), exc_info=True)
    _team = None
    _root_agent = None
    _session_service = None
    _runner = None


async def run_agent_async(session_id: str, question: str, state_delta: Optional[Dict[str, Any]] = None) -> Tuple[str, str, List[str], Optional[str], Optional[List[Dict[str, Any]]]]:
    """Run the agent asynchronously and return the final response.

    Returns: (content, resolved_question, source_labels, generated_by, source_items)
    """
    if _runner is None:
        raise RuntimeError("Agent system not initialized. Check logs for initialization errors.")
    
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")
    
    # Smalltalk fast-path: respond without running the agent graph
    if _is_smalltalk(question):
        content = _friendly_greeting_message()
        return content, question, [], "orchestrator_agent", []

    message = question.strip()
    mode = (state_delta or {}).get("mode")
    if mode:
        message = f"[Mode: {mode}] {message}"

    try:
        user_content = types.Content(role="user", parts=[types.Part(text=message)])
    except Exception as e:
        logging.error("Failed to create user content: %s", str(e))
        raise

    # Ensure the session exists
    try:
        app_name = getattr(_runner, "app_name", "educai-ai-backend")
        session = await _session_service.get_session(app_name=app_name, user_id="user", session_id=session_id)
        if not session:
            await _session_service.create_session(app_name=app_name, user_id="user", session_id=session_id)
            # Update session state with mode if provided
            if state_delta and "mode" in state_delta:
                # Note: Session state update would go here if ADK supports it
                pass
    except Exception as e:
        logging.error("Failed to manage session: %s", str(e))
        raise

    content = ""
    report_sources: List[str] = []
    report_source_items: Optional[List[Dict[str, Any]]] = None
    generated_by: Optional[str] = None
    events = []
    last_specialist_author: Optional[str] = None
    
    # Retry logic for rate limiting (429 errors)
    retry_count = 0
    last_error = None
    
    while retry_count <= MAX_RETRIES:
        try:
            events = []  # Reset events for each retry
            async for event in _runner.run_async(user_id="user", session_id=session_id, new_message=user_content):
                events.append(event)
                # Track latest specialist-like author for attribution (skip manager/summary/user)
                try:
                    ev_author = getattr(event, "author", "") or ""
                    if ev_author and "agent" in ev_author.lower():
                        low = ev_author.lower()
                        if ("manager" not in low) and ("summary" not in low) and ("user" not in low):
                            last_specialist_author = ev_author
                except Exception:
                    pass
            break  # Success - exit retry loop
        except ClientError as e:
            last_error = e
            error_code = getattr(e, 'status_code', None) or getattr(e, 'code', None)
            error_status = getattr(e, 'status', '')
            
            # Check if it's a rate limit error (429)
            if error_code == 429 or 'RESOURCE_EXHAUSTED' in str(error_status) or '429' in str(e):
                retry_count += 1
                if retry_count > MAX_RETRIES:
                    logging.error("Rate limit exceeded after %d retries. Please try again later.", MAX_RETRIES)
                    raise RuntimeError(
                        "API rate limit exceeded. The service is temporarily unavailable due to high demand. "
                        "Please wait 60-120 seconds before retrying. If this persists, you may have reached your API quota limit. "
                        "Consider reducing the frequency of requests."
                    ) from e
                
                # Calculate exponential backoff delay
                delay = min(
                    INITIAL_RETRY_DELAY * (RETRY_BACKOFF_MULTIPLIER ** (retry_count - 1)),
                    MAX_RETRY_DELAY
                )
                logging.warning(
                    "Rate limit hit (429). Retrying in %d seconds (attempt %d/%d)...",
                    delay, retry_count, MAX_RETRIES
                )
                await asyncio.sleep(delay)
                continue
            else:
                # Not a rate limit error, re-raise
                logging.error("Non-rate-limit ClientError during agent execution: %s", str(e), exc_info=True)
                raise
        except Exception as e:
            last_error = e
            # For non-ClientError exceptions, check if they contain rate limit info
            error_str = str(e).lower()
            if '429' in error_str or 'resource_exhausted' in error_str or 'rate limit' in error_str:
                retry_count += 1
                if retry_count > MAX_RETRIES:
                    logging.error("Rate limit exceeded after %d retries.", MAX_RETRIES)
                    raise RuntimeError(
                        "API rate limit exceeded. The service is temporarily unavailable due to high demand. "
                        "Please wait 60-120 seconds before retrying. If this persists, you may have reached your API quota limit. "
                        "Consider reducing the frequency of requests."
                    ) from e
                
                delay = min(
                    INITIAL_RETRY_DELAY * (RETRY_BACKOFF_MULTIPLIER ** (retry_count - 1)),
                    MAX_RETRY_DELAY
                )
                logging.warning(
                    "Rate limit detected. Retrying in %d seconds (attempt %d/%d)...",
                    delay, retry_count, MAX_RETRIES
                )
                await asyncio.sleep(delay)
                continue
            else:
                # Other error, don't retry
                logging.error("Error during agent execution: %s", str(e), exc_info=True)
                raise
    
    # If we exhausted retries, raise the last error
    if last_error and not events:
        raise last_error

    # Enhanced response extraction with multiple strategies
    
    # Strategy 1: Look for build_report function_response in turnComplete events (PRIMARY METHOD)
    for event in reversed(events):
        if getattr(event, "turnComplete", False) and hasattr(event, "content"):
            for part in getattr(event.content, "parts", []):
                # Check for function_response from build_report
                if hasattr(part, "function_response"):
                    func_response = part.function_response
                    func_name = getattr(func_response, "name", "")
                    if func_name == "build_report":
                        response_data = getattr(func_response, "response", {})
                        if isinstance(response_data, dict):
                            content = response_data.get("report", "")
                            sources = response_data.get("sources", [])
                            generated_by = response_data.get("generated_by")
                            report_source_items = response_data.get("source_items")
                            if isinstance(sources, list):
                                report_sources = [str(s) for s in sources if s]
                            if content:
                                logging.info("Extracted content from build_report function_response")
                                break
            if content:
                break
    
    # Strategy 2: Look for build_report function_response in any event (not just turnComplete)
    if not content:
        for event in reversed(events):
            if hasattr(event, "content"):
                for part in getattr(event.content, "parts", []):
                    if hasattr(part, "function_response"):
                        func_response = part.function_response
                        func_name = getattr(func_response, "name", "")
                        if func_name == "build_report":
                            response_data = getattr(func_response, "response", {})
                            if isinstance(response_data, dict):
                                content = response_data.get("report", "")
                                sources = response_data.get("sources", [])
                                generated_by = response_data.get("generated_by")
                                report_source_items = response_data.get("source_items")
                                if isinstance(sources, list):
                                    report_sources = [str(s) for s in sources if s]
                                if content:
                                    logging.info("Extracted content from build_report (any event)")
                                    break
                if content:
                    break
    
    # Strategy 3: Look for any text content in turnComplete events from manager
    if not content:
        for event in reversed(events):
            if getattr(event, "turnComplete", False) and hasattr(event, "content"):
                author = getattr(event, "author", "")
                if "manager" in author.lower() or not author:
                    parts = getattr(event.content, "parts", [])
                    text_parts = []
                    for p in parts:
                        if hasattr(p, "text") and p.text and p.text.strip():
                            text_parts.append(p.text.strip())
                    if text_parts:
                        content = "\n".join(text_parts)
                        logging.info("Extracted content from manager agent text response")
                        break
    
    # Strategy 4: Look for any agent's text response (not just manager)
    if not content:
        for event in reversed(events):
            if hasattr(event, "content") and hasattr(event, "author"):
                author = getattr(event, "author", "")
                # Skip user messages
                if author and "user" not in author.lower():
                    parts = getattr(event.content, "parts", [])
                    text_parts = []
                    for p in parts:
                        if hasattr(p, "text") and p.text and p.text.strip():
                            # Skip very short or system messages
                            text = p.text.strip()
                            if len(text) > 30 and not text.startswith("[Mode:") and not text.startswith("[Safety"):
                                text_parts.append(text)
                    if text_parts:
                        # Prefer manager or specialist agent responses
                        full_text = "\n".join(text_parts)
                        content = full_text
                        logging.info(f"Extracted content from {author} agent")
                        if not generated_by:
                            generated_by = author
                        break
    
    # Strategy 5: Look for specialist agent DRAFT responses and extract them
    if not content:
        for event in reversed(events):
            if hasattr(event, "content"):
                parts = getattr(event.content, "parts", [])
                for p in parts:
                    if hasattr(p, "text") and p.text:
                        text = p.text.strip()
                        if text.startswith("DRAFT:"):
                            # Remove DRAFT prefix
                            content = text.replace("DRAFT:", "").strip()
                            if content:
                                logging.info("Extracted content from specialist DRAFT response")
                                break
                if content:
                    break
    
    # Strategy 6: Extract from any event with substantial text content (last resort)
    if not content:
        all_texts = []
        for event in events:
            if hasattr(event, "content"):
                parts = getattr(event.content, "parts", [])
                for p in parts:
                    if hasattr(p, "text") and p.text:
                        text = p.text.strip()
                        # Skip very short or system messages
                        if len(text) > 30 and not text.startswith("[Mode:") and not text.startswith("[Safety"):
                            author = getattr(event, "author", "")
                            if author and "user" not in author.lower():
                                all_texts.append(text)
        
        if all_texts:
            # Combine substantial text responses, prioritizing longer ones
            all_texts.sort(key=len, reverse=True)
            content = "\n\n".join(all_texts[:3])  # Take top 3 substantial responses
            logging.info(f"Extracted content from combined agent responses ({len(all_texts)} found)")

    # Log tool usage and agent activity for debugging
    tools_used = []
    agents_called = set()
    function_calls = []
    function_responses = []
    
    for ev in events:
        if hasattr(ev, "content"):
            for p in getattr(ev.content, "parts", []):
                if hasattr(p, "function_call") and hasattr(p.function_call, "name"):
                    func_name = p.function_call.name
                    tools_used.append(func_name)
                    function_calls.append(func_name)
                if hasattr(p, "function_response") and hasattr(p.function_response, "name"):
                    func_name = p.function_response.name
                    function_responses.append(func_name)
        author = getattr(ev, "author", "")
        if author:
            agents_called.add(author)
    
    if tools_used:
        logging.info("ADK session=%s tools_used=%s", session_id, ",".join(sorted(set(tools_used))))
    if agents_called:
        logging.info("ADK session=%s agents_called=%s", session_id, ",".join(sorted(agents_called)))
    if function_calls:
        logging.info("ADK session=%s function_calls=%s", session_id, ",".join(function_calls))
    if function_responses:
        logging.info("ADK session=%s function_responses=%s", session_id, ",".join(function_responses))
    
    # Final fallback if still no content
    if not content:
        logging.error("No content extracted after all strategies. Event count: %d", len(events))
        # Log detailed event information for debugging
        for i, ev in enumerate(events[-5:]):  # Log last 5 events
            ev_type = type(ev).__name__
            author = getattr(ev, "author", "unknown")
            turn_complete = getattr(ev, "turnComplete", False)
            logging.error("Event[%d]: type=%s, author=%s, turnComplete=%s", i, ev_type, author, turn_complete)
        
        # Check if build_report was called but not responded to
        if "build_report" in function_calls and "build_report" not in function_responses:
            logging.error("build_report was called but no response received!")
        
        content = (
            "I apologize, but I was unable to generate a response to your question. "
            "This may be due to a technical issue or incomplete information. "
            "Please try rephrasing your question or try again later."
        )

    # Final cleanup: remove accidental DRAFT: prefix if present and sanitize system leakage
    try:
        if content and isinstance(content, str):
            stripped = content.lstrip()
            if stripped.upper().startswith("DRAFT:"):
                content = stripped[6:].lstrip()
            # Replace undesirable INSUFFICIENT responses with a friendly guidance message
            elif stripped.upper().startswith("INSUFFICIENT"):
                content = (
                    "Hello! I'm your medical learning assistant. Ask me any medical topic, mechanism, disease, or drug, "
                    "and I'll generate a structured, student‑friendly explanation with sources.\n\n"
                    "Examples: \n"
                    "- Explain the mechanism of action of beta blockers.\n"
                    "- Everything about nephrotic syndrome (beginner).\n"
                    "- Compare type 1 vs type 2 hypersensitivity (neet).\n"
                    "- MCQ: Which vitamin deficiency causes megaloblastic anemia and why?\n"
                )
                report_sources = []
            # Remove leaked system/debug lines and apologies
            lines = [ln for ln in content.splitlines()]
            cleaned: List[str] = []
            for ln in lines:
                ln_stripped = ln.strip()
                low = ln_stripped.lower()
                if not ln_stripped:
                    cleaned.append(ln)
                    continue
                # Filter internal orchestration/debug artifacts
                if "transfer_to_agent(" in ln_stripped:
                    continue
                if ln_stripped in {"summary_agent_general", "summary_agent_neet", "orchestrator_agent"}:
                    continue
                if "orchestrator_agent" in low and "prepared by" not in low:
                    # avoid exposing internal agent name
                    continue
                # Filter apology/source unavailability boilerplate
                if "unable to provide sources" in low or "i apologize" in low:
                    continue
                cleaned.append(ln)
            content = "\n".join(cleaned).strip()
    except Exception:
        pass

    # Fallback attribution to last specialist if none set
    if not generated_by and last_specialist_author:
        generated_by = last_specialist_author

    return content, question, report_sources, generated_by, report_source_items


def run_agent(session_id: str, question: str, state_delta: Optional[Dict[str, Any]] = None) -> Tuple[str, str, List[str], Optional[str], Optional[List[Dict[str, Any]]]]:
    """Synchronous wrapper for the async agent runner.

    Returns: (content, resolved_question, source_labels, generated_by, source_items)
    """
    if _runner is None:
        raise RuntimeError("Agent system not initialized. Check logs for initialization errors.")
    
    try:
        # Try to get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Check if loop is running
        if loop.is_running():
            # If loop is already running, we need to use a different approach
            # This shouldn't happen in Flask, but handle it gracefully
            logging.warning("Event loop is already running, attempting nested execution")
            try:
                import nest_asyncio
                nest_asyncio.apply()
            except ImportError:
                logging.error("nest_asyncio not available. Creating a new event loop instead.")
                # Fall through to create a new loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        
        # Run with timeout
        try:
            return loop.run_until_complete(
                asyncio.wait_for(run_agent_async(session_id, question, state_delta), timeout=AGENT_TIMEOUT)
            )
        finally:
            # Give async cleanup tasks time to complete before closing loop
            if not loop.is_running():
                try:
                    # Run any pending callbacks
                    pending = asyncio.all_tasks(loop)
                    if pending:
                        # Wait briefly for cleanup tasks (non-blocking)
                        loop.run_until_complete(asyncio.sleep(0.1))
                except Exception:
                    pass  # Ignore cleanup errors
    except asyncio.TimeoutError:
        logging.error("Agent execution timed out after %s seconds", AGENT_TIMEOUT)
        raise RuntimeError(f"Agent execution timed out after {AGENT_TIMEOUT} seconds")
    except RuntimeError as e:
        error_str = str(e).lower()
        # Check for rate limit errors in RuntimeError
        if 'rate limit' in error_str or '429' in error_str or 'resource_exhausted' in error_str:
            raise  # Re-raise rate limit errors as-is
        if "cannot run loop while another loop is running" in str(e):
            # Last resort: try creating a new event loop
            new_loop = None
            try:
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(
                        asyncio.wait_for(run_agent_async(session_id, question, state_delta), timeout=AGENT_TIMEOUT)
                    )
                finally:
                    # Allow cleanup tasks to complete
                    try:
                        pending = asyncio.all_tasks(new_loop)
                        if pending:
                            new_loop.run_until_complete(asyncio.sleep(0.1))
                    except Exception:
                        pass
            finally:
                if new_loop and not new_loop.is_closed():
                    try:
                        new_loop.close()
                    except Exception:
                        pass  # Ignore cleanup errors
        raise
    except Exception as e:
        error_str = str(e).lower()
        # Check if it's a rate limit error
        if '429' in error_str or 'resource_exhausted' in error_str or 'rate limit' in error_str:
            logging.error("Rate limit error detected: %s", str(e))
            raise RuntimeError(
                "API rate limit exceeded. The service is temporarily unavailable. "
                "Please wait a moment and try again."
            ) from e
        logging.error("Error in run_agent: %s", str(e), exc_info=True)
        raise
