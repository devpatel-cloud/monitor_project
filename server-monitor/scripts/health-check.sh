#!/usr/bin/env bash
# Quick CLI Health Check Script for Native Deployment on Rocky Linux 9.8
set -euo pipefail

echo "1. Checking FastAPI Backend Service (127.0.0.1:8000)..."
curl -sf http://127.0.0.1:8000/api/v1/health >/dev/null && echo "🟢 Backend API online" || echo "🔴 Backend API unreachable"

echo "2. Checking Frontend Static Build Directory..."
if [ -d "/opt/server-monitor/server-monitor/frontend/dist" ]; then
  echo "🟢 Frontend production build present"
else
  echo "🔴 Frontend dist folder missing!"
fi

echo "3. Checking Systemd Services..."
systemctl is-active server-monitor-backend.service >/dev/null && echo "🟢 server-monitor-backend.service active" || echo "🔴 server-monitor-backend.service inactive"
systemctl is-active server-monitor-collector.service >/dev/null && echo "🟢 server-monitor-collector.service active" || echo "🔴 server-monitor-collector.service inactive"
systemctl is-active server-monitor.service >/dev/null && echo "🟢 server-monitor.service active" || echo "🔴 server-monitor.service inactive"

echo "=========================================================="
echo "Health Check Complete"
echo "URL: https://sanjaya-server.duckdns.org/monitor/"
echo "=========================================================="
