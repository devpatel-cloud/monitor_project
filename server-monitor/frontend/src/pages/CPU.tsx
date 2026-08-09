import React, { useState, useEffect } from 'react';
import { Cpu as CpuIcon } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from 'recharts';
import api from '../api/client';
import { TimeRangeSelector, TimeRangeValue } from '../components/TimeRangeSelector';

interface CPUProps {
  cpuData: any;
}

export const CPU: React.FC<CPUProps> = ({ cpuData }) => {
  const [timeRange, setTimeRange] = useState<TimeRangeValue>('15m');
  const [cpuHistory, setCpuHistory] = useState<any[]>([]);

  const fetchCpuHistory = async (range: TimeRangeValue) => {
    try {
      const res = await api.get(`/history/cpu?range=${range}`);
      if (Array.isArray(res.data)) {
        setCpuHistory(res.data.map(item => ({
          time: new Date(item.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          cpu: typeof item.usage_percent === 'number' ? Math.round(item.usage_percent * 10) / 10 : 0
        })));
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchCpuHistory(timeRange);
    const interval = setInterval(() => fetchCpuHistory(timeRange), 10000);
    return () => clearInterval(interval);
  }, [timeRange]);

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
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <CpuIcon size={24} style={{ color: 'var(--accent-primary)' }} />
          CPU Monitoring & Analysis
        </h2>
        <TimeRangeSelector value={timeRange} onChange={setTimeRange} />
      </div>

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

      {/* Historical Trend Graph */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3 className="card-title" style={{ marginBottom: '1rem' }}>CPU Utilization Trend ({timeRange.toUpperCase()})</h3>
        <div style={{ height: 240, width: '100%' }}>
          <ResponsiveContainer>
            <AreaChart data={cpuHistory}>
              <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={11} />
              <YAxis stroke="var(--text-muted)" fontSize={11} domain={[0, 100]} />
              <Tooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-color)' }} />
              <Area type="monotone" dataKey="cpu" name="CPU Usage %" stroke="var(--accent-primary)" fill="var(--accent-primary-glow)" />
            </AreaChart>
          </ResponsiveContainer>
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
