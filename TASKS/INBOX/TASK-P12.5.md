# TASK: Phase 12.5 — Monitoring Enhancements (P1)

## Context
Phase 12 — UX Audit & Next-Stage Roadmap. All work in `/Users/tron/grid-network-wiki-tool/`

## Tasks

### 12.5.1 - Service hierarchy drill-down
Fix: Reorganize monitoring: Site → Server → Container → Running Services.
Clicking any level drills down to show next level.

### 12.5.2 - Clickable service cards
Fix: Each service clickable to show: how to connect, how to use, setup, access, admin pages.

### 12.5.3 - Service detail enrichment
Fix: Pull together wiki data for each service: LXC info, backups, plugins, DNS, Tailscale, users, updates, cron jobs.
Already in wiki docs — needs to be surfaced.

### 12.5.4 - Make top cards clickable
Fix: Summary cards (Prometheus, Uptime Kuma, Grafana) clickable to see full info.

### 12.5.5 - Investigate Prometheus connection failure
Fix: Check if Prometheus actually running and accessible. Fix "connection failed" error.

### 12.5.6 - Omada webhook monitoring (P2)
Note: Defer — investigate Omada Controller webhooks later.

### 12.5.7 - Monitoring page load performance (P2)
Note: Defer — optimize caching/pagination later.

## Verification
- Monitoring shows hierarchy correctly
- Service cards clickable with details
- Prometheus connection works
- No "connection failed" errors
