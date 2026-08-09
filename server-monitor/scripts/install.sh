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

echo "4. Safely installing Nginx location snippet (Non-conflicting)..."
# On RHEL/Rocky Linux Nginx, /etc/nginx/default.d/ snippets are automatically included
# inside the main server block without creating duplicate server_name or listen directives.
SNIPPET_DIR="/etc/nginx/default.d"
SNIPPETS_ALT="/etc/nginx/snippets"

if [ -d "$SNIPPET_DIR" ]; then
  cp deployment/nginx/server-monitor.conf "$SNIPPET_DIR/server-monitor.conf"
  echo "Installed location snippet to $SNIPPET_DIR/server-monitor.conf"
elif [ -d "$SNIPPETS_ALT" ]; then
  cp deployment/nginx/location-snippet.conf "$SNIPPETS_ALT/server-monitor-location.conf"
  echo "Installed location snippet to $SNIPPETS_ALT/server-monitor-location.conf"
else
  mkdir -p "$SNIPPETS_ALT"
  cp deployment/nginx/location-snippet.conf "$SNIPPETS_ALT/server-monitor-location.conf"
  echo "Installed location snippet to $SNIPPETS_ALT/server-monitor-location.conf"
fi

echo "5. Testing Nginx configuration syntax..."
if nginx -t; then
  echo "Nginx configuration syntax test passed. Reloading Nginx safely..."
  systemctl reload nginx
else
  echo "❌ Error: nginx -t failed! Preserving existing Nginx configuration. Nginx reload aborted."
  exit 1
fi

echo "6. Installing systemd unit files..."
cp deployment/systemd/server-monitor-collector.service /etc/systemd/system/
cp deployment/systemd/server-monitor.service /etc/systemd/system/
cp deployment/systemd/server-monitor-cleanup.timer /etc/systemd/system/

systemctl daemon-reload

echo "7. Enabling Master Server Monitor Service..."
systemctl enable --now server-monitor.service

echo ""
echo "=========================================================="
echo "✅ Installation complete!"
echo "Master Service: sudo systemctl status server-monitor"
echo "Host Agent:    sudo systemctl status server-monitor-collector"
echo "Web URL:       https://sanjaya-server.duckdns.org/monitor/"
echo "=========================================================="
