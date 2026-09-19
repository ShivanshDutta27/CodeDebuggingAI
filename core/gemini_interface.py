# core/gemini_interface.py
"""Google Gemini API Interface for Fixie AI Code Debugger.

Provides an LLM query interface powered by the Gemini API,
replacing local Ollama subprocess calls.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


def get_api_key() -> str:
    """Retrieve Gemini API key from environment."""
    return os.getenv("GEMINI_API_KEY", "").strip()


def is_gemini_configured() -> bool:
    """Check whether a Gemini API key is configured."""
    key = get_api_key()
    return bool(key and key != "your_gemini_api_key_here")


def query_gemini(prompt: str, model: Optional[str] = None) -> str:
    """Send a prompt to the Google Gemini API and return the response text.

    Uses the google-genai SDK when available, with an automatic REST
    fallback via httpx.
    """
    api_key = get_api_key()
    if not is_gemini_configured():
        return (
            "Error: GEMINI_API_KEY is not configured. "
            "Please add your API key to the .env file (GEMINI_API_KEY=your_key) and restart."
        )

    target_model = model or os.getenv("GEMINI_MODEL", DEFAULT_MODEL)

    # Strategy 1: Try official google-genai SDK
    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=target_model,
            contents=prompt,
        )
        if response and response.text:
            return response.text
        return "Error: Gemini returned an empty response."
    except ImportError:
        logger.info("google-genai SDK not found; using REST fallback.")
    except Exception as e:
        logger.warning(f"google-genai SDK error: {e}. Attempting REST fallback.")

    # Strategy 2: Direct REST fallback via httpx (already installed)
    try:
        import httpx

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent"
        params = {"key": api_key}
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }

        with httpx.Client(timeout=30.0) as client:
            res = client.post(url, params=params, headers=headers, json=payload)
            if res.status_code != 200:
                error_detail = res.text
                try:
                    err_json = res.json()
                    error_detail = err_json.get("error", {}).get("message", res.text)
                except Exception:
                    pass
                return f"Gemini API error ({res.status_code}): {error_detail}"

            data = res.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts and "text" in parts[0]:
                    return parts[0]["text"]
            return "Error: Could not extract response text from Gemini API response."
    except Exception as e:
        return f"Error querying Gemini API: {str(e)}"
