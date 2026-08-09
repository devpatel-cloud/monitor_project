#!/usr/bin/env bash
# Update script for Server Monitor Platform
set -euo pipefail

PROJECT_DIR="/opt/server-monitor/server-monitor"

if [ -d "$PROJECT_DIR" ]; then
  cd "$PROJECT_DIR"
  echo "Pulling latest code changes..."
  git pull origin main || true

  echo "Rebuilding Docker images..."
  docker compose build

  echo "Restarting Master Server Monitor Service..."
  systemctl restart server-monitor.service
  echo "✅ Server Monitor Platform updated successfully!"
else
  echo "Error: Directory $PROJECT_DIR not found."
  exit 1
fi
