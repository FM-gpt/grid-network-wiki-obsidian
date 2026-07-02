# GRID Wiki Architecture

## Overview
The GRID Wiki is a self-maintaining infrastructure documentation system that:
- Discovers infrastructure automatically
- Maintains wiki content from live data
- Provides real-time monitoring dashboards
- Tracks configuration drift
- Manages change requests

## Architecture

### Components
1. **Discovery Engine** - Scans Proxmox, containers, services
2. **Wiki Engine** - Generates markdown from discovered data
3. **Dashboard** - Real-time monitoring and management UI
4. **Drift Detection** - Compares vault vs overlay
5. **Kanban** - Change request management
6. **Maintenance** - Auto-resolution rules

### Data Flow
```
Proxmox/Infrastructure → Discovery → Data Models → Wiki Generation → Dashboard
                              ↓
                        Drift Detection
                              ↓
                        Change Kanban
```

### Deployment
- Local development on Mac mini
- Production on CT131 (10.10.30.131)
- Reverse proxy via Caddy on grid-pve
- Caddy routes wiki.grid → CT131:8082
