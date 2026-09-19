"""Fixie AI Project Documentation Generator.

Generates a comprehensive, publication-quality HTML document and converts it
into a vector PDF using headless Microsoft Edge or Google Chrome.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def find_browser_executable() -> str:
    """Find Microsoft Edge or Google Chrome executable on Windows."""
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        shutil.which("msedge"),
        shutil.which("chrome"),
    ]
    for c in candidates:
        if c and os.path.isfile(c):
            return c
    return ""


HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Fixie AI Agent Debugger Studio - Complete System Architecture & Component Guide</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

  @page {
    size: A4 portrait;
    margin: 18mm 16mm 18mm 16mm;
    @bottom-right {
      content: counter(page);
      font-family: 'Inter', sans-serif;
      font-size: 8pt;
      color: #71717a;
    }
    @bottom-left {
      content: "Fixie AI Agent Debugger Studio - Architecture & Component Guide";
      font-family: 'Inter', sans-serif;
      font-size: 8pt;
      color: #71717a;
    }
  }

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background-color: #ffffff;
    color: #18181b;
    line-height: 1.55;
    font-size: 9.5pt;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }

  /* Cover Page */
  .cover-page {
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 40px 20px;
    page-break-after: always;
    border-left: 6px solid #8b5cf6;
    background: linear-gradient(135deg, #09090b 0%, #18181b 100%);
    color: #f4f4f5;
    border-radius: 4px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
  }

  .cover-header {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .cover-badge {
    display: inline-block;
    padding: 6px 14px;
    background: rgba(139, 92, 246, 0.25);
    border: 1px solid #8b5cf6;
    color: #c4b5fd;
    font-size: 9pt;
    font-weight: 600;
    border-radius: 9999px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }

  .cover-title {
    font-size: 32pt;
    font-weight: 800;
    line-height: 1.15;
    margin-top: 24px;
    background: linear-gradient(135deg, #ffffff 30%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .cover-subtitle {
    font-size: 13pt;
    color: #a1a1aa;
    margin-top: 14px;
    max-width: 90%;
    font-weight: 400;
    line-height: 1.5;
  }

  .cover-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 30px;
  }

  .tag-pill {
    padding: 5px 12px;
    border-radius: 6px;
    font-size: 8.5pt;
    font-weight: 500;
    background: #27272a;
    color: #e4e4e7;
    border: 1px solid #3f3f46;
  }

  .cover-footer {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    border-top: 1px solid #27272a;
    padding-top: 20px;
    color: #71717a;
    font-size: 8.5pt;
  }

  .page-break {
    page-break-after: always;
  }

  /* Section Styling */
  h1 {
    font-size: 18pt;
    font-weight: 700;
    color: #09090b;
    margin-top: 28px;
    margin-bottom: 12px;
    padding-bottom: 6px;
    border-bottom: 2px solid #e4e4e7;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  h1 .sec-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    background: #8b5cf6;
    color: #ffffff;
    border-radius: 6px;
    font-size: 10pt;
    font-weight: 700;
  }

  h2 {
    font-size: 13pt;
    font-weight: 600;
    color: #18181b;
    margin-top: 18px;
    margin-bottom: 8px;
  }

  h3 {
    font-size: 10.5pt;
    font-weight: 600;
    color: #27272a;
    margin-top: 12px;
    margin-bottom: 6px;
  }

  p {
    margin-bottom: 9px;
    color: #3f3f46;
  }

  ul, ol {
    margin-left: 18px;
    margin-bottom: 10px;
    color: #3f3f46;
  }

  li {
    margin-bottom: 4px;
  }

  /* Code and Mono */
  code {
    font-family: 'JetBrains Mono', Consolas, Monaco, monospace;
    font-size: 8.5pt;
    background: #f4f4f5;
    padding: 2px 5px;
    border-radius: 4px;
    color: #7c3aed;
    border: 1px solid #e4e4e7;
  }

  pre {
    font-family: 'JetBrains Mono', Consolas, Monaco, monospace;
    font-size: 8pt;
    background: #18181b;
    color: #e4e4e7;
    padding: 12px 14px;
    border-radius: 6px;
    overflow-x: auto;
    margin-bottom: 12px;
    line-height: 1.45;
    border: 1px solid #27272a;
    page-break-inside: avoid;
  }

  pre code {
    background: none;
    padding: 0;
    color: inherit;
    border: none;
    font-size: 8pt;
  }

  /* Callout Boxes */
  .callout {
    padding: 10px 14px;
    border-radius: 6px;
    margin-bottom: 12px;
    font-size: 9pt;
    page-break-inside: avoid;
  }

  .callout-info {
    background: #eff6ff;
    border-left: 4px solid #3b82f6;
    color: #1e40af;
  }

  .callout-success {
    background: #ecfdf5;
    border-left: 4px solid #10b981;
    color: #065f46;
  }

  .callout-purple {
    background: #f5f3ff;
    border-left: 4px solid #8b5cf6;
    color: #5b21b6;
  }

  .callout-warning {
    background: #fffbeb;
    border-left: 4px solid #f59e0b;
    color: #92400e;
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 8px;
    margin-bottom: 14px;
    font-size: 8.5pt;
    page-break-inside: avoid;
  }

  th, td {
    padding: 7px 10px;
    text-align: left;
    border-bottom: 1px solid #e4e4e7;
  }

  th {
    background: #f8fafc;
    font-weight: 600;
    color: #0f172a;
    border-top: 1px solid #cbd5e1;
    border-bottom: 2px solid #cbd5e1;
  }

  tr:nth-child(even) td {
    background: #fafafa;
  }

  /* Cards and Grids */
  .grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 14px;
    page-break-inside: avoid;
  }

  .grid-3 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 10px;
    margin-bottom: 14px;
    page-break-inside: avoid;
  }

  .card {
    border: 1px solid #e4e4e7;
    background: #ffffff;
    border-radius: 6px;
    padding: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    page-break-inside: avoid;
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
    font-size: 9.5pt;
    margin-bottom: 6px;
  }

  .badge {
    display: inline-block;
    font-size: 7.5pt;
    font-weight: 600;
    padding: 2px 7px;
    border-radius: 4px;
    text-transform: uppercase;
  }

  .badge-purple { background: #ede9fe; color: #6d28d9; border: 1px solid #ddd6fe; }
  .badge-cyan { background: #cffafe; color: #0e7490; border: 1px solid #a5f3fc; }
  .badge-emerald { background: #d1fae5; color: #047857; border: 1px solid #a7f3d0; }
  .badge-pink { background: #fce7f3; color: #be185d; border: 1px solid #fbcfe8; }
  .badge-amber { background: #fef3c7; color: #b45309; border: 1px solid #fde68a; }

  /* Architecture Diagram Box */
  .diagram-box {
    background: #09090b;
    color: #f4f4f5;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 14px;
    border: 1px solid #27272a;
    page-break-inside: avoid;
  }

  .diagram-title {
    font-size: 9pt;
    font-weight: 600;
    color: #a1a1aa;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 12px;
  }

  .pipeline-flow {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .pipeline-node {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #18181b;
    border: 1px solid #3f3f46;
    border-radius: 6px;
    padding: 8px 12px;
  }

  .pipeline-node.active {
    border-color: #8b5cf6;
    background: #1e1b4b;
  }

  .node-name {
    font-weight: 600;
    font-size: 9pt;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .node-desc {
    font-size: 8pt;
    color: #a1a1aa;
  }

  .arrow-down {
    text-align: center;
    color: #8b5cf6;
    font-size: 10pt;
    font-weight: bold;
    line-height: 0.6;
  }

  /* Table of Contents */
  .toc {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 24px;
  }

  .toc-title {
    font-size: 11pt;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .toc-list {
    list-style: none;
    margin: 0;
    padding: 0;
  }

  .toc-item {
    display: flex;
    justify-content: space-between;
    padding: 5px 0;
    border-bottom: 1px dotted #cbd5e1;
    font-size: 9pt;
  }

  .toc-item:last-child {
    border-bottom: none;
  }

  .toc-name {
    font-weight: 500;
    color: #1e293b;
  }

  .toc-num {
    font-weight: 600;
    color: #8b5cf6;
  }
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover-page">
  <div>
    <div class="cover-header">
      <span class="cover-badge">Fixie AI Agent Debugger Studio</span>
      <span style="color: #71717a; font-size: 9pt;">System Architecture & Component Guide</span>
    </div>
    <h1 class="cover-title">Autonomous Polyglot<br>Debugging & Repository<br>Intelligence Engine</h1>
    <p class="cover-subtitle">
      A comprehensive technical deep-dive into Fixie's 6-agent LangGraph orchestration pipeline,
      Server-Sent Events streaming engine, MySQL session memory layer, and Obsidian-dark React 18 Studio frontend.
    </p>
    <div class="cover-tags">
      <span class="tag-pill">LangGraph & LangChain</span>
      <span class="tag-pill">Google Gemini 1.5 Flash</span>
      <span class="tag-pill">FastAPI & Python 3.10+</span>
      <span class="tag-pill">MySQL 8.0 Persistence</span>
      <span class="tag-pill">React 18 & Vite</span>
      <span class="tag-pill">Polyglot: C++, JS/TS, Python, Java, Go, Rust</span>
      <span class="tag-pill">Dual Execution: Snippet & Full-Repo</span>
    </div>
  </div>

  <div class="cover-footer">
    <div>
      <strong>Fixie Engineering & Architecture Team</strong><br>
      <span>Comprehensive Component Specification & Operational Manual</span>
    </div>
    <div style="text-align: right;">
      <span>Document Version: <strong>2.4.0</strong></span><br>
      <span>Status: <strong>Production Ready</strong></span>
    </div>
  </div>
</div>

<!-- TABLE OF CONTENTS -->
<div class="toc">
  <div class="toc-title">Table of Contents</div>
  <ul class="toc-list">
    <li class="toc-item"><span class="toc-name">1. Executive Summary & Core Value Proposition</span><span class="toc-num">Section 1</span></li>
    <li class="toc-item"><span class="toc-name">2. High-Level System Architecture & End-to-End Data Flow</span><span class="toc-num">Section 2</span></li>
    <li class="toc-item"><span class="toc-name">3. The 6-Agent LangGraph Multi-Agent Pipeline</span><span class="toc-num">Section 3</span></li>
    <li class="toc-item"><span class="toc-name">4. Core Services & Infrastructure Subsystem</span><span class="toc-num">Section 4</span></li>
    <li class="toc-item"><span class="toc-name">5. FastAPI Backend Server & Endpoint Specifications</span><span class="toc-num">Section 5</span></li>
    <li class="toc-item"><span class="toc-name">6. MySQL Database Subsystem & Session Memory</span><span class="toc-num">Section 6</span></li>
    <li class="toc-item"><span class="toc-name">7. Frontend Studio Architecture & Component Hierarchy</span><span class="toc-num">Section 7</span></li>
    <li class="toc-item"><span class="toc-name">8. Testing Fixtures, Sample Repositories & Operational Runbook</span><span class="toc-num">Section 8</span></li>
  </ul>
</div>

<!-- SECTION 1 -->
<h1><span class="sec-num">1</span> Executive Summary & Core Value Proposition</h1>

<p>
  <strong>Fixie</strong> is an autonomous, multi-agent AI debugging studio designed to eliminate the manual, error-prone cycle of diagnosing bugs, understanding legacy logic, writing patches, and constructing verification tests across heterogeneous programming languages and complex repository structures.
</p>

<div class="grid-2">
  <div class="card">
    <div class="card-header">
      <span class="badge badge-purple">Snippet Mode</span>
      <span>Focused Algorithmic & File Debugging</span>
    </div>
    <p>
      Designed for LeetCode algorithms, single-file scripts, competitive programming, and isolated functions. Evaluates syntax/compilation rules, intent flow, edge cases, and produces executable test harnesses.
    </p>
  </div>
  <div class="card">
    <div class="card-header">
      <span class="badge badge-pink">Repository Mode</span>
      <span>Full-Project Cross-File Auditing</span>
    </div>
    <p>
      Ingests entire multi-file codebases (MERN web apps, C++ CMake engines, microservices). Maps inter-file dependencies, API contracts, scouts bugs across modules, and provides cross-file context to the repair engine.
    </p>
  </div>
</div>

<h3>Key Architectural Capabilities:</h3>
<ul>
  <li><strong>Multi-Language Polyglot Support</strong>: Natively supports C++, Python, JavaScript/React, TypeScript, Java, Go, Rust, and systems languages with specialized compiler AST and memory safety heuristics.</li>
  <li><strong>Zero-Simulation Real-Time Streaming</strong>: Built on genuine Server-Sent Events (SSE). Nodes push live execution state chunks as each agent in the LangGraph finishes work, giving real-time visual pipeline feedback without synthetic delays.</li>
  <li><strong>Client-Side & Server-Side Dual Ingestion</strong>: Projects can be scanned locally on the server file system, cloned from remote Git repositories, or parsed client-side in the browser using the HTML5 <code>webkitdirectory</code> and <code>DataTransfer</code> APIs without server file upload overhead.</li>
  <li><strong>Dual Verification Harnesses</strong>: Produces both executable programmatic test suites (for LeetCode/CLI) and interactive browser verification runbooks (for MERN/frontend applications).</li>
  <li><strong>Persistent Diagnostic Memory</strong>: Retains historical debugging runs, code revisions, and bug classifications inside a MySQL 8.0 relational database with 1-click historical reload.</li>
</ul>

<!-- SECTION 2 -->
<div class="page-break"></div>
<h1><span class="sec-num">2</span> High-Level System Architecture & End-to-End Data Flow</h1>

<p>
  The system consists of three interconnected layers: the <strong>React 18 Studio Frontend</strong>, the <strong>FastAPI Orchestration Gateway</strong>, and the <strong>LangGraph Multi-Agent Engine</strong> backed by the <strong>Google Gemini API</strong> and <strong>MySQL Session Storage</strong>.
</p>

<div class="diagram-box">
  <div class="diagram-title">System Architecture Topology</div>
  <pre style="margin-bottom:0; background: transparent; border: none; padding: 0; color: #a78bfa;">
+-----------------------------------------------------------------------------------------+
|                                    REACT 18 STUDIO UI                                   |
|  [Navbar / Mode Toggle]  [CodeEditor (Gutters)]  [RepoExplorer]  [AgentPipeline]  [Results] |
+-----------------------------------------------------------------------------------------+
             | POST /api/debug/stream (SSE)              ^ Server-Sent Events (text/event-stream)
             v                                           |
+-----------------------------------------------------------------------------------------+
|                                  FASTAPI APPLICATION SERVER                             |
|  - CORS & Static Serving         - JSON Request Validation      - Async SSE Event Queue |
|  - RepoScanner (File Tree/Git)   - Database Service Interface   - Session Persistence   |
+-----------------------------------------------------------------------------------------+
             |                                           |
             v                                           v
+------------------------------------+   +------------------------------------------------+
|     LANGGRAPH AGENT WORKFLOW       |   |             MYSQL 8.0 RELATIONAL DB            |
|                                    |   |                                                |
|  [RepoAnalyzer] -> Full Repo Scout |   |  Table: `debugging_sessions`                   |
|         v                          |   |  - id (AUTO_INCREMENT PRIMARY KEY)             |
|  [ContextProfiler] -> Env & Lang   |   |  - language (VARCHAR 50)                       |
|         v                          |   |  - original_code (LONGTEXT)                    |
|  [SyntaxChecker] -> AST / Compiler |   |  - error_description (TEXT)                    |
|         v                          |   |  - created_at (TIMESTAMP)                      |
|  [LogicReasoner] -> Intent Flow    |   +------------------------------------------------+
|         v                          |
|  [FixSuggester] -> Idiomatic Fix   |                      +-----------------------------+
|         v                          |                      |      GOOGLE GEMINI API      |
|  [TestHarness] -> Verification     | <------------------> |   gemini-1.5-flash / Pro    |
+------------------------------------+                      |   Official SDK / REST Fallback
                                                            +-----------------------------+
  </pre>
</div>

<h3>Data Flow Lifecycle:</h3>
<ol>
  <li><strong>Ingestion</strong>: The user selects Snippet Mode (pastes code or selects preset) or Repo Mode (specifies local path, drops folder, or clicks sample repo).</li>
  <li><strong>Dispatch</strong>: Frontend issues an HTTP <code>POST /api/debug/stream</code> request with the payload (code, mode, repo manifest, focus file).</li>
  <li><strong>Graph Execution</strong>: FastAPI dispatches an asynchronous worker thread invoking <code>stream_fixie_graph()</code> on the LangGraph state machine.</li>
  <li><strong>Real-Time SSE Yields</strong>: As each agent node finishes, it yields a <code>node_complete</code> event over the SSE connection containing its structured telemetry.</li>
  <li><strong>UI Animation & Rendering</strong>: Frontend's <code>EventSource</code> / stream reader updates the pipeline step indicator from <em>running</em> to <em>completed</em> and activates the subsequent agent.</li>
  <li><strong>Persistence & Termination</strong>: Upon graph termination, the session is saved to MySQL, a <code>complete</code> event with the <code>session_id</code> is dispatched, and the diagnostic results panel renders all solutions, tests, and traces.</li>
</ol>

<!-- SECTION 3 -->
<div class="page-break"></div>
<h1><span class="sec-num">3</span> The 6-Agent LangGraph Multi-Agent Pipeline</h1>

<p>
  The core reasoning brain of Fixie resides in <code>core/langgraph_runner.py</code> and six specialized agents located in the <code>agents/</code> directory. Agents communicate through a shared state container defined by the <code>FixieState</code> TypedDict.
</p>

<div class="callout callout-purple">
  <strong>FixieState Schema:</strong> Holds <code>mode</code>, <code>repo_path</code>, <code>repo_manifest</code>, <code>repo_analysis</code>, <code>focus_file</code>, <code>code</code>, <code>language</code>, <code>context_profile</code>, <code>syntax_report</code>, <code>logic</code>, <code>fix</code>, and <code>test_suite</code>.
</div>

<div class="diagram-box">
  <div class="diagram-title">Sequential Graph Workflow</div>
  <div class="pipeline-flow">
    <div class="pipeline-node active">
      <div class="node-name"><span class="badge badge-pink">Agent 1</span> RepoAnalyzer</div>
      <div class="node-desc">Scouts repository topology, traces dependency graph, pinpoints primary defect file.</div>
    </div>
    <div class="arrow-down">&#9660;</div>
    <div class="pipeline-node">
      <div class="node-name"><span class="badge badge-cyan">Agent 2</span> ContextProfiler</div>
      <div class="node-desc">Classifies language, environment (leetcode / mern / compiled_app), and build commands.</div>
    </div>
    <div class="arrow-down">&#9660;</div>
    <div class="pipeline-node">
      <div class="node-name"><span class="badge badge-amber">Agent 3</span> SyntaxChecker</div>
      <div class="node-desc">Audits compiler violations, AST syntax errors, and memory safety flaws.</div>
    </div>
    <div class="arrow-down">&#9660;</div>
    <div class="pipeline-node">
      <div class="node-name"><span class="badge badge-purple">Agent 4</span> LogicReasoner</div>
      <div class="node-desc">Deduces intended business logic, data flow progression, and invariants.</div>
    </div>
    <div class="arrow-down">&#9660;</div>
    <div class="pipeline-node">
      <div class="node-name"><span class="badge badge-emerald">Agent 5</span> FixSuggester</div>
      <div class="node-desc">Synthesizes complete, idiomatic code repair with cross-file contract adherence.</div>
    </div>
    <div class="arrow-down">&#9660;</div>
    <div class="pipeline-node">
      <div class="node-name"><span class="badge badge-purple">Agent 6</span> TestHarness</div>
      <div class="node-desc">Generates runnable test runner + test cases OR browser verification runbook.</div>
    </div>
  </div>
</div>

<h2>Deep-Dive Agent Specifications</h2>

<h3>1. RepoAnalyzer (<code>agents/repo_analyzer.py</code>)</h3>
<ul>
  <li><strong>Role</strong>: Principal Software Architect & Full-Repository Code Auditor.</li>
  <li><strong>Inputs</strong>: Repository manifest containing filtered file tree, build configs (<code>package.json</code>, <code>CMakeLists.txt</code>), and source file contents.</li>
  <li><strong>Outputs</strong>: JSON containing <code>stack_summary</code>, <code>architecture_type</code>, <code>dependency_graph</code> (caller/callee module mapping), <code>build_and_test_commands</code>, <code>detected_issues</code> list with file paths and severity, <code>primary_target_file</code>, and <code>cross_file_context</code>.</li>
  <li><strong>Mechanism</strong>: In Snippet Mode, passes through instantly. In Repo Mode, isolates the primary buggy file and loads its contents into <code>state["code"]</code> for downstream agents.</li>
</ul>

<h3>2. ContextProfiler (<code>agents/context_profiler.py</code>)</h3>
<ul>
  <li><strong>Role</strong>: Senior Software Architect & Build Environment Classifier.</li>
  <li><strong>Inputs</strong>: Source code and optional user language hint (or "auto").</li>
  <li><strong>Outputs</strong>: <code>language</code>, <code>display_language</code>, <code>environment_type</code> (<code>leetcode</code>, <code>mern</code>, <code>compiled_app</code>, <code>backend_api</code>, <code>script</code>), <code>build_system</code>, and <code>test_strategy</code>.</li>
  <li><strong>Mechanism</strong>: Employs few-shot prompt heuristics and regex fallback to detect idioms (e.g. <code>vector&lt;int&gt;& nums</code> -> C++ LeetCode, <code>import React, { useState }</code> -> React MERN).</li>
</ul>

<h3>3. SyntaxChecker (<code>agents/syntax_checker.py</code>)</h3>
<ul>
  <li><strong>Role</strong>: Expert Compiler, Linter, and Memory Safety Diagnostician.</li>
  <li><strong>Inputs</strong>: Source code, detected language, and context profile (including cross-file context).</li>
  <li><strong>Outputs</strong>: <code>bug_explanation</code>, <code>line_number</code>, and <code>severity</code> (<code>high</code>, <code>medium</code>, <code>low</code>, <code>none</code>).</li>
  <li><strong>Mechanism</strong>: Detects language-specific compiler traps: out-of-bounds array access in C++, unhandled Promise awaits in Express, infinite re-render loops in React hooks, and division-by-zero in Python.</li>
</ul>

<h3>4. LogicReasoner (<code>agents/logic_reasoner.py</code>)</h3>
<ul>
  <li><strong>Role</strong>: Algorithmic Logic Explainer & Program Intent Analyst.</li>
  <li><strong>Inputs</strong>: Source code, language, and context profile.</li>
  <li><strong>Outputs</strong>: Structured Markdown breakdown covering Intended Logic, Expected Data Flow, and Required Constraints/Invariants.</li>
  <li><strong>Mechanism</strong>: Reconstructs what the author attempted to achieve before the defect was introduced, providing cognitive grounding for the fix generator.</li>
</ul>

<h3>5. FixSuggester (<code>agents/fix_suggester.py</code>)</h3>
<ul>
  <li><strong>Role</strong>: Master Software Engineer & Code Synthesis Engine.</li>
  <li><strong>Inputs</strong>: Source code, bug report, logic explanation, language, and cross-file contract context.</li>
  <li><strong>Outputs</strong>: <code>explanation</code>, complete corrected <code>fix</code> code, and <code>confidence</code> score (0.0 to 1.0).</li>
  <li><strong>Mechanism</strong>: Generates the full, drop-in replacement function or module (never partial pseudo-diffs) preserving conventions and variable naming while honoring cross-file types and endpoints.</li>
</ul>

<h3>6. TestHarness (<code>agents/test_harness.py</code>)</h3>
<ul>
  <li><strong>Role</strong>: Senior QA Automation Engineer & Verification Architect.</li>
  <li><strong>Inputs</strong>: Original code, suggested fix, context profile, and logic breakdown.</li>
  <li><strong>Outputs</strong>: Dual-strategy JSON:
    <ul>
      <li><strong>Algorithmic Mode</strong>: 3-4 diverse test cases (normal, edge, boundary) + complete runnable test script in the target language.</li>
      <li><strong>Web / MERN Mode</strong>: Browser runbook with dev server startup command, target URL, step-by-step reproduction/verification guide, expected UI visuals, and DevTools console checklist.</li>
      <li><strong>CLI / Systems Mode</strong>: Compiler invocation command and execution flags.</li>
    </ul>
  </li>
</ul>

<!-- SECTION 4 -->
<div class="page-break"></div>
<h1><span class="sec-num">4</span> Core Services & Infrastructure Subsystem</h1>

<p>
  The <code>core/</code> directory contains foundational utilities that decouple external APIs, file system scanning, and LLM providers from high-level agent logic.
</p>

<div class="grid-2">
  <div class="card">
    <div class="card-header">
      <span class="badge badge-cyan">core/gemini_interface.py</span>
    </div>
    <p><strong>Gemini Client & REST Fallback:</strong></p>
    <ul>
      <li>Attempts to query via official <code>google-genai</code> SDK using <code>genai.Client(api_key=...)</code>.</li>
      <li>If the SDK is unavailable or encounters environment issues, automatically falls back to direct HTTP REST calls via <code>httpx.Client</code> to <code>https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent</code>.</li>
      <li>Validates API key status through <code>is_gemini_configured()</code>.</li>
    </ul>
  </div>

  <div class="card">
    <div class="card-header">
      <span class="badge badge-emerald">core/repo_scanner.py</span>
    </div>
    <p><strong>Repository File Tree & Git Ingestion:</strong></p>
    <ul>
      <li>Recursively traverses directories while skipping noise directories (<code>node_modules</code>, <code>.git</code>, <code>__pycache__</code>, <code>dist</code>, <code>build</code>, <code>venv</code>).</li>
      <li>Ignores binary file extensions (<code>.exe</code>, <code>.so</code>, <code>.png</code>, <code>.zip</code>, <code>.pdf</code>).</li>
      <li>Recognizes manifest files (<code>package.json</code>, <code>CMakeLists.txt</code>, <code>requirements.txt</code>, <code>Cargo.toml</code>).</li>
      <li>Supports remote Git cloning via <code>clone_and_scan_repo(url)</code>.</li>
    </ul>
  </div>
</div>

<div class="card" style="margin-top: 10px;">
  <div class="card-header">
    <span class="badge badge-purple">core/langgraph_runner.py</span>
  </div>
  <p><strong>Graph Construction & Dual Execution Handlers:</strong></p>
  <pre><code>def build_fixie_graph():
    builder = StateGraph(FixieState)
    builder.add_node("RepoAnalyzer", repo_node)
    builder.add_node("ContextProfiler", context_node)
    builder.add_node("SyntaxChecker", syntax_node)
    builder.add_node("LogicReasoner", logic_node)
    builder.add_node("FixSuggester", fix_node)
    builder.add_node("TestHarness", test_node)

    builder.set_entry_point("RepoAnalyzer")
    builder.add_edge("RepoAnalyzer", "ContextProfiler")
    builder.add_edge("ContextProfiler", "SyntaxChecker")
    builder.add_edge("SyntaxChecker", "LogicReasoner")
    builder.add_edge("LogicReasoner", "FixSuggester")
    builder.add_edge("FixSuggester", "TestHarness")
    builder.add_edge("TestHarness", "__end__")
    return builder.compile()</code></pre>
  <p>
    Exposes <code>run_fixie_graph()</code> for single-call synchronous debugging and <code>stream_fixie_graph()</code> which yields intermediate chunk objects containing each node's output as it executes.
  </p>
</div>

<!-- SECTION 5 -->
<div class="page-break"></div>
<h1><span class="sec-num">5</span> FastAPI Backend Server & Endpoint Specifications</h1>

<p>
  The backend server is implemented in <code>app.py</code> using <strong>FastAPI</strong> and <strong>Uvicorn</strong>. It connects the web client to the agent pipeline, serves the React production bundle, and provides diagnostic REST/SSE endpoints.
</p>

<table>
  <thead>
    <tr>
      <th>Method</th>
      <th>Endpoint</th>
      <th>Description</th>
      <th>Payload / Parameters</th>
      <th>Response Structure</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>GET</code></td>
      <td><code>/</code></td>
      <td>Serves compiled React frontend or static fallback.</td>
      <td>None</td>
      <td>HTML document</td>
    </tr>
    <tr>
      <td><code>GET</code></td>
      <td><code>/api/health</code></td>
      <td>Diagnostic check for MySQL server and Gemini API key.</td>
      <td>None</td>
      <td><code>{ status, mysql: { connected, message }, gemini: { available, message } }</code></td>
    </tr>
    <tr>
      <td><code>GET</code></td>
      <td><code>/api/examples</code></td>
      <td>Multi-language preset buggy snippets for 1-click testing.</td>
      <td>None</td>
      <td><code>{ examples: [ { title, language, description, code } ] }</code></td>
    </tr>
    <tr>
      <td><code>GET</code></td>
      <td><code>/api/sessions</code></td>
      <td>Retrieves recent debugging sessions from MySQL database.</td>
      <td><code>limit: int = 20</code></td>
      <td><code>{ sessions: [ DebuggingSession ] }</code></td>
    </tr>
    <tr>
      <td><code>POST</code></td>
      <td><code>/api/repo/scan</code></td>
      <td>Scans a local directory path or clones and scans a Git URL.</td>
      <td><code>{ repo_path: str }</code></td>
      <td><code>{ success: bool, repo: RepoManifest }</code></td>
    </tr>
    <tr>
      <td><code>GET</code></td>
      <td><code>/api/repo/examples</code></td>
      <td>Returns pre-configured sample repositories (MERN, C++ CMake).</td>
      <td>None</td>
      <td><code>{ sample_repos: [ { name, path, category, description } ] }</code></td>
    </tr>
    <tr>
      <td><code>POST</code></td>
      <td><code>/api/debug</code></td>
      <td>Runs complete LangGraph pipeline synchronously; saves session.</td>
      <td><code>DebugRequest (code, language, mode, repo_path, repo_manifest)</code></td>
      <td><code>DebugResponse (syntax_report, logic, fix, test_suite, session_id)</code></td>
    </tr>
    <tr>
      <td><code>POST</code></td>
      <td><code>/api/debug/stream</code></td>
      <td>Streams agent node execution in real time via Server-Sent Events.</td>
      <td><code>DebugRequest</code></td>
      <td><code>text/event-stream (data: { type, node, data })</code></td>
    </tr>
  </tbody>
</table>

<h3>Server-Sent Events (SSE) Protocol Details</h3>
<p>
  When calling <code>/api/debug/stream</code>, the client receives a live event stream with three message types:
</p>
<ul>
  <li><code>{"type": "init", "message": "..."}</code>: Handshake notification confirming pipeline startup.</li>
  <li><code>{"type": "node_complete", "node": "&lt;AgentName&gt;", "data": {...}}</code>: Dispatched immediately as each agent finishes, delivering incremental results.</li>
  <li><code>{"type": "complete", "session_id": 42, "db_saved": true, "state": {...}}</code>: Final termination event delivering session persistence ID and full state.</li>
  <li><code>{"type": "error", "message": "..."}</code>: Dispatched upon unexpected execution failure.</li>
</ul>

<!-- SECTION 6 -->
<div class="page-break"></div>
<h1><span class="sec-num">6</span> MySQL Database Subsystem & Session Memory</h1>

<p>
  Session memory is managed within the <code>database/</code> package using <strong>PyMySQL</strong>, providing persistent storage for debug runs, language metrics, and error histories.
</p>

<div class="grid-2">
  <div class="card">
    <div class="card-header">
      <span class="badge badge-emerald">database/models.py</span>
      <span>Schema Definition</span>
    </div>
    <pre><code>CREATE TABLE IF NOT EXISTS debugging_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    language VARCHAR(50) NOT NULL DEFAULT 'python',
    original_code LONGTEXT NOT NULL,
    error_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_language (language),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci;</code></pre>
  </div>

  <div class="card">
    <div class="card-header">
      <span class="badge badge-cyan">database/service.py</span>
      <span>Service Layer Methods</span>
    </div>
    <ul>
      <li><code>check_connection() -> (bool, str)</code>: Validates MySQL server availability and checks if the database/tables exist.</li>
      <li><code>init_db() -> bool</code>: Automatically issues <code>CREATE DATABASE IF NOT EXISTS</code> and executes DDL table creation.</li>
      <li><code>create_session(code, language, error) -> DebuggingSession</code>: Records a completed debug run.</li>
      <li><code>list_sessions(limit) -> List[DebuggingSession]</code>: Fetches recent sessions ordered by timestamp descending.</li>
    </ul>
  </div>
</div>

<h3>Database Diagnostics Tool: <code>verify_db.py</code></h3>
<p>
  A dedicated CLI tool provides immediate verification, automated migrations, and CRUD roundtrip checks:
</p>
<pre><code># Check MySQL server reachability and schema status
python verify_db.py

# Initialize database schema and required tables
python verify_db.py --init

# Run end-to-end diagnostics: ping, initialization, and CRUD roundtrip
python verify_db.py --test-all</code></pre>

<!-- SECTION 7 -->
<div class="page-break"></div>
<h1><span class="sec-num">7</span> Frontend Studio Architecture & Component Hierarchy</h1>

<p>
  The frontend is a single-page application built with <strong>React 18</strong>, <strong>Vite</strong>, custom <strong>Vanilla CSS</strong> (Obsidian dark aesthetic), and <strong>Lucide React</strong> icons. It is designed without external CSS frameworks to ensure maximum performance and pixel-perfect design control.
</p>

<div class="diagram-box">
  <div class="diagram-title">Frontend Component Hierarchy</div>
  <pre style="margin-bottom:0; background: transparent; border: none; padding: 0; color: #38bdf8;">
&lt;App /&gt; (Root State Machine, SSE Stream Consumer, Toast Dispatcher)
  |-- &lt;Navbar /&gt; (Mode Toggle, Health Diagnostics Pills, History Drawer Trigger)
  |-- &lt;main className="studio-layout"&gt;
  |     |-- [Left Column]:
  |     |     |-- (Snippet Mode) &lt;CodeEditor /&gt; (Gutter Line Numbers, Presets, Run/Clear)
  |     |     \-- (Repo Mode)    &lt;RepoExplorer /&gt; (Folder Dropzone, Tree, Active Viewer)
  |     \-- [Right Column]:
  |           |-- &lt;AgentPipeline /&gt; (6-Agent Status Timeline: idle/running/completed/error)
  |           \-- &lt;ResultsPanel /&gt; (Tabbed Diagnostics Studio)
  |                 |-- Tab: Repo Architecture (Topology, Dependency Graph, Build Cmds)
  |                 |-- Tab: Solution & Fix (Corrected Code, Copy Button, Confidence %)
  |                 |-- Tab: Verification & Tests (Runnable Test Script / Browser Runbook)
  |                 |-- Tab: Bug Analysis (Severity Badge, Line Number, Explanation)
  |                 |-- Tab: Logic Breakdown (Algorithmic Intent, Data Flow, Invariants)
  |                 \-- Tab: Raw Trace (Full JSON telemetry payload)
  |-- &lt;HistoryDrawer /&gt; (Slide-out past debugging sessions panel with 1-click reload)
  \-- &lt;Toast /&gt; (Floating non-blocking notification alerts)
  </pre>
</div>

<h3>Detailed Component Breakdown</h3>

<table>
  <thead>
    <tr>
      <th>Component File</th>
      <th>Primary Responsibility</th>
      <th>Key Features & Interactions</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>Navbar.jsx</code></td>
      <td>Top navigation and system telemetry bar.</td>
      <td>Mode switcher (Snippet vs Repo), real-time MySQL and Gemini health status pills with tooltips, session count badge, drawer open trigger.</td>
    </tr>
    <tr>
      <td><code>CodeEditor.jsx</code></td>
      <td>Syntax-aware code editor for snippet mode.</td>
      <td>Dynamic line number gutters synchronized with scrolling, language selector dropdown, preset code examples, run debugger CTA, clear button.</td>
    </tr>
    <tr>
      <td><code>RepoExplorer.jsx</code></td>
      <td>Full-repository exploration workspace.</td>
      <td>Drag-and-drop folder dropzone, native folder picker dialog, sample repository 1-click loaders, file search filter, tree viewer with bug badges, integrated code preview.</td>
    </tr>
    <tr>
      <td><code>AgentPipeline.jsx</code></td>
      <td>Visual execution timeline of the 6 agents.</td>
      <td>Displays status icons (clock, spinner, check, alert) and pulsating progress indicators as agents execute in real time.</td>
    </tr>
    <tr>
      <td><code>ResultsPanel.jsx</code></td>
      <td>Multi-tab diagnostics and solution view.</td>
      <td>Displays confidence gauge, severity badges, syntax report, full fixed code block with clipboard copy, runnable test runner script, browser verification steps, and raw telemetry.</td>
    </tr>
    <tr>
      <td><code>HistoryDrawer.jsx</code></td>
      <td>Slide-out past debugging sessions drawer.</td>
      <td>Lists historical sessions retrieved from MySQL with timestamp and language; clicking a session instantly restores code into the editor.</td>
    </tr>
    <tr>
      <td><code>folderParser.js</code></td>
      <td>Client-side folder ingestion engine.</td>
      <td>Uses HTML5 <code>webkitdirectory</code> and <code>DataTransferItem.webkitGetAsEntry</code> to recursively read local directories in the browser, filtering noise and producing manifest JSON without uploading files.</td>
    </tr>
  </tbody>
</table>

<!-- SECTION 8 -->
<div class="page-break"></div>
<h1><span class="sec-num">8</span> Testing Fixtures, Sample Repositories & Operational Runbook</h1>

<h3>Built-In Testing Fixtures & Repositories</h3>
<p>
  Fixie includes realistic multi-file test repositories under <code>examples/sample_repos/</code> designed to validate cross-file agent reasoning:
</p>

<div class="grid-2">
  <div class="card">
    <div class="card-header">
      <span class="badge badge-pink">MERN Stack Hardware Store</span>
    </div>
    <p><code>examples/sample_repos/mern_store</code></p>
    <ul>
      <li><strong>Frontend</strong>: React (Vite) with <code>ProductList.jsx</code> and <code>Navbar.jsx</code>. Contains an infinite <code>useEffect</code> fetch loop due to missing dependency array.</li>
      <li><strong>Backend</strong>: Express.js with <code>server.js</code> and <code>routes/products.js</code>. Contains an API contract mismatch (returning <code>item_name</code> instead of expected <code>title</code>).</li>
      <li><strong>Agent Validation</strong>: RepoAnalyzer traces the frontend-backend contract mismatch across files and fixes both the loop and interface.</li>
    </ul>
  </div>

  <div class="card">
    <div class="card-header">
      <span class="badge badge-cyan">C++ High Performance Engine</span>
    </div>
    <p><code>examples/sample_repos/cpp_engine</code></p>
    <ul>
      <li><strong>Structure</strong>: CMake build system with <code>CMakeLists.txt</code>, <code>src/engine.h</code>, <code>src/engine.cpp</code>, and <code>src/main.cpp</code>.</li>
      <li><strong>Bugs</strong>: Contains an off-by-one buffer overflow in array processing and an unreleased dynamic memory allocation (memory leak).</li>
      <li><strong>Agent Validation</strong>: RepoAnalyzer identifies CMake targets, SyntaxChecker detects memory safety hazards, and TestHarness produces compiler flags (<code>g++ -Wall -fsanitize=address</code>).</li>
    </ul>
  </div>
</div>

<h3>Quick Start & Operational Runbook</h3>

<pre><code># 1. Clone repository and set up virtual environment
git clone &lt;repo-url&gt;
cd DebuggingAI
python -m venv fixie
fixie\\Scripts\\activate

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Configure Environment (.env)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=fixie_db

# 4. Initialize Database
python verify_db.py --init

# 5. Build and Launch Frontend
cd frontend
npm install
npm run build
cd ..

# 6. Start FastAPI Application Server
uvicorn app:app --host 0.0.0.0 --port 8000 --reload</code></pre>

<div class="callout callout-success">
  <strong>Operational Tip:</strong> Navigate to <code>http://localhost:8000</code> in your browser to access the unified production studio. For frontend hot-reloading during development, run <code>npm run dev</code> inside <code>frontend/</code> and access <code>http://localhost:5173</code> (CORS is pre-configured).
</div>

</body>
</html>
"""


