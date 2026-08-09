import React from 'react';
import { Bell, AlertTriangle, CheckCircle, AlertOctagon } from 'lucide-react';
import api from '../api/client';

interface AlertsProps {
  alertsData: any[];
  onRefreshAlerts?: () => void;
}

export const Alerts: React.FC<AlertsProps> = ({ alertsData, onRefreshAlerts }) => {
  const handleResolve = async (id: number) => {
    try {
      await api.post(`/alerts/${id}/resolve`);
      if (onRefreshAlerts) onRefreshAlerts();
    } catch (e) {
      console.error(e);
    }
  };

  const activeAlerts = alertsData.filter(a => !a.resolved);
  const resolvedAlerts = alertsData.filter(a => a.resolved);

  return (
    <div>
      <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Bell size={24} style={{ color: 'var(--accent-primary)' }} />
        Active System Alerts & Event Log
      </h2>

      {/* Active Alerts List */}
      <div style={{ marginBottom: '2rem' }}>
        <h3 className="card-title" style={{ marginBottom: '1rem' }}>Active Unresolved Alerts ({activeAlerts.length})</h3>

        {activeAlerts.length === 0 ? (
          <div className="card" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            <CheckCircle size={36} style={{ color: 'var(--color-success)', marginBottom: '0.5rem' }} />
            <div>No active alerts. All server subsystems operating normally.</div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {activeAlerts.map((alt: any) => {
              const isCrit = alt.severity === 'CRITICAL';
              return (
                <div
                  key={alt.id}
                  className="card"
                  style={{
                    borderLeft: `6px solid ${isCrit ? 'var(--color-critical)' : 'var(--color-warning)'}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    {isCrit ? (
                      <AlertOctagon size={24} style={{ color: 'var(--color-critical)' }} />
                    ) : (
                      <AlertTriangle size={24} style={{ color: 'var(--color-warning)' }} />
                    )}
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                        <span className={`status-pill ${isCrit ? 'critical' : 'warning'}`}>
                          {alt.severity}
                        </span>
                        <strong style={{ fontSize: '1.05rem' }}>{alt.title}</strong>
                      </div>
                      <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{alt.message}</p>
                    </div>
                  </div>
                  <button onClick={() => handleResolve(alt.id)} className="btn-icon">
                    Acknowledge & Resolve
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
