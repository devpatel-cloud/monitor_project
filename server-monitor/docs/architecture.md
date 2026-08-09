# System Architecture Overview

The Server Monitor Platform is a standalone, enterprise-grade Linux server monitoring system designed for Rocky Linux 9.x / RHEL-compatible Linux hosts.

## Core Topology

```
Internet -> IPv6/HTTPS -> Nginx (Port 443) -> React Frontend (Vite Static Build)
                                           -> FastAPI Backend (Port 8000)
                                                   |
                                            SQLite Metric Store
                                                   ^
                                            Host Python Collector
```

- **Host Agent**: Python collector running as a systemd service querying Linux `/proc`, `/sys`, `lsblk`, `smartctl`, `systemctl`, `journalctl`, `firewalld`, `SELinux`, and Docker socket.
- **Backend**: FastAPI app supporting JWT authentication, metric persistence, historical downsampling, and alert engine evaluations.
- **Frontend**: React + TypeScript + Vite dashboard featuring Dark, Light, and System themes, responsive layouts, and interactive Recharts graphs.
