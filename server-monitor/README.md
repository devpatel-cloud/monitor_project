# 🚀 Linux Server Monitor Platform

Production-style Linux Server Monitoring Platform designed for **Rocky Linux 9.8 / RHEL-compatible Linux** hosts.

- **Production Access URL**: `https://sanjaya-server.duckdns.org/monitor/`
- **Deployment Path**: `/opt/server-monitor/server-monitor`

## 📌 Architecture Highlights

- **Non-Conflicting Nginx Integration**: Coexists safely with the existing Sanjaya application at `https://sanjaya-server.duckdns.org` via a location snippet (`/etc/nginx/default.d/server-monitor.conf`).
- **Sanjaya-Style Systemd Management**: Master `server-monitor.service` controls both Docker containers (`docker compose up -d`) and the host monitoring agent (`server-monitor-collector.service`).
- **Path Routing**:
  - `/monitor/` -> React Frontend container (`http://127.0.0.1:3000/monitor/`)
  - `/monitor/api/v1/` -> FastAPI Backend container (`http://127.0.0.1:8000/api/v1/`)

## 🛠️ Quick Installation (Rocky Linux 9.8)

```bash
cd /opt/server-monitor/server-monitor
sudo ./scripts/install.sh
```

## 🧪 System Verification

```bash
sudo ./scripts/health-check.sh
```
