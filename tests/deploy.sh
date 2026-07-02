#!/bin/bash
# Deployment script for GRID Wiki on CT131
set -e

echo "=== Step 1: Stop old service ==="
ssh grid-pve "pkill -9 -f 'wiki-service.py' 2>/dev/null; sleep 3; ps aux | grep 'wiki-service' | grep -v grep || echo 'Service stopped'"

echo "=== Step 2: Create new directory ==="
ssh grid-pve "mkdir -p /srv/grid-wiki-tool && ls -la /srv/grid-wiki-tool/"

echo "=== Step 3: Copy files ==="
rsync -avz --delete /Users/tron/Documents/Obsidian\ Vault/Projects/GRID\ Network\ Wiki\ tool/ grid-pve:/srv/grid-wiki-tool/ 2>&1 | tail -5

echo "=== Step 4: Start service ==="
ssh grid-pve "cd /srv/grid-wiki-tool && python3 -u wiki-service.py > /tmp/wiki-service.log 2>&1 & sleep 3 && ps aux | grep 'wiki-service.py' | grep -v grep"

echo "=== Step 5: Run tests ==="
ssh grid-pve "curl -s http://127.0.0.1:8082/ | head -5; echo '---'; curl -s http://127.0.0.1:8082/api/dashboard/status | head -10"
