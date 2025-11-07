from typing import Dict, Any, List, Optional
import json
import logging


def build_report(
    content: str, 
    user_mode: str, 
    section_title: str, 
    generated_by: str, 
    trace_json: str
) -> Dict[str, Any]:
    """Deterministic report formatter tool.

    Args:
        content: Main body text produced by medical reasoning.
        user_mode: One of general|neet|exam|beginner|advanced.
        section_title: Title for the main section.
        generated_by: Agent label to attribute.
        trace_json: JSON string of a list with a single item containing key 'sources' (optional fields inside).
    """
    # Validate inputs
    if not content or not isinstance(content, str):
        content = "No content provided."
    
    if not section_title or not isinstance(section_title, str):
        section_title = "Report"
    
    if not user_mode or not isinstance(user_mode, str):
        user_mode = "general"
    
    header = {
        "general": "Report (General)",
        "neet": "Report (NEET)",
        "exam": "Report (Exam)",
        "beginner": "Report (Beginner)",
        "advanced": "Report (Advanced)",
    }.get(user_mode.lower(), "Report")

    report_lines: List[str] = [
        f"# {header}",
        "",
        f"## {section_title}",
        "",
        content.strip() if content else "",
        "",
    ]

    sources = []
    try:
        if trace_json and isinstance(trace_json, str) and trace_json.strip():
            parsed = json.loads(trace_json)
            if isinstance(parsed, list) and parsed:
                sources = parsed[0].get("sources") or []
            elif isinstance(parsed, dict):
                sources = parsed.get("sources", [])
    except json.JSONDecodeError as e:
        logging.warning(f"Failed to parse trace_json: {e}")
        sources = []
    except Exception as e:
        logging.warning(f"Error processing trace_json: {e}")
        sources = []
    # Build a concise sources label list with URLs (up to 5, deduped, no scores)
    labels: List[str] = []
    source_dicts: List[Dict[str, Any]] = []
    if sources and isinstance(sources, list):
        # Deduplicate by URL while keeping highest score if present
        dedup: Dict[str, Dict[str, Any]] = {}
        for s in sources:
            if not isinstance(s, dict):
                continue
                
            st = (s or {}).get("type") or "WebSearch"
            if st == "WebSearch":
                url = (s.get("url") or s.get("link") or "").strip()
                title = (s.get("title") or url or "").strip()
                # Use URL as key for deduplication
                key = url if url else title
                if not key:
                    continue
            else:
                # Handle other source types if needed
                topic = (s.get("topic") or "").strip()
                source_file = (s.get("source_file") or "").strip()
                title = (s.get("title") or "").strip()
                key = title or topic or source_file
                if not key:
                    continue
                url = ""
            
            prev = dedup.get(key)
            if prev is None:
                dedup[key] = s
            else:
                try:
                    current_score = float(s.get("score", 0.0))
                    prev_score = float(prev.get("score", 0.0))
                    if current_score > prev_score:
                        dedup[key] = s
                except (ValueError, TypeError):
                    # If scores can't be compared, keep the first one
                    pass
        
        # Sort by score desc if present, else keep insertion order, then cap at 5
        items = list(dedup.items())
        try:
            items.sort(key=lambda kv: float((kv[1] or {}).get("score", 0.0)), reverse=True)
        except (ValueError, TypeError):
            # Keep insertion order if sorting fails
            pass
        
        # Keep selected source dicts (max 5) for numbered rendering later
        for key, source_dict in items:
            # Filter out low-quality entries (no URL and generic titles)
            stype = (source_dict or {}).get("type") or "WebSearch"
            title = (source_dict or {}).get("title", "").strip()
            url = (source_dict or {}).get("url") or (source_dict or {}).get("link") or ""
            url = url.strip()
            if stype == "WebSearch":
                if not url:
                    continue  # require a concrete URL
                if not title or title.lower() in {"general knowledge", "untitled", "no title"}:
                    # Replace with URL if title is generic
                    title = url
                    source_dict["title"] = title
            # Append after filtering
            source_dicts.append(source_dict)
            if len(source_dicts) >= 5:
                break
    
    # Add Sources section to report text if sources are available
    if source_dicts:
        report_lines.append("")
        report_lines.append("## Sources")
        report_lines.append("")
        # Render as numbered references [1], [2], ... to match inline citations
        for idx, sd in enumerate(source_dicts, start=1):
            source_type = (sd or {}).get("type") or "WebSearch"
            if source_type == "WebSearch":
                url = (sd.get("url") or sd.get("link") or "").strip()
                title = (sd.get("title") or url or "").strip()
                label = f"[{idx}] {title} - {url}" if url and title else f"[{idx}] {title or url}"
            else:
                title = (sd or {}).get("title") or "Source"
                label = f"[{idx}] {title}"
            labels.append(label)
            report_lines.append(label)
    
    # Filter out None values from lines
    report_lines = [ln for ln in report_lines if ln is not None]
    report_text = "\n".join(report_lines)
    
    return {
        "status": "success",
        "report": report_text,
        "sources": labels,  # numbered labels matching inline [n]
        "generated_by": (generated_by or "").strip(),
        "section_title": (section_title or "").strip(),
        "source_items": source_dicts,
    }
