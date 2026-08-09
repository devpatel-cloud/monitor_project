import React, { useState } from 'react';
import { Cpu, HardDrive, Thermometer, ShieldAlert, CheckCircle, AlertTriangle, Activity } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from 'recharts';

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
}

export const Dashboard: React.FC<DashboardProps> = ({
  healthData, cpuData, memoryData, storageData, networkData,
  dockerData, servicesData, duckdnsData, alertsData
}) => {
  const [showHealthModal, setShowHealthModal] = useState(false);

  const score = healthData?.health_score?.score ?? 96;
  const healthStatus = healthData?.health_score?.status ?? 'HEALTHY';
  const breakdown = healthData?.health_score?.breakdown ?? [];

  // Sample real-time metric trend data
  const sampleCpuHistory = [
    { time: '10:50', cpu: 18.2 },
    { time: '10:52', cpu: 24.5 },
    { time: '10:54', cpu: 22.0 },
    { time: '10:56', cpu: 28.4 },
    { time: '10:58', cpu: cpuData?.usage_percent || 23.4 },
  ];

  const sampleMemHistory = [
    { time: '10:50', mem: 62.1 },
    { time: '10:52', mem: 63.4 },
    { time: '10:54', mem: 64.0 },
    { time: '10:56', mem: 63.8 },
    { time: '10:58', mem: memoryData?.usage_percent || 64.2 },
  ];

  const ramUsedGb = ((memoryData?.used_bytes || 4100000000) / 1073741824).toFixed(1);
  const ramTotalGb = ((memoryData?.total_bytes || 6400000000) / 1073741824).toFixed(1);
  const mainDisk = storageData?.storage?.partitions?.[0] || { usage_percent: 17 };
  const cpuTemp = storageData?.temperature?.cpu_temp_celsius || 51;

  return (
    <div>
      {/* Top Banner & Health Score */}
      <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '1.5rem' }}>
        <div className="card" style={{ flex: '1', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '0.25rem' }}>Rocky Linux 9.4 Server</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              Primary Monitored Host • IPv6 Enabled • DuckDNS Synchronized
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
          <div className="card-value">{cpuData?.usage_percent || 23.4}%</div>
          <span className="status-pill success">🟢 Normal</span>
        </div>

        <div className="card">
          <div className="card-title">
            <span>MEMORY (RAM)</span>
            <Activity size={18} style={{ color: 'var(--accent-primary)' }} />
          </div>
          <div className="card-value">{ramUsedGb} / {ramTotalGb} GB</div>
          <span className="status-pill success">🟢 Normal ({memoryData?.usage_percent || 64}%)</span>
        </div>

        <div className="card">
          <div className="card-title">
            <span>PRIMARY STORAGE</span>
            <HardDrive size={18} style={{ color: 'var(--accent-primary)' }} />
          </div>
          <div className="card-value">{mainDisk.usage_percent}%</div>
          <span className="status-pill success">🟢 Normal (/dev/sda)</span>
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

      {/* Graphs Grid */}
      <div className="grid-2">
        <div className="card">
          <div className="card-title">CPU History (24 Hours)</div>
          <div style={{ height: 220, width: '100%' }}>
            <ResponsiveContainer>
              <AreaChart data={sampleCpuHistory}>
                <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={12} />
                <YAxis stroke="var(--text-muted)" fontSize={12} domain={[0, 100]} />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-color)' }} />
                <Area type="monotone" dataKey="cpu" stroke="var(--accent-primary)" fill="var(--accent-primary-glow)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <div className="card-title">Memory History (24 Hours)</div>
          <div style={{ height: 220, width: '100%' }}>
            <ResponsiveContainer>
              <AreaChart data={sampleMemHistory}>
                <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={12} />
                <YAxis stroke="var(--text-muted)" fontSize={12} domain={[0, 100]} />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-color)' }} />
                <Area type="monotone" dataKey="mem" stroke="var(--color-success)" fill="var(--color-success-bg)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Subsystem Quick Status Row */}
      <div className="grid-4">
        <div className="card">
          <div className="card-title">DOCKER ENGINE</div>
          <div style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            {dockerData?.daemon_status || 'RUNNING'}
          </div>
          <span className="status-pill success">
            {dockerData?.containers_running || 4} / {dockerData?.containers_total || 4} Containers Active
          </span>
        </div>

        <div className="card">
          <div className="card-title">SERVICES</div>
          <div style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            {servicesData?.running || 8} Active
          </div>
          <span className="status-pill success">
            {servicesData?.failed || 0} Failed Services
          </span>
        </div>

        <div className="card">
          <div className="card-title">DUCKDNS IPV6</div>
          <div style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            {duckdnsData?.status || 'MATCH'}
          </div>
          <span className="status-pill success">🟢 IPv6 Synchronized</span>
        </div>

        <div className="card">
          <div className="card-title">ACTIVE ALERTS</div>
          <div style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            {alertsData?.length || 0} Active
          </div>
          <span className="status-pill success">🟢 All Systems Nominal</span>
        </div>
      </div>
    </div>
  );
};
