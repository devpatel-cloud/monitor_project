import React from 'react';
import { Network as NetworkIcon, Wifi, Globe } from 'lucide-react';

interface NetworkProps {
  networkData: any;
  duckdnsData: any;
}

export const Network: React.FC<NetworkProps> = ({ networkData, duckdnsData }) => {
  const net = networkData?.network || {};
  const wifi = networkData?.wifi || {};
  const interfaces = net?.interfaces || [];
  const conn = net?.connectivity || { ipv4_online: true, ipv6_online: true, dns_resolution: true };

  return (
    <div>
      <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <NetworkIcon size={24} style={{ color: 'var(--accent-primary)' }} />
        Network & IPv6 / DuckDNS Status
      </h2>

      {/* IPv6 & DuckDNS Card */}
      <div className="grid-2">
        <div className="card">
          <h3 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Globe size={18} /> Connectivity Status
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>IPv4 Internet</div>
              <span className={`status-pill ${conn.ipv4_online ? 'success' : 'critical'}`}>
                {conn.ipv4_online ? '🟢 Connected' : '🔴 Offline'}
              </span>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>IPv6 Internet</div>
              <span className={`status-pill ${conn.ipv6_online ? 'success' : 'critical'}`}>
                {conn.ipv6_online ? '🟢 Connected' : '🔴 Offline'}
              </span>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>DuckDNS AAAA</div>
              <span className={`status-pill ${duckdnsData?.mismatch ? 'warning' : 'success'}`}>
                {duckdnsData?.mismatch ? '🟠 MISMATCH' : '🟢 MATCH'}
              </span>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>DNS Resolution</div>
              <span className={`status-pill ${conn.dns_resolution ? 'success' : 'critical'}`}>
                {conn.dns_resolution ? '🟢 Operational' : '🔴 Failure'}
              </span>
            </div>
          </div>
        </div>

        {/* Wi-Fi Card */}
        <div className="card">
          <h3 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Wifi size={18} /> Wi-Fi Connection
          </h3>
          <div style={{ marginTop: '1rem' }}>
            <div style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              SSID: {wifi.ssid || 'Unavailable'}
            </div>
            <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
              Signal Strength: {wifi.signal_percent || 0}% • Bitrate: {wifi.bitrate || 'N/A'}
            </div>
            <div style={{ height: 8, backgroundColor: 'var(--border-color)', borderRadius: 4, marginTop: '0.75rem', overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${wifi.signal_percent || 0}%`, backgroundColor: 'var(--accent-primary)' }} />
            </div>
          </div>
        </div>
      </div>

      {/* Network Interfaces Table */}
      <div className="card">
        <h3 className="card-title" style={{ marginBottom: '1rem' }}>Network Interfaces</h3>
        <table className="custom-table">
          <thead>
            <tr>
              <th>Interface</th>
              <th>State</th>
              <th>MAC Address</th>
              <th>IPv4 Address</th>
              <th>IPv6 Address</th>
              <th>RX / TX Bytes</th>
            </tr>
          </thead>
          <tbody>
            {interfaces.map((iface: any, idx: number) => (
              <tr key={idx}>
                <td className="font-mono" style={{ fontWeight: 600 }}>{iface.name}</td>
                <td>
                  <span className={`status-pill ${iface.state === 'UP' ? 'success' : 'critical'}`}>
                    {iface.state}
                  </span>
                </td>
                <td className="font-mono">{iface.mac}</td>
                <td className="font-mono">{iface.ipv4?.join(', ') || 'N/A'}</td>
                <td className="font-mono" style={{ fontSize: '0.8rem' }}>{iface.ipv6?.join(', ') || 'N/A'}</td>
                <td className="font-mono">
                  {(iface.rx_bytes / 1048576).toFixed(1)} MB / {(iface.tx_bytes / 1048576).toFixed(1)} MB
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
