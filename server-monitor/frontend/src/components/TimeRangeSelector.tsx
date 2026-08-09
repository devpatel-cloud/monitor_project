import React from 'react';
import { Clock } from 'lucide-react';

export type TimeRangeValue = '15m' | '30m' | '1h' | '3h' | '6h' | '12h' | '24h';

interface TimeRangeSelectorProps {
  value: TimeRangeValue;
  onChange: (range: TimeRangeValue) => void;
}

export const TimeRangeSelector: React.FC<TimeRangeSelectorProps> = ({ value, onChange }) => {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
      <Clock size={16} style={{ color: 'var(--accent-primary)' }} />
      <span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Time Range:</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as TimeRangeValue)}
        style={{
          backgroundColor: 'var(--bg-secondary)',
          color: 'var(--text-main)',
          border: '1px solid var(--border-color)',
          borderRadius: '6px',
          padding: '0.35rem 0.65rem',
          fontSize: '0.85rem',
          fontWeight: 600,
          cursor: 'pointer',
          outline: 'none'
        }}
      >
        <option value="15m">15 Minutes</option>
        <option value="30m">30 Minutes</option>
        <option value="1h">1 Hour</option>
        <option value="3h">3 Hours</option>
        <option value="6h">6 Hours</option>
        <option value="12h">12 Hours</option>
        <option value="24h">24 Hours</option>
      </select>
    </div>
  );
};
