#!/usr/bin/env bash
# Update Script for Native Server Monitor Platform
set -euo pipefail

PROJECT_DIR="/opt/server-monitor/server-monitor"
VENV_DIR="/opt/server-monitor/venv"

if [ -d "$PROJECT_DIR" ]; then
  cd "$PROJECT_DIR"
  echo "1. Pulling latest code changes..."
  git pull origin main || true

  echo "2. Updating Python virtual environment dependencies..."
  if [ -d "$VENV_DIR" ]; then
    "$VENV_DIR/bin/pip" install -r backend/requirements.txt
  fi

  echo "3. Rebuilding React frontend static assets..."
  if [ -d "frontend" ]; then
    cd frontend
    npm install
    npm run build
    cd "$PROJECT_DIR"
  fi

  echo "4. Restarting Master Server Monitor Service..."
  systemctl restart server-monitor.service
  echo "✅ Server Monitor Platform updated successfully!"
else
  echo "Error: Directory $PROJECT_DIR not found."
  exit 1
fi
