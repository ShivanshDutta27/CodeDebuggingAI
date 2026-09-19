# agents/syntax_checker.py

from core.gemini_interface import query_gemini
import json
import re
from typing import Optional, Dict, Any


class SyntaxChecker:
    def __init__(self, model=None):
        self.model = model

    def check(
        self,
        code: str,
        language: str = "auto",
        context_profile: Optional[Dict[str, Any]] = None,
    ) -> dict:
        display_lang = "source"
        if context_profile and "display_language" in context_profile:
            display_lang = context_profile["display_language"]
        elif language and language != "auto":
            display_lang = language.capitalize()

        prompt = f"""You are an expert compiler, linter, and runtime error diagnostician for {display_lang}.
Analyze this {display_lang} code for compilation errors, syntax violations, memory management bugs (e.g. out-of-bounds access, dangling pointers, null dereferences), runtime crashes, or framework/API misuses:

```{language}
{code}
```

Respond with a valid JSON object in the following format.
Do not include markdown or explanations outside the JSON object.

{{"bug_explanation": "Clear explanation of the error, invalid syntax, or crash condition in {display_lang}", "line_number": "...", "severity": "high|medium|low"}}

If no issues are found, respond with:
{{"bug_explanation": "No syntax, compilation, or obvious runtime errors detected in {display_lang}", "line_number": "N/A", "severity": "none"}}
"""
        response = query_gemini(prompt, model=self.model)
        return self._parse_response(response, display_lang)

    def _parse_response(self, response: str, display_lang: str) -> dict:
        response = response.strip()

        # Try strict JSON first
        try:
            return json.loads(response)
        except Exception:
            pass

        # Try extracting JSON block
        match = re.search(r'\{[\s\S]*?\}', response)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass

        # Final fallback
        return {
            "bug_explanation": response[:300] if response else f"Analyzed {display_lang} code",
            "line_number": "Unknown",
            "severity": "medium",
        }
