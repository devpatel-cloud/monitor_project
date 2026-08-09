import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Cpu,
  HardDrive,
  Network,
  Box,
  Server,
  Shield,
  BatteryCharging,
  Globe,
  Bell,
  Settings,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggle }) => {
  const navItems = [
    { label: 'Overview', path: '/', icon: LayoutDashboard },
    { label: 'CPU', path: '/cpu', icon: Cpu },
    { label: 'Memory', path: '/memory', icon: Cpu },
    { label: 'Storage', path: '/storage', icon: HardDrive },
    { label: 'Network', path: '/network', icon: Network },
    { label: 'Docker', path: '/docker', icon: Box },
    { label: 'Services', path: '/services', icon: Server },
    { label: 'Security', path: '/security', icon: Shield },
    { label: 'Battery', path: '/battery', icon: BatteryCharging },
    { label: 'DuckDNS', path: '/duckdns', icon: Globe },
    { label: 'Alerts', path: '/alerts', icon: Bell },
  ];

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <Server className="icon" style={{ color: 'var(--accent-primary)' }} />
        {!collapsed && <span className="title">Server Monitor</span>}
        <button onClick={onToggle} className="btn-icon" style={{ marginLeft: 'auto', border: 'none' }}>
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>
      <ul className="nav-list">
        {navItems.map((item) => {
          const IconComponent = item.icon;
          return (
            <li key={item.path} className="nav-item">
              <NavLink to={item.path} end={item.path === '/'}>
                <IconComponent size={20} />
                {!collapsed && <span>{item.label}</span>}
              </NavLink>
            </li>
          );
        })}
        <li className="nav-item" style={{ marginTop: 'auto' }}>
          <NavLink to="/settings">
            <Settings size={20} />
            {!collapsed && <span>Settings</span>}
          </NavLink>
        </li>
      </ul>
    </aside>
  );
};
