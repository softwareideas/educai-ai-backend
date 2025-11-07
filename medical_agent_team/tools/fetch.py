from typing import Dict, Any, Optional
import requests


def fetch_url_content(url: str, max_chars: int = 4000) -> Dict[str, Any]:
    """Fetch a web page and extract readable text content.

    Returns a dict with keys: status, url, title, content, error_message.
    Uses trafilatura if available; falls back to raw text if not.
    """
    import logging

    if not url or not isinstance(url, str):
        return {"status": "error", "error_message": "URL is required"}

    try:
        resp = requests.get(url, timeout=12, headers={
            "User-Agent": "educai-agent/1.0 (+https://github.com/)"
        })
        resp.raise_for_status()

        html = resp.text or ""
        title: Optional[str] = None
        text: Optional[str] = None

        try:
            # Prefer trafilatura for readability extraction
            import trafilatura
            downloaded = trafilatura.extract(html, include_comments=False, include_links=False)
            if downloaded:
                text = downloaded.strip()
        except Exception as e:  # noqa: BLE001 - best-effort extraction
            logging.debug("Trafilatura extract failed: %s", e)

        # Fallback to naive text if extractor failed
        if not text:
            text = html

        # Try to extract a title tag if present
        try:
            start = html.lower().find("<title>")
            end = html.lower().find("</title>")
            if start != -1 and end != -1 and end > start:
                title = html[start + 7:end].strip()
        except Exception:
            title = None

        if not title:
            title = url

        # Trim content
        if isinstance(max_chars, int) and max_chars > 0 and len(text) > max_chars:
            text = text[:max_chars].rstrip() + "\n…"

        return {
            "status": "success",
            "url": url,
            "title": title,
            "content": text,
        }
    except requests.exceptions.Timeout:
        return {"status": "error", "error_message": "Fetch timed out"}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "error_message": f"Fetch failed: {e}"}
    except Exception as e:  # noqa: BLE001
        logging.exception("Unexpected error in fetch_url_content")
        return {"status": "error", "error_message": str(e)}


