#!/usr/bin/env bash
# Uninstallation script for Server Monitor Platform
set -euo pipefail

PROJECT_DIR="/opt/server-monitor/server-monitor"

echo "Stopping Server Monitor master service and host collector..."
systemctl stop server-monitor.service || true
systemctl stop server-monitor-collector.service || true
systemctl disable server-monitor.service || true
systemctl disable server-monitor-collector.service || true

if [ -d "$PROJECT_DIR" ]; then
  cd "$PROJECT_DIR"
  docker compose down --volumes || true
fi

echo "Removing systemd unit files..."
rm -f /etc/systemd/system/server-monitor.service
rm -f /etc/systemd/system/server-monitor-collector.service
rm -f /etc/systemd/system/server-monitor-cleanup.timer
systemctl daemon-reload

echo "✅ Server Monitor Platform uninstalled cleanly."
