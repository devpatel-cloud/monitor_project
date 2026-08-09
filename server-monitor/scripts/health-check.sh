#!/usr/bin/env bash
# Quick CLI Health Check Script
set -euo pipefail

echo "Checking FastAPI Backend..."
curl -sf http://127.0.0.1:8000/api/v1/health || { echo "❌ Backend offline!"; exit 1; }

echo "Checking Systemd Services..."
systemctl is-active server-monitor.service >/dev/null && echo "🟢 server-monitor active"
systemctl is-active server-monitor-collector.service >/dev/null && echo "🟢 server-monitor-collector active"

echo "✅ Health check passed!"
