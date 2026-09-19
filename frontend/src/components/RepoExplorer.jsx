import React, { useState, useRef } from 'react';
import {
  FolderOpen,
  FolderGit2,
  FileCode,
  FileText,
  Upload,
  Sparkles,
  AlertTriangle,
  Package,
  Layers,
  Search,
  CheckCircle2,
  Loader2,
  RefreshCw,
  GitBranch,
  Laptop,
} from 'lucide-react';
import { parseFilesToManifest, getFilesFromDataTransfer } from '../utils/folderParser';

export default function RepoExplorer({
  repoPath,
  setRepoPath,
  repoManifest,
  onScanRepo,
  onFolderLoaded,
  sampleRepos,
  onLoadSampleRepo,
  activeFile,
  setActiveFile,
  activeFileCode,
  repoAnalysis,
  isRunning,
  onRunRepoPipeline,
}) {
  const [inputVal, setInputVal] = useState(repoPath || '');
  const [filterQuery, setFilterQuery] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessingFolder, setIsProcessingFolder] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');

  const folderInputRef = useRef(null);

  const fileTree = repoManifest?.file_tree || [];
  const detectedIssues = repoAnalysis?.detected_issues || [];

  // Map of file_path -> issue for badging
  const issueMap = {};
  detectedIssues.forEach((issue) => {
    if (issue.file_path) {
      issueMap[issue.file_path] = issue;
    }
  });

  // Handle native folder picker selection
  const handleFolderInput = async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setIsProcessingFolder(true);
    setStatusMessage(`Reading ${files.length} files from folder...`);
    try {
      const manifest = await parseFilesToManifest(files);
      onFolderLoaded(manifest);
      setStatusMessage('');
    } catch (err) {
      alert(`Error reading folder: ${err.message}`);
      setStatusMessage('');
    } finally {
      setIsProcessingFolder(false);
      // Reset input value so same folder can be re-selected if needed
      e.target.value = '';
    }
  };

  // Drag and Drop handlers
  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isRunning) setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (isRunning) return;

    setIsProcessingFolder(true);
    setStatusMessage('Scanning dropped folder contents...');
    try {
      const files = await getFilesFromDataTransfer(e.dataTransfer);
      if (files.length === 0) {
        throw new Error('No files detected in the dropped folder.');
      }
      const manifest = await parseFilesToManifest(files);
      onFolderLoaded(manifest);
      setStatusMessage('');
    } catch (err) {
      alert(`Error importing dropped folder: ${err.message}`);
      setStatusMessage('');
    } finally {
      setIsProcessingFolder(false);
    }
  };

  const handlePathOrUrlSubmit = (e) => {
    e.preventDefault();
    if (inputVal.trim()) {
      setRepoPath(inputVal.trim());
      onScanRepo(inputVal.trim());
    }
  };

  const getFileIcon = (file) => {
    if (file.is_manifest) return <Package size={13} style={{ color: '#f59e0b' }} />;
    const ext = (file.extension || '').toLowerCase();
    if (['cpp', 'c', 'h', 'hpp'].includes(ext)) {
      return <FileCode size={13} style={{ color: '#06b6d4' }} />;
    }
    if (['jsx', 'js', 'tsx', 'ts'].includes(ext)) {
      return <FileCode size={13} style={{ color: '#60a5fa' }} />;
    }
    if (['py'].includes(ext)) {
      return <FileCode size={13} style={{ color: '#34d399' }} />;
    }
    return <FileText size={13} style={{ color: 'var(--text-dim)' }} />;
  };

  const filteredFiles = fileTree.filter((f) =>
    f.path.toLowerCase().includes(filterQuery.toLowerCase())
  );

  return (
    <div
      className={`panel ${isDragging ? 'drag-active' : ''}`}
      style={{ flex: 1, position: 'relative' }}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Hidden Native Folder Input */}
      <input
        type="file"
        ref={folderInputRef}
        webkitdirectory="true"
        directory="true"
        multiple
        style={{ display: 'none' }}
        onChange={handleFolderInput}
      />

      {/* Drag & Drop Visual Overlay */}
      {isDragging && (
        <div className="repo-drag-overlay">
          <FolderOpen size={48} style={{ color: '#60a5fa', animation: 'pulse 1s infinite' }} />
          <h3 style={{ margin: '12px 0 6px 0', color: '#f8fafc' }}>Drop Project Folder Here</h3>
          <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>
            Fixie will parse and load the repository instantly
          </p>
        </div>
      )}

      {/* Top Action Bar */}
      <div
        className="panel-header"
        style={{ height: 'auto', padding: '10px 16px', gap: 10, flexWrap: 'wrap' }}
      >
        {/* Primary Action: Choose Folder from Computer */}
        <button
          type="button"
          className="btn btn-primary"
          style={{
            background: 'linear-gradient(135deg, #2563eb, #3b82f6)',
            boxShadow: '0 2px 10px rgba(37,99,235,0.3)',
            display: 'flex',
            alignItems: 'center',
            gap: 6,
          }}
          onClick={() => folderInputRef.current?.click()}
          disabled={isRunning || isProcessingFolder}
          title="Pick any folder on your computer directly via file dialog"
        >
          {isProcessingFolder ? (
            <Loader2 size={15} style={{ animation: 'spin 1s linear infinite' }} />
          ) : (
            <FolderOpen size={15} />
          )}
          <span>Choose Project Folder</span>
        </button>

        {/* Path or Git URL input */}
        <form
          onSubmit={handlePathOrUrlSubmit}
          style={{ display: 'flex', alignItems: 'center', gap: 6, flex: 1, minWidth: 260 }}
        >
          <input
            type="text"
            className="repo-path-input"
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            placeholder="Or enter local path or GitHub URL (https://github.com/...)..."
            disabled={isRunning || isProcessingFolder}
          />
          <button
            type="submit"
            className="btn btn-secondary"
            disabled={isRunning || isProcessingFolder || !inputVal.trim()}
          >
            Scan / Clone
          </button>
        </form>

        {/* Quick Sample Repos */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Sample:</span>
          {sampleRepos.map((sample, idx) => (
            <button
              key={idx}
              className="btn btn-ghost"
              style={{
                padding: '4px 8px',
                fontSize: '0.72rem',
                border: '1px solid var(--border)',
                background: 'rgba(255,255,255,0.03)',
              }}
              onClick={() => {
                setInputVal(sample.path);
                setRepoPath(sample.path);
                onLoadSampleRepo(sample.path);
              }}
              disabled={isRunning || isProcessingFolder}
              title={sample.description}
            >
              {sample.category === 'mern' ? '⚛️ MERN' : '⚙️ C++'}
            </button>
          ))}
        </div>
      </div>

      {/* Main Workspace: Empty State or Active File Tree + Code Viewer */}
      {!repoManifest || fileTree.length === 0 ? (
        /* ================= EMPTY STATE INSERTION HUB ================= */
        <div className="repo-empty-hub">
          <div
            className="repo-dropzone"
            onClick={() => folderInputRef.current?.click()}
          >
            <div className="dropzone-icon-circle">
              <Upload size={32} style={{ color: '#38bdf8' }} />
            </div>
            <h3 style={{ margin: '14px 0 6px 0', fontSize: '1.2rem', color: '#f8fafc' }}>
              Insert Your Project Repository
            </h3>
            <p style={{ color: '#94a3b8', fontSize: '0.85rem', maxWidth: 440, lineHeight: 1.5 }}>
              Click here to <strong>choose a folder</strong> from your computer, or{' '}
              <strong>drag & drop</strong> your folder directly into this window.
            </p>

            <button
              type="button"
              className="btn btn-primary"
              style={{ marginTop: 16 }}
              onClick={(e) => {
                e.stopPropagation();
                folderInputRef.current?.click();
              }}
            >
              <FolderOpen size={15} />
              <span>Select Folder from Computer</span>
            </button>

            <div className="dropzone-tip">
              <span>🛡️ Safe & local:</span> Automatically excludes{' '}
              <code>node_modules</code>, <code>.git</code>, and build binaries.
            </div>
          </div>

          {/* Alternative Quick Presets */}
          <div className="repo-preset-cards">
            <div className="preset-card-label">Or test with a pre-configured sample repository:</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 12 }}>
              {sampleRepos.map((sample, idx) => (
                <div
                  key={idx}
                  className="preset-sample-card"
                  onClick={() => {
                    setInputVal(sample.path);
                    setRepoPath(sample.path);
                    onLoadSampleRepo(sample.path);
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                    <span style={{ fontSize: '1.2rem' }}>
                      {sample.category === 'mern' ? '⚛️' : '⚙️'}
                    </span>
                    <strong style={{ fontSize: '0.88rem', color: '#f1f5f9' }}>{sample.name}</strong>
                  </div>
                  <p style={{ fontSize: '0.76rem', color: '#94a3b8', margin: 0, lineHeight: 1.4 }}>
                    {sample.description}
                  </p>
                  <div style={{ marginTop: 8, display: 'flex', justifyContent: 'flex-end' }}>
                    <span className="sample-load-badge">Click to load &rarr;</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        /* ================= ACTIVE REPO WORKSPACE ================= */
        <div className="repo-workspace">
          {/* Left Column: File Tree */}
          <div className="repo-tree-pane">
            <div className="repo-tree-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, overflow: 'hidden' }}>
                <FolderGit2 size={15} style={{ color: '#60a5fa', flexShrink: 0 }} />
                <span
                  style={{ fontWeight: 600, color: '#f1f5f9', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}
                  title={repoManifest.repo_name}
                >
                  {repoManifest.repo_name}
                </span>
              </div>
              <span className="badge-tag">{fileTree.length} files</span>
            </div>

            {/* Quick File Filter */}
            <div className="repo-filter-box">
              <Search size={12} style={{ color: 'var(--text-dim)' }} />
              <input
                type="text"
                placeholder="Filter files..."
                value={filterQuery}
                onChange={(e) => setFilterQuery(e.target.value)}
              />
              {filterQuery && (
                <button
                  className="filter-clear-btn"
                  onClick={() => setFilterQuery('')}
                  title="Clear filter"
                >
                  &times;
                </button>
              )}
            </div>

            <div className="repo-file-list">
              {filteredFiles.length === 0 ? (
                <div style={{ padding: 16, textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.78rem' }}>
                  No matching files found.
                </div>
              ) : (
                filteredFiles.map((file) => {
                  const isSelected = activeFile === file.path;
                  const hasIssue = issueMap[file.path];

                  return (
                    <div
                      key={file.path}
                      className={`repo-file-item ${isSelected ? 'active' : ''} ${
                        hasIssue ? 'has-issue' : ''
                      }`}
                      onClick={() => setActiveFile(file.path)}
                      title={file.path}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, overflow: 'hidden' }}>
                        {getFileIcon(file)}
                        <span className="file-path-text">{file.path}</span>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: 4, flexShrink: 0 }}>
                        {hasIssue && (
                          <span
                            className="issue-dot"
                            title={`Issue: ${hasIssue.title} (${hasIssue.severity})`}
                          >
                            <AlertTriangle size={11} style={{ color: '#fb7185' }} />
                          </span>
                        )}
                        {file.is_manifest && (
                          <span className="badge-manifest">config</span>
                        )}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Right Column: Code Viewer of Active File */}
          <div className="repo-viewer-pane">
            <div className="code-display-header" style={{ background: 'rgba(0,0,0,0.2)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <FileCode size={14} style={{ color: '#60a5fa' }} />
                <span style={{ fontWeight: 600, color: '#e2e8f0', fontSize: '0.84rem' }}>
                  {activeFile || 'Select a file from tree to inspect'}
                </span>
                {issueMap[activeFile] && (
                  <span className="badge high" style={{ fontSize: '0.68rem', padding: '1px 6px' }}>
                    <AlertTriangle size={10} /> Bug Flagged: {issueMap[activeFile].severity}
                  </span>
                )}
              </div>

              <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                {activeFileCode ? `${activeFileCode.split('\n').length} lines` : ''}
              </span>
            </div>

            <div className="editor-container" style={{ minHeight: 380 }}>
              <pre className="editor-textarea" style={{ overflowY: 'auto' }}>
                {activeFileCode || '// Click a file in the left explorer to view its contents...'}
              </pre>
            </div>
          </div>
        </div>
      )}

      {/* Bottom Footer Actions */}
      <div className="editor-footer">
        <div className="editor-stats">
          <Layers size={13} style={{ color: '#a78bfa' }} />
          <span>
            {statusMessage ||
              (repoManifest
                ? `Loaded: ${repoManifest.repo_name} (${fileTree.length} files scanned)`
                : 'Full Repository Mode — Choose a folder or drop a project to begin')}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {repoManifest && (
            <button
              type="button"
              className="btn btn-ghost"
              style={{ fontSize: '0.76rem' }}
              onClick={() => folderInputRef.current?.click()}
              disabled={isRunning || isProcessingFolder}
            >
              <RefreshCw size={12} />
              <span>Change Folder</span>
            </button>
          )}

          <button
            className="btn btn-primary"
            onClick={onRunRepoPipeline}
            disabled={isRunning || isProcessingFolder || !repoManifest || fileTree.length === 0}
          >
            {isRunning ? (
              <>
                <Loader2 size={15} style={{ animation: 'spin 1s linear infinite' }} />
                <span>Scouting Repository & Running Pipeline...</span>
              </>
            ) : (
              <>
                <Sparkles size={14} />
                <span>Analyze & Debug Repository</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
