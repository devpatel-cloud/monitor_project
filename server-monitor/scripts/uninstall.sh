#!/usr/bin/env bash
# Native Uninstallation Script for Server Monitor Platform
set -euo pipefail

echo "Stopping Server Monitor systemd services..."
systemctl stop server-monitor.service || true
systemctl stop server-monitor-backend.service || true
systemctl stop server-monitor-collector.service || true

systemctl disable server-monitor.service || true
systemctl disable server-monitor-backend.service || true
systemctl disable server-monitor-collector.service || true

echo "Removing systemd unit files..."
rm -f /etc/systemd/system/server-monitor.service
rm -f /etc/systemd/system/server-monitor-backend.service
rm -f /etc/systemd/system/server-monitor-collector.service
rm -f /etc/systemd/system/server-monitor-cleanup.timer
systemctl daemon-reload

echo "Removing Nginx location snippet..."
rm -f /etc/nginx/default.d/server-monitor.conf
rm -f /etc/nginx/snippets/server-monitor-location.conf
nginx -t && systemctl reload nginx || true

echo "✅ Native Server Monitor Platform uninstalled cleanly."
