"""FastAPI Application Server for Fixie AI Code Debugger.

Connects the web frontend with the multi-agent LangGraph debugging pipeline
and MySQL session memory storage.
"""

import os
import json
import asyncio
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.langgraph_runner import run_fixie_graph, stream_fixie_graph
from core.gemini_interface import is_gemini_configured, DEFAULT_MODEL
from database.service import DatabaseService
from database.config import get_db_config

app = FastAPI(
    title="Fixie AI Code Debugger",
    description="Multi-Agent AI Code Debugging Studio with MySQL Memory",
    version="1.0.0",
)

# Enable CORS for local React development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_service = DatabaseService()

# Ensure static folder exists
os.makedirs("static", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)


# Mount static assets and built React frontend
dist_dir = os.path.join(os.path.dirname(__file__), "frontend", "dist")
dist_assets = os.path.join(dist_dir, "assets")
if os.path.exists(dist_assets):
    app.mount("/assets", StaticFiles(directory=dist_assets), name="assets")


from core.repo_scanner import scan_repository, is_git_url, clone_and_scan_repo


class DebugRequest(BaseModel):
    code: str = ""
    language: str = "auto"
    mode: str = "snippet"  # "snippet" | "repo"
    repo_path: Optional[str] = None
    repo_manifest: Optional[Dict[str, Any]] = None
    focus_file: Optional[str] = None


class RepoScanRequest(BaseModel):
    repo_path: str


class DebugResponse(BaseModel):
    success: bool
    mode: str = "snippet"
    repo_analysis: Optional[Dict[str, Any]] = None
    context_profile: Optional[Dict[str, Any]] = None
    syntax_report: Optional[Dict[str, Any]] = None
    logic: Optional[str] = None
    fix: Optional[Dict[str, Any]] = None
    test_suite: Optional[Dict[str, Any]] = None
    session_id: Optional[int] = None
    db_saved: bool = False
    raw_result: Optional[Dict[str, Any]] = None


@app.get("/")
async def serve_index():
    """Serve the React application frontend if built, or fallback to static."""
    react_index = os.path.join(dist_dir, "index.html")
    if os.path.exists(react_index):
        return FileResponse(react_index)
    return FileResponse("static/index.html")


@app.get("/api/health")
async def health_check():
    """Diagnostic health check for MySQL database and Gemini API."""
    db_ok, db_msg = False, "Not initialized"
    try:
        db_ok, db_msg = db_service.check_connection()
    except Exception as e:
        db_msg = str(e)

    gemini_ok = is_gemini_configured()
    gemini_msg = (
        f"API key configured (Model: {DEFAULT_MODEL})"
        if gemini_ok
        else "GEMINI_API_KEY is not set in .env"
    )

    return {
        "status": "healthy" if (db_ok and gemini_ok) else "degraded",
        "mysql": {
            "connected": db_ok,
            "message": db_msg,
        },
        "gemini": {
            "available": gemini_ok,
            "message": gemini_msg,
        },
    }


