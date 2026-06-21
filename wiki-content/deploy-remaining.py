#!/usr/bin/env python3
import base64
import subprocess
import sys

files = {
    "/srv/grid-wiki/sites/grid/site-info.md": """---
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
""",
    "/srv/grid-wiki/sites/fmsa/site-info.md": """---
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
""",
    "/srv/grid-wiki/sites/fmsa/services.md": """---
title: FMSA - Services
site: fmsa
last_updated: 2026-06-21
status: pending
---

# FMSA Services

| Service | Status | IP | Ports | Monitoring |
| --- | --- | --- | --- | --- |
| Pending | TBD | TBD | TBD | TBD |
""",
}

for path, content in files.items():
    encoded = base64.b64encode(content.encode()).decode()
    cmd = f'ssh grid-pve "pct exec 120 -- bash -c \'echo {encoded} | base64 -d > {path}\'"'
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True)

print("Done!")
