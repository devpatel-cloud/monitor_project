#!/usr/bin/env bash
# Quick CLI Health Check Script for Rocky Linux 9.8
set -euo pipefail

echo "1. Checking Backend API (Docker Port 8000)..."
curl -sf http://127.0.0.1:8000/api/v1/health >/dev/null && echo "🟢 Backend API online" || echo "🔴 Backend API unreachable"

echo "2. Checking Frontend Container (Docker Port 3000 /monitor/)..."
curl -sf http://127.0.0.1:3000/monitor/ >/dev/null && echo "🟢 Frontend container online" || echo "🔴 Frontend container unreachable"

echo "3. Checking Master Systemd Service..."
systemctl is-active server-monitor.service >/dev/null && echo "🟢 server-monitor.service active" || echo "🔴 server-monitor.service inactive"

echo "4. Checking Linux Host Monitoring Agent..."
systemctl is-active server-monitor-collector.service >/dev/null && echo "🟢 server-monitor-collector.service active" || echo "🔴 server-monitor-collector.service inactive"

echo "=========================================================="
echo "Health Check Complete"
echo "Public URL: https://sanjaya-server.duckdns.org/monitor/"
echo "=========================================================="
