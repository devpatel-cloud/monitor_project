import React from 'react';
import { Globe, CheckCircle2, AlertOctagon } from 'lucide-react';

interface DuckDNSProps {
  duckdnsData: any;
}

export const DuckDNS: React.FC<DuckDNSProps> = ({ duckdnsData }) => {
  const domain = duckdnsData?.domain || 'sanjaya-server.duckdns.org';
  const currentIp = duckdnsData?.current_ipv6 || '2402:a00:404:1234::1';
  const aaaaIp = duckdnsData?.duckdns_aaaa || '2402:a00:404:1234::1';
  const status = duckdnsData?.status || 'MATCH';
  const mismatch = duckdnsData?.mismatch || false;
  const serviceInstalled = duckdnsData?.service_installed ?? true;
  const scriptInstalled = duckdnsData?.script_installed ?? true;
  const lastSync = duckdnsData?.last_update_status || 'Synchronized';

  return (
    <div>
      <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Globe size={24} style={{ color: 'var(--accent-primary)' }} />
        DuckDNS & IPv6 Dynamic Synchronizer
      </h2>

      <div className="card" style={{ marginBottom: '1.5rem', borderColor: mismatch ? 'var(--color-warning)' : 'var(--border-color)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>{domain}</h3>
            <span className="font-mono" style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              duckdns-ipv6.service • /usr/local/bin/duckdns-ipv6.sh
            </span>
          </div>
          <span className={`status-pill ${mismatch ? 'warning' : 'success'}`} style={{ fontSize: '1rem', padding: '0.4rem 1rem' }}>
            {mismatch ? '🟠 MISMATCH' : '🟢 SYNCHRONIZED'}
          </span>
        </div>

        <div className="grid-2">
          <div style={{ padding: '1rem', backgroundColor: 'var(--bg-primary)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Local Host IPv6 Address</div>
            <div className="font-mono" style={{ fontSize: '1.1rem', fontWeight: 600, wordBreak: 'break-all' }}>{currentIp}</div>
          </div>

          <div style={{ padding: '1rem', backgroundColor: 'var(--bg-primary)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>DuckDNS Public AAAA Record</div>
            <div className="font-mono" style={{ fontSize: '1.1rem', fontWeight: 600, wordBreak: 'break-all' }}>{aaaaIp}</div>
          </div>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <h3 className="card-title">Systemd Service Integration</h3>
          <p style={{ marginTop: '0.5rem', color: 'var(--text-muted)' }}>
            duckdns-ipv6.service status: <strong style={{ color: 'var(--color-success)' }}>{serviceInstalled ? 'Installed & Active' : 'Not Found'}</strong>
          </p>
        </div>

        <div className="card">
          <h3 className="card-title">Last Synchronization Log</h3>
          <p className="font-mono" style={{ marginTop: '0.5rem', fontSize: '0.9rem' }}>
            {lastSync}
          </p>
        </div>
      </div>
    </div>
  );
};
