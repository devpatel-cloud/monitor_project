#!/usr/bin/env bash
# Update script for Server Monitor Platform
set -euo pipefail

echo "Updating Server Monitor Platform..."
git pull origin main || true

systemctl restart server-monitor.service
systemctl restart server-monitor-collector.service
echo "✅ Server Monitor updated successfully!"
