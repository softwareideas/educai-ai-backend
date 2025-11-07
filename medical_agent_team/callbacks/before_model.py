from typing import Any, Optional

try:
    from profanity_check import predict_prob  # type: ignore
except Exception:  # pragma: no cover
    predict_prob = None


def before_model_callback(callback_context: Any, llm_request: Any) -> Optional[Any]:
    """
    ADK before_model callback (safe, conservative):
    - Injects mode from session state into the last user message.
    - Applies a lightweight safety check; if unsafe, injects a brief refusal note to the user message
      (non-blocking; returns None so ADK proceeds).

    Note: This implementation avoids returning a custom LlmResponse to prevent tight coupling to ADK internals.
    Wiring: pass this function in your agent creation (if supported):
        LlmAgent(..., callbacks=[before_model_callback, ...])
    """
    try:
        state = getattr(callback_context, "state", {}) or {}
        mode = state.get("mode")

        contents = getattr(llm_request, "contents", None) or []
        if not contents:
            return None
        # Find last user content
        last_user = None
        for c in reversed(contents):
            role = getattr(c, "role", None)
            if role == "user":
                last_user = c
                break
        if last_user is None:
            return None
        parts = getattr(last_user, "parts", None)
        if parts is None:
            return None
        # Get last text or append a small preface with mode
        if mode:
            from google.genai import types  # lazy import to avoid hard dependency at import time
            parts.append(types.Part(text=f"[Mode: {mode}]"))

        # Lightweight safety (non-blocking)
        if predict_prob is not None:
            # Extract plain text from user parts
            text = " ".join([getattr(p, "text", "") for p in parts if hasattr(p, "text")])
            try:
                prob = float(predict_prob([text])[0])
            except Exception:
                prob = 0.0
            if prob >= 0.90:
                from google.genai import types
                parts.append(types.Part(text="[Safety Note] Your last message may contain offensive content. Please rephrase."))
        return None
    except Exception:
        # Be conservative: never block on error
        return None
