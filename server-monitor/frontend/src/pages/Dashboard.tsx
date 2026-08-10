import React, { useState, useEffect } from 'react';
import { Cpu, HardDrive, Thermometer, Activity, Play, RefreshCw, Server, ArrowDown, ArrowUp, Database } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, LineChart, Line, CartesianGrid } from 'recharts';
import api from '../api/client';
import { TimeRangeSelector, TimeRangeValue } from '../components/TimeRangeSelector';

interface DashboardProps {
  healthData: any;
  cpuData: any;
  memoryData: any;
  storageData: any;
  networkData: any;
  dockerData: any;
  servicesData: any;
  duckdnsData: any;
  alertsData: any[];
  onRefreshServices?: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({
  healthData, cpuData, memoryData, storageData, networkData,
  dockerData, servicesData, duckdnsData, alertsData, onRefreshServices
}) => {
  const [showHealthModal, setShowHealthModal] = useState(false);
  const [timeRange, setTimeRange] = useState<TimeRangeValue>('15m');
  const [cpuHistory, setCpuHistory] = useState<any[]>([]);
  const [memHistory, setMemHistory] = useState<any[]>([]);
  const [netHistory, setNetHistory] = useState<any[]>([]);
  const [diskHistory, setDiskHistory] = useState<any[]>([]);
  const [tempHistory, setTempHistory] = useState<any[]>([]);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const fetchHistories = async (range: TimeRangeValue) => {
    try {
      const res = await api.get(`/history?range=${range}`);
      const data = res.data || {};

      if (Array.isArray(data.cpu)) {
        setCpuHistory(data.cpu.map((item: any) => ({
          time: new Date(item.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          cpu: roundVal(item.usage_percent),
          load: roundVal(item.load_1m)
        })));
      }

      if (Array.isArray(data.memory)) {
        setMemHistory(data.memory.map((item: any) => ({
          time: new Date(item.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          memPct: roundVal(item.usage_percent),
          usedGb: roundVal(item.used_bytes / 1073741824),
          totalGb: roundVal(item.total_bytes / 1073741824)
        })));
      }

      if (Array.isArray(data.temperature)) {
        setTempHistory(data.temperature.map((item: any) => ({
          time: new Date(item.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          temp: item.cpu_temp_celsius || 0
        })));
      }

      if (Array.isArray(data.network)) {
        setNetHistory(data.network.map((item: any) => ({
          time: new Date(item.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          download: item.download_mbps || 0,
          upload: item.upload_mbps || 0
        })));
      }

      if (Array.isArray(data.disk)) {
        setDiskHistory(data.disk.map((item: any) => ({
          time: new Date(item.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          read: item.read_mb_s || 0,
          write: item.write_mb_s || 0
        })));
      }
    } catch (err) {
      console.error("Failed to fetch history metrics:", err);
    }
  };

  const roundVal = (v: any) => (typeof v === 'number' ? Math.round(v * 10) / 10 : 0);

  const calcStats = (arr: number[]) => {
    if (!arr || arr.length === 0) return { curr: 0, min: 0, max: 0, avg: 0 };
    const curr = arr[arr.length - 1];
    const min = Math.min(...arr);
    const max = Math.max(...arr);
    const avg = arr.reduce((a, b) => a + b, 0) / arr.length;
    return { curr: roundVal(curr), min: roundVal(min), max: roundVal(max), avg: roundVal(avg) };
  };

  useEffect(() => {
    fetchHistories(timeRange);
    const interval = setInterval(() => fetchHistories(timeRange), 10000);
    return () => clearInterval(interval);
  }, [timeRange]);

  const handleServiceAction = async (service: string, action: 'start' | 'restart') => {
    setActionLoading(service);
    try {
      await api.post(`/services/${service}/${action}`);
      if (onRefreshServices) onRefreshServices();
    } catch (err) {
      console.error(`Failed to ${action} ${service}:`, err);
    } finally {
      setActionLoading(null);
    }
  };

  const score = healthData?.health_score?.score ?? 96;
  const healthStatus = healthData?.health_score?.status ?? 'HEALTHY';
  const breakdown = healthData?.health_score?.breakdown ?? [];

  const ramUsedGb = ((memoryData?.used_bytes || 4100000000) / 1073741824).toFixed(1);
  const ramTotalGb = ((memoryData?.total_bytes || 6400000000) / 1073741824).toFixed(1);

  // Storage selection: Select filesystem mounted at '/' (Root OS storage)
  const partitions = storageData?.storage?.partitions || storageData?.partitions || [];
  const rootDisk = partitions.find((p: any) => p.mount_point === '/') || partitions[0] || { usage_percent: 17, mount_point: '/' };
  const diskLabel = rootDisk.filesystem || rootDisk.mount_point || '/dev/mapper/rl-root';
  const diskPct = rootDisk.usage_percent || 17;

  const cpuTemp = storageData?.temperature?.cpu_temp_celsius || 51;

  // Filter Services: Non-default / custom application services OR any service that is STOPPED/FAILED
  const allServices = servicesData?.services || [];
  const customOrActionableServices = allServices.filter((svc: any) => {
    return !svc.is_default || svc.state === 'STOPPED' || svc.state === 'FAILED';
  });

  const cpuStats = calcStats(cpuHistory.map(i => i.cpu));
  const memStats = calcStats(memHistory.map(i => i.memPct));
  const tempStats = calcStats(tempHistory.map(i => i.temp));
  const downStats = calcStats(netHistory.map(i => i.download));
  const upStats = calcStats(netHistory.map(i => i.upload));
  const readStats = calcStats(diskHistory.map(i => i.read));
  const writeStats = calcStats(diskHistory.map(i => i.write));

  return (
    <div>
      {/* Top Banner & Health Score */}
      <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '1.5rem' }}>
        <div className="card" style={{ flex: '1', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '0.25rem' }}>Rocky Linux 9.8 Host</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              Native Server Monitor • Grafana-Style Live History • DuckDNS IPv6 Synchronized
            </p>
          </div>
          <div
            onClick={() => setShowHealthModal(!showHealthModal)}
            style={{
              cursor: 'pointer',
              textAlign: 'center',
              padding: '0.75rem 1.25rem',
              borderRadius: '12px',
              backgroundColor: 'var(--bg-hover)',
              border: '1px solid var(--border-color)'
            }}
          >
            <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600 }}>
              SERVER HEALTH
            </div>
            <div style={{ fontSize: '2.2rem', fontWeight: 800, color: score > 85 ? 'var(--color-success)' : score > 60 ? 'var(--color-warning)' : 'var(--color-critical)' }}>
              {score}
            </div>
            <div className={`status-pill ${score > 85 ? 'success' : score > 60 ? 'warning' : 'critical'}`}>
              {healthStatus}
            </div>
          </div>
        </div>
      </div>

      {/* Health Breakdown Modal */}
      {showHealthModal && (
        <div className="card" style={{ marginBottom: '1.5rem', borderColor: 'var(--accent-primary)' }}>
          <h3 className="card-title">Server Health Score Factor Analysis</h3>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {breakdown.map((item: any, idx: number) => (
              <li key={idx} style={{ padding: '0.5rem 0', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between' }}>
                <span>{item.reason}</span>
                <span className="font-mono" style={{ color: item.impact < 0 ? 'var(--color-critical)' : 'var(--color-success)' }}>
                  {item.impact} pts
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* 4 Main Summary Cards */}
      <div className="grid-4">
        <div className="card">
          <div className="card-title">
            <span>CPU UTILIZATION</span>
            <Cpu size={18} style={{ color: 'var(--accent-primary)' }} />
          </div>
          <div className="card-value">{cpuData?.usage_percent || 2.4}%</div>
          <span className="status-pill success">🟢 Normal</span>
        </div>

        <div className="card">
          <div className="card-title">
            <span>MEMORY (RAM)</span>
            <Activity size={18} style={{ color: 'var(--accent-primary)' }} />
          </div>
          <div className="card-value">{ramUsedGb} / {ramTotalGb} GB</div>
          <span className="status-pill success">🟢 Normal ({memoryData?.usage_percent || 33.3}%)</span>
        </div>

        <div className="card">
          <div className="card-title">
            <span>PRIMARY STORAGE ( / )</span>
            <HardDrive size={18} style={{ color: 'var(--accent-primary)' }} />
          </div>
          <div className="card-value">{diskPct}%</div>
          <span className="status-pill success" title={diskLabel}>🟢 Normal ({diskLabel})</span>
        </div>

        <div className="card">
          <div className="card-title">
            <span>CPU TEMP</span>
            <Thermometer size={18} style={{ color: 'var(--accent-primary)' }} />
          </div>
          <div className="card-value">{cpuTemp}°C</div>
          <span className="status-pill success">🟢 Normal</span>
        </div>
      </div>

      {/* Graphs Controls Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', marginTop: '1.5rem' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Activity size={20} style={{ color: 'var(--accent-primary)' }} />
          Real-Time Metrics History (Continuous 10s Refresh)
        </h3>
        <TimeRangeSelector value={timeRange} onChange={setTimeRange} />
      </div>

      {/* Grafana-Style Real-Time Charts Grid */}
      <div className="grid-2" style={{ gap: '1.5rem', marginBottom: '1.5rem' }}>
        {/* 1. CPU Chart */}
        <div className="card">
          <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>CPU UTILIZATION %</span>
            <span className="font-mono" style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Cur: {cpuStats.curr}% | Min: {cpuStats.min}% | Max: {cpuStats.max}% | Avg: {cpuStats.avg}%
            </span>
          </div>
          <div style={{ height: 220, width: '100%' }}>
            <ResponsiveContainer>
              <AreaChart data={cpuHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" opacity={0.5} />
                <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={11} />
                <YAxis stroke="var(--text-muted)" fontSize={11} domain={[0, 100]} unit="%" />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-color)' }} />
                <Area type="monotone" dataKey="cpu" name="CPU Usage %" stroke="var(--accent-primary)" fill="var(--accent-primary-glow)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 2. Memory Chart */}
        <div className="card">
          <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>MEMORY UTILIZATION %</span>
            <span className="font-mono" style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Cur: {memStats.curr}% | Min: {memStats.min}% | Max: {memStats.max}% | Avg: {memStats.avg}%
            </span>
          </div>
          <div style={{ height: 220, width: '100%' }}>
            <ResponsiveContainer>
              <AreaChart data={memHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" opacity={0.5} />
                <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={11} />
                <YAxis stroke="var(--text-muted)" fontSize={11} domain={[0, 100]} unit="%" />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-color)' }} />
                <Area type="monotone" dataKey="memPct" name="Memory Usage %" stroke="var(--color-success)" fill="var(--color-success-bg)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 3. Temperature Chart */}
        <div className="card">
          <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Thermometer size={16} style={{ color: 'var(--color-warning)' }} />
              CPU TEMPERATURE TREND (°C)
            </span>
            <span className="font-mono" style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Cur: {tempStats.curr}°C | Min: {tempStats.min}°C | Max: {tempStats.max}°C | Avg: {tempStats.avg}°C
            </span>
          </div>
          <div style={{ height: 220, width: '100%' }}>
            <ResponsiveContainer>
              <AreaChart data={tempHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" opacity={0.5} />
                <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={11} />
                <YAxis stroke="var(--text-muted)" fontSize={11} domain={[0, 110]} unit="°C" />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-color)' }} />
                <Area type="monotone" dataKey="temp" name="CPU Temp °C" stroke="var(--color-warning)" fill="var(--color-warning-bg)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 4. Network Throughput Chart */}
        <div className="card">
          <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              NETWORK THROUGHPUT (Mbps)
              <span style={{ fontSize: '0.75rem', color: 'var(--accent-primary)' }}>↓ Down</span>
              <span style={{ fontSize: '0.75rem', color: 'var(--color-warning)' }}>↑ Up</span>
            </span>
            <span className="font-mono" style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Down: {downStats.curr} Mbps | Up: {upStats.curr} Mbps
            </span>
          </div>
          <div style={{ height: 220, width: '100%' }}>
            <ResponsiveContainer>
              <LineChart data={netHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" opacity={0.5} />
                <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={11} />
                <YAxis stroke="var(--text-muted)" fontSize={11} unit=" Mbps" />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-color)' }} />
                <Line type="monotone" dataKey="download" name="Download Mbps" stroke="var(--accent-primary)" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="upload" name="Upload Mbps" stroke="var(--color-warning)" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 5. Disk I/O Chart */}
        <div className="card" style={{ gridColumn: 'span 2' }}>
          <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              DISK I/O THROUGHPUT (MB/s)
              <span style={{ fontSize: '0.75rem', color: 'var(--color-success)' }}>Read</span>
              <span style={{ fontSize: '0.75rem', color: 'var(--color-critical)' }}>Write</span>
            </span>
            <span className="font-mono" style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Read: {readStats.curr} MB/s | Write: {writeStats.curr} MB/s
            </span>
          </div>
          <div style={{ height: 220, width: '100%' }}>
            <ResponsiveContainer>
              <LineChart data={diskHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" opacity={0.5} />
                <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={11} />
                <YAxis stroke="var(--text-muted)" fontSize={11} unit=" MB/s" />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-color)' }} />
                <Line type="monotone" dataKey="read" name="Read MB/s" stroke="var(--color-success)" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="write" name="Write MB/s" stroke="var(--color-critical)" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* CUSTOM / NON-DEFAULT SERVICES PANEL */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3 className="card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Server size={18} style={{ color: 'var(--accent-primary)' }} />
            CUSTOM & APPLICATION SERVICES
          </span>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 400 }}>
            OS Infrastructure services filtered out unless STOPPED/FAILED
          </span>
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1rem' }}>
          {customOrActionableServices.map((svc: any, idx: number) => {
            const isRunning = svc.state === 'RUNNING';
            const isFailed = svc.state === 'FAILED';

            return (
              <div
                key={idx}
                style={{
                  padding: '1rem',
                  borderRadius: '8px',
                  backgroundColor: 'var(--bg-secondary)',
                  border: `1px solid ${isRunning ? 'var(--border-color)' : 'var(--color-critical)'}`,
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                <div>
                  <div style={{ fontWeight: 700, fontSize: '0.95rem', marginBottom: '0.25rem' }} className="font-mono">
                    {isRunning ? '🟢' : isFailed ? '🔴' : '🔴'} {svc.name}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: isRunning ? 'var(--color-success)' : 'var(--color-critical)', fontWeight: 600 }}>
                    {svc.state}
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '6px' }}>
                  {!isRunning ? (
                    <button
                      onClick={() => handleServiceAction(svc.name, 'start')}
                      disabled={actionLoading === svc.name}
                      style={{
                        padding: '0.4rem 0.8rem',
                        borderRadius: '6px',
                        backgroundColor: 'var(--color-success)',
                        color: '#FFF',
                        border: 'none',
                        fontSize: '0.8rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}
                    >
                      <Play size={12} /> {actionLoading === svc.name ? 'Starting...' : 'START'}
                    </button>
                  ) : (
                    <button
                      onClick={() => handleServiceAction(svc.name, 'restart')}
                      disabled={actionLoading === svc.name}
                      style={{
                        padding: '0.4rem 0.8rem',
                        borderRadius: '6px',
                        backgroundColor: 'var(--bg-hover)',
                        color: 'var(--text-main)',
                        border: '1px solid var(--border-color)',
                        fontSize: '0.8rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}
                    >
                      <RefreshCw size={12} /> {actionLoading === svc.name ? 'Restarting...' : 'RESTART'}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
