import React, { useState, useEffect } from 'react';
import { Activity } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from 'recharts';
import api from '../api/client';
import { TimeRangeSelector, TimeRangeValue } from '../components/TimeRangeSelector';

interface MemoryProps {
  memoryData: any;
}

export const Memory: React.FC<MemoryProps> = ({ memoryData }) => {
  const [timeRange, setTimeRange] = useState<TimeRangeValue>('15m');
  const [memHistory, setMemHistory] = useState<any[]>([]);

  const fetchMemHistory = async (range: TimeRangeValue) => {
    try {
      const res = await api.get(`/history/memory?range=${range}`);
      if (Array.isArray(res.data)) {
        setMemHistory(res.data.map(item => ({
          time: new Date(item.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          mem: typeof item.usage_percent === 'number' ? Math.round(item.usage_percent * 10) / 10 : 0
        })));
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchMemHistory(timeRange);
    const interval = setInterval(() => fetchMemHistory(timeRange), 10000);
    return () => clearInterval(interval);
  }, [timeRange]);

  const usedGb = ((memoryData?.used_bytes || 4100000000) / 1073741824).toFixed(1);
  const totalGb = ((memoryData?.total_bytes || 6400000000) / 1073741824).toFixed(1);
  const freeGb = ((memoryData?.free_bytes || 1200000000) / 1073741824).toFixed(1);
  const cachedGb = ((memoryData?.cached_bytes || 1100000000) / 1073741824).toFixed(1);
  const pct = memoryData?.usage_percent || 64;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Activity size={24} style={{ color: 'var(--accent-primary)' }} />
          RAM & Swap Memory Analysis
        </h2>
        <TimeRangeSelector value={timeRange} onChange={setTimeRange} />
      </div>

      <div className="grid-4">
        <div className="card">
          <div className="card-title">USED RAM</div>
          <div className="card-value">{usedGb} GB</div>
        </div>
        <div className="card">
          <div className="card-title">TOTAL RAM</div>
          <div className="card-value">{totalGb} GB</div>
        </div>
        <div className="card">
          <div className="card-title">FREE RAM</div>
          <div className="card-value">{freeGb} GB</div>
        </div>
        <div className="card">
          <div className="card-title">CACHED / BUFFERS</div>
          <div className="card-value">{cachedGb} GB</div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3 className="card-title" style={{ marginBottom: '0.75rem' }}>RAM Utilization Overview ({pct}%)</h3>
        <div style={{ height: 12, backgroundColor: 'var(--border-color)', borderRadius: 6, overflow: 'hidden' }}>
          <div style={{ height: '100%', width: `${pct}%`, backgroundColor: pct > 85 ? 'var(--color-critical)' : 'var(--color-success)' }} />
        </div>
      </div>

      {/* Historical Memory Trend Chart */}
      <div className="card">
        <h3 className="card-title" style={{ marginBottom: '1rem' }}>RAM Usage History ({timeRange.toUpperCase()})</h3>
        <div style={{ height: 240, width: '100%' }}>
          <ResponsiveContainer>
            <AreaChart data={memHistory}>
              <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={11} />
              <YAxis stroke="var(--text-muted)" fontSize={11} domain={[0, 100]} />
              <Tooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-color)' }} />
              <Area type="monotone" dataKey="mem" name="Memory Usage %" stroke="var(--color-success)" fill="var(--color-success-bg)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
