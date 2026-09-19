import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './components/Navbar';
import CodeEditor from './components/CodeEditor';
import RepoExplorer from './components/RepoExplorer';
import AgentPipeline from './components/AgentPipeline';
import ResultsPanel from './components/ResultsPanel';
import HistoryDrawer from './components/HistoryDrawer';
import Toast from './components/Toast';

export default function App() {
  const [mode, setMode] = useState('snippet'); // 'snippet' | 'repo'

  // Snippet Mode States
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('auto');
  const [detectedLanguage, setDetectedLanguage] = useState(null);
  const [examples, setExamples] = useState([]);

  // Repository Mode States
  const [repoPath, setRepoPath] = useState('');
  const [repoManifest, setRepoManifest] = useState(null);
  const [sampleRepos, setSampleRepos] = useState([]);
  const [activeFile, setActiveFile] = useState(null);

  // Common Health & Sessions
  const [health, setHealth] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [isRunning, setIsRunning] = useState(false);

  // 6-Agent Pipeline States: 'idle' | 'running' | 'completed' | 'error'
  const [agentStates, setAgentStates] = useState({
    RepoAnalyzer: 'idle',
    ContextProfiler: 'idle',
    SyntaxChecker: 'idle',
    LogicReasoner: 'idle',
    FixSuggester: 'idle',
    TestHarness: 'idle',
  });
  const [pipelineStatus, setPipelineStatus] = useState('idle');

  // Diagnostic Results
  const [results, setResults] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [dbSaved, setDbSaved] = useState(false);

  // History Drawer State
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  // Toast System
  const [toasts, setToasts] = useState([]);

  const showToast = useCallback((message, type = 'info') => {
    const id = Date.now() + Math.random();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3500);
  }, []);

  // Fetch Health Diagnostics
  const fetchHealth = useCallback(async () => {
    try {
      const res = await fetch('/api/health');
      if (res.ok) {
        const data = await res.json();
        setHealth(data);
      }
    } catch (err) {
      console.warn('Health check failed:', err);
    }
  }, []);

  // Fetch Snippet Examples
  const fetchExamples = useCallback(async () => {
    try {
      const res = await fetch('/api/examples');
      if (res.ok) {
        const data = await res.json();
        const items = data.examples || [];
        setExamples(items);
        if (items.length > 0 && !code) {
          setCode(items[0].code);
          if (items[0].language) setLanguage(items[0].language);
        }
      }
    } catch (err) {
      console.warn('Could not load examples:', err);
    }
  }, [code]);

  // Fetch Sample Repositories
  const fetchSampleRepos = useCallback(async () => {
    try {
      const res = await fetch('/api/repo/examples');
      if (res.ok) {
        const data = await res.json();
        setSampleRepos(data.sample_repos || []);
      }
    } catch (err) {
      console.warn('Could not load sample repos:', err);
    }
  }, []);

  // Fetch Sessions History
  const fetchSessions = useCallback(async () => {
    try {
      const res = await fetch('/api/sessions');
      if (res.ok) {
        const data = await res.json();
        setSessions(data.sessions || []);
      }
    } catch (err) {
      console.warn('Could not load sessions:', err);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
    fetchExamples();
    fetchSampleRepos();
    fetchSessions();

    const interval = setInterval(fetchHealth, 10000);
    return () => clearInterval(interval);
  }, [fetchHealth, fetchExamples, fetchSampleRepos, fetchSessions]);

  // Scan Repository Path
  const scanRepo = async (targetPath) => {
    try {
      const res = await fetch('/api/repo/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_path: targetPath }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Failed to scan repository');
      }
      const data = await res.json();
      setRepoManifest(data.repo);
      setResults(null);

      // Default active file
      const tree = data.repo.file_tree || [];
      if (tree.length > 0) {
        const firstSource = tree.find((f) => !f.is_manifest) || tree[0];
        setActiveFile(firstSource.path);
      }
      showToast(`Scanned repository: ${data.repo.repo_name} (${data.repo.total_files} files)`);
    } catch (err) {
      console.error(err);
      showToast(`Scan error: ${err.message}`, 'error');
    }
  };

  const handleLoadSampleRepo = (path) => {
    setRepoPath(path);
    scanRepo(path);
  };

  // Direct client-side folder upload / drop handler
  const handleFolderUploaded = (manifest) => {
    setRepoManifest(manifest);
    setRepoPath(manifest.repo_name || 'Uploaded Project');
    setResults(null);
    setPipelineStatus('idle');
    resetAgents();

    const tree = manifest.file_tree || [];
    if (tree.length > 0) {
      const firstSource = tree.find((f) => !f.is_manifest) || tree[0];
      setActiveFile(firstSource.path);
    }
    showToast(`Loaded "${manifest.repo_name}" (${manifest.total_files} files ready for analysis)`, 'success');
  };

  // Get active file source code
  const getActiveFileCode = () => {
    if (!repoManifest || !activeFile) return '';
    if (repoManifest.manifest_files && repoManifest.manifest_files[activeFile]) {
      return repoManifest.manifest_files[activeFile];
    }
    if (repoManifest.source_files && repoManifest.source_files[activeFile]) {
      return repoManifest.source_files[activeFile];
    }
    return '';
  };

  // Reset agent states helper
  const resetAgents = () => {
    setAgentStates({
      RepoAnalyzer: 'idle',
      ContextProfiler: 'idle',
      SyntaxChecker: 'idle',
      LogicReasoner: 'idle',
      FixSuggester: 'idle',
      TestHarness: 'idle',
    });
  };

  // Handle Example Selection (Snippet Mode)
  const handleSelectExample = (idx) => {
    if (examples[idx]) {
      const ex = examples[idx];
      setCode(ex.code);
      if (ex.language) setLanguage(ex.language);
      setDetectedLanguage(null);
      setResults(null);
      setSessionId(null);
      setDbSaved(false);
      setPipelineStatus('idle');
      resetAgents();
      showToast(`Loaded preset: ${ex.title}`);
    }
  };

  // Handle Session Selection from Drawer
  const handleSelectSession = (session) => {
    if (session.original_code) {
      setMode('snippet');
      setCode(session.original_code);
      if (session.language) setLanguage(session.language);
      setDetectedLanguage(session.language);
      setResults(null);
      setSessionId(session.id);
      setDbSaved(true);
      showToast(`Loaded Session #${session.id} (${session.language})`);
    }
  };

  // Clear Snippet Editor
  const handleClear = () => {
    setCode('');
    setDetectedLanguage(null);
    setResults(null);
    setSessionId(null);
    setDbSaved(false);
    setPipelineStatus('idle');
    resetAgents();
  };

  // =========================================================================
  // Real-Time Server-Sent Events (SSE) Debugger Runner (6 AGENTS IN REPO MODE)
  // =========================================================================
  const runDebugger = async () => {
    if (mode === 'snippet' && !code.trim()) {
      showToast('Please enter code to debug.', 'error');
      return;
    }
    if (mode === 'repo' && !repoPath.trim() && !repoManifest) {
      showToast('Please specify a repository path to debug.', 'error');
      return;
    }

    setIsRunning(true);
    setPipelineStatus('running');
    setResults(null);
    setSessionId(null);
    setDbSaved(false);

    // Initial state based on mode
    if (mode === 'repo') {
      setAgentStates({
        RepoAnalyzer: 'running',
        ContextProfiler: 'idle',
        SyntaxChecker: 'idle',
        LogicReasoner: 'idle',
        FixSuggester: 'idle',
        TestHarness: 'idle',
      });
    } else {
      setAgentStates({
        RepoAnalyzer: 'idle',
        ContextProfiler: 'running',
        SyntaxChecker: 'idle',
        LogicReasoner: 'idle',
        FixSuggester: 'idle',
        TestHarness: 'idle',
      });
    }

    try {
      const payload =
        mode === 'repo'
          ? {
              mode: 'repo',
              repo_path: repoPath,
              repo_manifest: repoManifest,
              focus_file: activeFile,
              code: getActiveFileCode(),
              language: 'auto',
            }
          : {
              mode: 'snippet',
              code: code.trim(),
              language,
            };

      const response = await fetch('/api/debug/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server returned ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const block of lines) {
          const trimmedBlock = block.trim();
          if (!trimmedBlock.startsWith('data:')) continue;

          const jsonStr = trimmedBlock.replace(/^data:\s*/, '');
          try {
            const event = JSON.parse(jsonStr);

            if (event.type === 'node_complete') {
              const { node, data } = event;

              if (node === 'RepoAnalyzer') {
                setResults((prev) => ({ ...prev, ...data }));
                const targetFile = data.repo_analysis?.primary_target_file;
                if (targetFile) {
                  setActiveFile(targetFile);
                }
                setAgentStates({
                  RepoAnalyzer: 'completed',
                  ContextProfiler: 'running',
                  SyntaxChecker: 'idle',
                  LogicReasoner: 'idle',
                  FixSuggester: 'idle',
                  TestHarness: 'idle',
                });
              } else if (node === 'ContextProfiler') {
                setResults((prev) => ({ ...prev, ...data }));
                const profile = data.context_profile || {};
                if (profile.display_language) {
                  setDetectedLanguage(profile.display_language);
                }
                setAgentStates((prev) => ({
                  ...prev,
                  ContextProfiler: 'completed',
                  SyntaxChecker: 'running',
                }));
              } else if (node === 'SyntaxChecker') {
                setResults((prev) => ({ ...prev, ...data }));
                setAgentStates((prev) => ({
                  ...prev,
                  SyntaxChecker: 'completed',
                  LogicReasoner: 'running',
                }));
              } else if (node === 'LogicReasoner') {
                setResults((prev) => ({ ...prev, ...data }));
                setAgentStates((prev) => ({
                  ...prev,
                  LogicReasoner: 'completed',
                  FixSuggester: 'running',
                }));
              } else if (node === 'FixSuggester') {
                setResults((prev) => ({ ...prev, ...data }));
                setAgentStates((prev) => ({
                  ...prev,
                  FixSuggester: 'completed',
                  TestHarness: 'running',
                }));
              } else if (node === 'TestHarness') {
                setResults((prev) => ({ ...prev, ...data }));
                setAgentStates((prev) => ({
                  ...prev,
                  TestHarness: 'completed',
                }));
              }
            } else if (event.type === 'complete') {
              setSessionId(event.session_id);
              setDbSaved(event.db_saved);
              setPipelineStatus('completed');
              fetchSessions();
              showToast(
                mode === 'repo'
                  ? 'Full-Repository Analysis & Cross-File Verification Complete!'
                  : '5-Agent Analysis & Test Harness Complete!',
                'success'
              );
            } else if (event.type === 'error') {
              throw new Error(event.message);
            }
          } catch (parseErr) {
            console.warn('Failed to parse SSE event:', jsonStr, parseErr);
          }
        }
      }
    } catch (err) {
      console.error('Debug pipeline error:', err);
      showToast(`Error: ${err.message}`, 'error');
      setPipelineStatus('idle');
      setAgentStates((prev) => ({
        ...prev,
        RepoAnalyzer: prev.RepoAnalyzer === 'running' ? 'error' : prev.RepoAnalyzer,
        ContextProfiler: prev.ContextProfiler === 'running' ? 'error' : prev.ContextProfiler,
        SyntaxChecker: prev.SyntaxChecker === 'running' ? 'error' : prev.SyntaxChecker,
        LogicReasoner: prev.LogicReasoner === 'running' ? 'error' : prev.LogicReasoner,
        FixSuggester: prev.FixSuggester === 'running' ? 'error' : prev.FixSuggester,
        TestHarness: prev.TestHarness === 'running' ? 'error' : prev.TestHarness,
      }));
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="app-container">
      {/* Top Navbar */}
      <Navbar
        mode={mode}
        setMode={setMode}
        health={health}
        sessionCount={sessions.length}
        onOpenHistory={() => setIsHistoryOpen(true)}
      />

      {/* Main Studio Viewport */}
      <main className="studio-layout">
        {/* Left Column: Code Editor OR Repository Explorer */}
        {mode === 'snippet' ? (
          <CodeEditor
            code={code}
            setCode={setCode}
            language={language}
            setLanguage={setLanguage}
            detectedLanguage={detectedLanguage}
            examples={examples}
            onSelectExample={handleSelectExample}
            onRun={runDebugger}
            isRunning={isRunning}
            onClear={handleClear}
          />
        ) : (
          <RepoExplorer
            repoPath={repoPath}
            setRepoPath={setRepoPath}
            repoManifest={repoManifest}
            onScanRepo={scanRepo}
            onFolderLoaded={handleFolderUploaded}
            sampleRepos={sampleRepos}
            onLoadSampleRepo={handleLoadSampleRepo}
            activeFile={activeFile}
            setActiveFile={setActiveFile}
            activeFileCode={getActiveFileCode()}
            repoAnalysis={results?.repo_analysis}
            isRunning={isRunning}
            onRunRepoPipeline={runDebugger}
          />
        )}

        {/* Right Column: Multi-Agent Pipeline & Diagnostics Studio */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <AgentPipeline
            agentStates={agentStates}
            pipelineStatus={pipelineStatus}
            mode={mode}
          />

          <ResultsPanel
            results={results}
            isRunning={isRunning}
            sessionId={sessionId}
            dbSaved={dbSaved}
            onCopyCode={() => showToast('Corrected code copied to clipboard!', 'success')}
            onSelectTargetFile={(file) => {
              setMode('repo');
              setActiveFile(file);
            }}
          />
        </div>
      </main>

      {/* History Slide-Out Drawer */}
      <HistoryDrawer
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        sessions={sessions}
        onSelectSession={handleSelectSession}
      />

      {/* Floating Toast Notification Container */}
      <Toast toasts={toasts} />
    </div>
  );
}
