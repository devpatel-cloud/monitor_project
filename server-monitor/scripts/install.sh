#!/usr/bin/env bash
# Installation script for Server Monitor Platform on Rocky Linux 9.8
set -euo pipefail

echo "=========================================================="
echo "🚀 Server Monitor Platform Installer — Rocky Linux 9.8"
echo "=========================================================="

PROJECT_DIR="/opt/server-monitor/server-monitor"
CONFIG_DIR="/etc/server-monitor"
DATA_DIR="/var/lib/server-monitor"
LOG_DIR="/var/log/server-monitor"

if [ ! -d "$PROJECT_DIR" ]; then
  echo "Error: Working directory $PROJECT_DIR does not exist!"
  echo "Please place the repository at $PROJECT_DIR"
  exit 1
fi

cd "$PROJECT_DIR"

echo "1. Creating runtime directories..."
mkdir -p "$CONFIG_DIR" "$DATA_DIR" "$LOG_DIR"

echo "2. Copying default configurations if absent..."
if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
  cp config/config.example.yaml "$CONFIG_DIR/config.yaml"
  cp config/thresholds.example.yaml "$CONFIG_DIR/thresholds.yaml"
fi

echo "3. Building Docker containers (Backend & Frontend)..."
docker compose build

echo "4. Safely installing Nginx application configuration..."
if [ -d "/etc/nginx/conf.d" ]; then
  cp deployment/nginx/server-monitor.conf /etc/nginx/conf.d/server-monitor.conf
  echo "Checking Nginx configuration syntax..."
  nginx -t && systemctl reload nginx || echo "Warning: Nginx reload deferred. Please verify /etc/nginx/conf.d/server-monitor.conf"
else
  echo "Note: /etc/nginx/conf.d directory not found. Nginx configuration snippet available at $PROJECT_DIR/deployment/nginx/server-monitor.conf"
fi

echo "5. Installing systemd unit files..."
cp deployment/systemd/server-monitor-collector.service /etc/systemd/system/
cp deployment/systemd/server-monitor.service /etc/systemd/system/
cp deployment/systemd/server-monitor-cleanup.timer /etc/systemd/system/

systemctl daemon-reload

echo "6. Enabling Master Server Monitor Service..."
systemctl enable --now server-monitor.service

echo ""
echo "=========================================================="
echo "✅ Installation complete!"
echo "Master Service: sudo systemctl status server-monitor"
echo "Host Agent:    sudo systemctl status server-monitor-collector"
echo "=========================================================="
