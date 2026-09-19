# agents/context_profiler.py
"""Context & Environment Profiler Agent for Fixie AI Debugger.

Identifies:
1. The programming language (C++, Python, JavaScript/TypeScript, Java, Go, Rust, etc.)
2. The project/environment type (LeetCode algorithmic problem, MERN/React web project,
   CLI compiled binary, backend service, or standalone script)
3. The build & test strategy (test cases vs browser verification vs compiler flags).
"""

import json
import re
from typing import Optional, Dict, Any
from core.gemini_interface import query_gemini


class ContextProfiler:
    def __init__(self, model: Optional[str] = None):
        self.model = model

    def profile(self, code: str, hint_language: Optional[str] = "auto") -> Dict[str, Any]:
        prompt = f"""You are a senior software architect and build environment detector.
Analyze this code snippet and determine:
1. Programming language and framework (e.g. C++, Python, JavaScript, TypeScript, React / MERN, Java, Go, Rust, C#, PHP).
2. Environment / Project Type:
   - "leetcode": Algorithmic problem, Solution class, data structures, competitive programming.
   - "mern": React / Vue frontend, Node.js / Express backend, MongoDB / full-stack web component.
   - "compiled_app": C++, Rust, Go, or Java systems / CLI application requiring compiler flags.
   - "backend_api": REST / GraphQL / FastAPI / Express server endpoint.
   - "script": Standalone automation / data processing script.
3. Build system or compiler command (e.g. "g++ -std=c++20", "npm run dev / Vite", "python 3", "cargo run").
4. Test / Verification Strategy:
   - "algorithmic_testcases": If leetcode or algorithmic, test with custom input/output test cases.
   - "browser_verification": If MERN or frontend web component, test on browser with dev server.
   - "cli_execution": If CLI or script, test with terminal command and stdin/args.
   - "unit_test": If unit testing suite or class.

Code:
```
{code}
```
User Language Hint: {hint_language if hint_language else 'auto'}

Respond ONLY with a valid JSON object in this exact structure:
{{
  "language": "cpp|python|javascript|typescript|java|go|rust|csharp|other",
  "display_language": "C++|Python|React (MERN)|TypeScript|Java|Go|Rust",
  "environment_type": "leetcode|mern|compiled_app|backend_api|script",
  "build_system": "Short build / run command or environment descriptor",
  "test_strategy": "algorithmic_testcases|browser_verification|cli_execution|unit_test",
  "summary": "1-2 sentence description of what kind of codebase and problem this is"
}}
"""
        response = query_gemini(prompt, model=self.model)
        return self._parse_response(response, hint_language)

    def _parse_response(self, response: str, hint_language: Optional[str]) -> Dict[str, Any]:
        response = response.strip()

        # Try direct JSON parse
        try:
            return json.loads(response)
        except Exception:
            pass

        # Try regex search for JSON block
        match = re.search(r'\{[\s\S]*?\}', response)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass

        # Fallback defaults based on hint or heuristic
        lang = hint_language if hint_language and hint_language != "auto" else "python"
        return {
            "language": lang,
            "display_language": lang.capitalize(),
            "environment_type": "script",
            "build_system": "Standard runtime",
            "test_strategy": "cli_execution",
            "summary": "General code execution context",
        }
