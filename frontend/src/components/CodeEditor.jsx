import React, { useRef } from 'react';
import { Play, RotateCcw, Code2, Loader2, Globe } from 'lucide-react';

const SUPPORTED_LANGUAGES = [
  { value: 'auto', label: 'Auto-Detect' },
  { value: 'cpp', label: 'C++' },
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript / React (MERN)' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'java', label: 'Java' },
  { value: 'go', label: 'Go' },
  { value: 'rust', label: 'Rust' },
];

export default function CodeEditor({
  code,
  setCode,
  language,
  setLanguage,
  detectedLanguage,
  examples,
  onSelectExample,
  onRun,
  isRunning,
  onClear,
}) {
  const textareaRef = useRef(null);
  const gutterRef = useRef(null);

  const lines = code.split('\n');
  const lineCount = lines.length;

  const handleScroll = () => {
    if (textareaRef.current && gutterRef.current) {
      gutterRef.current.scrollTop = textareaRef.current.scrollTop;
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const start = e.target.selectionStart;
      const end = e.target.selectionEnd;
      const newCode = code.substring(0, start) + '    ' + code.substring(end);
      setCode(newCode);

      setTimeout(() => {
        if (textareaRef.current) {
          textareaRef.current.selectionStart = textareaRef.current.selectionEnd = start + 4;
        }
      }, 0);
    } else if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      if (!isRunning && code.trim()) {
        onRun();
      }
    }
  };

  return (
    <div className="panel">
      {/* Panel Header */}
      <div className="panel-header">
        <div className="panel-title">
          <Code2 size={16} style={{ color: '#60a5fa' }} />
          <span>Source Code</span>

          {/* Language Selector */}
          <select
            className="select-input"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            disabled={isRunning}
            style={{ marginLeft: 6, fontWeight: 500 }}
          >
            {SUPPORTED_LANGUAGES.map((lang) => (
              <option key={lang.value} value={lang.value}>
                {lang.label}
              </option>
            ))}
          </select>

          {detectedLanguage && language === 'auto' && (
            <span
              className="badge-tag"
              style={{
                background: 'rgba(59, 130, 246, 0.15)',
                color: '#60a5fa',
                borderColor: 'rgba(59, 130, 246, 0.3)',
              }}
              title="Automatically profiled language"
            >
              Detected: {detectedLanguage}
            </span>
          )}
        </div>

        <div className="panel-actions">
          {examples.length > 0 && (
            <select
              className="select-input"
              onChange={(e) => onSelectExample(Number(e.target.value))}
              defaultValue=""
              disabled={isRunning}
            >
              <option value="" disabled>
                Load Polyglot Preset...
              </option>
              {examples.map((ex, idx) => (
                <option key={idx} value={idx}>
                  {ex.title}
                </option>
              ))}
            </select>
          )}

          <button
            className="btn btn-ghost"
            onClick={onClear}
            disabled={isRunning || !code}
            title="Clear Editor"
          >
            <RotateCcw size={14} />
            <span>Clear</span>
          </button>
        </div>
      </div>

      {/* Editor Body with Gutter */}
      <div className="editor-container">
        <div className="editor-gutter" ref={gutterRef}>
          {Array.from({ length: Math.max(lineCount, 16) }, (_, i) => (
            <div key={i + 1} className="gutter-number">
              {i + 1}
            </div>
          ))}
        </div>

        <textarea
          ref={textareaRef}
          className="editor-textarea"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          onScroll={handleScroll}
          onKeyDown={handleKeyDown}
          placeholder="# Paste your C++, Python, JavaScript/React, Java, Go, or Rust code here...&#10;# The Context Profiler agent will auto-detect your language and project type!"
          spellCheck={false}
          disabled={isRunning}
        />
      </div>

      {/* Editor Footer */}
      <div className="editor-footer">
        <div className="editor-stats">
          <span>{lineCount} {lineCount === 1 ? 'line' : 'lines'}</span>
          <span>{code.length} chars</span>
          <span><kbd style={{ background: 'rgba(255,255,255,0.08)', padding: '2px 5px', borderRadius: 4 }}>Ctrl+Enter</kbd> to debug</span>
        </div>

        <button
          className="btn btn-primary"
          onClick={onRun}
          disabled={isRunning || !code.trim()}
        >
          {isRunning ? (
            <>
              <Loader2 size={15} style={{ animation: 'spin 1s linear infinite' }} />
              <span>Analyzing Pipeline...</span>
            </>
          ) : (
            <>
              <Play size={14} fill="currentColor" />
              <span>Run Polyglot Debugger</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
