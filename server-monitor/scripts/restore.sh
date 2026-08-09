#!/usr/bin/env bash
# Restore script for Server Monitor Platform
set -euo pipefail

if [ -z "${1:-}" ]; then
  echo "Usage: $0 /path/to/backup.tar.gz"
  exit 1
fi

BACKUP_FILE="$1"
if [ ! -f "$BACKUP_FILE" ]; then
  echo "Backup archive file not found: $BACKUP_FILE"
  exit 1
fi

echo "Restoring configuration and database from $BACKUP_FILE..."
tar -xzf "$BACKUP_FILE" -C /

systemctl restart server-monitor.service
echo "✅ Restoration completed successfully!"
