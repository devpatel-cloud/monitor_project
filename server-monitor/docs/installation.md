# Installation Guide for Rocky Linux 9.x

## Prerequisites
- Rocky Linux 9.x / RHEL 9 compatible host
- Python 3.9+
- Node.js 18+ (for building frontend)
- Nginx & systemd

## Quick Installation
```bash
git clone <repo-url> /opt/server-monitor
cd /opt/server-monitor
sudo ./scripts/install.sh
```

## Post-Installation Verification
```bash
sudo ./scripts/health-check.sh
```
