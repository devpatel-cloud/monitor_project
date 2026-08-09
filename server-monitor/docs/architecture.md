# Rocky Linux 9.8 Production Architecture Overview

The Server Monitor Platform is deployed at `/opt/server-monitor/server-monitor` on Rocky Linux 9.8.

## Hybrid Container + Host Native Architecture

```
                                  PUBLIC INTERNET / IPv6
                                             │
                                     HTTPS (Port 443)
                                             │
                                             ▼
                                  Host Nginx Reverse Proxy
                                 (/etc/nginx/conf.d/server-monitor.conf)
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       │ (Proxy to 127.0.0.1:3000)                 │ (Proxy to 127.0.0.1:8000)
                       ▼                                           ▼
            ┌─────────────────────┐                     ┌─────────────────────┐
            │ Frontend Container  │                     │  Backend Container  │
            │  (React / Nginx)    │                     │  (FastAPI Server)   │
            └─────────────────────┘                     └──────────┬──────────┘
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

## Systemd Control Interface

Sanjaya-style master systemd controls managing both Docker containers and the host agent:

```bash
sudo systemctl start server-monitor
sudo systemctl stop server-monitor
sudo systemctl restart server-monitor
sudo systemctl status server-monitor
sudo systemctl enable server-monitor
```
