import React, { useState } from 'react';
import { Bell, AlertTriangle, CheckCircle, AlertOctagon, CheckSquare, Eye } from 'lucide-react';
import api from '../api/client';
import { getCurrentUserRole } from '../utils/auth';

interface AlertsProps {
  alertsData: any[];
  onRefreshAlerts?: () => void;
}

export const Alerts: React.FC<AlertsProps> = ({ alertsData, onRefreshAlerts }) => {
  const isAdmin = getCurrentUserRole() === 'admin';
  const [showHistory, setShowHistory] = useState(false);

  const handleAcknowledge = async (id: number) => {
    try {
      await api.post(`/alerts/${id}/acknowledge`);
      if (onRefreshAlerts) onRefreshAlerts();
    } catch (e) {
      console.error(e);
    }
  };

  const handleResolve = async (id: number) => {
    try {
      await api.post(`/alerts/${id}/resolve`);
      if (onRefreshAlerts) onRefreshAlerts();
    } catch (e) {
      console.error(e);
    }
  };

  const activeAlerts = alertsData.filter(a => !a.resolved && a.status !== 'RESOLVED');
  const historyAlerts = alertsData.filter(a => a.resolved || a.status === 'RESOLVED');
  const displayedAlerts = showHistory ? alertsData : activeAlerts;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Bell size={24} style={{ color: 'var(--accent-primary)' }} />
          System Alerts & Event Lifecycle
        </h2>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => setShowHistory(false)}
            className={`btn-icon ${!showHistory ? 'active' : ''}`}
            style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
          >
            Active Alerts ({activeAlerts.length})
          </button>
          <button
            onClick={() => setShowHistory(true)}
            className={`btn-icon ${showHistory ? 'active' : ''}`}
            style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
          >
            All History ({alertsData.length})
          </button>
        </div>
      </div>

      {/* Alerts List */}
      <div>
        {displayedAlerts.length === 0 ? (
          <div className="card" style={{ padding: '2.5rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            <CheckCircle size={42} style={{ color: 'var(--color-success)', marginBottom: '0.5rem' }} />
            <div style={{ fontSize: '1.1rem', fontWeight: 600 }}>No alerts to display.</div>
            <p style={{ fontSize: '0.9rem', marginTop: '0.25rem' }}>All server subsystems operating normally.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {displayedAlerts.map((alt: any) => {
              const isCrit = alt.severity === 'CRITICAL';
              const isResolved = alt.resolved || alt.status === 'RESOLVED';
              const isAck = alt.status === 'ACKNOWLEDGED';

              let borderColor = isCrit ? 'var(--color-critical)' : 'var(--color-warning)';
              if (isResolved) borderColor = 'var(--color-success)';
              else if (isAck) borderColor = 'var(--accent-primary)';

              return (
                <div
                  key={alt.id}
                  className="card"
                  style={{
                    borderLeft: `6px solid ${borderColor}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    {isResolved ? (
                      <CheckCircle size={24} style={{ color: 'var(--color-success)' }} />
                    ) : isCrit ? (
                      <AlertOctagon size={24} style={{ color: 'var(--color-critical)' }} />
                    ) : (
                      <AlertTriangle size={24} style={{ color: 'var(--color-warning)' }} />
                    )}
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                        <span className={`status-pill ${isResolved ? 'success' : isCrit ? 'critical' : 'warning'}`}>
                          {alt.severity}
                        </span>
                        <span className="status-pill" style={{ backgroundColor: isResolved ? 'var(--color-success-bg)' : isAck ? 'var(--accent-primary-glow)' : 'var(--color-critical-bg)', color: isResolved ? 'var(--color-success)' : isAck ? 'var(--accent-primary)' : 'var(--color-critical)' }}>
                          {alt.status}
                        </span>
                        <strong style={{ fontSize: '1.05rem' }}>{alt.title}</strong>
                      </div>
                      <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{alt.message}</p>

                      {alt.acknowledged_by && (
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                          Acknowledged by {alt.acknowledged_by}
                        </div>
                      )}
                    </div>
                  </div>

                  {!isResolved && (
                    <div style={{ display: 'flex', gap: '6px' }}>
                      {isAdmin && !isAck && (
                        <button onClick={() => handleAcknowledge(alt.id)} className="btn-icon" style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}>
                          <CheckSquare size={14} style={{ marginRight: 4 }} /> Acknowledge
                        </button>
                      )}
                      <button onClick={() => handleResolve(alt.id)} className="btn-icon" style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}>
                        Resolve
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
