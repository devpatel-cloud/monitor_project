# 🚀 Linux Server Monitor Platform

Production-style Linux Server Monitoring Platform designed for **Rocky Linux 9.x / RHEL-compatible Linux** hosts.

![Platform Architecture](docs/architecture.md)

## 📌 Key Features

- **Target Host**: Rocky Linux 9.x (Host-native system agent reading `/proc`, `/sys`, `lsblk`, `smartctl`, `systemctl`, `journalctl`, `firewalld`, `SELinux`, `docker`).
- **Backend**: FastAPI + Pydantic + SQLAlchemy + SQLite database with metric downsampling retention.
- **Frontend**: React + TypeScript + Vite dashboard with **Dark**, **Light**, and **System** themes (zero-flash script, `localStorage` persistence).
- **Subsystem Metrics**:
  - **CPU**: Model, physical cores, threads, overall %, per-core %, load 1m/5m/15m, frequency, temperatures.
  - **Memory**: RAM total, used, free, available, cached, buffers, Swap.
  - **Storage**: Automatic physical drive discovery (HDD, SSD, NVMe, USB), SMART health diagnostics, partitions, filesystems, inodes, LVM structures, disk I/O stats.
  - **Network**: All interfaces (wlp2s0, docker0, lo, etc.), IPv4, IPv6, MAC, RX/TX, drops, Wi-Fi, listening ports.
  - **DuckDNS & IPv6**: Inspection of `duckdns-ipv6.service`, local IPv6 vs DuckDNS AAAA record mismatch detection with strict token privacy.
  - **Docker & Services**: Docker daemon, containers status, images, volumes, systemd service states (`nginx`, `docker`, `sshd`, etc.).
  - **Security Audit**: Firewalld active zones, SELinux enforcing mode, logged-in users, failed SSH attempts, journal error logs.
  - **Alert Engine**: Sustained threshold evaluation for CPU, RAM, Disk, Temperature, SMART, Docker, Services, IPv6/DuckDNS, and Battery.

## 🛠️ Quick Installation (Rocky Linux 9)

```bash
git clone <repo-url> /opt/server-monitor
cd /opt/server-monitor
sudo ./scripts/install.sh
```

## 🧪 Testing

```bash
# Run backend tests
cd server-monitor/backend
pytest backend/tests

# Run frontend build test
cd server-monitor/frontend
npm run build
```
