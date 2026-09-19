import React, { useState } from 'react';
import {
  Sparkles,
  AlertTriangle,
  Brain,
  Copy,
  Check,
  ShieldAlert,
  Database,
  Terminal,
  FlaskConical,
  Globe,
  Layers,
  Cpu,
  FolderGit2,
  GitFork,
  ArrowRight,
} from 'lucide-react';

export default function ResultsPanel({
  results,
  isRunning,
  sessionId,
  dbSaved,
  onCopyCode,
  onSelectTargetFile,
}) {
  const [activeTab, setActiveTab] = useState('solution');
  const [copied, setCopied] = useState(false);
  const [copiedRunner, setCopiedRunner] = useState(false);

  const repoAnalysis = results?.repo_analysis;
  const contextProfile = results?.context_profile || {};
  const syntaxReport = results?.syntax_report || {};
  const logic = results?.logic || '';
  const fix = results?.fix || {};
  const testSuite = results?.test_suite || {};

  const displayLang = contextProfile?.display_language || 'Source';
  const envType = contextProfile?.environment_type || (repoAnalysis?.architecture_type || 'general');
  const buildSystem = contextProfile?.build_system || (repoAnalysis?.build_and_test_commands?.dev || 'Standard Runtime');

  const confidence = typeof fix?.confidence === 'number' ? fix.confidence : 0.9;
  const confidencePercent = Math.round(confidence * 100);

  const severity = (syntaxReport?.severity || 'medium').toLowerCase();
  const lineNumber = syntaxReport?.line_number || 'N/A';
  const bugExplanation =
    syntaxReport?.bug_explanation || 'No syntax or runtime errors detected.';
  const fixCode = fix?.fix || '';
  const fixExplanation = fix?.explanation || 'No fix explanation available.';

  const handleCopy = () => {
    if (!fixCode) return;
    navigator.clipboard.writeText(fixCode);
    setCopied(true);
    if (onCopyCode) onCopyCode();
    setTimeout(() => setCopied(false), 2000);
  };

  const handleCopyRunner = () => {
    if (!testSuite?.runner_code) return;
    navigator.clipboard.writeText(testSuite.runner_code);
    setCopiedRunner(true);
    setTimeout(() => setCopiedRunner(false), 2000);
  };

  const hasAnyResult = Boolean(
    results &&
      (repoAnalysis ||
        contextProfile.language ||
        syntaxReport.bug_explanation ||
        logic ||
        fix.fix)
  );

  return (
    <div className="panel">
      {/* Panel Header */}
      <div className="panel-header">
        <div className="panel-title">
          <Sparkles size={16} style={{ color: '#8b5cf6' }} />
          <span>Agent Diagnostics</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {repoAnalysis && (
            <span
              className="badge-tag"
              style={{
                background: 'rgba(236, 72, 153, 0.12)',
                color: '#f472b6',
                borderColor: 'rgba(236, 72, 153, 0.3)',
              }}
            >
              Repo Scouted
            </span>
          )}

          {contextProfile.display_language && (
            <span
              className="badge-tag"
              style={{
                background: 'rgba(6, 182, 212, 0.12)',
                color: '#22d3ee',
                borderColor: 'rgba(6, 182, 212, 0.3)',
              }}
            >
              {contextProfile.display_language}
            </span>
          )}

          {dbSaved && sessionId && (
            <div
              className="badge success"
              title={`Session #${sessionId} synced to MySQL database`}
            >
              <Database size={11} />
              <span>Saved (Session #{sessionId})</span>
            </div>
          )}
        </div>
      </div>

      {/* Environment & Repo Profile Header Banner */}
      {hasAnyResult && (contextProfile.environment_type || repoAnalysis) && (
        <div className="env-profile-banner">
          {repoAnalysis?.stack_summary && (
            <div className="env-pill">
              <FolderGit2 size={13} style={{ color: '#ec4899' }} />
              <span>Stack: <strong>{repoAnalysis.stack_summary}</strong></span>
            </div>
          )}
          <div className="env-pill">
            <Globe size={13} style={{ color: '#06b6d4' }} />
            <span>Target: <strong>{displayLang}</strong></span>
          </div>
          <div className="env-pill">
            <Layers size={13} style={{ color: '#8b5cf6' }} />
            <span>Environment: <strong>{envType.toUpperCase()}</strong></span>
          </div>
          <div className="env-pill">
            <Cpu size={13} style={{ color: '#10b981' }} />
            <span>Build: <strong>{buildSystem}</strong></span>
          </div>
        </div>
      )}

      {/* Tabs */}
      {hasAnyResult && (
        <div className="tabs-nav">
          {repoAnalysis && (
            <button
              className={`tab-btn ${activeTab === 'repo' ? 'active' : ''}`}
              onClick={() => setActiveTab('repo')}
            >
              <FolderGit2 size={14} />
              <span>Repo Architecture</span>
            </button>
          )}

          <button
            className={`tab-btn ${activeTab === 'solution' ? 'active' : ''}`}
            onClick={() => setActiveTab('solution')}
          >
            <Sparkles size={14} />
            <span>Solution & Fix</span>
          </button>

          <button
            className={`tab-btn ${activeTab === 'tests' ? 'active' : ''}`}
            onClick={() => setActiveTab('tests')}
          >
            <FlaskConical size={14} />
            <span>Verification & Tests</span>
          </button>

          <button
            className={`tab-btn ${activeTab === 'bug' ? 'active' : ''}`}
            onClick={() => setActiveTab('bug')}
          >
            <ShieldAlert size={14} />
            <span>Bug Analysis</span>
          </button>

          <button
            className={`tab-btn ${activeTab === 'logic' ? 'active' : ''}`}
            onClick={() => setActiveTab('logic')}
          >
            <Brain size={14} />
            <span>Logic Breakdown</span>
          </button>

          <button
            className={`tab-btn ${activeTab === 'raw' ? 'active' : ''}`}
            onClick={() => setActiveTab('raw')}
          >
            <Terminal size={14} />
            <span>Raw Trace</span>
          </button>
        </div>
      )}

      {/* Results Viewport */}
      <div className="results-viewport">
        {!hasAnyResult && !isRunning && (
          <div className="empty-state">
            <div className="empty-icon">
              <Terminal size={28} />
            </div>
            <div className="empty-title">Ready for Multi-Agent Analysis</div>
            <div className="empty-desc">
              Scan a whole repository or paste code to launch the coordinated LangGraph pipeline in real time.
            </div>
          </div>
        )}

        {isRunning && !hasAnyResult && (
          <div className="empty-state">
            <div className="empty-icon">
              <Sparkles
                size={28}
                style={{ color: '#60a5fa', animation: 'spin 3s linear infinite' }}
              />
            </div>
            <div className="empty-title">Scouting Codebase & Running Pipeline...</div>
            <div className="empty-desc">
              Repo Scout is auditing cross-file dependencies and locating target defects...
            </div>
          </div>
        )}

        {hasAnyResult && (
          <div className="tab-content">
            {/* Tab: Repository Architecture */}
            {activeTab === 'repo' && repoAnalysis && (
              <div>
                {/* Repo Overview */}
                <div className="section-box" style={{ borderColor: 'rgba(236, 72, 153, 0.3)' }}>
                  <div className="section-box-title" style={{ color: '#f472b6' }}>
                    <FolderGit2 size={13} />
                    <span>Repository Overview & Stack</span>
                  </div>
                  <p style={{ color: '#e2e8f0', fontSize: '0.86rem', lineHeight: 1.6, marginBottom: 10 }}>
                    {repoAnalysis.stack_summary || 'Full-stack repository architecture detected.'}
                  </p>

                  {repoAnalysis.primary_target_file && (
                    <div style={{ background: 'rgba(0,0,0,0.3)', padding: '8px 12px', borderRadius: 8, fontSize: '0.8rem' }}>
                      <span style={{ color: 'var(--text-dim)' }}>Primary Defect Location: </span>
                      <code style={{ color: '#60a5fa', fontWeight: 600 }}>{repoAnalysis.primary_target_file}</code>
                      {onSelectTargetFile && (
                        <button
                          className="btn btn-ghost"
                          style={{ padding: '2px 8px', fontSize: '0.72rem', marginLeft: 8 }}
                          onClick={() => onSelectTargetFile(repoAnalysis.primary_target_file)}
                        >
                          View File
                        </button>
                      )}
                    </div>
                  )}
                </div>

                {/* Detected Cross-File Issues */}
                {repoAnalysis.detected_issues && repoAnalysis.detected_issues.length > 0 && (
                  <div style={{ marginBottom: 16 }}>
                    <div className="section-box-title" style={{ color: '#fb7185' }}>
                      <ShieldAlert size={13} />
                      <span>Scouted Cross-File Issues ({repoAnalysis.detected_issues.length})</span>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                      {repoAnalysis.detected_issues.map((issue, iIdx) => (
                        <div
                          key={iIdx}
                          className="section-box"
                          style={{
                            margin: 0,
                            borderColor: issue.severity === 'high' ? 'rgba(244, 63, 94, 0.4)' : 'var(--border)',
                          }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                              <span className={`badge ${issue.severity || 'medium'}`} style={{ fontSize: '0.68rem' }}>
                                {(issue.severity || 'medium').toUpperCase()}
                              </span>
                              <strong style={{ color: '#f1f5f9', fontSize: '0.86rem' }}>{issue.title || 'Issue'}</strong>
                            </div>
                            <code style={{ color: '#60a5fa', fontSize: '0.75rem' }}>{issue.file_path}</code>
                          </div>

                          <p style={{ color: '#cbd5e1', fontSize: '0.82rem', lineHeight: 1.5, marginBottom: 6 }}>
                            {issue.description}
                          </p>

                          {issue.affected_files && (
                            <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                              Affected files: {issue.affected_files.join(', ')}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Dependency Graph */}
                {repoAnalysis.dependency_graph && repoAnalysis.dependency_graph.length > 0 && (
                  <div className="section-box">
                    <div className="section-box-title" style={{ color: '#a78bfa' }}>
                      <GitFork size={13} />
                      <span>Cross-File Dependency Graph</span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                      {repoAnalysis.dependency_graph.map((edge, eIdx) => (
                        <div
                          key={eIdx}
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 8,
                            fontSize: '0.78rem',
                            padding: '6px 10px',
                            background: 'rgba(0,0,0,0.25)',
                            borderRadius: 6,
                          }}
                        >
                          <code style={{ color: '#60a5fa' }}>{edge.from}</code>
                          <ArrowRight size={12} style={{ color: 'var(--text-dim)' }} />
                          <code style={{ color: '#34d399' }}>{edge.to}</code>
                          <span style={{ color: 'var(--text-dim)', marginLeft: 'auto', fontSize: '0.72rem' }}>
                            {edge.relationship}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Tab: Solution & Fix */}
            {activeTab === 'solution' && (
              <div>
                <div className="meta-strip">
                  <span className={`badge ${severity}`}>
                    <AlertTriangle size={11} />
                    <span>Severity: {severity.toUpperCase()}</span>
                  </span>

                  {lineNumber !== 'N/A' && (
                    <span className="badge low">
                      <span>Line {lineNumber}</span>
                    </span>
                  )}

                  <div className="confidence-widget">
                    <span>Confidence:</span>
                    <div className="confidence-track">
                      <div
                        className="confidence-fill"
                        style={{ width: `${confidencePercent}%` }}
                      />
                    </div>
                    <strong>{confidencePercent}%</strong>
                  </div>
                </div>

                <div className="section-box">
                  <div className="section-box-title">
                    <Brain size={12} />
                    <span>Diagnosis & Fix Rationale</span>
                  </div>
                  <p style={{ color: '#e2e8f0', fontSize: '0.85rem', lineHeight: 1.6 }}>
                    {fixExplanation}
                  </p>
                </div>

                {fixCode && (
                  <div className="code-display-box">
                    <div className="code-display-header">
                      <span>Corrected Implementation ({displayLang})</span>
                      <button
                        className="btn btn-ghost"
                        onClick={handleCopy}
                        style={{ padding: '3px 8px', fontSize: '0.72rem' }}
                      >
                        {copied ? (
                          <>
                            <Check size={12} style={{ color: '#34d399' }} />
                            <span>Copied</span>
                          </>
                        ) : (
                          <>
                            <Copy size={12} />
                            <span>Copy Code</span>
                          </>
                        )}
                      </button>
                    </div>
                    <pre className="code-content">{fixCode}</pre>
                  </div>
                )}
              </div>
            )}

            {/* Tab: Verification & Tests */}
            {activeTab === 'tests' && (
              <div>
                <div className="section-box" style={{ borderColor: 'rgba(245, 158, 11, 0.3)' }}>
                  <div className="section-box-title" style={{ color: '#fbbf24' }}>
                    <FlaskConical size={13} />
                    <span>Environment Test Strategy</span>
                  </div>
                  <p style={{ color: '#e2e8f0', fontSize: '0.85rem', lineHeight: 1.5 }}>
                    {testSuite.summary || 'Custom verification strategy tailored to this build environment.'}
                  </p>
                </div>

                {testSuite.test_cases && testSuite.test_cases.length > 0 && (
                  <div style={{ marginBottom: 16 }}>
                    <div className="section-box-title">
                      <span>Algorithmic Test Suite & Edge Cases</span>
                    </div>

                    <div className="testcase-table-container">
                      <table className="testcase-table">
                        <thead>
                          <tr>
                            <th>Case</th>
                            <th>Category</th>
                            <th>Input</th>
                            <th>Expected Output</th>
                            <th>Explanation</th>
                          </tr>
                        </thead>
                        <tbody>
                          {testSuite.test_cases.map((tc, idx) => (
                            <tr key={idx}>
                              <td style={{ fontWeight: 600, color: '#f1f5f9' }}>{tc.name}</td>
                              <td>
                                <span className="badge low" style={{ fontSize: '0.68rem' }}>
                                  {tc.category}
                                </span>
                              </td>
                              <td><code>{tc.input}</code></td>
                              <td><code style={{ color: '#34d399' }}>{tc.expected_output}</code></td>
                              <td style={{ color: 'var(--text-muted)', fontSize: '0.78rem' }}>{tc.explanation}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {testSuite.runner_code && (
                  <div className="code-display-box" style={{ marginBottom: 16 }}>
                    <div className="code-display-header">
                      <span>Executable Test Runner Script ({displayLang})</span>
                      <button
                        className="btn btn-ghost"
                        onClick={handleCopyRunner}
                        style={{ padding: '3px 8px', fontSize: '0.72rem' }}
                      >
                        {copiedRunner ? (
                          <>
                            <Check size={12} style={{ color: '#34d399' }} />
                            <span>Copied</span>
                          </>
                        ) : (
                          <>
                            <Copy size={12} />
                            <span>Copy Runner Code</span>
                          </>
                        )}
                      </button>
                    </div>
                    <pre className="code-content">{testSuite.runner_code}</pre>
                  </div>
                )}

                {testSuite.browser_runbook && (
                  <div className="section-box">
                    <div className="section-box-title" style={{ color: '#38bdf8' }}>
                      <Globe size={13} />
                      <span>Browser Verification Runbook (MERN / Web Project)</span>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 14 }}>
                      <div style={{ background: 'rgba(0,0,0,0.3)', padding: '10px 12px', borderRadius: 8 }}>
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginBottom: 4 }}>Dev Server Command</div>
                        <code style={{ color: '#38bdf8' }}>{testSuite.browser_runbook.dev_command || 'npm run dev'}</code>
                      </div>
                      <div style={{ background: 'rgba(0,0,0,0.3)', padding: '10px 12px', borderRadius: 8 }}>
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginBottom: 4 }}>Browser Target URL</div>
                        <code style={{ color: '#a78bfa' }}>{testSuite.browser_runbook.browser_url || 'http://localhost:5173'}</code>
                      </div>
                    </div>

                    {testSuite.browser_runbook.steps && (
                      <div style={{ marginBottom: 14 }}>
                        <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: 6 }}>
                          Interactive Browser Verification Steps:
                        </div>
                        <ol style={{ paddingLeft: 18, display: 'flex', flexDirection: 'column', gap: 6, fontSize: '0.84rem' }}>
                          {testSuite.browser_runbook.steps.map((step, sIdx) => (
                            <li key={sIdx} style={{ color: '#e2e8f0' }}>{step}</li>
                          ))}
                        </ol>
                      </div>
                    )}

                    {testSuite.browser_runbook.expected_ui_behavior && (
                      <div style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.2)', padding: '10px 12px', borderRadius: 8, marginBottom: 10 }}>
                        <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#34d399', marginBottom: 2 }}>Expected Visual Behavior:</div>
                        <div style={{ fontSize: '0.82rem', color: '#e2e8f0' }}>{testSuite.browser_runbook.expected_ui_behavior}</div>
                      </div>
                    )}

                    {testSuite.browser_runbook.console_checklist && (
                      <div style={{ background: 'rgba(59, 130, 246, 0.08)', border: '1px solid rgba(59, 130, 246, 0.2)', padding: '10px 12px', borderRadius: 8 }}>
                        <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#60a5fa', marginBottom: 2 }}>DevTools Console Checklist:</div>
                        <div style={{ fontSize: '0.82rem', color: '#e2e8f0' }}>{testSuite.browser_runbook.console_checklist}</div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Tab: Bug Analysis */}
            {activeTab === 'bug' && (
              <div>
                <div className="meta-strip">
                  <span className={`badge ${severity}`}>
                    <AlertTriangle size={11} />
                    <span>Severity: {severity.toUpperCase()}</span>
                  </span>
                  <span className="badge low">
                    <span>Line: {lineNumber}</span>
                  </span>
                </div>

                <div className="section-box">
                  <div className="section-box-title">
                    <ShieldAlert size={12} />
                    <span>Compiler / Runtime Error Explanation ({displayLang})</span>
                  </div>
                  <p style={{ color: '#e2e8f0', fontSize: '0.85rem', lineHeight: 1.6 }}>
                    {bugExplanation}
                  </p>
                </div>
              </div>
            )}

            {/* Tab: Logic */}
            {activeTab === 'logic' && (
              <div className="section-box">
                <div className="section-box-title">
                  <Brain size={12} />
                  <span>Deduced Program Intent & Data Flow</span>
                </div>
                <div
                  style={{
                    color: '#e2e8f0',
                    fontSize: '0.85rem',
                    lineHeight: 1.6,
                    whiteSpace: 'pre-line',
                  }}
                >
                  {logic || 'No logic analysis recorded.'}
                </div>
              </div>
            )}

            {/* Tab: Raw Trace */}
            {activeTab === 'raw' && (
              <div className="code-display-box">
                <div className="code-display-header">
                  <span>Complete Multi-Agent Pipeline State Object</span>
                </div>
                <pre className="code-content" style={{ fontSize: '0.75rem' }}>
                  {JSON.stringify(results, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
