#!/usr/bin/env bash
# Installation script for Server Monitor Platform on Rocky Linux 9.x
set -euo pipefail

echo "================================================="
echo "🚀 Server Monitor Platform Installer — Rocky Linux"
echo "================================================="

INSTALL_DIR="/opt/server-monitor"
CONFIG_DIR="/etc/server-monitor"
DATA_DIR="/var/lib/server-monitor"
LOG_DIR="/var/log/server-monitor"

# Ensure directories exist
mkdir -p "$INSTALL_DIR" "$CONFIG_DIR" "$DATA_DIR" "$LOG_DIR"

echo "1. Checking Python 3 and dependencies..."
python3 --version || { echo "Python 3 required!"; exit 1; }

echo "2. Copying configuration templates..."
if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
  cp config/config.example.yaml "$CONFIG_DIR/config.yaml"
  cp config/thresholds.example.yaml "$CONFIG_DIR/thresholds.yaml"
fi

echo "3. Installing systemd services..."
cp deployment/systemd/server-monitor.service /etc/systemd/system/
cp deployment/systemd/server-monitor-collector.service /etc/systemd/system/
cp deployment/systemd/server-monitor-cleanup.timer /etc/systemd/system/

systemctl daemon-reload
systemctl enable --now server-monitor.service
systemctl enable --now server-monitor-collector.service
systemctl enable --now server-monitor-cleanup.timer

echo "✅ Server Monitor Platform installed and started successfully!"
