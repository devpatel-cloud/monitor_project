# Rocky Linux 9.8 Deployment Guide

## Target URL
`https://sanjaya-server.duckdns.org/monitor/`

## Deployment Directory
`/opt/server-monitor/server-monitor`

## Step-by-Step Installation
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
