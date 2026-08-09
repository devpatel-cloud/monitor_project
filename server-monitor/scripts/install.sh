#!/usr/bin/env bash
# Native Installation Script for Server Monitor Platform on Rocky Linux 9.8
set -euo pipefail

echo "=========================================================="
echo "🚀 Server Monitor Platform Native Installer — Rocky Linux 9.8"
echo "=========================================================="

BASE_DIR="/opt/server-monitor"
PROJECT_DIR="/opt/server-monitor/server-monitor"
VENV_DIR="/opt/server-monitor/venv"
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

echo "2. Backup existing configuration if present..."
if [ -f "$PROJECT_DIR/scripts/backup.sh" ]; then
  bash "$PROJECT_DIR/scripts/backup.sh" || true
fi

echo "3. Creating Python virtual environment at $VENV_DIR..."
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

echo "4. Installing Python dependencies into virtual environment..."
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r backend/requirements.txt

echo "5. Building React frontend static assets..."
if [ -d "frontend" ]; then
  cd frontend
  npm install
  npm run build
  cd "$PROJECT_DIR"
fi

echo "6. Copying default configuration files if absent..."
if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
  cp config/config.example.yaml "$CONFIG_DIR/config.yaml"
  cp config/thresholds.example.yaml "$CONFIG_DIR/thresholds.yaml"
fi

echo "7. Installing Nginx location snippet..."
SNIPPET_DIR="/etc/nginx/default.d"
if [ -d "$SNIPPET_DIR" ]; then
  cp deployment/nginx/server-monitor.conf "$SNIPPET_DIR/server-monitor.conf"
  echo "Installed snippet to $SNIPPET_DIR/server-monitor.conf"
else
  mkdir -p /etc/nginx/snippets
  cp deployment/nginx/location-snippet.conf /etc/nginx/snippets/server-monitor-location.conf
  echo "Installed snippet to /etc/nginx/snippets/server-monitor-location.conf"
fi

echo "8. Testing Nginx configuration syntax..."
if nginx -t; then
  echo "Nginx syntax test passed. Reloading Nginx safely..."
  systemctl reload nginx
else
  echo "❌ Error: nginx -t failed! Aborting Nginx reload to preserve existing configuration."
  exit 1
fi

echo "9. Installing systemd unit files..."
cp deployment/systemd/server-monitor-backend.service /etc/systemd/system/
cp deployment/systemd/server-monitor-collector.service /etc/systemd/system/
cp deployment/systemd/server-monitor.service /etc/systemd/system/
cp deployment/systemd/server-monitor-cleanup.timer /etc/systemd/system/

systemctl daemon-reload

echo "10. Enabling & Starting Master Server Monitor Service..."
systemctl enable --now server-monitor.service

echo ""
echo "=========================================================="
echo "✅ Native Installation Complete!"
echo "Master Service: sudo systemctl status server-monitor"
echo "Backend API:    sudo systemctl status server-monitor-backend"
echo "Host Agent:     sudo systemctl status server-monitor-collector"
echo "URL:            https://sanjaya-server.duckdns.org/monitor/"
echo "=========================================================="
