import React from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

interface LayoutProps {
  children: React.ReactNode;
  systemInfo: any;
  onLogout: () => void;
}

export const Layout: React.FC<LayoutProps> = ({ children, systemInfo, onLogout }) => {
  const [collapsed, setCollapsed] = React.useState(false);

  return (
    <div className="app-container">
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />
      <div className="main-layout">
        <Header systemInfo={systemInfo} onLogout={onLogout} />
        <main className="content-body">
          {children}
        </main>
      </div>
    </div>
  );
};
