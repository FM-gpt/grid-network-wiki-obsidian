#!/bin/bash
# Deploy GRID Wiki to CT130
# Usage: ./deploy-ct130.sh

set -e

echo "Deploying GRID Wiki to CT130..."

# Define paths
LOCAL_DIR="/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki/tool"
REMOTE_USER="root"
REMOTE_HOST="10.10.30.130"
REMOTE_DIR="/opt/grid-wiki"

# Sync files
echo "Syncing files..."
rsync -avz --delete \
    --exclude=".git" \
    --exclude=".DS_Store" \
    --exclude="node_modules" \
    --exclude="__pycache__" \
    "$LOCAL_DIR/" \
    "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/" 2>&1

# Restart service
echo "Restarting wiki-service..."
ssh "$REMOTE_USER@$REMOTE_HOST" "systemctl restart grid-wiki" 2>&1 || echo "Service restart failed (may need manual intervention)"

# Verify deployment
echo "Verifying deployment..."
sleep 2
curl -sk https://$REMOTE_HOST:8082/ > /dev/null 2>&1 && echo "Deployment successful!" || echo "Deployment verification failed"

echo "Deploy complete."
