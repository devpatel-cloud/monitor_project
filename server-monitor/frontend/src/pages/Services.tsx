import React from 'react';
import { Server } from 'lucide-react';

interface ServicesProps {
  servicesData: any;
}

export const Services: React.FC<ServicesProps> = ({ servicesData }) => {
  const services = servicesData?.services || [
    { name: 'nginx', state: 'RUNNING', enabled: true },
    { name: 'docker', state: 'RUNNING', enabled: true },
    { name: 'sshd', state: 'RUNNING', enabled: true },
    { name: 'NetworkManager', state: 'RUNNING', enabled: true },
    { name: 'chronyd', state: 'RUNNING', enabled: true },
    { name: 'firewalld', state: 'RUNNING', enabled: true },
    { name: 'server-monitor', state: 'RUNNING', enabled: true },
    { name: 'duckdns-ipv6', state: 'RUNNING', enabled: true }
  ];

  return (
    <div>
      <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Server size={24} style={{ color: 'var(--accent-primary)' }} />
        Linux Systemd Services
      </h2>

      <div className="card">
        <h3 className="card-title" style={{ marginBottom: '1rem' }}>Monitored System Services</h3>
        <table className="custom-table">
          <thead>
            <tr>
              <th>Service Name</th>
              <th>Status</th>
              <th>Enabled on Boot</th>
            </tr>
          </thead>
          <tbody>
            {services.map((svc: any, idx: number) => (
              <tr key={idx}>
                <td className="font-mono" style={{ fontWeight: 600 }}>{svc.name}.service</td>
                <td>
                  <span className={`status-pill ${svc.state === 'RUNNING' ? 'success' : svc.state === 'FAILED' ? 'critical' : 'warning'}`}>
                    {svc.state === 'RUNNING' ? '🟢 RUNNING' : svc.state === 'FAILED' ? '🔴 FAILED' : '🟠 STOPPED'}
                  </span>
                </td>
                <td className="font-mono">{svc.enabled ? 'Yes (Enabled)' : 'No'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
