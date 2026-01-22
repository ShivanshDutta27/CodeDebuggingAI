# agents/syntax_checker.py

from core.llama_interface import query_llama
import json
import re

class SyntaxChecker:
    def __init__(self, model='gemma3:4b'):
        self.model = model
    
    def check(self, code: str) -> dict:
        prompt = f"""Analyze this Python code for syntax and runtime errors:

{code}

Respond with a JSON object in the following format.
Do not include markdown. Do not include explanations outside JSON.

{{"bug_explanation": "...", "line_number": "...", "severity": "high|medium|low"}}

If no issues found, respond with:
{{"bug_explanation": "No syntax or obvious runtime errors detected", "line_number": "N/A", "severity": "none"}}
"""
        
        response = query_llama(prompt, model=self.model)
        return self._parse_response(response)
    
    def _parse_response(self, response: str) -> dict:
        response = response.strip()

        # Try strict JSON first
        try:
            return json.loads(response)
        except:
            pass

        # Try extracting JSON block
        match = re.search(r'\{[\s\S]*?\}', response)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass

        # Final fallback
        return {
            "bug_explanation": response[:300],  # keep model insight
            "line_number": "Unknown",
            "severity": "unknown"
        }
