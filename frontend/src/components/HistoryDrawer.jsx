import React from 'react';
import { X, History, ArrowRight, Code, Calendar } from 'lucide-react';

export default function HistoryDrawer({
  isOpen,
  onClose,
  sessions,
  onSelectSession,
}) {
  return (
    <>
      {/* Backdrop */}
      <div
        className={`drawer-backdrop ${isOpen ? 'open' : ''}`}
        onClick={onClose}
      />

      {/* Drawer */}
      <div className={`drawer ${isOpen ? 'open' : ''}`}>
        <div className="drawer-header">
          <div className="panel-title">
            <History size={17} style={{ color: '#8b5cf6' }} />
            <span>Session History</span>
            <span className="count-badge">{sessions.length}</span>
          </div>

          <button className="btn btn-ghost" onClick={onClose} title="Close History">
            <X size={16} />
          </button>
        </div>

        <div className="drawer-body">
          {sessions.length === 0 ? (
            <div className="empty-state" style={{ minHeight: 300 }}>
              <History size={32} style={{ color: 'var(--text-dim)', marginBottom: 12 }} />
              <div className="empty-title">No Saved Sessions</div>
              <div className="empty-desc">
                Your past debugging sessions will be recorded in the MySQL database and appear here.
              </div>
            </div>
          ) : (
            sessions.map((item) => (
              <div
                key={item.id}
                className="history-card"
                onClick={() => {
                  onSelectSession(item);
                  onClose();
                }}
                title="Click to load this code into editor"
              >
                <div className="history-card-top">
                  <span style={{ fontWeight: 600, color: '#60a5fa' }}>
                    Session #{item.id}
                  </span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <Calendar size={11} />
                    {item.created_at ? new Date(item.created_at).toLocaleDateString() : 'Recent'}
                  </span>
                </div>

                <div className="history-card-desc">
                  {item.error_description || 'Debugging session'}
                </div>

                <pre className="history-card-code">
                  {item.original_code ? item.original_code.slice(0, 100) : ''}
                </pre>
              </div>
            ))
          )}
        </div>
      </div>
    </>
  );
}
