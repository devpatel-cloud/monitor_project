# Rocky Linux 9.8 Deployment Guide

## Deployment Directory
Target Path: `/opt/server-monitor/server-monitor`

## Dependencies Required on Rocky Linux 9.8
- `docker` (Docker Engine 29.x & Docker Compose plugin `docker-compose-plugin`)
- `python3` (Python 3.9+)
- `nginx` (Host Nginx web server)
- `smartmontools` (for SMART drive health diagnostics)
- `lm_sensors` (for thermal sensors monitoring)
- `sysstat` (for disk I/O monitoring)

## Deployment Steps
```bash
sudo mkdir -p /opt/server-monitor
cd /opt/server-monitor
git clone <repo-url> server-monitor
cd /opt/server-monitor/server-monitor

sudo ./scripts/install.sh
```

## Systemd Control Commands
```bash
sudo systemctl start server-monitor
sudo systemctl status server-monitor
sudo systemctl restart server-monitor
sudo systemctl stop server-monitor
```
