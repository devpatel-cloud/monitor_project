import React from 'react';
import { BatteryCharging } from 'lucide-react';

interface BatteryProps {
  batteryData: any;
}

export const Battery: React.FC<BatteryProps> = ({ batteryData }) => {
  const status = batteryData?.status || 'Unavailable';
  const cap = batteryData?.capacity_percent || 0;
  const state = batteryData?.state || 'No Battery';
  const health = batteryData?.health || 'N/A';
  const power = batteryData?.power_draw_watts || 0.0;

  return (
    <div>
      <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <BatteryCharging size={24} style={{ color: 'var(--accent-primary)' }} />
        Power & Battery Subsystem
      </h2>

      <div className="grid-4">
        <div className="card">
          <div className="card-title">BATTERY HARDWARE</div>
          <div className="card-value" style={{ fontSize: '1.4rem' }}>{status}</div>
        </div>
        <div className="card">
          <div className="card-title">CHARGE PERCENTAGE</div>
          <div className="card-value">{status === 'Available' ? `${cap}%` : 'N/A'}</div>
        </div>
        <div className="card">
          <div className="card-title">POWER STATE</div>
          <div className="card-value" style={{ fontSize: '1.4rem' }}>{state}</div>
        </div>
        <div className="card">
          <div className="card-title">POWER DRAW</div>
          <div className="card-value">{power} W</div>
        </div>
      </div>
    </div>
  );
};