def main():
    print("=" * 70)
    print("Fixie AI Agent Debugger Studio - Documentation & PDF Generator")
    print("=" * 70)

    base_dir = Path(__file__).resolve().parent
    html_path = base_dir / "Fixie_AI_Architecture_and_System_Guide.html"
    pdf_path = base_dir / "Fixie_AI_Architecture_and_System_Guide.pdf"

    # Step 1: Write HTML
    print(f"\n1. Writing publication-grade HTML documentation...")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)
    print(f"   [OK] Generated: {html_path.name} ({len(HTML_CONTENT)} bytes)")

    # Step 2: Locate Headless Browser
    print("\n2. Detecting Chromium/Edge rendering engine...")
    browser_exe = find_browser_executable()
    if not browser_exe:
        print("   [!] Could not locate Microsoft Edge or Google Chrome executable.")
        print(f"   [!] HTML documentation is available at: {html_path}")
        return 1

    print(f"   [OK] Found Browser Engine: {browser_exe}")

    # Step 3: Render PDF via Headless Browser
    print(f"\n3. Rendering high-resolution vector PDF...")
    cmd = [
        browser_exe,
        "--headless",
        "--disable-gpu",
        "--allow-file-access-from-files",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={pdf_path}",
        "--no-pdf-header-footer",
        str(html_path.resolve()),
    ]

    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
        if pdf_path.exists() and pdf_path.stat().st_size > 0:
            size_kb = pdf_path.stat().st_size / 1024
            print(f"   [OK] Successfully compiled PDF: {pdf_path.name} ({size_kb:.1f} KB)")
            print("\n" + "=" * 70)
            print(f"PDF GENERATION COMPLETE!")
            print(f"Output File: {pdf_path.resolve()}")
            print("=" * 70)
            return 0
        else:
            print(f"   [!] PDF file was not created or has 0 bytes.")
            print(f"   Stderr: {proc.stderr}")
            return 1
    except Exception as e:
        print(f"   [!] Error executing browser command: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
