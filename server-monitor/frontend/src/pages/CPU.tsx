import React from 'react';
import { Cpu as CpuIcon } from 'lucide-react';

interface CPUProps {
  cpuData: any;
}

export const CPU: React.FC<CPUProps> = ({ cpuData }) => {
  const model = cpuData?.model || '13th Gen Intel(R) Core(TM) i7-13700H';
  const cores = cpuData?.cores_physical || 8;
  const threads = cpuData?.threads || 14;
  const usage = cpuData?.usage_percent || 23.4;
  const load1 = cpuData?.load_1m || 0.45;
  const load5 = cpuData?.load_5m || 0.52;
  const load15 = cpuData?.load_15m || 0.48;
  const freq = cpuData?.frequency_mhz || 2400.0;
  const perCore = cpuData?.per_core_usage || [15.2, 28.1, 10.4, 42.0, 19.5, 33.1, 12.0, 24.5];

  return (
    <div>
      <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <CpuIcon size={24} style={{ color: 'var(--accent-primary)' }} />
        CPU Monitoring & Analysis
      </h2>

      <div className="grid-4">
        <div className="card">
          <div className="card-title">OVERALL CPU USAGE</div>
          <div className="card-value">{usage}%</div>
        </div>
        <div className="card">
          <div className="card-title">FREQUENCY</div>
          <div className="card-value">{freq} MHz</div>
        </div>
        <div className="card">
          <div className="card-title">CORES / THREADS</div>
          <div className="card-value">{cores} / {threads}</div>
        </div>
        <div className="card">
          <div className="card-title">LOAD AVERAGE (1/5/15m)</div>
          <div className="card-value" style={{ fontSize: '1.2rem' }}>{load1} / {load5} / {load15}</div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3 className="card-title">CPU Specifications</h3>
        <p className="font-mono" style={{ fontSize: '1.1rem', color: 'var(--text-main)' }}>{model}</p>
      </div>

      <div className="card">
        <h3 className="card-title" style={{ marginBottom: '1rem' }}>Per-Core Utilization</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
          {perCore.map((corePct: number, idx: number) => (
            <div key={idx} style={{ padding: '0.75rem', backgroundColor: 'var(--bg-primary)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Core {idx}</div>
              <div className="font-mono" style={{ fontSize: '1.3rem', fontWeight: 700 }}>{corePct}%</div>
              <div style={{ height: 6, width: '100%', backgroundColor: 'var(--border-color)', borderRadius: 3, marginTop: '0.5rem', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${corePct}%`, backgroundColor: corePct > 80 ? 'var(--color-critical)' : 'var(--accent-primary)' }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
