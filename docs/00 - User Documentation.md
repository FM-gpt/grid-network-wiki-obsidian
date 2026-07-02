# GRID Network Wiki — Product Documentation

**Version:** 2.0  
**Last Updated:** 2026-06-30  
**Author:** Principal Software Architect (AI)

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [Architecture](#2-architecture)
3. [Screens & Pages](#3-screens--pages)
   - [3.1 Dashboard (Home)](#31-dashboard-home)
   - [3.2 Monitoring](#32-monitoring)
   - [3.3 Drift Reports](#33-drift-reports)
   - [3.4 Change Kanban](#34-change-kanban)
   - [3.5 Maintenance Kanban](#35-maintenance-kanban)
   - [3.6 Wiki Browser](#36-wiki-browser)
   - [3.7 Sites Overview](#37-sites-overview)
   - [3.8 Agent Protocol](#38-agent-protocol)
   - [3.9 Settings](#39-settings)
4. [API Reference](#4-api-reference)
5. [Agent Integration](#5-agent-integration)
6. [Deployment](#6-deployment)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Product Overview

### What Is This?

The GRID Network Wiki is a self-contained, zero-dependency HTTP wiki and operations dashboard. It serves as the central hub for GRID infrastructure documentation, monitoring, change management, and agent-driven operations.

### Key Characteristics

- **Zero external dependencies** — Python 3.11+ stdlib only. No pip packages required.
- **Obsidian vault integration** — reads markdown from your Obsidian vault as the canonical source of truth (SOT), with an overlay directory for wiki-specific content.
- **Real-time monitoring** — SSE (Server-Sent Events) pushes live updates to the dashboard without polling.
- **Service health probes** — HTTP/TCP probes across the GRID network (CT120, CT121, CT122, etc.).
- **Drift detection** — compares vault vs. overlay file counts and checksums.
- **Kanban boards** — change management and maintenance task tracking.
- **Agent query interface** — agents can query wiki content, trigger drift detection, manage kanban, and execute operations via the API.
- **Accessible via Caddy** — served at `https://wiki.grid/` with automatic HTTPS.

### Access Points

| URL | Purpose |
|-----|---------|
| `https://wiki.grid/` | Main dashboard (Caddy reverse proxy) |
| `https://wiki.grid/index.html` | Dashboard home |
| `http://10.10.30.131:8082/` | Direct access to CT131 wiki-service |
| `http://127.0.0.1:8082/` | Local access (Mac mini / dev) |

---

## 2. Architecture

### Directory Structure

```
grid-network-wiki-tool/
├── wiki-service.py              # Main HTTP service (port 8082)
├── wiki-config.yaml             # Service configuration
├── PROJECT-MANIFEST.md          # Project brain (goals, phases)
├── ACTIVE-TASKS.md              # Active task list
├── AGENTS.md                    # Agent protocol
├── dashboard/
│   ├── index.html               # Dashboard home
│   ├── monitoring.html          # Monitoring status
│   ├── drift.html               # Drift reports
│   ├── kanban/
│   │   ├── change.html          # Change kanban
│   │   └── maintenance.html    # Maintenance kanban
│   ├── wiki-browser.html        # Wiki file browser
│   ├── sites.html               # Sites overview
│   ├── agents.html              # Agent protocol
│   ├── settings.html            # Settings (read-write)
│   ├── service.html             # Service detail
│   ├── search-wiki.html         # Wiki search
│   ├── css/
│   │   └── dashboard.css        # Shared styles
│   └── js/
│       ├── api.js               # API client class
│       ├── dashboard.js         # Main app logic
│       ├── sidebar.js           # Sidebar navigation
│       └── chatbox.js           # Chatbot interface
├── wiki-content/                # Overlay wiki root (SOT for wiki-specific files)
│   ├── wiki/                    # Wiki markdown files
│   ├── sites/                   # Site info files
│   ├── maintenance/             # Maintenance tasks
│   ├── change-kanban/           # Change kanban cards
│   └── sync/                    # Sync manifests and drift reports
├── scripts/                     # Utility scripts
├── cron/                        # Cron job definitions
└── tests/                       # Unit tests
```

### Data Flow

```
Obsidian Vault (canonical SOT)
    ↓
wiki-config.yaml (vault path, sync direction)
    ↓
wiki-service.py (reads vault + overlay, serves API + HTML)
    ↓
Dashboard HTML + JS (fetches API, renders pages, SSE updates)
    ↓
Caddy (reverse proxy, HTTPS termination)
    ↓
Browser (https://wiki.grid/)
```

### Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+ (stdlib only) |
| Frontend | Vanilla HTML5 + CSS3 + ES6 JavaScript |
| Data | Markdown (Obsidian vault) + JSON overlays |
| Cache | In-memory TTL dict (thread-safe) |
| Real-time | SSE (Server-Sent Events) |
| Monitoring | Prometheus + Uptime Kuma |
| Deployment | rsync + systemd on CT131 |
| Reverse Proxy | Caddy on grid-pve |

---

## 3. Screens & Pages

### 3.1 Dashboard (Home)

**URL:** `https://wiki.grid/` or `https://wiki.grid/index.html`

**What It Shows:**

| Section | Data Source | Description |
|---------|-------------|-------------|
| Project Status | `/api/manifest` | Current goal, active tasks count, completed phases |
| Goal Progress | `/api/manifest` | Progress bar showing phase completion (0–100%) |
| Active Tasks | `/api/active-tasks` | Task counts: pending, in-progress, completed |
| Monitoring Status | `/api/monitoring-status` | Services up/down count, last check timestamp |

**Where Data Comes From:**

- **Project Status / Goal Progress:** Reads `PROJECT-MANIFEST.md` from the root directory. Parses YAML frontmatter for `current_goal` and `completed_phases`.
- **Active Tasks:** Parses `ACTIVE-TASKS.md` — a markdown table with columns: Task ID, Description, Status, Assignee, Last Updated.
- **Monitoring Status:** Queries Prometheus at `http://10.10.30.120:9090` for target health, plus probes 15 GRID services directly (Caddy, Grafana, PostgreSQL, etc.).

**User Interactions:**

- **Refresh button** (`#refreshBtn`) — re-fetches all dashboard data.
- **Export Wiki button** (`#exportBtn`) — downloads a tar.gz archive of all wiki content.
- **Sidebar navigation** — click any link to navigate to a sub-page.
- **Onboarding modal** — shown once on first visit (tracked via `localStorage['grid-wiki-onboarding-complete']`). Dismissible.

**Agent Interactions:**

- Agents read `PROJECT-MANIFEST.md` to understand current goals and completed phases.
- Agents read `ACTIVE-TASKS.md` to see dev lock and current work.
- Agents can query `/api/agent/query?q=<query>` for wiki content search.
- Agents can trigger drift detection via `POST /api/drift/run`.
- Agents can manage kanban via `/api/kanban/changes/*` and `/api/kanban/maintenance/*`.

---

### 3.2 Monitoring

**URL:** `https://wiki.grid/monitoring.html`

**What It Shows:**

| Section | Data Source | Description |
|---------|-------------|-------------|
| Time Range Selector | UI | `1h`, `6h`, `24h`, `7d` — filters monitoring data (visual only; data is live) |
| Sparkline Charts | UI | SVG sparklines showing service health over time |
| Summary Cards | `/api/monitoring-status` | Total targets, up/down counts, last check |
| Prometheus Targets | `/api/monitoring-status` | Full list of Prometheus job targets with health status |
| Uptime Kuma | `/api/monitoring-status` | Configured monitors, down count, error details |
| Service Probes | `/api/service-status` | Live HTTP/TCP probes for 15 GRID services |

**Where Data Comes From:**

- **Prometheus data:** Queried from `http://10.10.30.120:9090/api/v1/targets`. Fetches all scrape targets and their health.
- **Uptime Kuma:** Queries `http://10.10.30.120:3001/api/status/all` for monitor status.
- **Service Probes:** Direct HTTP/TCP probes to each service URL (Caddy:8080, Grafana:3000, PostgreSQL:5432, etc.). Measures `response_time_ms` and `status` (up/down).

**User Interactions:**

- **Time range selector** — click `1h`, `6h`, `24h`, or `7d` to filter the view (UI filter; data is always live).
- **Refresh** — re-probes all services and re-fetches Prometheus/Uptime Kuma data.
- **Sparkline hover** — hover over sparkline segments to see timestamps and status.

**Agent Interactions:**

- Agents poll `/api/monitoring-status` for infrastructure health.
- Agents can trigger drift detection if monitoring detects anomalies.
- SSE events (`monitoring-update`) push real-time changes to any connected dashboard.

---

### 3.3 Drift Reports

**URL:** `https://wiki.grid/drift.html`

**What It Shows:**

| Section | Data Source | Description |
|---------|-------------|-------------|
| Drift Report List | `/api/drift` | List of all drift reports with dates, vault/overlay file counts |
| Report Details | `/api/drift/<id>` | Full drift analysis: vault-only files, overlay-only files, modified files, mismatches |
| Drift Detection | `POST /api/drift/run` | Trigger manual drift detection |
| Drift Resolution | `POST /api/drift/resolve/<idx>` | Resolve a specific drift entry |

**Where Data Comes From:**

- **Drift reports:** Stored in `wiki-content/sync/drift/` as JSON files (`drift-YYYYMMDD-HHMMSS.json`). Each report contains:
  - `vault_path` and `overlay_path`
  - `vault_files` count, `overlay_files` count
  - `vault_only` list, `overlay_only` list
  - `modified_files` list with hash comparison
  - `drift_detected` boolean
  - `baseline_file` (last-checksums.md5)
- **Drift detection:** Runs `scripts/check-drift.py --report` which compares vault vs. overlay file counts and checksums.

**User Interactions:**

- **Click a report** — expands to show full details (vault-only, overlay-only, modified files).
- **Resolve button** — marks a drift entry as resolved (removes it from active view).
- **Run drift detection** — triggers a manual drift scan.

**Agent Interactions:**

- Agents poll `/api/drift` for drift status.
- Agents can trigger drift detection via `POST /api/drift/run`.
- Agents can resolve drift entries via `POST /api/drift/resolve/<idx>`.
- Cron jobs run drift detection every 6 hours (auto-discovery window 1am–6am).

---

### 3.4 Change Kanban

**URL:** `https://wiki.grid/kanban/change.html`

**What It Shows:**

| Section | Data Source | Description |
|---------|-------------|-------------|
| Pending Board | `/api/kanban/changes` | Change cards in `wiki-content/change-kanban/pending/` |
| Approved Board | `/api/kanban/changes` | Change cards in `wiki-content/change-kanban/approved/` |
| Merged Board | `/api/kanban/changes` | Change cards in `wiki-content/change-kanban/merged/` |
| Reject Board | `/api/kanban/changes` | Change cards in `wiki-content/change-kanban/rejected/` |

**Where Data Comes From:**

- **Kanban cards:** Markdown files with YAML frontmatter in `wiki-content/change-kanban/<status>/`. Each card has:
  - `title`, `type`, `status` (pending/approved/rejected/merged)
  - `submitted`, `reviewed` timestamps
  - `risk` (low/medium/high)
  - Change description in body
- **Board state:** Aggregated from all four directories.

**User Interactions:**

- **Approve button** — moves card from pending → approved (`POST /api/kanban/changes/<id>/approve`).
- **Reject button** — moves card from pending → rejected (`POST /api/kanban/changes/<id>/reject`).
- **Drag & drop** — drag cards between boards (UI interaction; backend updates file location).
- **Click a card** — expands to show full change description.

**Agent Interactions:**

- Agents can submit changes via `POST /api/kanban/changes` (creates a new pending card).
- Agents can approve/reject changes via the respective endpoints.
- Agents monitor kanban boards for pending work items.
- SSE events (`kanban-update`) push real-time board changes.

---

### 3.5 Maintenance Kanban

**URL:** `https://wiki.grid/kanban/maintenance.html`

**What It Shows:**

| Section | Data Source | Description |
|---------|-------------|-------------|
| Open Board | `/api/kanban/maintenance` | Maintenance tasks in `wiki-content/maintenance/active/` |
| In Progress Board | `/api/kanban/maintenance` | Maintenance tasks in `wiki-content/maintenance/in_progress/` |
| Resolved Board | `/api/kanban/maintenance` | Maintenance tasks in `wiki-content/maintenance/resolved/` |
| Maintenance Rules | `/api/kanban/maintenance` | Auto-fix rules from `maintenance-rules/` directory |

**Where Data Comes From:**

- **Maintenance tasks:** Markdown files in `wiki-content/maintenance/<status>/`. Each task has:
  - `title`, `type` (maintenance), `status`
  - `created`, `resolved` timestamps
  - Description in body
- **Maintenance rules:** Markdown files in `maintenance-rules/` directory (e.g., `caddy-route-missing.md`, `disk-space-low.md`). Each rule defines an auto-fix procedure.

**User Interactions:**

- **Resolve button** — moves card from open/in-progress → resolved (`POST /api/kanban/maintenance/<id>/resolve`).
- **Click a card** — expands to show full task description and resolution steps.
- **Click a rule** — expands to show auto-fix procedure.

**Agent Interactions:**

- Agents run maintenance rules automatically when conditions are met.
- Agents can create maintenance tasks via the API.
- Agents monitor kanban boards for pending maintenance.
- SSE events (`kanban-update`) push real-time board changes.

---

### 3.6 Wiki Browser

**URL:** `https://wiki.grid/wiki-browser.html`

**What It Shows:**

| Section | Data Source | Description |
|---------|-------------|-------------|
| Wiki Index | `/api/wiki-index` | Paginated list of all wiki pages with metadata |
| Wiki Page Content | `/api/wiki/<slug>` | Full markdown content for a specific page |
| Wiki Search | `/api/wiki/search?query=<q>&limit=<n>` | Search results across all wiki pages |

**Where Data Comes From:**

- **Wiki index:** Scans `wiki-content/` recursively for `.md` files. Extracts YAML frontmatter (title, tags, category, status, last_updated, size_bytes). Generates `wiki-index.json` for fast lookup.
- **Wiki page content:** Reads the markdown file from `wiki-content/` or vault (if vault is active). Returns raw markdown.
- **Search:** Uses the in-memory search index (`wiki-index.json`) for full-text search across page titles and content.

**User Interactions:**

- **Click a page** — opens the full content in a modal or inline view.
- **Search box** — type to search across all wiki pages.
- **Pagination** — navigate through pages (20 per page).
- **Filter by category** — filter pages by category (infrastructure, monitoring, maintenance, etc.).

**Agent Interactions:**

- Agents query `/api/wiki/<slug>` to read wiki pages.
- Agents use `/api/wiki/search?query=<q>` for full-text search.
- Agents can read `wiki-index.json` for fast page discovery.
- Agents can write to `wiki-content/` to create/update wiki pages.

---

### 3.7 Sites Overview

**URL:** `https://wiki.grid/sites.html`

**What It Shows:**

| Section | Data Source | Description |
|---------|-------------|-------------|
| GRID Site | `/api/sites/overview` | GRID infrastructure: 14 services, monitoring configured |
| FMSA Site | `/api/sites/overview` | FMSA infrastructure: 5 services, monitoring configured |
| Site Details | `wiki-content/sites/<site>/site-info.md` | Full site documentation |
| Service Catalog | `wiki-content/sites/<site>/services.md` | Service list with status |

**Where Data Comes From:**

- **Sites overview:** Reads `wiki-content/sites/` directory. Each site has:
  - `site-info.md` — site metadata (name, status, services count, monitoring status)
  - `services.md` — service list with URLs and status
  - `monitoring-status.json` — Prometheus/Uptime Kuma data for the site
- **Site details:** Reads markdown files from `wiki-content/sites/<site>/`.

**User Interactions:**

- **Click a site** — expands to show full site documentation.
- **Click a service** — opens the service's documentation page.

**Agent Interactions:**

- Agents query `/api/sites/overview` for site discovery.
- Agents read `wiki-content/sites/<site>/site-info.md` for site details.
- Agents monitor service health via `/api/service-status`.

---

### 3.8 Agent Protocol

**URL:** `https://wiki.grid/agents.html`

**What It Shows:**

| Section | Data Source | Description |
|---------|-------------|-------------|
| Agent Protocol | `/api/agents` | Full AGENTS.md content (markdown) |
| Agent Query | `/api/agent/query?q=<q>` | Query results for a specific question |
| Agent Interactions | `/api/agent/interactions` | Log of agent interactions |

**Where Data Comes From:**

- **Agent Protocol:** Reads `AGENTS.md` from the root directory.
- **Agent Query:** Searches wiki content for the query term. Returns matching pages with snippets.
- **Agent Interactions:** Reads `wiki/AGENT-INTERACTIONS.md` (agent interaction log).

**User Interactions:**

- **Read the protocol** — understand how agents should interact with the wiki.
- **Query agents** — type a question to search wiki content.
- **View interaction log** — see historical agent interactions.

**Agent Interactions:**

- Agents follow the AGENTS.md protocol for all interactions.
- Agents can query wiki content via `/api/agent/query?q=<q>`.
- Agents log interactions to `wiki/AGENT-INTERACTIONS.md`.
- Agents read `PROJECT-MANIFEST.md` and `ACTIVE-TASKS.md` for task alignment.

---

### 3.9 Settings

**URL:** `https://wiki.grid/settings.html`

**What It Shows:**

| Section | Data Source | Description |
|---------|-------------|-------------|
| Service Settings | `/api/settings` | Port, host, root, version, uptime |
| Vault Settings | `/api/settings` | Vault path, active status, effective path |
| Overlay Settings | `/api/settings` | Overlay path, enabled status |
| UI Settings | `/api/settings` | Theme, auto-refresh, refresh interval, language |
| Cache Settings | `/api/settings` | Cache enabled, TTL |
| Monitoring Settings | `/api/settings` | Prometheus, Grafana, Kuma URLs |
| Sync Settings | `/api/settings` | Sync enabled, direction, last sync |

**Where Data Comes From:**

- **Settings:** Reads `wiki-config.yaml` from the root directory. Parses YAML into a settings object.
- **Vault path:** Prioritizes `wiki-config.yaml` `vault.path` if set, falls back to `wiki-content` overlay path.
- **Effective path:** The actual path used for reading (vault if active, overlay if not).

**User Interactions:**

- **View settings** — read current configuration.
- **Update UI settings** — change theme, auto-refresh interval, language (saved to `wiki-config.yaml`).
- **Save settings** — POST to `/api/settings` to update configuration.

**Agent Interactions:**

- Agents read `wiki-config.yaml` for service configuration.
- Agents can update settings via `POST /api/settings`.
- Agents monitor sync status for vault/overlay consistency.

---

## 4. API Reference

### Authentication

No authentication required. All endpoints are public.

### Endpoints

| Method | Endpoint | Handler | Purpose | Response Format |
|--------|----------|---------|---------|-----------------|
| GET | `/api/health` | `serve_health_check` | Health check | `{status, uptime_seconds, service_name, started_at}` |
| GET | `/api/dashboard` | `serve_dashboard_stats` | Dashboard aggregate stats | `{wiki_files, wiki_total_size_mb, drift_reports, kanban: {pending, approved, merged}, services}` |
| GET | `/api/manifest` | `serve_manifest` | PROJECT-MANIFEST as JSON | `{current_goal, completed_phases, active_tasks, last_updated}` |
| GET | `/api/active-tasks` | `serve_active_tasks` | Parse ACTIVE-TASKS.md | `{tasks: [{id, title, status, assignee, updated}], counts: {pending, in_progress, completed}}` |
| GET | `/api/monitoring-status` | `serve_monitoring_status` | Prometheus + Uptime Kuma status | `{last_check, prometheus: {...}, uptime_kuma: {...}, services: [...]}` |
| GET | `/api/service-status` | `serve_service_status` | Service health probes | `{services: [{name, url, status, response_time_ms, last_check}]}` |
| GET | `/api/wiki-index` | `_serve_wiki_index` | Wiki page index | `{pages: [...], sites: [...], generated_at}` |
| GET | `/api/wiki-data` | `serve_wiki_pages` | Legacy wiki data | `{pages: [{name, content, title, status}], generated_at}` |
| GET | `/api/wiki/<slug>` | (new) | Wiki page content | `text/markdown` |
| GET | `/api/wiki/search?query=&limit=` | `_serve_search_api` | Search wiki | `{results: [{slug, title, path, category, score}], total}` |
| GET | `/api/search-index` | `_serve_search_index` | Search index | `{words: {word: [pages]}, pages: {slug: {title, path}}}` |
| GET | `/api/drift` | `serve_drift_api` | List drift reports | `{reports: [{id, report_date, type, drift_detected, vault_files, overlay_files, summary}]}` |
| GET | `/api/drift/<id>` | `serve_drift_api` (with ID) | Specific drift report | Full drift report JSON |
| POST | `/api/drift/run` | `serve_drift_api` | Trigger drift detection | `{status, output, stderr}` |
| POST | `/api/drift/resolve/<idx>` | `serve_drift_resolve` | Resolve drift entry | `{resolved, drift_id}` |
| GET | `/api/kanban/changes` | `serve_kanban_change` | Change kanban boards | `{pending: [...], approved: [...], merged: [...], rejected: [...]}` |
| POST | `/api/kanban/changes/<id>/approve` | `serve_kanban_change` | Approve change | `{status, message}` |
| POST | `/api/kanban/changes/<id>/reject` | `serve_kanban_change` | Reject change | `{status, message}` |
| GET | `/api/kanban/maintenance` | `serve_kanban_maintenance` | Maintenance kanban | `{maintenance: [{open, in_progress, resolved}], rules: [...]}` |
| POST | `/api/kanban/maintenance/<id>/resolve` | `serve_kanban_maintenance` | Resolve maintenance | `{status, message}` |
| GET | `/api/sites/overview` | `serve_sites_overview` | Sites overview | `{sites: [{name, status, services, monitoring}]}` |
| GET | `/api/sites-index` | `serve_sites_index` | Sites index | `{sites: [{name, path, status, service_count}]}` |
| GET | `/api/settings` | `_serve_settings` | Service settings | Full settings JSON (see schema above) |
| POST | `/api/settings` | `_update_settings` | Update settings | `{status, updated}` |
| POST | `/api/sync/run` | `serve_sync_run` | Trigger vault sync | `{status, steps: [{name, output}], completed_at}` |
| GET | `/api/sync-status` / `/api/sync/status` | `serve_sync_status` | Last sync status | `{last_sync, direction, files_synced, status}` |
| GET | `/api/proxmox/hardware-metrics` | `serve_proxmox_metrics` | Proxmox hardware | `{cpu, memory, disk, gpu, containers}` |
| GET | `/api/agents` | `serve_agents_protocol` | AGENTS.md content | `text/markdown` |
| POST | `/api/chat/query` | `handle_chat_query` | Chatbot query | `{reply, source}` |
| POST | `/api/chat/action` | `handle_chat_action` | Create kanban from chat | `{status, card_id, message}` |
| GET | `/api/knowledge-base` | `serve_knowledge_base` | Knowledge base | `{entities: [...], syntheses: [...]}` |
| GET | `/api/agent/query?q=` | `serve_agent_query` | Agent query | `{answer, sources: [...]}` |
| GET | `/api/agent/interactions` | `serve_agent_interactions` | Interaction log | `{interactions: [...]}` |
| GET | `/api/wiki-export` | `serve_wiki_export` | Export as tar.gz | `application/x-gzip` (binary) |
| GET | `/sse` | `_handle_sse` | SSE endpoint for real-time updates | `text/event-stream` |
| GET | `/metrics` | `serve_metrics` | Prometheus metrics | `text/plain` (Prometheus format) |

### SSE Events

| Event | Data | Description |
|-------|------|-------------|
| `connected` | `{status: "connected", timestamp: ...}` | SSE connection established |
| `monitoring-update` | `{last_check: ..., services: [...]}` | Monitoring data updated |
| `drift-update` | `{report_id: ..., timestamp: ...}` | New drift report generated |
| `kanban-update` | `{board: "change"|"maintenance", action: "approve"|"reject"|"resolve"}` | Kanban board changed |
| `sync-update` | `{status: "success"|"error", files_synced: ...}` | Sync completed |

---

## 5. Agent Integration

### How Agents Interact

Agents interact with the GRID Wiki through the API. Key integration points:

1. **Task Alignment:**
   - Read `PROJECT-MANIFEST.md` for current goals and completed phases.
   - Read `ACTIVE-TASKS.md` for current work items.
   - Follow the AGENTS.md protocol for all interactions.

2. **Wiki Content:**
   - Query `/api/wiki/<slug>` to read specific pages.
   - Use `/api/wiki/search?query=<q>` for full-text search.
   - Read `wiki-index.json` for fast page discovery.
   - Write to `wiki-content/` to create/update pages.

3. **Infrastructure Monitoring:**
   - Poll `/api/monitoring-status` for health data.
   - Poll `/api/service-status` for live service probes.
   - React to SSE events (`monitoring-update`) for real-time changes.

4. **Change Management:**
   - Submit changes via `POST /api/kanban/changes`.
   - Approve/reject changes via respective endpoints.
   - Monitor kanban boards for pending work.

5. **Drift Detection:**
   - Poll `/api/drift` for drift status.
   - Trigger drift detection via `POST /api/drift/run`.
   - Resolve drift entries via `POST /api/drift/resolve/<idx>`.

6. **Cron Jobs:**
   - Auto-discovery runs 1am–6am (drift detection, sync).
   - Maintenance worker runs on schedule.
   - Sync runs on schedule (vault ↔ overlay).

### Agent Best Practices

- **NEVER** read the entire project directory. Only read files explicitly linked in the Manifest or your current task.
- **ALWAYS** follow the AGENTS.md protocol.
- **USE** the project manifest to stay aligned with current goals.
- **LOG** all interactions to `wiki/AGENT-INTERACTIONS.md`.
- **POLL** `/api/health` to verify service availability before making requests.

---

## 6. Deployment

### CT131 Deployment

1. **Stop existing service:**
   ```bash
   systemctl stop wiki-service
   ```

2. **Pull latest code:**
   ```bash
   cd /srv/grid-wiki-tool
   git pull origin main
   ```

3. **Restart service:**
   ```bash
   systemctl start wiki-service
   ```

4. **Verify:**
   ```bash
   curl -s http://127.0.0.1:8082/api/health
   ```

### Caddy Configuration

Caddy on grid-pve routes `wiki.grid` → `http://10.10.30.131:8082`:

```caddyfile
wiki.grid {
    reverse_proxy http://10.10.30.131:8082
    tls internal
}
```

### Local Development

```bash
cd /Users/tron/grid-network-wiki-tool
python3 -u wiki-service.py
# Access at http://127.0.0.1:8082/
```

---

## 7. Troubleshooting

### Dashboard Shows "Unable to Load"

- **Cause:** API endpoint returned an error or the JS failed to execute.
- **Fix:** Check browser console (F12) for errors. Verify `/api/health` responds correctly.

### Service Status Shows "down" for GRID Wiki

- **Cause:** The probe targets `http://10.10.30.131:8082` — if the service is running on a different port or host, the probe will fail.
- **Fix:** Verify `lsof -i:8082` shows the service listening. Check `wiki-config.yaml` for correct port.

### Drift Reports Show Discrepancies

- **Cause:** Vault and overlay directories have different file counts.
- **Fix:** Run `scripts/check-drift.py --report` manually. Review `wiki-content/sync/drift/` for details.

### SSE Not Connecting

- **Cause:** Browser doesn't support EventSource, or the SSE endpoint is blocked.
- **Fix:** Check browser console for EventSource errors. Verify `/sse` endpoint responds.

### Wiki Pages Not Found

- **Cause:** Page slug doesn't match any file in `wiki-content/` or vault.
- **Fix:** Check `wiki-index.json` for available pages. Verify file exists in the correct directory.

### Settings Page Shows "N/A" for Vault Path

- **Cause:** `wiki-config.yaml` doesn't have a vault path configured.
- **Fix:** Edit `wiki-config.yaml` to set `vault.path` to your Obsidian vault directory.

---

## Appendix: Glossary

| Term | Definition |
|------|------------|
| **Vault** | Obsidian vault directory (canonical source of truth) |
| **Overlay** | `wiki-content/` directory (wiki-specific files, sync'd from vault) |
| **Drift** | Difference between vault and overlay file counts/contents |
| **Kanban** | Change management or maintenance task board |
| **SSE** | Server-Sent Events (real-time push from server to browser) |
| **Caddy** | Reverse proxy that routes `wiki.grid` → `http://10.10.30.131:8082` |
| **GRID** | Internal network infrastructure (Proxmox, services, etc.) |
| **FMSA** | FMSA office infrastructure |
| **CT** | Container (Proxmox LXC) |
| **SOT** | Source of Truth |
| **TTL** | Time-To-Live (cache expiration) |

---

*End of documentation.*
