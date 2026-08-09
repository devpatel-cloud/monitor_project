#!/usr/bin/env bash
# Uninstallation script for Server Monitor Platform
set -euo pipefail

echo "Stopping services..."
systemctl stop server-monitor.service || true
systemctl stop server-monitor-collector.service || true
systemctl disable server-monitor.service || true
systemctl disable server-monitor-collector.service || true

rm -f /etc/systemd/system/server-monitor.service
rm -f /etc/systemd/system/server-monitor-collector.service
systemctl daemon-reload

echo "Server Monitor services removed."
