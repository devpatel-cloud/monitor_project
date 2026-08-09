import React from 'react';
import { Shield } from 'lucide-react';

interface SecurityProps {
  securityData: any;
}

export const Security: React.FC<SecurityProps> = ({ securityData }) => {
  const fw = securityData?.firewalld || { status: 'RUNNING', active_zones: ['public (default)'] };
  const selinux = securityData?.selinux || { status: 'Enforcing', mode: 'enforcing' };
  const users = securityData?.logged_in_users || [
    { username: 'sanjaya', tty: 'pts/0', login_time: '2026-08-09 09:12', remote_host: '192.168.1.100' }
  ];
  const events = securityData?.events || { failed_ssh_24h: 3, successful_ssh_24h: 12, oom_events_24h: 0, recent_critical_errors: [] };

  return (
    <div>
      <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Shield size={24} style={{ color: 'var(--accent-primary)' }} />
        Security & Audit Dashboard
      </h2>

      <div className="grid-4">
        <div className="card">
          <div className="card-title">FIREWALLD STATUS</div>
          <div className="card-value" style={{ color: 'var(--color-success)' }}>
            {fw.status}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Zones: {fw.active_zones?.join(', ') || 'public'}</div>
        </div>

        <div className="card">
          <div className="card-title">SELINUX MODE</div>
          <div className="card-value" style={{ color: 'var(--color-success)' }}>
            {selinux.status}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Mode: {selinux.mode}</div>
        </div>

        <div className="card">
          <div className="card-title">FAILED SSH (24H)</div>
          <div className="card-value" style={{ color: events.failed_ssh_24h > 10 ? 'var(--color-critical)' : 'var(--text-main)' }}>
            {events.failed_ssh_24h}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Successful: {events.successful_ssh_24h}</div>
        </div>

        <div className="card">
          <div className="card-title">OOM EVENTS (24H)</div>
          <div className="card-value" style={{ color: 'var(--color-success)' }}>
            {events.oom_events_24h}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Kernel OOM killer alerts</div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3 className="card-title" style={{ marginBottom: '1rem' }}>Logged-In System Users</h3>
        <table className="custom-table">
          <thead>
            <tr>
              <th>Username</th>
              <th>Terminal</th>
              <th>Login Time</th>
              <th>Remote Host</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u: any, idx: number) => (
              <tr key={idx}>
                <td className="font-mono" style={{ fontWeight: 600 }}>{u.username}</td>
                <td className="font-mono">{u.tty || u.terminal}</td>
                <td className="font-mono">{u.login_time}</td>
                <td className="font-mono">{u.remote_host || u.ip}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
