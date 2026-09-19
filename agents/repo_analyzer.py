# agents/repo_analyzer.py
"""Repository Scout & Architecture Analyzer Agent for Fixie AI Debugger.

Audits an entire multi-file repository:
- Maps project topology, tech stack, and build scripts.
- Traces cross-file dependencies and API contracts.
- Scouts for bugs, leaks, broken imports, and contract mismatches across all files.
- Pinpoints primary suspect file(s) and provides cross-file context for downstream agents.
"""

import json
import re
from typing import Dict, Any, Optional
from core.gemini_interface import query_gemini


class RepoAnalyzer:
    def __init__(self, model: Optional[str] = None):
        self.model = model

    def analyze(self, repo_manifest: Dict[str, Any], focus_file: Optional[str] = None) -> Dict[str, Any]:
        file_tree = repo_manifest.get("file_tree", [])
        manifests = repo_manifest.get("manifest_files", {})
        source_files = repo_manifest.get("source_files", {})
        repo_name = repo_manifest.get("repo_name", "Repository")

        # Format file list
        files_summary = "\n".join(
            f"- {f.get('path')} ({f.get('size', 0)} bytes)" for f in file_tree[:40]
        )

        # Format key configs
        manifest_text = ""
        for path, content in list(manifests.items())[:5]:
            manifest_text += f"\n--- File: {path} ---\n{content[:2000]}\n"

        # Format source files with truncation per file
        source_text = ""
        for path, content in list(source_files.items())[:15]:
            source_text += f"\n--- File: {path} ---\n{content[:2500]}\n"

        prompt = f"""You are a Principal Software Architect and Full-Repository Code Auditor.
Analyze this entire multi-file project repository ({repo_name}):

FILE TREE:
{files_summary}

BUILD / MANIFEST CONFIGS:
{manifest_text if manifest_text else "No manifest files found."}

SOURCE CODE FILES:
{source_text}

{f"USER FOCUS FILE: {focus_file}" if focus_file else ""}

TASK:
1. Map the Architecture & Tech Stack (e.g. MERN, C++ CMake, Python FastAPI, Next.js).
2. Trace the Inter-File Dependency Graph (which files import/call which modules/APIs).
3. Identify Build, Dev, and Test Commands from the configs (e.g. "npm run dev", "cmake --build .", "npm test").
4. Scout for Bugs, Broken Contracts, Memory Leaks, Infinite Loops, or Logic Errors across the repository.
5. Identify the Primary Target File that contains the bug that must be repaired first.
6. Formulate Cross-File Context: what external imports, API payloads, or types must the downstream Fix Architect agent respect?

Respond ONLY with a valid JSON object in this exact structure:
{{
  "repo_name": "{repo_name}",
  "stack_summary": "Short description of the framework & stack",
  "architecture_type": "mern|cpp_cmake|python_fastapi|general",
  "dependency_graph": [
    {{"from": "...", "to": "...", "relationship": "..."}}
  ],
  "build_and_test_commands": {{
    "install": "...",
    "dev": "...",
    "test": "..."
  }},
  "detected_issues": [
    {{
      "file_path": "...",
      "severity": "high|medium|low",
      "title": "...",
      "description": "Detailed explanation of the bug and how it affects other files",
      "affected_files": ["..."]
    }}
  ],
  "primary_target_file": "relative/path/to/buggy_file",
  "primary_target_code": "Full content of the primary buggy file",
  "cross_file_context": "Explanation of cross-file imports/contracts the fix must conform to"
}}
"""
        response = query_gemini(prompt, model=self.model)
        return self._parse_response(response, repo_manifest, focus_file)

    def _parse_response(
        self,
        response: str,
        repo_manifest: Dict[str, Any],
        focus_file: Optional[str] = None,
    ) -> Dict[str, Any]:
        response = response.strip()

        parsed = None
        try:
            parsed = json.loads(response)
        except Exception:
            pass

        if not parsed:
            match = re.search(r'\{[\s\S]*\}', response)
            if match:
                try:
                    parsed = json.loads(match.group())
                except Exception:
                    pass

        source_files = repo_manifest.get("source_files", {})
        default_file = focus_file or (list(source_files.keys())[0] if source_files else "main.py")
        default_code = source_files.get(default_file, "")

        if not parsed:
            return {
                "repo_name": repo_manifest.get("repo_name", "Repository"),
                "stack_summary": "Multi-file Project Codebase",
                "architecture_type": "general",
                "dependency_graph": [],
                "build_and_test_commands": {
                    "install": "npm install / pip install",
                    "dev": "npm run dev / python main.py",
                    "test": "npm test",
                },
                "detected_issues": [
                    {
                        "file_path": default_file,
                        "severity": "medium",
                        "title": "Suspected Module Issue",
                        "description": "Cross-file review suggested checking imports and interfaces.",
                        "affected_files": [default_file],
                    }
                ],
                "primary_target_file": default_file,
                "primary_target_code": default_code,
                "cross_file_context": "Standard multi-file context",
            }

        # Ensure primary_target_code is filled
        target_file = parsed.get("primary_target_file") or default_file
        if not parsed.get("primary_target_code"):
            parsed["primary_target_code"] = source_files.get(target_file, default_code)

        return parsed