@app.get("/api/examples")
async def get_examples():
    """Return pre-configured multi-language code examples for quick debugging testing."""
    examples = [
        {
            "title": "C++ LeetCode: Vector Out-of-Bounds & Negative Max Bug",
            "language": "cpp",
            "description": "Algorithmic C++ function with out-of-bounds loop and zero-initialization flaw for negative arrays.",
            "code": """#include <iostream>
#include <vector>
using namespace std;

class Solution {
public:
    // LeetCode: Find maximum element in array
    int findMax(vector<int>& nums) {
        int max_val = 0; // BUG: fails for all-negative arrays like {-10, -5, -20}
        
        // BUG: <= causes std::out_of_range memory access beyond array boundary
        for (int i = 0; i <= nums.size(); i++) {
            if (nums[i] > max_val) {
                max_val = nums[i];
            }
        }
        return max_val;
    }
};

int main() {
    Solution s;
    vector<int> nums = {-10, -5, -20};
    cout << "Max: " << s.findMax(nums) << endl;
    return 0;
}
""",
        },
        {
            "title": "MERN Stack: React Infinite Re-Render Fetch Loop",
            "language": "javascript",
            "description": "React component with missing useEffect dependency array triggering continuous browser API calls.",
            "code": """import React, { useState, useEffect } from 'react';
import axios from 'axios';

// MERN Stack Component: User Profile Card
export default function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // BUG: Missing dependency array [] causes infinite re-render loop on browser!
  useEffect(() => {
    axios.get(`/api/users/${userId}`)
      .then(res => {
        setUser(res.data);
        setLoading(false);
      })
      .catch(err => console.error(err));
  });

  if (loading) return <div className="spinner">Loading user profile...</div>;
  return (
    <div className="user-card">
      <h2>{user.name}</h2>
      <p>Email: {user.email}</p>
    </div>
  );
}
""",
        },
        {
            "title": "Python: Safe Division & ZeroDivisionError",
            "language": "python",
            "description": "Unchecked division by zero without edge-case validation.",
            "code": """def calculate_ratios(data):
    results = []
    for item in data:
        # BUG: ZeroDivisionError occurs when item['count'] is 0
        ratio = item['total'] / item['count']
        results.append(ratio)
    return results

data = [{'total': 100, 'count': 5}, {'total': 50, 'count': 0}]
print(calculate_ratios(data))
""",
        },
        {
            "title": "Node.js / Express: Missing Await on Async Database Query",
            "language": "javascript",
            "description": "Missing await on Mongoose async call causing unhandled Promise response.",
            "code": """const express = require('express');
const router = express.Router();
const User = require('../models/User');

// BUG: Missing 'await' returns pending Promise object instead of user document
router.get('/users/:id', async (req, res) => {
  try {
    const user = User.findById(req.params.id);
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }
    res.json(user);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
""",
        },
    ]
    return {"examples": examples}


@app.get("/api/sessions")
async def list_sessions(limit: int = 20):
    """Retrieve recent debugging sessions from MySQL."""
    try:
        sessions = db_service.list_sessions(limit=limit)
        return {"sessions": [s.to_dict() for s in sessions]}
    except Exception as e:
        return {"sessions": [], "warning": f"Unable to fetch sessions: {e}"}


