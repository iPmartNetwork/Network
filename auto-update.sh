#!/bin/bash
set -e

REPO_DIR="/opt/net-orchestrator"
SERVICE_NAME="net-orchestrator"
BRANCH="master"

echo "🔄 Net-Orchestrator Auto Update"

cd "$REPO_DIR"

echo "📦 Backing up config..."
cp config/profiles.json /tmp/profiles.json.bak.$(date +%s)

echo "⬇️ Fetching latest changes..."
git fetch origin

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/$BRANCH)

if [ "$LOCAL" = "$REMOTE" ]; then
  echo "✅ Already up to date"
  exit 0
fi

echo "🛑 Stopping service..."
systemctl stop "$SERVICE_NAME"

echo "📥 Updating code..."
git pull origin "$BRANCH"

echo "▶️ Starting service..."
systemctl start "$SERVICE_NAME"

sleep 2

if systemctl is-active --quiet "$SERVICE_NAME"; then
  echo "✅ Update successful"
else
  echo "❌ Service failed, rolling back config"
  cp /tmp/profiles.json.bak.* config/profiles.json
  systemctl restart "$SERVICE_NAME"
  exit 1
fi
