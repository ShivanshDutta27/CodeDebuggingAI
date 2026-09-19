# core/langgraph_runner.py
"""LangGraph Workflow Runner for Fixie AI Polyglot & Full-Repository Multi-Agent Debugger.

Coordinates 6 specialized agents:
1. RepoAnalyzer: Scans full repositories, maps architecture & dependencies, and pinpoints buggy files.
2. ContextProfiler: Detects language, project type (LeetCode vs MERN vs CLI), and build system.
3. SyntaxChecker: Language-specific compiler, AST, and cross-file contract auditor.
4. LogicReasoner: Intent and algorithmic/architectural data flow analyzer.
5. FixSuggester: Synthesizes complete, idiomatic fixes in the target language with cross-file awareness.
6. TestHarness: Generates runnable LeetCode test cases or MERN/repository browser verification runbooks.
"""

from typing import Dict, List, TypedDict, Optional, Any
from langgraph.graph import StateGraph

from core.repo_scanner import scan_repository
from agents.repo_analyzer import RepoAnalyzer
from agents.context_profiler import ContextProfiler
from agents.syntax_checker import SyntaxChecker
from agents.logic_reasoner import LogicReasoner
from agents.fix_suggester import FixSuggester
from agents.test_harness import TestHarness


class FixieState(TypedDict, total=False):
    mode: str  # "snippet" | "repo"
    repo_path: Optional[str]
    repo_manifest: Optional[Dict[str, Any]]
    repo_analysis: Optional[Dict[str, Any]]
    focus_file: Optional[str]
    code: str
    language: Optional[str]
    context_profile: Optional[Dict[str, Any]]
    syntax_report: Optional[Dict[str, Any]]
    logic: Optional[str]
    fix: Optional[Dict[str, Any]]
    test_suite: Optional[Dict[str, Any]]
    error: Optional[str]
    context: Optional[List[str]]
    confidence_scores: Optional[Dict[str, float]]


repo_scout = RepoAnalyzer()
profiler = ContextProfiler()
checker = SyntaxChecker()
reasoner = LogicReasoner()
fixer = FixSuggester()
tester = TestHarness()


def repo_node(state: FixieState) -> FixieState:
    """Analyze entire repository if running in repository mode."""
    if state.get("mode") == "repo":
        repo_manifest = state.get("repo_manifest")
        repo_path = state.get("repo_path")

        if not repo_manifest and repo_path:
            try:
                repo_manifest = scan_repository(repo_path)
            except Exception as e:
                return {**state, "error": f"Failed to scan repository: {str(e)}"}

        if repo_manifest:
            analysis = repo_scout.analyze(repo_manifest, focus_file=state.get("focus_file"))
            target_code = analysis.get("primary_target_code") or state.get("code", "")
            return {
                **state,
                "repo_manifest": repo_manifest,
                "repo_analysis": analysis,
                "code": target_code,
            }

    return state


def context_node(state: FixieState) -> FixieState:
    hint_lang = state.get("language") or "auto"
    profile = profiler.profile(state.get("code", ""), hint_language=hint_lang)
    detected_lang = profile.get("language") or hint_lang

    # Merge repo context if available
    if state.get("repo_analysis"):
        repo_info = state["repo_analysis"]
        if repo_info.get("stack_summary"):
            profile["repo_stack"] = repo_info["stack_summary"]
        if repo_info.get("architecture_type") and profile.get("environment_type") == "script":
            profile["environment_type"] = repo_info["architecture_type"]

    return {
        **state,
        "context_profile": profile,
        "language": detected_lang,
    }


def syntax_node(state: FixieState) -> FixieState:
    ctx = state.get("context_profile") or {}
    if state.get("repo_analysis"):
        ctx["cross_file_context"] = state["repo_analysis"].get("cross_file_context", "")

    report = checker.check(
        code=state.get("code", ""),
        language=state.get("language", "auto"),
        context_profile=ctx,
    )
    return {**state, "syntax_report": report}


def logic_node(state: FixieState) -> FixieState:
    logic = reasoner.reason(
        code=state.get("code", ""),
        language=state.get("language", "auto"),
        context_profile=state.get("context_profile"),
    )
    return {**state, "logic": logic}


def fix_node(state: FixieState) -> FixieState:
    ctx = state.get("context_profile") or {}
    if state.get("repo_analysis"):
        ctx["cross_file_context"] = state["repo_analysis"].get("cross_file_context", "")

    fix = fixer.suggest(
        code=state.get("code", ""),
        bug_report=state.get("syntax_report", {}),
        logic=state.get("logic", ""),
        language=state.get("language", "auto"),
        context_profile=ctx,
    )
    return {**state, "fix": fix}


def test_node(state: FixieState) -> FixieState:
    ctx = state.get("context_profile") or {}
    if state.get("repo_analysis"):
        repo_cmds = state["repo_analysis"].get("build_and_test_commands", {})
        if repo_cmds.get("dev"):
            ctx["build_system"] = repo_cmds["dev"]

    test_suite = tester.generate(
        code=state.get("code", ""),
        fix=state.get("fix", {}),
        context_profile=ctx,
        logic=state.get("logic", ""),
    )

    # If repo commands exist, ensure they're populated
    if state.get("repo_analysis") and "browser_runbook" in test_suite:
        repo_cmds = state["repo_analysis"].get("build_and_test_commands", {})
        if repo_cmds.get("dev"):
            test_suite["browser_runbook"]["dev_command"] = repo_cmds["dev"]

    return {**state, "test_suite": test_suite}


def build_fixie_graph():
    builder = StateGraph(FixieState)

    # Register 6 agent nodes
    builder.add_node("RepoAnalyzer", repo_node)
    builder.add_node("ContextProfiler", context_node)
    builder.add_node("SyntaxChecker", syntax_node)
    builder.add_node("LogicReasoner", logic_node)
    builder.add_node("FixSuggester", fix_node)
    builder.add_node("TestHarness", test_node)

    # Flow
    builder.set_entry_point("RepoAnalyzer")
    builder.add_edge("RepoAnalyzer", "ContextProfiler")
    builder.add_edge("ContextProfiler", "SyntaxChecker")
    builder.add_edge("SyntaxChecker", "LogicReasoner")
    builder.add_edge("LogicReasoner", "FixSuggester")
    builder.add_edge("FixSuggester", "TestHarness")
    builder.add_edge("TestHarness", "__end__")

    return builder.compile()


def run_fixie_graph(
    code: str = "",
    language: str = "auto",
    mode: str = "snippet",
    repo_path: Optional[str] = None,
    repo_manifest: Optional[Dict[str, Any]] = None,
    focus_file: Optional[str] = None,
) -> Dict[str, Any]:
    graph = build_fixie_graph()
    payload = {
        "mode": mode,
        "code": code,
        "language": language,
        "repo_path": repo_path,
        "repo_manifest": repo_manifest,
        "focus_file": focus_file,
    }
    result = graph.invoke(payload)
    return result


def stream_fixie_graph(
    code: str = "",
    language: str = "auto",
    mode: str = "snippet",
    repo_path: Optional[str] = None,
    repo_manifest: Optional[Dict[str, Any]] = None,
    focus_file: Optional[str] = None,
):
    """Yield intermediate node updates as each agent completes execution."""
    graph = build_fixie_graph()
    payload = {
        "mode": mode,
        "code": code,
        "language": language,
        "repo_path": repo_path,
        "repo_manifest": repo_manifest,
        "focus_file": focus_file,
    }
    for chunk in graph.stream(payload):
        yield chunk