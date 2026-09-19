# core/llama_interface.py
"""Deprecated: Kept for backwards compatibility. Routes to query_gemini."""

from core.gemini_interface import query_gemini


def query_llama(prompt: str, model: str = "gemini-1.5-flash") -> str:
    """Legacy interface forwarding calls to query_gemini."""
    return query_gemini(prompt, model=model)