# 🚀 Native Linux Server Monitor Platform

Production-style Linux Server Monitoring Platform deployed natively on **Rocky Linux 9.8 / RHEL-compatible Linux** hosts (No Docker required for application runtime).

- **Production Access URL**: `https://sanjaya-server.duckdns.org/monitor/`
- **Deployment Directory**: `/opt/server-monitor/server-monitor`
- **Python Venv Path**: `/opt/server-monitor/venv`

## 📌 Architecture Highlights

- **Native Python Backend**: FastAPI app running on `127.0.0.1:8000` via `server-monitor-backend.service`.
- **Native React Frontend**: Built directly on host (`npm run build`) and served by Nginx from `/opt/server-monitor/server-monitor/frontend/dist`.
- **Docker Monitoring Preserved**: The host agent continues monitoring Docker daemon, containers, CPU/memory, images, volumes, and networks directly on Rocky Linux.
- **Non-Conflicting Nginx Integration**: Location snippet (`/etc/nginx/default.d/server-monitor.conf`) preserves the root Sanjaya application at `https://sanjaya-server.duckdns.org`.
- **Sanjaya-Style Systemd Management**: Master `server-monitor.service` controls both `server-monitor-backend.service` and `server-monitor-collector.service`.

## 🛠️ Quick Native Installation

```bash
cd /opt/server-monitor/server-monitor
sudo ./scripts/install.sh
```

## 🧪 System Verification

```bash
sudo ./scripts/health-check.sh
```
