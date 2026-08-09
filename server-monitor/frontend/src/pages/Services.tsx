import React, { useState } from 'react';
import { Server, Play, Square, RefreshCw, FileText, AlertTriangle, X, ShieldAlert, Cpu } from 'lucide-react';
import api from '../api/client';
import { getCurrentUserRole } from '../utils/auth';

interface ServicesProps {
  servicesData: any;
  onRefreshServices?: () => void;
}

const PROTECTED_SERVICES = ["nginx", "server-monitor", "server-monitor-backend", "server-monitor-collector"];

export const Services: React.FC<ServicesProps> = ({ servicesData, onRefreshServices }) => {
  const userRole = getCurrentUserRole();
  const isAdmin = userRole === 'admin';

  const [confirmModal, setConfirmModal] = useState<{
    show: boolean;
    service: string;
    action: 'start' | 'stop' | 'restart' | 'enable' | 'disable';
    isProtected: boolean;
  }>({ show: false, service: '', action: 'start', isProtected: false });

  const [logsModal, setLogsModal] = useState<{
    show: boolean;
    service: string;
    logs: string[];
    loading: boolean;
  }>({ show: false, service: '', logs: [], loading: false });

  const [actionError, setActionError] = useState<string>('');

  const services = servicesData?.services || [
    { name: 'server-monitor-backend', state: 'RUNNING', enabled: true, is_default: false },
    { name: 'server-monitor-collector', state: 'RUNNING', enabled: true, is_default: false },
    { name: 'duckdns-ipv6', state: 'RUNNING', enabled: true, is_default: false },
    { name: 'nginx', state: 'RUNNING', enabled: true, is_default: true },
    { name: 'docker', state: 'RUNNING', enabled: true, is_default: true },
    { name: 'sshd', state: 'RUNNING', enabled: true, is_default: true },
    { name: 'NetworkManager', state: 'RUNNING', enabled: true, is_default: true },
    { name: 'chronyd', state: 'RUNNING', enabled: true, is_default: true },
    { name: 'firewalld', state: 'RUNNING', enabled: true, is_default: true }
  ];

  // Custom/Application services OR any default service that is STOPPED/FAILED
  const customOrActionable = services.filter((s: any) => !s.is_default || s.state === 'STOPPED' || s.state === 'FAILED');
  const osDefaultServices = services.filter((s: any) => s.is_default && s.state === 'RUNNING');

  const handleOpenActionModal = (service: string, action: 'start' | 'stop' | 'restart' | 'enable' | 'disable') => {
    const isProt = PROTECTED_SERVICES.includes(service.replace('.service', ''));
    setConfirmModal({
      show: true,
      service,
      action,
      isProtected: isProt && (action === 'stop' || action === 'restart')
    });
  };

  const handleExecuteAction = async () => {
    const { service, action } = confirmModal;
    setConfirmModal({ ...confirmModal, show: false });
    setActionError('');

    try {
      await api.post(`/services/${service}/${action}`);
      if (onRefreshServices) onRefreshServices();
    } catch (err: any) {
      const msg = err.response?.data?.detail || `Failed to ${action} ${service}`;
      setActionError(msg);
    }
  };

  const handleOpenLogs = async (service: string) => {
    setLogsModal({ show: true, service, logs: [], loading: true });
    try {
      const res = await api.get(`/services/${service}/logs?lines=60`);
      setLogsModal({
        show: true,
        service,
        logs: res.data?.logs || [],
        loading: false
      });
    } catch (e) {
      setLogsModal({
        show: true,
        service,
        logs: ["Failed to load journal logs."],
        loading: false
      });
    }
  };

  const renderServiceRow = (svc: any, idx: number) => {
    const name = svc.name;
    const isRunning = svc.state === 'RUNNING';
    const isFailed = svc.state === 'FAILED';

    return (
      <tr key={idx}>
        <td className="font-mono" style={{ fontWeight: 600 }}>
          {name}.service {!svc.is_default && <span className="status-pill info" style={{ fontSize: '0.7rem', marginLeft: '6px' }}>Custom</span>}
        </td>
        <td>
          <span className={`status-pill ${isRunning ? 'success' : isFailed ? 'critical' : 'warning'}`}>
            {isRunning ? '🟢 RUNNING' : isFailed ? '🔴 FAILED' : '🟠 STOPPED'}
          </span>
        </td>
        <td>
          <span className="font-mono" style={{ fontSize: '0.85rem' }}>
            {svc.enabled ? 'Enabled' : 'Disabled'}
          </span>
        </td>
        <td style={{ textAlign: 'right' }}>
          <div style={{ display: 'flex', gap: '6px', justifyContent: 'flex-end' }}>
            <button
              onClick={() => handleOpenLogs(name)}
              className="btn-icon"
              title="View Journal Logs"
              style={{ padding: '4px 8px', fontSize: '0.8rem' }}
            >
              <FileText size={14} style={{ marginRight: 4 }} /> Logs
            </button>

            {isAdmin && (
              <>
                {!isRunning ? (
                  <button
                    onClick={() => handleOpenActionModal(name, 'start')}
                    className="btn-icon"
                    title="Start Service"
                    style={{ padding: '4px 8px', color: 'var(--color-success)', fontSize: '0.8rem' }}
                  >
                    <Play size={14} style={{ marginRight: 4 }} /> Start
                  </button>
                ) : (
                  <button
                    onClick={() => handleOpenActionModal(name, 'stop')}
                    className="btn-icon"
                    title="Stop Service"
                    style={{ padding: '4px 8px', color: 'var(--color-critical)', fontSize: '0.8rem' }}
                  >
                    <Square size={14} style={{ marginRight: 4 }} /> Stop
                  </button>
                )}

                <button
                  onClick={() => handleOpenActionModal(name, 'restart')}
                  className="btn-icon"
                  title="Restart Service"
                  style={{ padding: '4px 8px', color: 'var(--color-warning)', fontSize: '0.8rem' }}
                >
                  <RefreshCw size={14} style={{ marginRight: 4 }} /> Restart
                </button>
              </>
            )}
          </div>
        </td>
      </tr>
    );
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Server size={24} style={{ color: 'var(--accent-primary)' }} />
          Linux Systemd Services Management
        </h2>
        <span className={`status-pill ${isAdmin ? 'success' : 'warning'}`}>
          Role: {userRole.toUpperCase()} {isAdmin ? '(Full Control)' : '(Read-Only)'}
        </span>
      </div>

      {actionError && (
        <div style={{ padding: '0.75rem 1rem', borderRadius: 8, backgroundColor: 'var(--color-critical-bg)', color: 'var(--color-critical)', fontSize: '0.9rem', marginBottom: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>{actionError}</span>
          <button onClick={() => setActionError('')} className="btn-icon" style={{ borderWidth: 0 }}>
            <X size={16} />
          </button>
        </div>
      )}

      {/* Primary Table: Custom & Actionable Services */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3 className="card-title" style={{ marginBottom: '1rem' }}>Custom & Actionable Application Services</h3>
        <table className="custom-table">
          <thead>
            <tr>
              <th>Service Name</th>
              <th>Status</th>
              <th>Boot Status</th>
              <th style={{ textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {customOrActionable.map((svc: any, idx: number) => renderServiceRow(svc, idx))}
          </tbody>
        </table>
      </div>

      {/* Secondary Table: Running OS Infrastructure Services */}
      <div className="card">
        <h3 className="card-title" style={{ marginBottom: '1rem', color: 'var(--text-muted)' }}>
          OS Infrastructure Services (Default Running Baseline)
        </h3>
        <table className="custom-table">
          <thead>
            <tr>
              <th>Service Name</th>
              <th>Status</th>
              <th>Boot Status</th>
              <th style={{ textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {osDefaultServices.map((svc: any, idx: number) => renderServiceRow(svc, idx))}
          </tbody>
        </table>
      </div>

      {/* Confirmation & Safety Warning Modal */}
      {confirmModal.show && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="card" style={{ width: 440, padding: '1.5rem', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
              {confirmModal.isProtected ? (
                <ShieldAlert size={28} style={{ color: 'var(--color-critical)' }} />
              ) : (
                <AlertTriangle size={28} style={{ color: 'var(--color-warning)' }} />
              )}
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>
                {confirmModal.isProtected ? 'Protected Service Warning' : 'Confirm Service Action'}
              </h3>
            </div>

            {confirmModal.isProtected ? (
              <div style={{ padding: '0.75rem', borderRadius: 8, backgroundColor: 'var(--color-critical-bg)', color: 'var(--color-critical)', fontSize: '0.9rem', marginBottom: '1.25rem' }}>
                ⚠️ <strong>WARNING:</strong> Stopping or restarting <code>{confirmModal.service}.service</code> may make the monitoring website temporarily or permanently unavailable!
              </div>
            ) : (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', marginBottom: '1.25rem' }}>
                Are you sure you want to <strong>{confirmModal.action.toUpperCase()}</strong> <code>{confirmModal.service}.service</code>?
              </p>
            )}

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button onClick={() => setConfirmModal({ ...confirmModal, show: false })} className="btn-icon">
                Cancel
              </button>
              <button
                onClick={handleExecuteAction}
                style={{
                  padding: '0.5rem 1rem',
                  borderRadius: 8,
                  backgroundColor: confirmModal.isProtected ? 'var(--color-critical)' : 'var(--accent-primary)',
                  color: '#FFFFFF',
                  border: 'none',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                Confirm {confirmModal.action.toUpperCase()}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Journal Logs Modal */}
      {logsModal.show && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="card" style={{ width: 680, maxHeight: '80vh', display: 'flex', flexDirection: 'column', padding: '1.5rem', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <FileText size={20} style={{ color: 'var(--accent-primary)' }} />
                Journal Logs: {logsModal.service}.service
              </h3>
              <button onClick={() => setLogsModal({ ...logsModal, show: false })} className="btn-icon">
                <X size={18} />
              </button>
            </div>

            <div style={{ flex: 1, backgroundColor: 'var(--bg-primary)', padding: '1rem', borderRadius: 8, overflowY: 'auto', border: '1px solid var(--border-color)', fontSize: '0.85rem' }} className="font-mono">
              {logsModal.loading ? (
                <div style={{ color: 'var(--text-muted)' }}>Fetching journalctl logs...</div>
              ) : logsModal.logs.length === 0 ? (
                <div style={{ color: 'var(--text-muted)' }}>No log entries found.</div>
              ) : (
                logsModal.logs.map((line, idx) => (
                  <div key={idx} style={{ padding: '2px 0', borderBottom: '1px solid rgba(255,255,255,0.03)', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                    {line}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
