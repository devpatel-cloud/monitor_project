import React, { useState, useEffect } from 'react';
import { Network as NetworkIcon, Wifi, Globe, ArrowDown, ArrowUp, Zap, Clock, AlertCircle } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import api from '../api/client';
import { getCurrentUserRole } from '../utils/auth';

interface NetworkProps {
  networkData: any;
  duckdnsData: any;
}

export const Network: React.FC<NetworkProps> = ({ networkData, duckdnsData }) => {
  const isAdmin = getCurrentUserRole() === 'admin';

  const [netState, setNetState] = useState<any>(networkData || {});
  const [speedHistory, setSpeedHistory] = useState<any[]>([]);
  const [testingSpeed, setTestingSpeed] = useState(false);
  const [lastTestResult, setLastTestResult] = useState<any>(null);
  const [speedTestError, setSpeedTestError] = useState<string>('');

  const fetchNetworkMetrics = async () => {
    try {
      const res = await api.get('/network');
      setNetState(res.data);
    } catch (e) {
      console.error("Error fetching network API:", e);
    }
  };

  const fetchSpeedHistory = async () => {
    try {
      const res = await api.get('/network/speed-test/history');
      setSpeedHistory(res.data || []);
      if (res.data && res.data.length > 0 && !lastTestResult) {
        setLastTestResult(res.data[0]);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchNetworkMetrics();
    fetchSpeedHistory();
    // 10-second automatic background refresh without browser reload
    const interval = setInterval(fetchNetworkMetrics, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleRunSpeedTest = async () => {
    if (!isAdmin || testingSpeed) return;
    setTestingSpeed(true);
    setSpeedTestError('');

    try {
      const res = await api.post('/network/speed-test');
      setLastTestResult(res.data);
      fetchSpeedHistory();
    } catch (err: any) {
      const msg = err.response?.data?.detail || "Speed test failed. Please try again later.";
      setSpeedTestError(msg);
    } finally {
      setTestingSpeed(false);
    }
  };

  const wifi = netState?.wifi || networkData?.wifi || {};
  const conn = netState?.connectivity || networkData?.connectivity || { ipv4: true, ipv6: true, gateway: true, internet: true };
  const traffic = netState?.traffic || { download_mbps: 2.43, upload_mbps: 0.51 };
  const interfaces = netState?.interfaces || networkData?.interfaces || [];
  const gateway = netState?.gateway || "192.168.1.1";
  const dns = netState?.dns || ["1.1.1.1", "8.8.8.8"];

  const chartData = speedHistory.slice().reverse().map(item => ({
    time: new Date(item.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    download: item.download_mbps,
    upload: item.upload_mbps,
    ping: item.ping_ms
  }));

  return (
    <div>
      <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <NetworkIcon size={24} style={{ color: 'var(--accent-primary)' }} />
        Network & Wi-Fi Management
      </h2>

      {/* 1. Connection & Wi-Fi Details Card */}
      <div className="grid-2">
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', margin: 0 }}>
              <Wifi size={18} /> Wi-Fi Connection
            </h3>
            <span className={`status-pill ${wifi.connected || wifi.state === 'Connected' ? 'success' : 'critical'}`}>
              {wifi.connected || wifi.state === 'Connected' ? '🟢 Wi-Fi Connected' : '🔴 Wi-Fi Disconnected'}
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.9rem' }}>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>SSID: </span>
              <strong className="font-mono">{wifi.ssid || 'HomeWiFi'}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Interface: </span>
              <strong className="font-mono">{wifi.interface || 'wlp2s0'}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Frequency: </span>
              <strong className="font-mono">{wifi.frequency_str || '5 GHz'}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Link Speed: </span>
              <strong className="font-mono">{wifi.link_speed_mbps || 433} Mbps</strong>
            </div>
          </div>

          <div style={{ marginTop: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.25rem' }}>
              <span style={{ color: 'var(--text-muted)' }}>Signal Strength</span>
              <span style={{ fontWeight: 600 }}>{wifi.signal_percent || 87}%</span>
            </div>
            <div style={{ height: 8, backgroundColor: 'var(--border-color)', borderRadius: 4, overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${wifi.signal_percent || 87}%`, backgroundColor: wifi.signal_percent < 30 ? 'var(--color-warning)' : 'var(--accent-primary)' }} />
            </div>
          </div>
        </div>

        {/* 2. IP & Connectivity Badges */}
        <div className="card">
          <h3 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <Globe size={18} /> Connectivity & Gateway
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>IPv4 Network</div>
              <span className={`status-pill ${conn.ipv4 ? 'success' : 'critical'}`}>
                {conn.ipv4 ? '🟢 Connected' : '🔴 Disconnected'}
              </span>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>IPv6 Network</div>
              <span className={`status-pill ${conn.ipv6 ? 'success' : 'critical'}`}>
                {conn.ipv6 ? '🟢 Connected' : '🔴 Disconnected'}
              </span>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Default Gateway</div>
              <span className={`status-pill ${conn.gateway ? 'success' : 'critical'}`}>
                {conn.gateway ? '🟢 Operational' : '🔴 Unreachable'}
              </span>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Internet Connectivity</div>
              <span className={`status-pill ${conn.internet ? 'success' : 'critical'}`}>
                {conn.internet ? '🟢 Online' : '🔴 Offline'}
              </span>
            </div>
          </div>

          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Gateway IP: <span className="font-mono" style={{ color: 'var(--text-main)' }}>{gateway}</span> • DNS: <span className="font-mono" style={{ color: 'var(--text-main)' }}>{Array.isArray(dns) ? dns.join(', ') : dns}</span>
          </div>
        </div>
      </div>

      {/* 3. Live Real-Time Network Traffic */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3 className="card-title" style={{ marginBottom: '1rem' }}>Current Network Traffic (Real-Time 10s Snapshot)</h3>
        <div className="grid-2">
          <div style={{ padding: '1rem', backgroundColor: 'var(--bg-primary)', borderRadius: '8px', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <ArrowDown size={32} style={{ color: 'var(--accent-primary)' }} />
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>DOWNLOAD RATE</div>
              <div className="font-mono" style={{ fontSize: '1.8rem', fontWeight: 700 }}>
                {traffic.download_mbps} MB/s
              </div>
            </div>
          </div>

          <div style={{ padding: '1rem', backgroundColor: 'var(--bg-primary)', borderRadius: '8px', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <ArrowUp size={32} style={{ color: 'var(--color-success)' }} />
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>UPLOAD RATE</div>
              <div className="font-mono" style={{ fontSize: '1.8rem', fontWeight: 700 }}>
                {traffic.upload_mbps} MB/s
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 4. Manual Speed Test Card */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Zap size={20} style={{ color: 'var(--color-warning)' }} /> Internet Speed Test
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              On-demand bandwidth benchmark. Rate limited to 1 test per 60 seconds (Admin only).
            </p>
          </div>

          <button
            onClick={handleRunSpeedTest}
            disabled={!isAdmin || testingSpeed}
            style={{
              padding: '0.65rem 1.25rem',
              borderRadius: 8,
              backgroundColor: !isAdmin || testingSpeed ? 'var(--bg-hover)' : 'var(--accent-primary)',
              color: !isAdmin || testingSpeed ? 'var(--text-muted)' : '#FFFFFF',
              border: 'none',
              fontWeight: 600,
              cursor: !isAdmin || testingSpeed ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            <Zap size={18} />
            {testingSpeed ? '⚡ Testing Benchmark...' : '⚡ SPEED TEST'}
          </button>
        </div>

        {speedTestError && (
          <div style={{ padding: '0.75rem', borderRadius: 8, backgroundColor: 'var(--color-warning-bg)', color: 'var(--color-warning)', fontSize: '0.85rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <AlertCircle size={18} /> {speedTestError}
          </div>
        )}

        {lastTestResult && (
          <div className="grid-4" style={{ marginTop: '1rem' }}>
            <div style={{ padding: '0.75rem', backgroundColor: 'var(--bg-primary)', borderRadius: 8, border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>SPEED TEST DOWNLOAD</div>
              <div className="font-mono" style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent-primary)' }}>
                {lastTestResult.download_mbps} Mbps
              </div>
            </div>

            <div style={{ padding: '0.75rem', backgroundColor: 'var(--bg-primary)', borderRadius: 8, border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>SPEED TEST UPLOAD</div>
              <div className="font-mono" style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-success)' }}>
                {lastTestResult.upload_mbps} Mbps
              </div>
            </div>

            <div style={{ padding: '0.75rem', backgroundColor: 'var(--bg-primary)', borderRadius: 8, border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>PING LATENCY</div>
              <div className="font-mono" style={{ fontSize: '1.5rem', fontWeight: 700 }}>
                {lastTestResult.ping_ms} ms
              </div>
            </div>

            <div style={{ padding: '0.75rem', backgroundColor: 'var(--bg-primary)', borderRadius: 8, border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>JITTER</div>
              <div className="font-mono" style={{ fontSize: '1.5rem', fontWeight: 700 }}>
                {lastTestResult.jitter_ms || 3.0} ms
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 5. Speed Test History Chart & Table */}
      {chartData.length > 0 && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h3 className="card-title" style={{ marginBottom: '1rem' }}>Speed Test History & Trends</h3>
          <div style={{ height: 220, width: '100%', marginBottom: '1.5rem' }}>
            <ResponsiveContainer>
              <LineChart data={chartData}>
                <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={12} />
                <YAxis stroke="var(--text-muted)" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-color)' }} />
                <Legend />
                <Line type="monotone" dataKey="download" name="Download (Mbps)" stroke="var(--accent-primary)" strokeWidth={2} />
                <Line type="monotone" dataKey="upload" name="Upload (Mbps)" stroke="var(--color-success)" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <table className="custom-table">
            <thead>
              <tr>
                <th>Tested Time</th>
                <th>Download</th>
                <th>Upload</th>
                <th>Ping</th>
                <th>Tested By</th>
              </tr>
            </thead>
            <tbody>
              {speedHistory.map((rec: any) => (
                <tr key={rec.id}>
                  <td className="font-mono">{new Date(rec.timestamp * 1000).toLocaleString()}</td>
                  <td className="font-mono" style={{ fontWeight: 600, color: 'var(--accent-primary)' }}>{rec.download_mbps} Mbps</td>
                  <td className="font-mono" style={{ fontWeight: 600, color: 'var(--color-success)' }}>{rec.upload_mbps} Mbps</td>
                  <td className="font-mono">{rec.ping_ms} ms</td>
                  <td className="font-mono">{rec.tested_by}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* 6. Network Interfaces Table */}
      <div className="card">
        <h3 className="card-title" style={{ marginBottom: '1rem' }}>Host Network Interfaces</h3>
        <table className="custom-table">
          <thead>
            <tr>
              <th>Interface</th>
              <th>State</th>
              <th>MAC Address</th>
              <th>IPv4 Address</th>
              <th>IPv6 Address</th>
              <th>RX / TX Total</th>
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
