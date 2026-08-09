import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import api from './api/client';
import { Layout } from './components/layout/Layout';
import { Dashboard } from './pages/Dashboard';
import { CPU } from './pages/CPU';
import { Memory } from './pages/Memory';
import { Storage } from './pages/Storage';
import { Network } from './pages/Network';
import { Docker } from './pages/Docker';
import { Services } from './pages/Services';
import { Security } from './pages/Security';
import { Battery } from './pages/Battery';
import { DuckDNS } from './pages/DuckDNS';
import { Alerts } from './pages/Alerts';
import { SettingsPage } from './pages/Settings';
import { Login } from './pages/Login';

export const App: React.FC = () => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('server_monitor_token'));
  const [healthData, setHealthData] = useState<any>(null);
  const [systemData, setSystemData] = useState<any>(null);
  const [cpuData, setCpuData] = useState<any>(null);
  const [memoryData, setMemoryData] = useState<any>(null);
  const [storageData, setStorageData] = useState<any>(null);
  const [networkData, setNetworkData] = useState<any>(null);
  const [dockerData, setDockerData] = useState<any>(null);
  const [servicesData, setServicesData] = useState<any>(null);
  const [securityData, setSecurityData] = useState<any>(null);
  const [batteryData, setBatteryData] = useState<any>(null);
  const [duckdnsData, setDuckdnsData] = useState<any>(null);
  const [alertsData, setAlertsData] = useState<any[]>([]);

  const fetchAllMetrics = async () => {
    try {
      const [
        healthRes, sysRes, cpuRes, memRes, storageRes, netRes,
        docRes, svcRes, secRes, batRes, ddnsRes, alertsRes
      ] = await Promise.allSettled([
        api.get('/health'),
        api.get('/system'),
        api.get('/cpu'),
        api.get('/memory'),
        api.get('/storage'),
        api.get('/network'),
        api.get('/docker'),
        api.get('/services'),
        api.get('/security'),
        api.get('/battery'),
        api.get('/duckdns'),
        api.get('/alerts')
      ]);

      if (healthRes.status === 'fulfilled') setHealthData(healthRes.value.data);
      if (sysRes.status === 'fulfilled') setSystemData(sysRes.value.data);
      if (cpuRes.status === 'fulfilled') setCpuData(cpuRes.value.data);
      if (memRes.status === 'fulfilled') setMemoryData(memRes.value.data);
      if (storageRes.status === 'fulfilled') setStorageData(storageRes.value.data);
      if (netRes.status === 'fulfilled') setNetworkData(netRes.value.data);
      if (docRes.status === 'fulfilled') setDockerData(docRes.value.data);
      if (svcRes.status === 'fulfilled') setServicesData(svcRes.value.data);
      if (secRes.status === 'fulfilled') setSecurityData(secRes.value.data);
      if (batRes.status === 'fulfilled') setBatteryData(batRes.value.data);
      if (ddnsRes.status === 'fulfilled') setDuckdnsData(ddnsRes.value.data);
      if (alertsRes.status === 'fulfilled') setAlertsData(alertsRes.value.data);
    } catch (e) {
      console.error("Error fetching metrics:", e);
    }
  };

  useEffect(() => {
    if (token) {
      fetchAllMetrics();
      const interval = setInterval(fetchAllMetrics, 5000);
      return () => clearInterval(interval);
    }
  }, [token]);

  const handleLogout = () => {
    localStorage.removeItem('server_monitor_token');
    setToken(null);
  };

  if (!token) {
    return <Login onLoginSuccess={(t) => setToken(t)} />;
  }

  return (
    <BrowserRouter>
      <Layout systemInfo={systemData} onLogout={handleLogout}>
        <Routes>
          <Route
            path="/"
            element={
              <Dashboard
                healthData={healthData}
                cpuData={cpuData}
                memoryData={memoryData}
                storageData={storageData}
                networkData={networkData}
                dockerData={dockerData}
                servicesData={servicesData}
                duckdnsData={duckdnsData}
                alertsData={alertsData}
              />
            }
          />
          <Route path="/cpu" element={<CPU cpuData={cpuData} />} />
          <Route path="/memory" element={<Memory memoryData={memoryData} />} />
          <Route path="/storage" element={<Storage storageData={storageData} />} />
          <Route path="/network" element={<Network networkData={networkData} duckdnsData={duckdnsData} />} />
          <Route path="/docker" element={<Docker dockerData={dockerData} />} />
          <Route path="/services" element={<Services servicesData={servicesData} />} />
          <Route path="/security" element={<Security securityData={securityData} />} />
          <Route path="/battery" element={<Battery batteryData={batteryData} />} />
          <Route path="/duckdns" element={<DuckDNS duckdnsData={duckdnsData} />} />
          <Route path="/alerts" element={<Alerts alertsData={alertsData} onRefreshAlerts={fetchAllMetrics} />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
};
