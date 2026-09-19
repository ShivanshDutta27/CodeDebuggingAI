# agents/test_harness.py
"""Test Harness & Environment Verification Agent for Fixie AI Debugger.

Constructs concrete, environment-specific testing strategies:
- For LeetCode / Algorithmic: Generates standard & edge test cases plus executable runner code.
- For MERN / Web Projects: Generates browser verification runbooks (server commands, URL, interactive UI reproduction steps, DevTools checks).
- For Compiled / CLI Apps: Generates build and terminal execution commands.
"""

import json
import re
from typing import Optional, Dict, Any
from core.gemini_interface import query_gemini


class TestHarness:
    def __init__(self, model: Optional[str] = None):
        self.model = model

    def generate(
        self,
        code: str,
        fix: Dict[str, Any],
        context_profile: Dict[str, Any],
        logic: str,
    ) -> Dict[str, Any]:
        env_type = context_profile.get("environment_type", "script")
        language = context_profile.get("language", "python")
        display_lang = context_profile.get("display_language", language)
        fixed_code = fix.get("fix", "")

        prompt = f"""You are a senior QA automation engineer and test environment architect.
Analyze this code, its fix, and the target environment to generate an optimal verification strategy.

Context Profile:
- Language: {display_lang} ({language})
- Environment Type: {env_type}
- Build System: {context_profile.get('build_system', 'Default')}

Original Code:
```
{code}
```

Suggested Fix:
```
{fixed_code}
```

Intended Logic: {logic}

TASK:
Based on the environment type, generate a detailed verification strategy.

IF environment_type is "leetcode" or algorithmic:
1. Provide 3-4 diverse test cases (include at least 1 normal case and 2 critical edge/boundary cases like empty, negatives, or single-element).
2. Provide a complete, runnable test runner script in {display_lang} that runs these test cases against the fixed code and outputs PASS/FAIL.

IF environment_type is "mern" or web project:
1. Provide the exact dev server start command (e.g. "npm run dev").
2. Provide target browser URL (e.g. "http://localhost:5173").
3. Provide step-by-step browser interaction instructions to verify the fix and ensure no console errors/infinite loops occur.
4. Provide expected UI visual state vs previous buggy state.

IF environment_type is "compiled_app" or "script":
1. Provide the exact terminal build command (e.g. g++ flags).
2. Provide execution commands with sample arguments or stdin.

Respond ONLY with a JSON object in this exact format:
{{
  "strategy_type": "algorithmic_testcases|browser_runbook|cli_verification",
  "summary": "Short explanation of the verification methodology",
  "test_cases": [
    {{
      "name": "Test Case 1",
      "category": "Normal Case | Edge Case | Boundary Case",
      "input": "...",
      "expected_output": "...",
      "explanation": "..."
    }}
  ],
  "runner_code": "Runnable test harness code in {display_lang} (if applicable, else empty string)",
  "browser_runbook": {{
    "dev_command": "...",
    "browser_url": "...",
    "steps": [
      "Step 1: ...",
      "Step 2: ...",
      "Step 3: ..."
    ],
    "expected_ui_behavior": "...",
    "console_checklist": "..."
  }},
  "cli_runbook": {{
    "build_command": "...",
    "run_command": "...",
    "expected_output": "..."
  }}
}}
"""
        response = query_gemini(prompt, model=self.model)
        return self._parse_response(response, env_type, display_lang)

    def _parse_response(
        self, response: str, env_type: str, display_lang: str
    ) -> Dict[str, Any]:
        response = response.strip()

        try:
            return json.loads(response)
        except Exception:
            pass

        match = re.search(r'\{[\s\S]*\}', response)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass

        # Fallback default
        if env_type == "leetcode":
            return {
                "strategy_type": "algorithmic_testcases",
                "summary": f"Standard test case validation for {display_lang} algorithm",
                "test_cases": [
                    {
                        "name": "Sample Input",
                        "category": "Normal Case",
                        "input": "Standard input",
                        "expected_output": "Expected return value",
                        "explanation": "Validates base logic",
                    }
                ],
                "runner_code": "",
            }
        elif env_type == "mern":
            return {
                "strategy_type": "browser_runbook",
                "summary": "Browser-based interactive UI verification",
                "browser_runbook": {
                    "dev_command": "npm run dev",
                    "browser_url": "http://localhost:5173",
                    "steps": [
                        "Start dev server: npm run dev",
                        "Navigate to target route in browser",
                        "Verify component renders and interactions trigger correctly",
                    ],
                    "expected_ui_behavior": "UI updates smoothly without unhandled rejections",
                    "console_checklist": "Check DevTools Console for zero warning/error loops",
                },
            }
        else:
            return {
                "strategy_type": "cli_verification",
                "summary": "Terminal execution check",
                "cli_runbook": {
                    "build_command": "Execute in standard environment",
                    "run_command": "Run with sample input",
                    "expected_output": "Clean exit with code 0",
                },
            }
