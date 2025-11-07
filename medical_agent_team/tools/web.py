from typing import Dict, Any, List
import os
import requests

SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")

def web_search(question: str) -> Dict[str, Any]:
    """Perform web search using Serper API."""
    import logging
    
    if not question or not isinstance(question, str) or not question.strip():
        return {"status": "error", "error_message": "Question is required and must be non-empty"}
    
    try:
        if not SERPER_API_KEY:
            logging.info("SERPER_API_KEY not set, skipping web search")
            return {"status": "success", "used": False, "content": "", "sources": [], "confidence": 0.0}
        
        resp = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
            json={"q": question.strip()},
            timeout=10  # 10 second timeout
        )
        resp.raise_for_status()
        data = resp.json()
        organic: List[Dict[str, Any]] = data.get("organic", [])
        
        if not organic:
            return {
                "status": "success",
                "used": True,
                "content": "No results found.",
                "sources": [],
                "confidence": 0.0,
            }
        
        content = "\n".join([f"- {item.get('title', 'No title')}: {item.get('link', '')}" for item in organic[:5]])
        sources = [
            {
                "type": "WebSearch",
                "title": it.get("title", ""),
                "link": it.get("link", ""),
                "url": it.get("link", ""),
                "source": it.get("source", ""),
                # simple ranking score: higher for earlier results
                "score": max(0, 100 - idx * 10),
            }
            for idx, it in enumerate(organic[:5])
        ]
        
        return {
            "status": "success",
            "used": True,
            "content": content,
            "sources": sources,
            "confidence": 0.7 if organic else 0.0,
        }
    except requests.exceptions.Timeout:
        logging.warning("Web search request timed out")
        return {"status": "error", "error_message": "Web search request timed out"}
    except requests.exceptions.RequestException as e:
        logging.error(f"Web search request failed: {e}")
        return {"status": "error", "error_message": f"Web search failed: {str(e)}"}
    except Exception as e:
        logging.error(f"Unexpected error in web_search: {e}", exc_info=True)
        return {"status": "error", "error_message": str(e)}
