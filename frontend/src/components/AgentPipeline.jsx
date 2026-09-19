import React from 'react';
import {
  FolderGit2,
  Globe,
  Search,
  Brain,
  Wrench,
  CheckCircle2,
  Loader2,
  AlertCircle,
  FlaskConical,
} from 'lucide-react';

export default function AgentPipeline({ agentStates, pipelineStatus, mode = 'snippet' }) {
  const allAgents = [
    {
      id: 'RepoAnalyzer',
      name: 'Repo Scout',
      role: 'Architecture & Issue Map',
      icon: FolderGit2,
      color: '#ec4899',
      bgGlow: 'rgba(236, 72, 153, 0.15)',
      repoOnly: true,
    },
    {
      id: 'ContextProfiler',
      name: 'Context Profiler',
      role: 'Env & Language Detector',
      icon: Globe,
      color: '#06b6d4',
      bgGlow: 'rgba(6, 182, 212, 0.15)',
    },
    {
      id: 'SyntaxChecker',
      name: 'Compiler Auditor',
      role: 'Syntax & Contract Rules',
      icon: Search,
      color: '#3b82f6',
      bgGlow: 'rgba(59, 130, 246, 0.15)',
    },
    {
      id: 'LogicReasoner',
      name: 'Logic Reasoner',
      role: 'Intent & Architecture Flow',
      icon: Brain,
      color: '#8b5cf6',
      bgGlow: 'rgba(139, 92, 246, 0.15)',
    },
    {
      id: 'FixSuggester',
      name: 'Fix Architect',
      role: 'Cross-File Code Synthesis',
      icon: Wrench,
      color: '#10b981',
      bgGlow: 'rgba(16, 185, 129, 0.15)',
    },
    {
      id: 'TestHarness',
      name: 'Test & Verify',
      role: 'Build Runbook & Testcases',
      icon: FlaskConical,
      color: '#f59e0b',
      bgGlow: 'rgba(245, 158, 11, 0.15)',
    },
  ];

  const activeAgents = mode === 'repo' ? allAgents : allAgents.filter((a) => !a.repoOnly);

  return (
    <div className="pipeline-section">
      <div className="pipeline-header">
        <div className="pipeline-title">
          <span>
            {mode === 'repo' ? '6-Agent Repository Debug Pipeline' : '5-Agent Coordinated Pipeline'}
          </span>
        </div>
        <span
          className={`pipeline-badge ${
            pipelineStatus === 'running'
              ? 'active'
              : pipelineStatus === 'completed'
              ? 'completed'
              : 'idle'
          }`}
        >
          {pipelineStatus === 'running'
            ? 'Agents Streaming Live'
            : pipelineStatus === 'completed'
            ? 'Pipeline Verified'
            : 'Ready to Run'}
        </span>
      </div>

      <div className={mode === 'repo' ? 'agent-grid-6' : 'agent-grid-5'}>
        {activeAgents.map((agent) => {
          const state = agentStates[agent.id] || 'idle';
          const Icon = agent.icon;

          return (
            <div
              key={agent.id}
              className={`agent-card ${state}`}
            >
              <div className="agent-top">
                <div className="agent-identity">
                  <div
                    className="agent-icon"
                    style={{ background: agent.bgGlow, color: agent.color }}
                  >
                    <Icon size={13} />
                  </div>
                  <span className="agent-name">{agent.name}</span>
                </div>

                <div className={`agent-status-tag ${state}`}>
                  {state === 'running' && (
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                      <Loader2 size={10} style={{ animation: 'spin 1s linear infinite' }} />
                      Active
                    </span>
                  )}
                  {state === 'completed' && (
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                      <CheckCircle2 size={10} />
                      Done
                    </span>
                  )}
                  {state === 'error' && (
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, color: '#f87171' }}>
                      <AlertCircle size={10} />
                      Error
                    </span>
                  )}
                  {state === 'idle' && <span>Idle</span>}
                </div>
              </div>

              <div className="agent-desc">{agent.role}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
