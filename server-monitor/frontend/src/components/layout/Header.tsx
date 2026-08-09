import React from 'react';
import { Sun, Moon, Monitor, Bell, User, LogOut } from 'lucide-react';
import { ThemeMode, applyTheme, getStoredTheme } from '../../theme/theme';

interface HeaderProps {
  systemInfo: any;
  onLogout: () => void;
}

export const Header: React.FC<HeaderProps> = ({ systemInfo, onLogout }) => {
  const [currentTheme, setCurrentTheme] = React.useState<ThemeMode>(getStoredTheme());

  const handleThemeChange = (mode: ThemeMode) => {
    setCurrentTheme(mode);
    applyTheme(mode);
  };

  const nowStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return (
    <header className="top-header">
      <div className="host-info">
        <span className="status-pill success">
          <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: 'var(--color-success)' }}></span>
          SANJAYA SERVER
        </span>
        <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          {systemInfo?.os_name || 'Rocky Linux 9.4'} • Uptime: {systemInfo?.uptime_formatted || '4d 12h 38m'}
        </span>
      </div>

      <div className="controls">
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginRight: '0.5rem' }}>
          Updated: {nowStr}
        </span>

        <div style={{ display: 'flex', gap: '4px', backgroundColor: 'var(--bg-primary)', padding: '3px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
          <button
            onClick={() => handleThemeChange('dark')}
            className={`btn-icon ${currentTheme === 'dark' ? 'active' : ''}`}
            title="Dark Theme"
            style={{ padding: '4px 8px', borderWidth: 0 }}
          >
            <Moon size={16} />
          </button>
          <button
            onClick={() => handleThemeChange('light')}
            className={`btn-icon ${currentTheme === 'light' ? 'active' : ''}`}
            title="Light Theme"
            style={{ padding: '4px 8px', borderWidth: 0 }}
          >
            <Sun size={16} />
          </button>
          <button
            onClick={() => handleThemeChange('system')}
            className={`btn-icon ${currentTheme === 'system' ? 'active' : ''}`}
            title="System Preference"
            style={{ padding: '4px 8px', borderWidth: 0 }}
          >
            <Monitor size={16} />
          </button>
        </div>

        <button onClick={onLogout} className="btn-icon" title="Logout">
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
};
