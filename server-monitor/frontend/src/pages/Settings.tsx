import React from 'react';
import { Settings as SettingsIcon } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  return (
    <div>
      <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <SettingsIcon size={24} style={{ color: 'var(--accent-primary)' }} />
        Platform Settings & Thresholds
      </h2>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3 className="card-title" style={{ marginBottom: '1rem' }}>Alert Threshold Configuration</h3>
        <div className="grid-2">
          <div>
            <label style={{ display: 'block', fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
              CPU Warning Threshold (%)
            </label>
            <input type="number" defaultValue={90} className="font-mono" style={{ width: '100%', padding: '0.5rem', borderRadius: 6, border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-primary)', color: 'var(--text-main)' }} />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
              RAM Warning Threshold (%)
            </label>
            <input type="number" defaultValue={90} className="font-mono" style={{ width: '100%', padding: '0.5rem', borderRadius: 6, border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-primary)', color: 'var(--text-main)' }} />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
              Disk Warning Threshold (%)
            </label>
            <input type="number" defaultValue={85} className="font-mono" style={{ width: '100%', padding: '0.5rem', borderRadius: 6, border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-primary)', color: 'var(--text-main)' }} />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
              CPU Temp Warning (°C)
            </label>
            <input type="number" defaultValue={80} className="font-mono" style={{ width: '100%', padding: '0.5rem', borderRadius: 6, border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-primary)', color: 'var(--text-main)' }} />
          </div>
        </div>
      </div>
    </div>
  );
};
