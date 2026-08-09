# Native Rocky Linux 9.8 Installation & Rollback Guide

## Target URL
`https://sanjaya-server.duckdns.org/monitor/`

## Target Path
`/opt/server-monitor/server-monitor`

## Python Virtual Environment
`/opt/server-monitor/venv`

## Dependencies Required on Rocky Linux 9.8
```bash
sudo dnf install -y \
  python3 \
  python3-pip \
  nodejs \
  npm \
  nginx \
  smartmontools \
  lm_sensors \
  sysstat \
  NetworkManager \
  bind-utils
```

## Step-by-Step Native Installation
```bash
sudo mkdir -p /opt/server-monitor
cd /opt/server-monitor
git clone <repo-url> server-monitor
cd /opt/server-monitor/server-monitor

sudo ./scripts/install.sh
```

## Systemd Management Commands
```bash
sudo systemctl start server-monitor
sudo systemctl status server-monitor
sudo systemctl restart server-monitor
sudo systemctl stop server-monitor
```

## Rollback Instructions
If you ever need to roll back or cleanly remove the Server Monitor Platform:
```bash
cd /opt/server-monitor/server-monitor
sudo ./scripts/uninstall.sh
```
To restore a previous backup:
```bash
sudo ./scripts/restore.sh /var/backups/server-monitor/server_monitor_backup_<TIMESTAMP>.tar.gz
```
