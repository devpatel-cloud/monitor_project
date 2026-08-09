# Rocky Linux 9.8 Production Architecture Overview

The Server Monitor Platform is deployed at `/opt/server-monitor/server-monitor` on Rocky Linux 9.8 and accessible via `https://sanjaya-server.duckdns.org/monitor/`.

## Non-Conflicting Nginx Topology

The platform integrates into the existing Sanjaya Nginx setup via a location snippet (`/etc/nginx/default.d/server-monitor.conf`), preserving the existing Sanjaya root application at `https://sanjaya-server.duckdns.org`.

```
                        https://sanjaya-server.duckdns.org
                                       │
                     ┌─────────────────┴─────────────────┐
                     │                                   │
                     ▼                                   ▼
             Existing Sanjaya                     Server Monitor Platform
                   (/)                                 (/monitor/)
                                                         │
                                        ┌────────────────┴────────────────┐
                                        │                                 │
                                        ▼                                 ▼
                                Frontend Route                     Backend API Route
                                  (/monitor/)                     (/monitor/api/v1/)
                                        │                                 │
                                        ▼                                 ▼
                              127.0.0.1:3000                    127.0.0.1:8000
                            (React Container)                 (FastAPI Container)
                                                                          │
                                                                          ▼
                                                                   SQLite Database
                                                            (/var/lib/server-monitor/monitor.db)
                                                                          ▲
                                                                          │
                                                               ┌──────────┴──────────┐
                                                               │ Host Python Agent   │
                                                               │ (Native systemd)    │
                                                               └─────────────────────┘
```

## Systemd Master Control
```bash
sudo systemctl start server-monitor
sudo systemctl stop server-monitor
sudo systemctl restart server-monitor
sudo systemctl status server-monitor
```
