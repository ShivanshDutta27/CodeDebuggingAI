# agents/fix_suggester.py
"""Fix Suggester Agent for Fixie AI Debugger.

Synthesizes complete, idiomatic, syntactically correct code repairs across
any programming language, preserving original naming conventions and structure.
"""

from typing import Optional, Dict, Any
from core.gemini_interface import query_gemini
import json
import re


class FixSuggester:
    def __init__(self, model=None):
        self.model = model

    def suggest(
        self,
        code: str,
        bug_report: dict,
        logic: str,
        language: str = "auto",
        context_profile: Optional[Dict[str, Any]] = None,
    ) -> dict:
        display_lang = "source"
        if context_profile and "display_language" in context_profile:
            display_lang = context_profile["display_language"]
        elif language and language != "auto":
            display_lang = language.capitalize()

        if bug_report.get("severity") in ["none"]:
            return {
                "explanation": f"No critical issues detected in {display_lang} code.",
                "fix": code,
                "confidence": 0.9,
            }

        prompt = f"""You are a master {display_lang} software engineer and debugging assistant.
Analyze the bug report and intended logic, then provide a complete, idiomatic fix in {display_lang}.

Original {display_lang} Code:
```{language}
{code}
```

Bug Report:
{bug_report}

Intended Logic:
{logic}

Provide the COMPLETE corrected function or code block that fixes the issue, not just a single changed line.
Include necessary language headers / imports / type annotations where required.

Respond ONLY with valid JSON in this exact format:
{{
  "explanation": "Detailed explanation of why this fix resolves the issue in {display_lang}",
  "fix": "Complete corrected code as an escaped string",
  "confidence": 0.95
}}
"""
        response = query_gemini(prompt, model=self.model)
        return self._parse_response(response)

    def _parse_response(self, response: str) -> dict:
        """Parse LLM response with robust fallback handling."""
        response = response.strip()

        try:
            return json.loads(response)
        except Exception:
            pass

        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except Exception:
                pass

        # Fallback: manual extraction
        explanation = re.search(r'"explanation":\s*"([^"]*)"', response)
        fix = re.search(r'"fix":\s*"([\s\S]*?)"\s*,\s*"confidence"', response)
        if not fix:
            fix = re.search(r'"fix":\s*"([^"]*)"', response)
        confidence = re.search(r'"confidence":\s*([\d.]+)', response)

        return {
            "explanation": explanation.group(1) if explanation else (response[:200] if response else "Fix generated"),
            "fix": fix.group(1).replace('\\n', '\n').replace('\\"', '"') if fix else "// Unable to extract fix snippet",
            "confidence": float(confidence.group(1)) if confidence else 0.8,
        }