---
title: "GRID Infrastructure Overview"
tags: [grid, infrastructure, overview]
category: infrastructure
audience: [human, agent]
status: active
created: 2026-06-21
last_updated: 2026-07-01
confidence: verified-source
last_verified: 2026-07-01T12:00:00Z
---

# GRID Infrastructure Overview

## Overview
The GRID Network provides infrastructure services including:
- Proxmox VE cluster management
- Container orchestration
- Network services
- Monitoring and alerting

## Infrastructure
| Field | Value |
| --- | --- |
| Type | Proxmox VE Cluster |
| Host | grid-pve |
| IP | 10.10.30.22 |
| Nodes | 1 (grid-pve) |
| Containers | 10+ |

## Key Components
- **CT120**: Production services (Caddy, Prometheus, Grafana)
- **CT121**: Development environment
- **CT131**: Wiki service deployment
- **grid-pve**: Proxmox host

## Access
| Method | Address | Notes |
| --- | --- | --- |
| SSH | grid-pve | Proxmox host |
| Proxmox API | https://grid-pve:8006/api2/json | REST API |
| Caddy | http://10.10.30.120:8080 | Reverse proxy |
| Prometheus | http://10.10.30.120:9090 | Monitoring |
| Grafana | http://10.10.30.120:3000 | Dashboards |
| Uptime Kuma | http://10.10.30.120:3001 | Uptime monitoring |

## Configuration
- **Compose file**: /opt/grid-wiki/docker-compose.yml
- **Config path**: /opt/grid-wiki/caddy/
- **Data path**: /opt/grid-wiki/wiki-content/
- **Backups**: ZFS snapshots on CT121

## Monitoring
| Tool | Status | Endpoint |
| --- | --- | --- |
| Prometheus | up | grid-prometheus |
| Uptime Kuma | configured | grid-uptime-kuma |
| Blackbox | not set | N/A |

## Operational Notes
- **Health endpoint**: /api/dashboard/status
- **Restart command**: systemctl restart grid-wiki
- **Snapshot required**: yes
- **Rollback procedure**: Revert to previous commit, restart service

## Agent Instructions
### How to Use This Page
Agents should read this page to understand the GRID infrastructure. Key data for agent tasks:
- **Proxmox API**: Use MCP actions via port 8084
- **Wiki**: Access via /api/wiki-index for structured data
- **Monitoring**: Check /api/monitoring-status for live status
- **Change Management**: Submit changes through Kanban before acting

### Data Access
| Resource | Endpoint | Purpose |
|----------|----------|---------|
| Wiki Index | /api/wiki-index | Structured wiki content list |
| Wiki Pages | /wiki-content/{path} | Raw markdown files |
| Monitoring | /api/monitoring-status | Service health data |
| Proxmox MCP | /api/proxmox/{action} | Container management |

## Change History
| Date | Change | By | Notes |
| --- | --- | --- | --- |
| 2026-07-01 | Initial page created | Tron | Foundation page |
