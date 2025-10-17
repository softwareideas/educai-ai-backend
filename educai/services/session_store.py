from typing import Dict, List, Optional, Tuple
import threading

# Simple in-memory session store. Keyed by session_id.
# Each session tracks the last mode used and a rolling history of exchanges.
# History format: List[Tuple[user_text, assistant_text]]

_sessions: Dict[str, Dict[str, object]] = {}
_lock = threading.Lock()

DEFAULT_MAX_TURNS = 6


def _ensure_session(session_id: str) -> Dict[str, object]:
    sess = _sessions.get(session_id)
    if sess is None:
        sess = {"mode": None, "history": []}  # type: ignore[assignment]
        _sessions[session_id] = sess
    return sess


def reset_if_mode_changed(session_id: str, mode: Optional[str]) -> None:
    if not session_id:
        return
    with _lock:
        sess = _ensure_session(session_id)
        if sess.get("mode") != mode:
            sess["mode"] = mode
            sess["history"] = []


def append_exchange(session_id: str, mode: Optional[str], user_text: str, assistant_text: str) -> None:
    if not session_id:
        return
    with _lock:
        sess = _ensure_session(session_id)
        # Reset on mode change
        if sess.get("mode") != mode:
            sess["mode"] = mode
            sess["history"] = []
        hist: List[Tuple[str, str]] = sess.get("history", [])  # type: ignore[assignment]
        hist.append((user_text, assistant_text))
        # Trim to last DEFAULT_MAX_TURNS
        if len(hist) > DEFAULT_MAX_TURNS:
            hist[:] = hist[-DEFAULT_MAX_TURNS:]
        sess["history"] = hist


def get_history(session_id: str, mode: Optional[str], max_turns: int = DEFAULT_MAX_TURNS) -> List[Dict[str, str]]:
    if not session_id:
        return []
    with _lock:
        sess = _sessions.get(session_id)
        if not sess:
            return []
        # If mode changed, treat as new (empty history)
        if sess.get("mode") != mode:
            return []
        hist: List[Tuple[str, str]] = sess.get("history", [])  # type: ignore[assignment]
        recent = hist[-max_turns:]
        # Convert to role-based messages for LLM consumption
        messages: List[Dict[str, str]] = []
        for u, a in recent:
            messages.append({"role": "user", "content": u})
            messages.append({"role": "assistant", "content": a})
        return messages


def clear_session(session_id: str) -> None:
    if not session_id:
        return
    with _lock:
        if session_id in _sessions:
            del _sessions[session_id]
