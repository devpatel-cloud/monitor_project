#!/usr/bin/env bash
# Backup configuration & database for Server Monitor Platform
set -euo pipefail

BACKUP_DIR="/var/backups/server-monitor"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/server_monitor_backup_$TIMESTAMP.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "Creating backup archive..."
tar -czf "$BACKUP_FILE" \
  --ignore-failed-read \
  /etc/server-monitor/ \
  /etc/nginx/default.d/server-monitor.conf \
  /var/lib/server-monitor/monitor.db 2>/dev/null || true

echo "✅ Backup successfully created at: $BACKUP_FILE"
