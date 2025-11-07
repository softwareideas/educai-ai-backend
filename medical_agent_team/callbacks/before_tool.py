from typing import Any, Optional


def before_tool_callback(tool_context: Any, tool_request: Any) -> Optional[Any]:
    """
    ADK before_tool callback (argument guardrails, non-blocking):
    - Validates basic tool arguments for common tools used in this app.
    - On invalid args, appends a gentle note to the tool request if possible; otherwise no-op.
    - Returns None to let ADK proceed (no hard blocking to avoid tight coupling).

    Expected tools and minimal checks:
    - web_search(question): question must be non-empty
    - build_report(content, trace, user_mode, section_title, generated_by): content must be non-empty
    """
    try:
        # Try to obtain tool name and args
        name = getattr(tool_context, "tool_name", None) or getattr(tool_request, "name", None)
        args = getattr(tool_request, "args", None)
        if isinstance(args, dict):
            # Normalize keys
            lower = {str(k): v for k, v in args.items()}
            if name == "web_search":
                q = (lower.get("question") or "").strip()
                if not q:
                    setattr(tool_request, "args", {**lower, "question": "[Clarify] Please specify a short medical query."})
            elif name == "build_report":
                content = (lower.get("content") or "").strip()
                if not content:
                    setattr(tool_request, "args", {**lower, "content": "[Pending content]"})
        return None
    except Exception:
        return None
