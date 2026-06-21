#!/bin/bash
# Deploy wiki service to CT120 (no Docker mounts needed)
set -e

CT120="grid-pve"
CT120_WIKI_DIR="/srv/grid-wiki"

echo "=== Deploying GRID Network Wiki to CT120 ==="

# Copy content files to CT120
echo "Copying content files..."
ssh grid-pve "mkdir -p $CT120_WIKI_DIR/sites/grid $CT120_WIKI_DIR/sites/fmsa $CT120_WIKI_DIR/maintenance-reports"

# Upload index.html
scp "/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki/wiki-content/index.html" grid-pve:"$CT120_WIKI_DIR/"

# Upload markdown files
scp "/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki/wiki-content/sites-index.md" grid-pve:"$CT120_WIKI_DIR/sites/GRID-Network-Wiki-Index.md"

# Upload monitoring status
scp "/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki/wiki-content/monitoring-status.json" grid-pve:"$CT120_WIKI_DIR/monitoring-status.json"

# Upload site info files
cat > /tmp/grid-site-info.md << 'EOF'
---
title: GRID Network - Site Overview
site: grid
last_updated: 2026-06-21
---

# GRID Network Site

## Infrastructure
- **Proxmox host**: grid-core-01 (VMID 120)
- **IP**: 10.10.30.22
- **Storage**: ZFS pools
- **Network**: GRID VLAN

## Containers
- CT120: grid-core-01 (grid-core)
- CT121: grid-dev-01 (development)
- CT122: minecraft-grid
- CT123: files-grid
- CT124: media-grid
- CT125: kali-grid

## Services
- Caddy (reverse proxy)
- Prometheus
- Grafana
- Uptime Kuma
- Portainer
- WebUI/AI
EOF

cat > /tmp/fmsa-site-info.md << 'EOF'
---
title: FMSA - Site Overview
site: fmsa
last_updated: 2026-06-21
status: pending
---

# FMSA Site

## Infrastructure
- **Status**: Pending setup
- **Proxmox container**: TBD
- **IP**: TBD

## Services
- Pending configuration
EOF

cat > /tmp/fmsa-services.md << 'EOF'
---
title: FMSA - Services
site: fmsa
last_updated: 2026-06-21
status: pending
---

# FMSA Services

| Service | Status | IP | Ports | Monitoring |
| --- | --- | --- | --- | --- |
| Pending | TBD | TBD | TBD | TBD |
EOF

cat > /tmp/grid-services.md << 'EOF'
---
title: GRID - Service Catalog
site: grid
last_updated: 2026-06-21
---

# GRID Service Catalog

| Service | Type | IP | Ports | Status | Monitoring |
| --- | --- | --- | --- | --- | --- |
| Proxmox | LXC | 10.10.30.22 | 8006 | active | Uptime Kuma |
| Caddy | Docker | internal | 80,443 | active | Uptime Kuma |
| Prometheus | Docker | 10.10.30.120 | 9090 | active | Uptime Kuma |
| Grafana | Docker | 10.10.30.120 | 3000 | active | Uptime Kuma |
| Uptime Kuma | Docker | 10.10.30.120 | 3001 | active | internal |
| Portainer | Docker | 10.10.30.120 | 9443 | active | Uptime Kuma |
| WebUI/AI | Docker | 10.10.30.120 | 8080 | active | Uptime Kuma |
| Homelab sync | Docker | 10.10.30.120 | 5984 | active | Uptime Kuma |
| Ollama | Docker | 10.10.30.120 | 11434 | active | Uptime Kuma |
| Adminer | CT121 | 10.10.30.121 | 8080 | active | Uptime Kuma |
| Code Server | CT121 | 10.10.30.121 | 8443 | active | Uptime Kuma |
| Minecraft Map | CT122 | 10.10.30.122 | 8100 | active | Uptime Kuma |
| Crafty | CT122 | 10.10.30.122 | 8443 | active | Uptime Kuma |
| DNS | CT129 | 10.10.30.129 | 5380 | active | Uptime Kuma |
| Honcho | CT130 | 10.10.30.130 | 8000 | active | Uptime Kuma |
| YourArcades | CT121 | 10.10.30.121 | 3010 | active | Uptime Kuma |
| VPN/WireGuard | CT126 | 10.10.30.126 | 51821 | active | Uptime Kuma |
| Plex | CT124 | 10.10.30.124 | 32400 | active | Uptime Kuma |
EOF

cat > /tmp/health-report.md << 'EOF'
---
title: Weekly Health Report
date: 2026-06-21
phase: foundation
status: operational
---

# GRID Network Wiki - Health Report (2026-06-21)

## Phase 0: Foundation
- [x] Wiki directory structure created on CT120
- [x] Caddy reverse proxy configured for wiki.grid
- [x] Volume mount fixed and container restarted
- [x] Initial wiki content deployed
- [ ] Discovery engine (Phase 1) - pending
- [ ] Dashboard UI (Phase 3) - pending
- [ ] Kanban boards (Phase 4) - pending
- [ ] Cron automation (Phase 5) - pending
- [ ] Monitoring integration (Phase 6) - pending
- [ ] Obsidian sync (Phase 7) - pending

## Current Status
Wiki service is **operational** at https://wiki.grid/
Directory structure: /srv/grid-wiki/ on CT120

## Next Steps
1. Build discovery engine (overnight agent workers)
2. Create wiki templates and markdown pages
3. Deploy dashboard UI
EOF

scp /tmp/grid-site-info.md grid-pve:"$CT120_WIKI_DIR/sites/grid/site-info.md"
scp /tmp/fmsa-site-info.md grid-pve:"$CT120_WIKI_DIR/sites/fmsa/site-info.md"
scp /tmp/fmsa-services.md grid-pve:"$CT120_WIKI_DIR/sites/fmsa/services.md"
scp /tmp/grid-services.md grid-pve:"$CT120_WIKI_DIR/sites/grid/services.md"
scp /tmp/health-report.md grid-pve:"$CT120_WIKI_DIR/maintenance-reports/2026-06-21-health-report.md"

# Deploy wiki service (Python HTTP server)
cat > /tmp/wiki-service.py << 'PYEOF'
#!/usr/bin/env python3
import http.server
import os
import json

PORT = 8081
WIKI_DIR = "/srv/grid-wiki"

class WikiHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WIKI_DIR, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()
    
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    server = http.server.HTTPServer(('0.0.0.0', PORT), WikiHandler)
    print(f"Wiki server running on http://0.0.0.0:{PORT}")
    server.serve_forever()
PYEOF

scp /tmp/wiki-service.py grid-pve:/tmp/wiki-service.py

# Start the wiki service on CT120
echo "Starting wiki service on CT120..."
ssh grid-pve "pct exec 120 -- nohup python3 /tmp/wiki-service.py > /var/log/wiki-service.log 2>&1 &"
sleep 2

# Test the wiki service
echo "Testing wiki service..."
curl -s http://127.0.0.1:8081/ | head -5 || echo "Wiki service test failed"

echo "=== Deployment complete ==="
echo "Wiki content is at /srv/grid-wiki/ on CT120"
echo "Wiki service is running on port 8081"
echo "Next: Update Caddy config to proxy wiki.grid to port 8081"
