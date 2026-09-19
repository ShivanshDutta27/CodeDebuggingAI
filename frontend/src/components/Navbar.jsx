import React from 'react';
import {
  Wrench,
  Database,
  Sparkles,
  History,
  BookOpen,
  Code2,
  FolderGit2,
} from 'lucide-react';

export default function Navbar({
  mode,
  setMode,
  health,
  sessionCount,
  onOpenHistory,
}) {
  const geminiAvailable = health?.gemini?.available ?? false;
  const mysqlConnected = health?.mysql?.connected ?? false;

  return (
    <header className="navbar">
      <div className="nav-brand">
        <div className="brand-icon">
          <Wrench size={19} />
        </div>
        <div className="brand-title">
          Fixie <span>AI</span>
          <span className="badge-tag">Multi-Agent Studio</span>
        </div>
      </div>

      {/* Mode Switcher */}
      <div className="mode-switcher">
        <button
          className={`mode-btn ${mode === 'snippet' ? 'active' : ''}`}
          onClick={() => setMode('snippet')}
          title="Debug individual code snippets or functions"
        >
          <Code2 size={14} />
          <span>Snippet Studio</span>
        </button>

        <button
          className={`mode-btn ${mode === 'repo' ? 'active' : ''}`}
          onClick={() => setMode('repo')}
          title="Scan and debug full multi-file repositories with cross-file context"
        >
          <FolderGit2 size={14} />
          <span>Repository Studio</span>
          <span className="badge-mini-new">Full Repo</span>
        </button>
      </div>

      <div className="nav-center">
        {/* Gemini Status Pill */}
        <div
          className="system-pill"
          title={
            health?.gemini?.message ||
            (geminiAvailable ? 'Gemini 1.5 Flash is ready' : 'Gemini API key missing in .env')
          }
        >
          <span className={`status-dot ${geminiAvailable ? 'green' : 'red'}`} />
          <Sparkles size={13} style={{ color: geminiAvailable ? '#60a5fa' : 'var(--text-dim)' }} />
          <span>Gemini AI</span>
        </div>

        {/* MySQL Status Pill */}
        <div
          className="system-pill"
          title={health?.mysql?.message || (mysqlConnected ? 'MySQL Connected' : 'MySQL Offline')}
        >
          <span className={`status-dot ${mysqlConnected ? 'green' : 'red'}`} />
          <Database size={13} style={{ color: mysqlConnected ? '#34d399' : 'var(--text-dim)' }} />
          <span>MySQL DB</span>
        </div>
      </div>

      <div className="nav-actions">
        <button
          className="btn btn-secondary"
          onClick={onOpenHistory}
          title="View Past Debugging Sessions"
        >
          <History size={15} />
          <span>History</span>
          <span className="count-badge">{sessionCount}</span>
        </button>

        <a
          href="https://github.com/kawish918/Fixie-AI-Agent-Debugger"
          target="_blank"
          rel="noreferrer"
          className="btn btn-ghost"
          title="Project Documentation"
        >
          <BookOpen size={15} />
          <span>Docs</span>
        </a>
      </div>
    </header>
  );
}
