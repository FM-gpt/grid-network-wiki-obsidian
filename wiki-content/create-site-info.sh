#!/bin/bash
# Create site-info.md for GRID site on CT120
cat > /srv/grid-wiki/sites/grid/site-info.md << 'EOF'
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
