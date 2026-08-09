import React from 'react';
import { Box } from 'lucide-react';

interface DockerProps {
  dockerData: any;
}

export const Docker: React.FC<DockerProps> = ({ dockerData }) => {
  const daemonStatus = dockerData?.daemon_status || 'RUNNING';
  const total = dockerData?.containers_total || 4;
  const running = dockerData?.containers_running || 4;
  const images = dockerData?.images_total || 12;
  const volumes = dockerData?.volumes_total || 5;

  const containers = dockerData?.containers || [
    { id: 'a1b2c3d4', name: 'frontend', image: 'server-monitor-frontend:latest', status: 'RUNNING', cpu_percent: 2.1, memory_used: '142 MB', memory_limit: '2.0 GB', network_rx: '1.2 MB', network_tx: '8.4 MB', restart_count: 0 },
    { id: 'e5f6g7h8', name: 'backend', image: 'server-monitor-backend:latest', status: 'RUNNING', cpu_percent: 4.3, memory_used: '220 MB', memory_limit: '2.0 GB', network_rx: '8.4 MB', network_tx: '12.1 MB', restart_count: 0 },
    { id: 'i9j0k1l2', name: 'sqlite-db', image: 'sqlite-volume:latest', status: 'RUNNING', cpu_percent: 1.2, memory_used: '310 MB', memory_limit: '4.0 GB', network_rx: '5.0 MB', network_tx: '5.0 MB', restart_count: 0 },
    { id: 'm3n4o5p6', name: 'nginx-proxy', image: 'nginx:alpine', status: 'RUNNING', cpu_percent: 0.4, memory_used: '28 MB', memory_limit: '1.0 GB', network_rx: '15.2 MB', network_tx: '18.9 MB', restart_count: 0 }
  ];

  return (
    <div>
      <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Box size={24} style={{ color: 'var(--accent-primary)' }} />
        Docker Containers & Infrastructure
      </h2>

      <div className="grid-4">
        <div className="card">
          <div className="card-title">DOCKER ENGINE</div>
          <div className="card-value" style={{ color: daemonStatus === 'RUNNING' ? 'var(--color-success)' : 'var(--color-critical)' }}>
            {daemonStatus}
          </div>
        </div>
        <div className="card">
          <div className="card-title">CONTAINERS</div>
          <div className="card-value">{running} / {total}</div>
        </div>
        <div className="card">
          <div className="card-title">IMAGES</div>
          <div className="card-value">{images}</div>
        </div>
        <div className="card">
          <div className="card-title">VOLUMES</div>
          <div className="card-value">{volumes}</div>
        </div>
      </div>

      <div className="card">
        <h3 className="card-title" style={{ marginBottom: '1rem' }}>Active Containers</h3>
        <table className="custom-table">
          <thead>
            <tr>
              <th>Container Name</th>
              <th>Image</th>
              <th>Status</th>
              <th>CPU %</th>
              <th>Memory Usage</th>
              <th>Net RX / TX</th>
            </tr>
          </thead>
          <tbody>
            {containers.map((c: any, idx: number) => (
              <tr key={idx}>
                <td className="font-mono" style={{ fontWeight: 600 }}>{c.name}</td>
                <td className="font-mono">{c.image}</td>
                <td>
                  <span className={`status-pill ${c.status === 'RUNNING' ? 'success' : 'critical'}`}>
                    🟢 {c.status}
                  </span>
                </td>
                <td className="font-mono">{c.cpu_percent}%</td>
                <td className="font-mono">{c.memory_used} / {c.memory_limit}</td>
                <td className="font-mono">{c.network_rx} / {c.network_tx}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