@app.post("/api/repo/scan")
async def scan_repo_endpoint(payload: RepoScanRequest):
    """Scan a local directory or clone a Git URL and return its file tree and manifest summary."""
    try:
        path_or_url = payload.repo_path.strip()
        if is_git_url(path_or_url):
            data = await asyncio.to_thread(clone_and_scan_repo, path_or_url)
        else:
            data = scan_repository(path_or_url)
        return {"success": True, "repo": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/repo/examples")
async def get_repo_examples():
    """Return pre-configured sample repositories for 1-click testing."""
    base_dir = os.path.dirname(__file__)
    mern_path = os.path.join(base_dir, "examples", "sample_repos", "mern_store").replace("\\", "/")
    cpp_path = os.path.join(base_dir, "examples", "sample_repos", "cpp_engine").replace("\\", "/")
    return {
        "sample_repos": [
            {
                "name": "MERN Stack Hardware Store",
                "description": "Multi-file React + Express project with cross-file contract mismatch and infinite useEffect loop.",
                "path": mern_path,
                "category": "mern",
            },
            {
                "name": "C++ High Performance Engine",
                "description": "Multi-file C++ CMake project with buffer overflow and memory leak.",
                "path": cpp_path,
                "category": "cpp_cmake",
            },
        ]
    }


@app.post("/api/debug", response_model=DebugResponse)
async def debug_code(payload: DebugRequest):
    """Run the Fixie multi-agent LangGraph workflow and persist session in MySQL."""
    code = payload.code.strip()
    if payload.mode == "snippet" and not code:
        raise HTTPException(status_code=400, detail="Source code cannot be empty.")
    if payload.mode == "repo" and not payload.repo_path and not payload.repo_manifest and not code:
        raise HTTPException(status_code=400, detail="Repository path, folder manifest, or source code must be provided.")

    try:
        result = await asyncio.to_thread(
            run_fixie_graph,
            code=code,
            language=payload.language,
            mode=payload.mode,
            repo_path=payload.repo_path,
            repo_manifest=payload.repo_manifest,
            focus_file=payload.focus_file,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent workflow error: {str(e)}")

    repo_analysis = result.get("repo_analysis")
    context_profile = result.get("context_profile")
    syntax_report = result.get("syntax_report")
    logic = result.get("logic")
    fix = result.get("fix")
    test_suite = result.get("test_suite")
    detected_lang = result.get("language") or payload.language
    final_code = result.get("code") or code

    error_desc = None
    if isinstance(syntax_report, dict):
        error_desc = syntax_report.get("bug_explanation")

    session_id = None
    db_saved = False
    try:
        saved_session = db_service.create_session(
            original_code=final_code,
            language=detected_lang,
            error_description=error_desc,
        )
        if saved_session:
            session_id = saved_session.id
            db_saved = True
    except Exception:
        pass

    return DebugResponse(
        success=True,
        mode=payload.mode,
        repo_analysis=repo_analysis if isinstance(repo_analysis, dict) else None,
        context_profile=context_profile if isinstance(context_profile, dict) else None,
        syntax_report=syntax_report if isinstance(syntax_report, dict) else None,
        logic=logic if isinstance(logic, str) else None,
        fix=fix if isinstance(fix, dict) else None,
        test_suite=test_suite if isinstance(test_suite, dict) else None,
        session_id=session_id,
        db_saved=db_saved,
        raw_result=result,
    )


@app.post("/api/debug/stream")
async def debug_code_stream(payload: DebugRequest):
    """Stream LangGraph agent node executions in real time via Server-Sent Events."""
    code = payload.code.strip()
    if payload.mode == "snippet" and not code:
        raise HTTPException(status_code=400, detail="Source code cannot be empty.")
    if payload.mode == "repo" and not payload.repo_path and not payload.repo_manifest and not code:
        raise HTTPException(status_code=400, detail="Repository path, folder manifest, or source code must be provided.")

    async def event_stream():
        accumulated_state: Dict[str, Any] = {}
        loop = asyncio.get_running_loop()
        queue = asyncio.Queue()

        def worker():
            try:
                for chunk in stream_fixie_graph(
                    code=code,
                    language=payload.language,
                    mode=payload.mode,
                    repo_path=payload.repo_path,
                    repo_manifest=payload.repo_manifest,
                    focus_file=payload.focus_file,
                ):
                    loop.call_soon_threadsafe(queue.put_nowait, ("chunk", chunk))
                loop.call_soon_threadsafe(queue.put_nowait, ("done", None))
            except Exception as exc:
                loop.call_soon_threadsafe(queue.put_nowait, ("error", str(exc)))

        threading_task = asyncio.to_thread(worker)
        asyncio.create_task(threading_task)

        # Initial handshake event
        yield f"data: {json.dumps({'type': 'init', 'message': f'LangGraph {payload.mode.upper()} multi-agent pipeline initiated'})}\n\n"

        while True:
            msg_type, data = await queue.get()
            if msg_type == "chunk":
                for node_name, node_output in data.items():
                    accumulated_state.update(node_output)
                    yield f"data: {json.dumps({'type': 'node_complete', 'node': node_name, 'data': node_output})}\n\n"
            elif msg_type == "error":
                yield f"data: {json.dumps({'type': 'error', 'message': data})}\n\n"
                break
            elif msg_type == "done":
                syntax_report = accumulated_state.get("syntax_report")
                error_desc = None
                if isinstance(syntax_report, dict):
                    error_desc = syntax_report.get("bug_explanation")

                final_lang = accumulated_state.get("language") or payload.language
                final_code = accumulated_state.get("code") or code

                session_id = None
                db_saved = False
                try:
                    saved_session = db_service.create_session(
                        original_code=final_code,
                        language=final_lang,
                        error_description=error_desc,
                    )
                    if saved_session:
                        session_id = saved_session.id
                        db_saved = True
                except Exception:
                    pass

                yield f"data: {json.dumps({'type': 'complete', 'session_id': session_id, 'db_saved': db_saved, 'state': accumulated_state})}\n\n"
                break

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# Mount static assets
app.mount("/static", StaticFiles(directory="static"), name="static")
