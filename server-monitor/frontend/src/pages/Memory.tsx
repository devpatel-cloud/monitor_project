import React from 'react';
import { Activity } from 'lucide-react';

interface MemoryProps {
  memoryData: any;
}

export const Memory: React.FC<MemoryProps> = ({ memoryData }) => {
  const ramTotalMb = Math.round((memoryData?.total_bytes || 16000000000) / 1048576);
  const ramUsedMb = Math.round((memoryData?.used_bytes || 6400000000) / 1048576);
  const ramFreeMb = Math.round((memoryData?.free_bytes || 4000000000) / 1048576);
  const ramAvailMb = Math.round((memoryData?.available_bytes || 9600000000) / 1048576);
  const ramCachedMb = Math.round((memoryData?.cached_bytes || 3200000000) / 1048576);
  const ramBuffersMb = Math.round((memoryData?.buffers_bytes || 400000000) / 1048576);

  const swapTotalMb = Math.round((memoryData?.swap_total_bytes || 4000000000) / 1048576);
  const swapUsedMb = Math.round((memoryData?.swap_used_bytes || 200000000) / 1048576);

  return (
    <div>
      <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Activity size={24} style={{ color: 'var(--accent-primary)' }} />
        Memory (RAM) & Swap Monitoring
      </h2>

      <div className="grid-4">
        <div className="card">
          <div className="card-title">TOTAL RAM</div>
          <div className="card-value">{(ramTotalMb / 1024).toFixed(1)} GB</div>
        </div>
        <div className="card">
          <div className="card-title">USED RAM</div>
          <div className="card-value">{(ramUsedMb / 1024).toFixed(1)} GB</div>
        </div>
        <div className="card">
          <div className="card-title">AVAILABLE RAM</div>
          <div className="card-value">{(ramAvailMb / 1024).toFixed(1)} GB</div>
        </div>
        <div className="card">
          <div className="card-title">SWAP USAGE</div>
          <div className="card-value">{memoryData?.swap_percent || 5.0}%</div>
        </div>
      </div>

      <div className="card">
        <h3 className="card-title" style={{ marginBottom: '1rem' }}>Memory Allocation Breakdown</h3>
        <table className="custom-table">
          <thead>
            <tr>
              <th>Category</th>
              <th>Size (MB)</th>
              <th>Size (GB)</th>
              <th>Percentage</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Used Memory</td>
              <td className="font-mono">{ramUsedMb} MB</td>
              <td className="font-mono">{(ramUsedMb / 1024).toFixed(2)} GB</td>
              <td className="font-mono">{memoryData?.usage_percent || 40.0}%</td>
            </tr>
            <tr>
              <td>Cached Memory</td>
              <td className="font-mono">{ramCachedMb} MB</td>
              <td className="font-mono">{(ramCachedMb / 1024).toFixed(2)} GB</td>
              <td className="font-mono">{((ramCachedMb / ramTotalMb) * 100).toFixed(1)}%</td>
            </tr>
            <tr>
              <td>Buffer Memory</td>
              <td className="font-mono">{ramBuffersMb} MB</td>
              <td className="font-mono">{(ramBuffersMb / 1024).toFixed(2)} GB</td>
              <td className="font-mono">{((ramBuffersMb / ramTotalMb) * 100).toFixed(1)}%</td>
            </tr>
            <tr>
              <td>Free Memory</td>
              <td className="font-mono">{ramFreeMb} MB</td>
              <td className="font-mono">{(ramFreeMb / 1024).toFixed(2)} GB</td>
              <td className="font-mono">{((ramFreeMb / ramTotalMb) * 100).toFixed(1)}%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};
