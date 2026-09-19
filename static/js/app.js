/**
 * Fixie AI Code Debugger - Frontend Interactive Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const codeEditor = document.getElementById('code-editor');
  const lineNumbers = document.getElementById('line-numbers');
  const lineCountEl = document.getElementById('line-count');
  const charCountEl = document.getElementById('char-count');
  const exampleSelect = document.getElementById('example-select');
  const clearBtn = document.getElementById('clear-btn');
  const debugBtn = document.getElementById('debug-btn');
  const debugSpinner = document.getElementById('debug-spinner');
  const debugIcon = document.getElementById('debug-icon');
  const debugLabel = document.getElementById('debug-label');

  // Status Elements
  const geminiStatus = document.getElementById('gemini-status');
  const mysqlStatus = document.getElementById('mysql-status');
  const pipelineStatusText = document.getElementById('pipeline-status-text');

  // Agent Cards & States
  const cardSyntax = document.getElementById('card-syntax');
  const stateSyntax = document.getElementById('state-syntax');
  const cardLogic = document.getElementById('card-logic');
  const stateLogic = document.getElementById('state-logic');
  const cardFixer = document.getElementById('card-fixer');
  const stateFixer = document.getElementById('state-fixer');

  // Results Viewport
  const emptyState = document.getElementById('empty-state');
  const resultsContent = document.getElementById('results-content');
  const badgeSeverity = document.getElementById('badge-severity');
  const badgeLine = document.getElementById('badge-line');
  const confidenceBar = document.getElementById('confidence-bar');
  const confidenceValue = document.getElementById('confidence-value');
  const bugDescription = document.getElementById('bug-description');
  const intendedLogic = document.getElementById('intended-logic');
  const fixExplanation = document.getElementById('fix-explanation');
  const suggestedFixCode = document.getElementById('suggested-fix-code');
  const copyFixBtn = document.getElementById('copy-fix-btn');
  const dbSyncBadge = document.getElementById('db-sync-badge');
  const syncSessionId = document.getElementById('sync-session-id');

  // History Drawer
  const openHistoryBtn = document.getElementById('open-history-btn');
  const closeHistoryBtn = document.getElementById('close-history-btn');
  const historyDrawer = document.getElementById('history-drawer');
  const drawerBackdrop = document.getElementById('drawer-backdrop');
  const historyList = document.getElementById('history-list');
  const sessionCountBadge = document.getElementById('session-count-badge');
  const toastContainer = document.getElementById('toast-container');

  let currentExamples = [];
  let isDebugging = false;

  // =========================================================================
  // Editor Utilities (Line Numbers & Stats)
  // =========================================================================
  function updateEditorStats() {
    const text = codeEditor.value;
    const lines = text.split('\n');
    const count = lines.length;
    
    // Update line number gutter
    let numbersHtml = '';
    for (let i = 1; i <= count; i++) {
      numbersHtml += `<div>${i}</div>`;
    }
    lineNumbers.innerHTML = numbersHtml;

    // Update stats
    lineCountEl.textContent = `${count} lines`;
    charCountEl.textContent = `${text.length} chars`;
  }

  codeEditor.addEventListener('input', updateEditorStats);
  codeEditor.addEventListener('scroll', () => {
    lineNumbers.scrollTop = codeEditor.scrollTop;
  });

  // Support Tab key inside textarea
  codeEditor.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const start = codeEditor.selectionStart;
      const end = codeEditor.selectionEnd;
      codeEditor.value = codeEditor.value.substring(0, start) + '    ' + codeEditor.value.substring(end);
      codeEditor.selectionStart = codeEditor.selectionEnd = start + 4;
      updateEditorStats();
    }
  });

  clearBtn.addEventListener('click', () => {
    codeEditor.value = '';
    updateEditorStats();
    resetResults();
  });

  // =========================================================================
  // Health & System Status Polling
  // =========================================================================
  async function checkHealth() {
    try {
      const res = await fetch('/api/health');
      const data = await res.json();

      // Update Gemini Indicator
      const geminiDot = geminiStatus.querySelector('.dot');
      if (data.gemini && data.gemini.available) {
        geminiDot.className = 'dot green';
        geminiStatus.title = data.gemini.message || 'Gemini API is ready';
      } else {
        geminiDot.className = 'dot red';
        geminiStatus.title = (data.gemini && data.gemini.message) || 'Gemini API key is not configured in .env';
      }

      // Update MySQL Indicator
      const mysqlDot = mysqlStatus.querySelector('.dot');
      if (data.mysql && data.mysql.connected) {
        mysqlDot.className = 'dot green';
        mysqlStatus.title = data.mysql.message || 'MySQL connected';
      } else {
        mysqlDot.className = 'dot red';
        mysqlStatus.title = data.mysql.message || 'MySQL disconnected';
      }
    } catch (err) {
      console.warn('Health check failed:', err);
    }
  }

  // =========================================================================
  // Load Examples
  // =========================================================================
  async function loadExamples() {
    try {
      const res = await fetch('/api/examples');
      const data = await res.json();
      currentExamples = data.examples || [];

      exampleSelect.innerHTML = '<option value="" disabled selected>Select preset...</option>';
      currentExamples.forEach((ex, idx) => {
        const opt = document.createElement('option');
        opt.value = idx;
        opt.textContent = ex.title;
        exampleSelect.appendChild(opt);
      });

      // Default to first example
      if (currentExamples.length > 0 && !codeEditor.value) {
        codeEditor.value = currentExamples[0].code;
        exampleSelect.value = 0;
        updateEditorStats();
      }
    } catch (err) {
      console.warn('Failed to load examples:', err);
    }
  }

  exampleSelect.addEventListener('change', (e) => {
    const idx = parseInt(e.target.value, 10);
    if (!isNaN(idx) && currentExamples[idx]) {
      codeEditor.value = currentExamples[idx].code;
      updateEditorStats();
      showToast(`Loaded: ${currentExamples[idx].title}`);
    }
  });

  // =========================================================================
  // Multi-Agent Pipeline & Debug Execution
  // =========================================================================
  function setAgentState(card, stateEl, state, text) {
    card.className = `agent-card ${state}`;
    stateEl.className = `agent-state ${state}`;
    stateEl.textContent = text;
  }

  function resetAgentPipeline() {
    setAgentState(cardSyntax, stateSyntax, 'idle', 'Idle');
    setAgentState(cardLogic, stateLogic, 'idle', 'Idle');
    setAgentState(cardFixer, stateFixer, 'idle', 'Idle');
    pipelineStatusText.className = 'pipeline-status';
    pipelineStatusText.textContent = 'Ready';
  }

  function resetResults() {
    emptyState.classList.remove('hidden');
    resultsContent.classList.add('hidden');
    dbSyncBadge.classList.add('hidden');
    resetAgentPipeline();
  }

  debugBtn.addEventListener('click', async () => {
    const code = codeEditor.value.trim();
    if (!code) {
      showToast('Please enter Python code to debug.', 'error');
      return;
    }

    if (isDebugging) return;
    isDebugging = true;

    // UI Loading State
    debugBtn.disabled = true;
    debugSpinner.classList.remove('hidden');
    debugIcon.classList.add('hidden');
    debugLabel.textContent = 'Debugging...';
    pipelineStatusText.className = 'pipeline-status running';
    pipelineStatusText.textContent = 'Running Agents...';

    // Step 1: Active SyntaxChecker
    setAgentState(cardSyntax, stateSyntax, 'active', 'Scanning');
    setAgentState(cardLogic, stateLogic, 'idle', 'Waiting');
    setAgentState(cardFixer, stateFixer, 'idle', 'Waiting');

    const agentTimer1 = setTimeout(() => {
      setAgentState(cardSyntax, stateSyntax, 'completed', 'Done');
      setAgentState(cardLogic, stateLogic, 'active', 'Reasoning');
    }, 1500);

    const agentTimer2 = setTimeout(() => {
      setAgentState(cardLogic, stateLogic, 'completed', 'Done');
      setAgentState(cardFixer, stateFixer, 'active', 'Fixing');
    }, 3500);

    try {
      const res = await fetch('/api/debug', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code, language: 'python' })
      });

      clearTimeout(agentTimer1);
      clearTimeout(agentTimer2);

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Debug request failed');
      }

      const data = await res.json();
      displayResults(data);
      showToast('Debugging analysis complete!', 'success');

      // Refresh session count
      loadHistory();
    } catch (err) {
      console.error(err);
      showToast(`Error: ${err.message}`, 'error');
      resetAgentPipeline();
    } finally {
      isDebugging = false;
      debugBtn.disabled = false;
      debugSpinner.classList.add('hidden');
      debugIcon.classList.remove('hidden');
      debugLabel.textContent = 'Analyze & Debug Code';
    }
  });

  function displayResults(data) {
    // Set all agents completed
    setAgentState(cardSyntax, stateSyntax, 'completed', 'Done');
    setAgentState(cardLogic, stateLogic, 'completed', 'Done');
    setAgentState(cardFixer, stateFixer, 'completed', 'Done');
    pipelineStatusText.className = 'pipeline-status';
    pipelineStatusText.textContent = 'Complete';

    const syntax = data.syntax_report || {};
    const fix = data.fix || {};
    const logic = data.logic || 'No specific logic summary provided.';

    // Severity
    const severity = (syntax.severity || 'low').toLowerCase();
    badgeSeverity.className = `severity-badge ${severity}`;
    badgeSeverity.textContent = `${severity.toUpperCase()} SEVERITY`;

    // Line Number
    const lineNum = syntax.line_number || 'N/A';
    badgeLine.textContent = `Line ${lineNum}`;

    // Confidence
    const confVal = fix.confidence !== undefined ? fix.confidence : 0.85;
    const confPercent = Math.round(confVal <= 1 ? confVal * 100 : confVal);
    confidenceBar.style.width = `${confPercent}%`;
    confidenceValue.textContent = `${confPercent}%`;

    // Descriptions
    bugDescription.textContent = syntax.bug_explanation || 'No syntax errors detected.';
    intendedLogic.textContent = logic.replace(/^-\s*intended\s*Logic:\s*/i, '').trim();

    // Fix Content
    fixExplanation.textContent = fix.explanation || 'No fix explanation available.';
    const fixCode = fix.fix || '# No fix could be generated.';
    suggestedFixCode.textContent = fixCode;

    // MySQL Saved Badge
    if (data.db_saved && data.session_id) {
      syncSessionId.textContent = data.session_id;
      dbSyncBadge.classList.remove('hidden');
    } else {
      dbSyncBadge.classList.add('hidden');
    }

    // Show results section
    emptyState.classList.add('hidden');
    resultsContent.classList.remove('hidden');
  }

  // =========================================================================
  // Copy Patch Button
  // =========================================================================
  copyFixBtn.addEventListener('click', async () => {
    const code = suggestedFixCode.textContent;
    try {
      await navigator.clipboard.writeText(code);
      showToast('Patch copied to clipboard!', 'success');
      copyFixBtn.innerHTML = '<span class="copy-icon">✅</span> Copied!';
      setTimeout(() => {
        copyFixBtn.innerHTML = '<span class="copy-icon">📋</span> Copy Patch';
      }, 2000);
    } catch (err) {
      showToast('Failed to copy patch to clipboard', 'error');
    }
  });

  // =========================================================================
  // MySQL Session History
  // =========================================================================
  async function loadHistory() {
    try {
      const res = await fetch('/api/sessions');
      const data = await res.json();
      const sessions = data.sessions || [];

      sessionCountBadge.textContent = sessions.length;

      if (sessions.length === 0) {
        historyList.innerHTML = '<div class="loading-history">No past debugging sessions found.</div>';
        return;
      }

      historyList.innerHTML = '';
      sessions.forEach(sess => {
        const item = document.createElement('div');
        item.className = 'history-item';
        
        const dateStr = sess.created_at ? new Date(sess.created_at).toLocaleString() : 'Recent';
        const errorText = sess.error_description || 'No error description';

        item.innerHTML = `
          <div class="item-top">
            <span class="item-id">Session #${sess.id}</span>
            <span class="item-date">${dateStr}</span>
          </div>
          <div class="item-error">${escapeHtml(errorText)}</div>
          <div class="item-footer">
            <span>${sess.language || 'python'}</span>
            <span>Click to load ➔</span>
          </div>
        `;

        item.addEventListener('click', () => {
          codeEditor.value = sess.original_code;
          updateEditorStats();
          closeDrawer();
          showToast(`Loaded code from Session #${sess.id}`);
        });

        historyList.appendChild(item);
      });
    } catch (err) {
      console.warn('Failed to load sessions:', err);
      historyList.innerHTML = '<div class="loading-history">Error loading MySQL sessions.</div>';
    }
  }

  function openDrawer() {
    historyDrawer.classList.add('open');
    drawerBackdrop.classList.add('open');
    loadHistory();
  }

  function closeDrawer() {
    historyDrawer.classList.remove('open');
    drawerBackdrop.classList.remove('open');
  }

  openHistoryBtn.addEventListener('click', openDrawer);
  closeHistoryBtn.addEventListener('click', closeDrawer);
  drawerBackdrop.addEventListener('click', closeDrawer);

  // =========================================================================
  // Toast Helper
  // =========================================================================
  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(20px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3200);
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Initial Boot
  updateEditorStats();
  checkHealth();
  loadExamples();
  loadHistory();
  setInterval(checkHealth, 15000);
});
