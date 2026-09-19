# agents/logic_reasoner.py
"""Logic Reasoner Agent for Fixie AI Debugger.

Extracts program intent, algorithmic logic, control flow, and edge case expectations
across any supported programming language.
"""

from typing import Optional, Dict, Any
from core.gemini_interface import query_gemini


class LogicReasoner:
    def __init__(self, model=None):
        self.model = model

    def reason(
        self,
        code: str,
        language: str = "auto",
        context_profile: Optional[Dict[str, Any]] = None,
    ) -> str:
        display_lang = "source"
        if context_profile and "display_language" in context_profile:
            display_lang = context_profile["display_language"]
        elif language and language != "auto":
            display_lang = language.capitalize()

        env_type = context_profile.get("environment_type", "general") if context_profile else "general"

        prompt = f"""You are an expert {display_lang} software architect and algorithm logic explainer.
Analyze the following {display_lang} code (Environment: {env_type}) and explain in clear, structured terms:
1. What the code is intended to achieve (business / algorithmic goal).
2. The core data flow and logic progression.
3. Edge cases and constraints it must satisfy.

```{language}
{code}
```

Format your response cleanly:
- Intended Logic: <summary>
- Expected Flow: <bullet points>
- Expected Constraints / Invariants: <key invariants>
"""
        return query_gemini(prompt, model=self.model)