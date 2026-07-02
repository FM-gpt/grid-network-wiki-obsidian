#!/bin/bash
# Deploy GRID Wiki to CT131 from GitHub
set -e

echo "=== Deploying GRID Wiki to CT131 from GitHub ==="

# Stop any existing service
ssh grid-pve "pct exec 131 -- pkill -9 -f 'wiki-service.py' 2>/dev/null || true"
sleep 2

# Clone or pull from GitHub
ssh grid-pve "pct exec 131 -- bash -c '
  if [ -d /opt/grid-wiki/.git ]; then
    cd /opt/grid-wiki && git pull origin main
  else
    rm -rf /opt/grid-wiki
    cd /opt && git clone https://github.com/FM-gpt/grid-network-wiki-obsidian.git grid-wiki
  fi
'" 2>&1

# Fix paths in service code
ssh grid-pve "pct exec 131 -- sed -i 's|/srv/grid-wiki-tool/|/opt/grid-wiki/|g' /opt/grid-wiki/wiki-content/wiki-service.py 2>/dev/null || true"
ssh grid-pve "pct exec 131 -- sed -i 's|/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki/tool/dashboard|/opt/grid-wiki/dashboard|g' /opt/grid-wiki/wiki-content/wiki-service.py 2>/dev/null || true"

# Start the service
ssh grid-pve "pct exec 131 -- nohup python3 -u /opt/grid-wiki/wiki-content/wiki-service.py > /tmp/wiki-service.log 2>&1 &"
sleep 3

# Verify
echo "=== Verification ==="
ssh grid-pve "pct exec 131 -- ps aux | grep 'wiki-service.py' | grep -v grep || echo 'Service not running'"
ssh grid-pve "pct exec 131 -- ss -tlnp | grep 8082 || echo 'Port 8082 not listening'"
curl -s http://10.10.30.131:8082/api/health 2>&1 | head -5 || echo 'Service not responding'

echo "=== Deploy complete ==="
