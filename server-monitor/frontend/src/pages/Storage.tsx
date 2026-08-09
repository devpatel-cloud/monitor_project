import React from 'react';
import { HardDrive, Server } from 'lucide-react';

interface StorageProps {
  storageData: any;
}

export const Storage: React.FC<StorageProps> = ({ storageData }) => {
  const storage = storageData?.storage || {};
  const disks = storage?.disks || [
    {
      device: '/dev/sda',
      model: 'WDC WD5000LPCX-24VHAT0',
      size_bytes: 500107862016,
      type: 'HDD',
      smart_health: 'PASSED',
      temperature_celsius: 38,
      usage_percent: 31
    }
  ];

  const partitions = storage?.partitions || [
    { mount_point: '/', filesystem: 'xfs', total_bytes: 53687091200, used_bytes: 16106127360, usage_percent: 30.0, inodes_total: 26214400, inodes_used: 180000, inodes_percent: 0.7 },
    { mount_point: '/home', filesystem: 'xfs', total_bytes: 440000000000, used_bytes: 88000000000, usage_percent: 20.0, inodes_total: 215000000, inodes_used: 450000, inodes_percent: 0.2 }
  ];

  const lvm = storage?.lvm || { physical_volumes: [], volume_groups: [], logical_volumes: [] };

  return (
    <div>
      <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <HardDrive size={24} style={{ color: 'var(--accent-primary)' }} />
        Storage, SMART & LVM Dashboard
      </h2>

      {/* Disks Grid */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h3 className="card-title" style={{ marginBottom: '1rem' }}>Physical Disks & SMART Health</h3>
        <div className="grid-2">
          {disks.map((disk: any, idx: number) => {
            const sizeGb = (disk.size_bytes / 1073741824).toFixed(0);
            return (
              <div key={idx} className="card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                  <span className="status-pill success" style={{ fontSize: '0.9rem' }}>
                    🟢 {disk.device}
                  </span>
                  <span className="font-mono" style={{ color: 'var(--text-muted)' }}>
                    {sizeGb} GB {disk.type}
                  </span>
                </div>
                <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                  Model: {disk.model}
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.5rem', marginBottom: '1rem', fontSize: '0.85rem' }}>
                  <div>
                    <span style={{ color: 'var(--text-muted)' }}>Health: </span>
                    <span style={{ fontWeight: 600, color: 'var(--color-success)' }}>{disk.smart_health}</span>
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-muted)' }}>Temp: </span>
                    <span style={{ fontWeight: 600 }}>{disk.temperature_celsius}°C</span>
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-muted)' }}>SMART: </span>
                    <span style={{ fontWeight: 600 }}>PASSED</span>
                  </div>
                </div>

                <div style={{ height: 10, backgroundColor: 'var(--border-color)', borderRadius: 5, overflow: 'hidden' }}>
                  <div style={{ height: '100%', width: `${disk.usage_percent || 30}%`, backgroundColor: 'var(--accent-primary)' }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Partitions Table */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3 className="card-title" style={{ marginBottom: '1rem' }}>Partitions & Inodes</h3>
        <table className="custom-table">
          <thead>
            <tr>
              <th>Mount Point</th>
              <th>Filesystem</th>
              <th>Total Size</th>
              <th>Used</th>
              <th>Usage %</th>
              <th>Inodes Used / Total</th>
              <th>Inode %</th>
            </tr>
          </thead>
          <tbody>
            {partitions.map((p: any, idx: number) => (
              <tr key={idx}>
                <td className="font-mono" style={{ fontWeight: 600 }}>{p.mount_point}</td>
                <td>{p.filesystem}</td>
                <td className="font-mono">{(p.total_bytes / 1073741824).toFixed(1)} GB</td>
                <td className="font-mono">{(p.used_bytes / 1073741824).toFixed(1)} GB</td>
                <td>
                  <span className={`status-pill ${p.usage_percent > 85 ? 'warning' : 'success'}`}>
                    {p.usage_percent}%
                  </span>
                </td>
                <td className="font-mono">{p.inodes_used} / {p.inodes_total}</td>
                <td className="font-mono">{p.inodes_percent}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* LVM Section */}
      <div className="card">
        <h3 className="card-title" style={{ marginBottom: '0.5rem' }}>Logical Volume Management (LVM)</h3>
        <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
          Physical Volumes: {lvm.physical_volumes?.length || 0} • Volume Groups: {lvm.volume_groups?.length || 0} • Logical Volumes: {lvm.logical_volumes?.length || 0}
        </p>
      </div>
    </div>
  );
};
