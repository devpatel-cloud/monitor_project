# Native Rocky Linux 9.8 Deployment Architecture

The Server Monitor Platform is deployed natively at `/opt/server-monitor/server-monitor` on Rocky Linux 9.8.

## Native Application Topology

```
                         PUBLIC INTERNET / IPv6
                                    │
                            HTTPS (Port 443)
                                    │
                                    ▼
                         Host Nginx Web Server
                 (/etc/nginx/default.d/server-monitor.conf)
                                    │
                  ┌─────────────────┴─────────────────┐
                  │                                   │
                  ▼                                   ▼
          Frontend Static SPA                   FastAPI Backend API
        (/monitor/ -> dist/)                 (/monitor/api/v1/)
                  │                                   │
                  ▼                                   ▼
   /opt/server-monitor/server-monitor/         127.0.0.1:8000
             frontend/dist/                 (server-monitor-backend.service)
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

Sanjaya-style master systemd controls managing native backend and host agent:

```bash
sudo systemctl start server-monitor
sudo systemctl stop server-monitor
sudo systemctl restart server-monitor
sudo systemctl status server-monitor
```
