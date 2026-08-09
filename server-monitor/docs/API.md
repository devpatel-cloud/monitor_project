# REST API Documentation

Base URL: `/api/v1`

## Authentication
- `POST /api/v1/auth/login` - Authenticate and acquire Bearer JWT token.
- `GET /api/v1/auth/me` - Get current authenticated user details.

## Real-Time Subsystem Metrics
- `GET /api/v1/health` - Server Health Score & status
- `GET /api/v1/system` - Host OS, uptime, kernel metadata
- `GET /api/v1/cpu` - Per-core usage, load average, frequency
- `GET /api/v1/memory` - RAM, Swap, cached, buffers
- `GET /api/v1/storage` - Disks, partitions, SMART health, LVM
- `GET /api/v1/network` - Interfaces, IPv4/IPv6, Wi-Fi, listening ports
- `GET /api/v1/docker` - Container stats, daemon status, images, volumes
- `GET /api/v1/services` - Systemd services status
- `GET /api/v1/security` - Firewalld, SELinux, logged-in users, SSH audit
- `GET /api/v1/battery` - Power supply & battery stats
- `GET /api/v1/duckdns` - DuckDNS AAAA & IPv6 sync (tokens hidden)
- `GET /api/v1/alerts` - Active and resolved alerts

## Historical Graph Metrics
- `GET /api/v1/history/cpu?range_hours=24`
- `GET /api/v1/history/memory?range_hours=24`
- `GET /api/v1/history/temperature?range_hours=24`
- `GET /api/v1/history/network?range_hours=24`
