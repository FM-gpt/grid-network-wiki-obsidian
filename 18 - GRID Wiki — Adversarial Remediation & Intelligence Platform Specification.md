# GRID Wiki — Adversarial Remediation & Intelligence Platform Specification

**Date:** 2026-06-30
**Author:** Principal Software Architect (AI)
**Status:** Specification for automated agent execution
**Scope:** GRID Network Wiki — P0/P1 UX fixes, real-time monitoring, self-awareness platform

---

## PART 1: GLOBAL ARCHITECTURE SPECIFICATION

### Target Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Backend | Python 3.11+ (stdlib only) | No-framework HTTP server, zero-deploy dependencies |
| Frontend | Vanilla HTML5 + CSS3 + ES6 JavaScript | No framework deps, works offline, minimal surface |
| Data | Markdown files (Obsidian vault) + JSON overlays | Vault is canonical SOT; JSON for fast-lookup structures |
| Cache | In-memory TTL dict (thread-safe) | Simple, no external deps, sufficient for 10-page dashboard |
| Real-time | SSE (Server-Sent Events) via wiki-service-sse.py | Push updates to dashboard without polling |
| Monitoring | Prometheus (CT120:9090) + Uptime Kuma (CT120:3001) | Reuse existing, not build custom |
| Deployment | rsync + systemd on CT131 | Current pattern, proven |
| Reverse Proxy | Caddy on grid-pve | Routes wiki.grid -> CT131:8082 |

### Directory Structure

```
grid-network-wiki-tool/                          # Local workspace (Mac)
├── wiki-service.py                              # Main HTTP service (port 8082)
├── wiki-service-sse.py                          # SSE bridge (port 8083)
├── wiki-config.yaml                             # Service configuration
├── wiki-index.json                              # Fast wiki index (generated)
├── wiki-data.json                               # Legacy alias
├── PROJECT-MANIFEST.md                          # Project brain
├── ACTIVE-TASKS.md                              # Dev lock
├── AGENTS.md                                    # Agent protocol
├── 18 - GRID Wiki — Adversarial Remediation & Intelligence Platform Specification.md
├── dashboard/
│   ├── index.html                               # Main dashboard
│   ├── monitoring.html                          # Monitoring status
│   ├── drift.html                               # Drift reports
│   ├── kanban/
│   │   ├── change.html                          # Change kanban
│   │   └── maintenance.html                     # Maintenance kanban
│   ├── wiki-browser.html                        # Wiki file browser
│   ├── sites.html                               # Sites overview
│   ├── agents.html                              # Agent protocol
│   ├── settings.html                            # Settings (read-write)
│   ├── service.html                             # Service detail
│   ├── search-wiki.html                         # Wiki search
│   ├── css/
│   │   ├── dashboard.css                        # Shared styles
│   │   └── sidebar.css                          # Sidebar styles
│   └── js/
│       ├── api.js                               # API client class
│       ├── dashboard.js                         # Main app logic
│       ├── sidebar.js                           # Sidebar navigation
│       └── chatbox.js                           # Chatbot interface
├── wiki-content/                                # Overlay wiki root
│   ├── wiki/                                    # Wiki markdown files
│   ├── sites/
│   │   ├── grid/
│   │   │   ├── monitoring-status.json
│   │   │   ├── services.md
│   │   │   └── site-info.md
│   │   ├── fmsa/
│   │   │   ├── monitoring-status.json
│   │   │   ├── services.md
│   │   │   └── site-info.md
│   │   └── _index.md
│   ├── maintenance/
│   │   ├── active/                              # Open maintenance cards
│   │   ├── resolved/                            # Resolved cards
│   │   └── health-reports/                      # Generated reports
│   ├── change-kanban/
│   │   ├── pending/
│   │   ├── approved/
│   │   └── merged/
│   ├── sync/
│   │   ├── drift/                               # Drift report JSON files
│   │   ├── manifest.json                        # Sync manifest
│   │   └── last-checksums.md5                   # Baseline checksums
│   ├── wiki-templates/                          # Page templates
│   └── raw/                                     # Live state snapshots
├── maintenance-rules/                           # Auto-fix rules
│   ├── caddy-route-missing.md
│   ├── container-not-starting.md
│   ├── disk-space-low.md
│   ├── dns-resolution-failed.md
│   ├── monitoring-missing.md
│   ├── prometheus-target-down.md
│   ├── service-health-check-failed.md
│   └── zfs-snapshot-stale.md
├── scripts/
│   ├── sync-obsidian.sh / sync-obsidian-vault.py
│   ├── drift-detect.sh / check-drift.py
│   ├── build-search-index.py
│   ├── deploy-wiki.sh / deploy-ct130.sh
│   └── wiki-service.py / wiki-service-dashboard.py
├── cron/                                        # Cron scripts
│   ├── discovery.sh
│   ├── drift-detect.sh
│   ├── auto-discovery.sh
│   ├── maintenance-worker.sh
│   ├── sync-obsidian.sh
│   └── submit-change.sh
├── tests/                                       # Unit tests
│   ├── server-static.test.js
│   ├── status-adapter.test.js
│   ├── backup-status.test.js
│   └── hardware-status.test.js
├── Dockerfile
├── docker-compose.yml
├── docker-compose.ct131.yml
├── caddy/
│   └── Caddyfile
├── mcp/
│   └── proxmox-config.yaml
├── docs/
│   └── architecture.md, api.md, data-model.md, ...
└── wiki/                                        # Agent-queried wiki
    ├── INDEX.md
    ├── GRID-Infrastructure-Overview.md
    └── Sites-Overview.md
```

### Data Models / Schema

#### Wiki Page Frontmatter (YAML — on every .md file)

```yaml
---
title: "Page Title"
tags: [grid, proxmox, infrastructure]
category: infrastructure|monitoring|maintenance|security|networking|services|backup|tasks|planning|template
audience: [human, agent]
status: active|draft|deprecated|review
created: 2026-06-XX
last_updated: 2026-06-XX
---
```

#### Wiki Index (JSON — generated, cached)

```json
{
  "pages": [
    {
      "slug": "grid-infrastructure-overview",
      "title": "GRID Infrastructure Overview",
      "path": "wiki/grid-infrastructure-overview.md",
      "category": "infrastructure",
      "tags": ["grid", "infrastructure"],
      "status": "active",
      "last_updated": "2026-06-28T00:00:00Z",
      "size_bytes": 4096
    }
  ],
  "sites": [
    {
      "name": "GRID",
      "path": "sites/grid",
      "status": "active",
      "service_count": 12,
      "monitoring_status": "configured"
    }
  ],
  "generated_at": "2026-06-30T12:00:00Z"
}
```

#### Active Tasks (Markdown table in ACTIVE-TASKS.md)

```markdown
|| Task ID | Description | Status | Assignee | Last Updated |
||---|---|---|---|---|
|| TASK-01 | Fix Active Tasks API | In Progress | SELF | 2026-06-30 |
```

#### Project Manifest (YAML frontmatter in PROJECT-MANIFEST.md)

```yaml
---
title: "PROJECT MANIFEST"
current_goal: "Sprint 18: Adversarial Remediation"
completed_phases: [0,1,2,3,4,5,6,7,8,9]
last_updated: 2026-06-30 12:00 ACST
---
```

#### Monitoring Status (JSON — served by /api/monitoring-status)

```json
{
  "last_check": "2026-06-30T12:00:00Z",
  "prometheus": {
    "url": "http://10.10.30.120:9090",
    "total_targets": 73,
    "up": 69,
    "down": 4,
    "down_targets": [
      {"job": "grid-llamacpp-gpu", "instance": "10.10.30.128:8080", "health": "down", "notes": "GPU service down (expected)"},
      {"job": "grid-llamacpp-gpu", "instance": "10.10.30.128:8081", "health": "down", "notes": "GPU service down (expected)"},
      {"job": "grid-lxcs", "instance": "10.10.30.125:9100", "health": "down", "notes": "CT125 placeholder (expected)"},
      {"job": "grid-test-env-cadvisor", "instance": "10.10.30.121:8081", "health": "down", "notes": "Test env cadvisor (expected)"}
    ]
  },
  "uptime_kuma": {
    "url": "http://10.10.30.120:3001",
    "configured": 20,
    "down": 3
  },
  "services": [
    {
      "name": "caddy",
      "type": "http",
      "url": "http://10.10.30.120:8080",
      "status": "up",
      "last_check": "2026-06-30T12:00:00Z",
      "response_time_ms": 15,
      "prometheus_job": "grid-admin-http",
      "port": 8080
    }
  ]
}
```

#### Drift Report (JSON — stored in wiki-content/sync/drift/)

```json
{
  "timestamp": "2026-06-30T02:00:00Z",
  "vault_path": "/Users/tron/Documents/Obsidian Vault/GRID Network Wiki",
  "overlay_path": "/Users/tron/grid-network-wiki-tool/wiki-content",
  "vault_files": 152,
  "overlay_files": 198,
  "vault_only": ["file-a.md", "file-b.md"],
  "overlay_only": ["file-c.md", "file-d.md"],
  "modified_files": [
    {"path": "file-e.md", "vault_hash": "abc123", "overlay_hash": "def456"}
  ],
  "drift_detected": true,
  "baseline_file": "last-checksums.md5",
  "baseline_entries": 198
}
```

#### Kanban Card (Markdown with YAML frontmatter)

```markdown
---
title: "Change Summary"
type: change
status: pending|approved|rejected|merged
submitted: "2026-06-30T00:00:00Z"
reviewed: null
risk: low|medium|high
---
Change description here.
```

#### Settings (JSON — served by /api/settings)

```json
{
  "service": {
    "port": 8082,
    "host": "0.0.0.0",
    "root": "/Users/tron/grid-network-wiki-tool",
    "start_time": "2026-06-30T00:00:00Z",
    "uptime_seconds": 86400,
    "version": "2.0"
  },
  "vault": {
    "enabled": true,
    "path": "/Users/tron/Documents/Obsidian Vault/GRID Network Wiki",
    "active": true
  },
  "overlay": {
    "enabled": true,
    "path": "/Users/tron/grid-network-wiki-tool/wiki-content"
  },
  "ui": {
    "theme": "light",
    "auto_refresh": true,
    "refresh_interval_seconds": 30,
    "language": "en",
    "sidebar_collapsed": false
  },
  "cache": {
    "enabled": true,
    "ttl_seconds": 300
  },
  "monitoring": {
    "prometheus_url": "http://10.10.30.120:9090",
    "grafana_url": "https://grafana.grid/",
    "kuma_url": "https://kuma.grid/"
  },
  "sync": {
    "enabled": true,
    "direction": "vault_to_overlay",
    "last_sync": "2026-06-30T00:00:00Z"
  }
}
```

#### Drift Report List Format (for /api/drift endpoint)

```json
{
  "reports": [
    {
      "id": "drift-20260630-020000",
      "report_date": "2026-06-30T02:00:00Z",
      "timestamp": "2026-06-30T02:00:00Z",
      "type": "drift",
      "drift_detected": true,
      "vault_files": 152,
      "overlay_files": 198,
      "vault_only_count": 33,
      "overlay_only_count": 79,
      "modified_count": 2,
      "title": "Vault/Overlay Sync Drift",
      "summary": "33 vault-only files, 79 overlay-only files, 2 modified"
    }
  ]
}
```

### System Boundaries & Contracts

#### API Endpoints

| Method | Endpoint | Handler | Purpose | Response Format |
|--------|----------|---------|---------|-----------------|
| GET | `/api/health` | `serve_health_check` | Health check | `{status, uptime_seconds, service_name, started_at}` |
| GET | `/api/dashboard` | `serve_dashboard_stats` | Dashboard aggregate stats | `{wiki_pages, drift_reports, kanban_pending, kanban_approved, kanban_merged, services}` |
| GET | `/api/manifest` | `serve_manifest` | PROJECT-MANIFEST as JSON | `{current_goal, completed_phases, active_tasks, last_updated}` |
| GET | `/api/active-tasks` | `serve_active_tasks` | Parse ACTIVE-TASKS.md | `{tasks: [{id, title, status, assignee, updated}], counts: {pending, in_progress, completed}}` |
| GET | `/api/monitoring-status` | `serve_monitoring_status` | Prometheus + Uptime Kuma status | `{last_check, prometheus: {...}, uptime_kuma: {...}, services: [...]}` |
| GET | `/api/service-status` | `serve_service_status` | Service health probes | `{services: [{name, url, status, response_time_ms, last_check}]}` |
| GET | `/api/wiki-index` | `_serve_wiki_index` | Wiki page index | `{pages: [...], sites: [...], generated_at}` |
| GET | `/api/wiki-data` | `serve_wiki_pages` | Legacy wiki data | `{pages: [{name, content, title, status}], generated_at}` |
| GET | `/api/wiki/<slug>` | (new) | Wiki page content | `text/markdown` |
| GET | `/api/wiki/search?query=&limit=` | `_serve_search_api` | Search wiki | `{results: [{slug, title, path, category, score}], total}` |
| GET | `/api/search-index` | `_serve_search_index` | Search index | `{words: {word: [pages]}, pages: {slug: {title, path}}}` |
| GET | `/api/drift` | `serve_drift_api` (no ID) | List drift reports | `{reports: [{id, report_date, type, drift_detected, vault_files, overlay_files, summary}]}` |
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
| GET | `/metrics` | `serve_metrics` | Prometheus metrics | `text/plain` (Prometheus format) |

#### Internal Module Interfaces

```python
# wiki-service.py — WikiHandler class
class WikiHandler(http.server.SimpleHTTPRequestHandler):
    # Core methods
    def do_GET(self)          # Route all GET requests
    def do_POST(self)         # Route all POST requests
    def do_OPTIONS(self)      # CORS preflight
    def _send_cors_headers()  # CORS headers helper
    def _send_json(code, data) # JSON response helper
    def _serve_file(path, ct)  # Static file serving

    # API handlers (one per endpoint)
    def serve_health_check(self) -> dict
    def serve_dashboard_stats(self) -> dict
    def serve_manifest(self) -> dict
    def serve_active_tasks(self) -> dict
    def serve_monitoring_status(self) -> dict
    def serve_service_status(self) -> dict
    def _serve_wiki_index(self) -> dict
    def serve_wiki_pages(self) -> dict
    def _serve_search_api(self, path) -> dict
    def _serve_search_index(self) -> dict
    def serve_drift_api(self, path) -> dict
    def serve_drift_resolve(self, idx) -> dict
    def serve_kanban_change(self) -> dict
    def serve_kanban_maintenance(self) -> dict
    def serve_sites_overview(self) -> dict
    def serve_sites_index(self) -> dict
    def _serve_settings(self) -> dict
    def _update_settings(self) -> dict
    def serve_sync_run(self) -> dict
    def serve_sync_status(self) -> dict
    def serve_proxmox_metrics(self) -> dict
    def serve_agents_protocol(self) -> str
    def handle_chat_query(self) -> dict
    def handle_chat_action(self) -> dict
    def handle_honcho_proxy(self, path) -> dict
    def serve_wiki_export(self) -> bytes
    def serve_metrics(self) -> str

# wiki-service-sse.py — SSEBridge class
class SSEBridge:
    def __init__(self, port, wiki_service)
    def start(self)
    def stop(self)
    def broadcast(self, event, data)
    def subscribe(self, callback)
    def unsubscribe(self, callback)
    def trigger_monitoring_update(self)
    def trigger_drift_update(self)
    def trigger_kanban_update(self)
    def trigger_chat_update(self)

# dashboard/js/api.js — WikiAPI class
class WikiAPI {
    static async getWikiIndex()
    static async getWikiPage(slug)
    static async searchWiki(query, limit)
    static async getActiveTasks()
    static async getMonitoringStatus()
    static async getDriftReport(date)
    static async getDriftLatest()
    static async getDriftList()
    static async getKanbanChanges()
    static async getKanbanMaintenance()
    static async approveChange(cardId)
    static async rejectChange(cardId)
    static async resolveMaintenance(cardId)
    static async chatQuery(message)
    static async chatAction(message)
    static async syncVaultToOverlay()
    static async getSettings()
    static async updateSettings(settings)
    static async exportWiki()
    static async getManifest()
    static async getAgentsProtocol()
    static async queryWiki(q)
    static async getSitesOverview()
}

# dashboard/js/dashboard.js — Dashboard class
class Dashboard {
    constructor()
    init()
    loadDashboardIndex()       // Dashboard home
    loadWikiBrowser()          // Wiki browser
    loadMonitoringPage()       // Monitoring
    loadDriftPage()            // Drift reports
    loadChangeKanban()         // Change kanban
    loadMaintenanceKanban()    // Maintenance kanban
    loadSitesPage()            // Sites overview
    loadAgentsPage()           // Agent protocol
    loadSettingsPage()         // Settings
    refreshPage()
    exportWiki()
    showNotification(msg, type)
}
```

---

## PART 2: ATOMIC TASK MANIFEST

#### [TASK-18-001]: Fix Active Tasks API — Parse ACTIVE-TASKS.md correctly

- Component/Scope: `wiki-service.py` — `serve_active_tasks()` method
- Core Objective: Replace the current broken implementation (which reads change-kanban files) with a correct parser that reads ACTIVE-TASKS.md and returns the task list with accurate counts.

- Dependencies: None

- Context Contextual Payload:
```python
# CURRENT (BROKEN) IMPLEMENTATION — replace entirely:
def serve_active_tasks(self):
    # Currently reads change-kanban/pending and change-kanban/approved
    # This is wrong — should read ACTIVE-TASKS.md
    kanban_pending = ROOT / 'wiki-content' / 'change-kanban' / 'pending'
    ...

# TARGET IMPLEMENTATION:
def serve_active_tasks(self):
    """Serve /api/active-tasks — parse ACTIVE-TASKS.md markdown table."""
    tasks_file = ROOT / 'ACTIVE-TASKS.md'
    if not tasks_file.exists():
        self._send_json(200, {"tasks": [], "counts": {"pending": 0, "in_progress": 0, "completed": 0}})
        return

    content = tasks_file.read_text()
    lines = content.split('\n')
    tasks = []
    counts = {"pending": 0, "in_progress": 0, "completed": 0}

    for line in lines:
        # Match table rows: || TASK-01 | Description | In Progress | SELF | 2026-06-30 |
        if line.strip().startswith('||'):
            cells = line.strip().strip('|').split('||')
            # Filter empty cells
            cells = [c.strip() for c in cells if c.strip()]
            if len(cells) >= 4:
                task_id = cells[0].replace('TASK-', 'TASK-').replace('T', 'TASK-').strip()
                # Clean task ID: handle T12-01 format
                if task_id.startswith('T') and '-' in task_id:
                    task_id = task_id.replace('T', 'TASK-')
                title = cells[1]
                status_raw = cells[2]
                assignee = cells[3] if len(cells) > 3 else ''
                updated = cells[4] if len(cells) > 4 else ''

                # Normalize status
                status = status_raw.lower().replace(' ', '_')
                if 'complete' in status or 'done' in status or 'complet' in status:
                    status = 'completed'
                elif 'progress' in status or 'in_progress' in status or 'active' in status:
                    status = 'in_progress'
                elif 'park' in status:
                    status = 'pending'
                else:
                    status = 'pending'

                if status == 'completed':
                    counts['completed'] += 1
                elif status == 'in_progress':
                    counts['in_progress'] += 1
                else:
                    counts['pending'] += 1

                tasks.append({
                    "id": task_id,
                    "title": title,
                    "status": status,
                    "assignee": assignee,
                    "last_updated": updated
                })

    self._send_json(200, {
        "tasks": tasks,
        "counts": counts,
        "total": len(tasks)
    })
```

- Strict Evaluation Criteria:
  1. GET /api/active-tasks returns HTTP 200 with JSON containing `tasks` array and `counts` object
  2. `counts.pending` equals number of rows with "Parked" status in ACTIVE-TASKS.md
  3. `counts.in_progress` equals number of rows with "In Progress" status
  4. Dashboard "Active Tasks" card displays correct counts matching kanban board data
  5. No console errors when dashboard loads data via WikiAPI.getActiveTasks()

#### [TASK-18-002]: Fix Goal Progress Math — Cap progress at 100%

- Component/Scope: `dashboard/js/dashboard.js` — `loadDashboardData()` method, lines 52-72
- Core Objective: Fix the goal progress calculation so it never exceeds 100%, and display the actual phase count correctly.

- Dependencies: [TASK-18-001]

- Context Contextual Payload:
```javascript
// BROKEN CODE (current):
const totalPhases = 9;
const completedPhases = manifest.completed_phases?.length || 0;
const progress = (completedPhases / totalPhases) * 100;
// When completed_phases = [0,1,2,3,4,5,6,7,8,9] = 10 items:
// progress = (10/9) * 100 = 111.11% — shows "11/9 = 122%"

// FIXED CODE:
const totalPhases = manifest.completed_phases?.length || 10; // Use actual planned count
const completedPhases = manifest.completed_phases?.length || 0;
const progress = Math.min(100, Math.max(0, (completedPhases / totalPhases) * 100));
// Also: if completedPhases >= totalPhases, show "100% (complete)" not "111%"
const progressText = completedPhases >= totalPhases
    ? `${completedPhases}/${totalPhases} phases complete (100%)`
    : `${completedPhases}/${totalPhases} phases complete (${progress.toFixed(0)}%)`;
```

- Strict Evaluation Criteria:
  1. When 10 phases are completed out of 10 planned, progress shows "100%" not "111%"
  2. When 5 phases are completed out of 10 planned, progress shows "50%"
  3. Progress bar width never exceeds 100%
  4. Dashboard "Goal Progress" card displays accurate percentage

#### [TASK-18-003]: Fix Monitoring Status — Show real Prometheus data

- Component/Scope: `wiki-service.py` — `serve_monitoring_status()` method; `dashboard/js/dashboard.js` — `loadDashboardData()` monitoring section
- Core Objective: Replace static monitoring status with live Prometheus API queries and real service health probes.

- Dependencies: [TASK-18-001], [TASK-18-002]

- Context Contextual Payload:
```python
# TARGET: serve_monitoring_status() should query Prometheus API directly:
def serve_monitoring_status(self):
    """Serve monitoring status — query Prometheus API live."""
    prom_url = "http://10.10.30.120:9090/api/v1/targets"
    uptime_url = "http://10.10.30.120:3001/api/monitors"

    # Query Prometheus for target status
    prom_data = {"total_targets": 0, "up": 0, "down": 0, "down_targets": []}
    try:
        import urllib.request
        req = urllib.request.Request(prom_url)
        resp = urllib.request.urlopen(req, timeout=5)
        prom_json = json.loads(resp.read())
        if prom_json.get('status') == 'success':
            targets = prom_json.get('data', {}).get('activeTargets', [])
            prom_data['total_targets'] = len(targets)
            prom_data['up'] = sum(1 for t in targets if t.get('health') == 'up')
            prom_data['down'] = prom_data['total_targets'] - prom_data['up']
            prom_data['down_targets'] = [
                {
                    "job": t.get('labels', {}).get('job', 'unknown'),
                    "instance": t.get('labels', {}).get('instance', 'unknown'),
                    "health": t.get('health', 'unknown'),
                    "last_error": t.get('lastError', '')
                }
                for t in targets if t.get('health') != 'up'
            ]
    except Exception as e:
        prom_data['error'] = str(e)

    # Query Uptime Kuma
    kuma_data = {"configured": 0, "down": 0}
    try:
        req = urllib.request.Request(uptime_url)
        resp = urllib.request.urlopen(req, timeout=5)
        kuma_json = json.loads(resp.read())
        kuma_data['configured'] = len(kuma_json) if isinstance(kuma_json, list) else 0
        kuma_data['down'] = sum(1 for m in kuma_json if m.get('status') != 1) if isinstance(kuma_json, list) else 0
    except Exception:
        kuma_data['error'] = 'unreachable'

    # Probe individual services
    service_targets = [
        {"name": "Prometheus", "url": "http://10.10.30.120:9090", "port": 9090},
        {"name": "Grafana", "url": "http://10.10.30.120:3000", "port": 3000},
        {"name": "Uptime Kuma", "url": "http://10.10.30.120:3001", "port": 3001},
        {"name": "Caddy", "url": "http://10.10.30.120:8080", "port": 8080},
        {"name": "Portainer", "url": "http://10.10.30.120:9443", "port": 9443},
        {"name": "Ollama", "url": "http://10.10.30.120:11434", "port": 11434},
        {"name": "Open WebUI", "url": "http://10.10.30.120:3002", "port": 3002},
        {"name": "PostgreSQL", "url": "http://10.10.30.120:5432", "port": 5432},
        {"name": "Redis", "url": "http://10.10.30.120:6379", "port": 6379},
        {"name": "Minecraft", "url": "http://10.10.30.120:25565", "port": 25565},
        {"name": "Samba", "url": "http://10.10.30.120:445", "port": 445},
        {"name": "GRID Wiki", "url": "http://10.10.30.131:8082", "port": 8082},
    ]

    services = []
    def probe_service(svc):
        try:
            import urllib.request
            start = time.time()
            req = urllib.request.Request(svc['url'], method='HEAD')
            resp = urllib.request.urlopen(req, timeout=3)
            elapsed = int((time.time() - start) * 1000)
            return {
                "name": svc['name'],
                "type": "http",
                "url": svc['url'],
                "status": "up",
                "last_check": datetime.datetime.utcnow().isoformat() + "Z",
                "response_time_ms": elapsed,
                "prometheus_job": f"grid-admin-{svc['name'].lower()}"
            }
        except Exception:
            return {
                "name": svc['name'],
                "type": "http",
                "url": svc['url'],
                "status": "down",
                "last_check": datetime.datetime.utcnow().isoformat() + "Z",
                "response_time_ms": None,
                "prometheus_job": f"grid-admin-{svc['name'].lower()}"
            }

    # Use threading for parallel probes
    import threading
    results = {}
    def do_probe(svc):
        results[svc['name']] = probe_service(svc)
    threads = [threading.Thread(target=do_probe, args=(s,)) for s in service_targets]
    for t in threads: t.start()
    for t in threads: t.join(timeout=10)
    services = [results[k] for k in sorted(results.keys())]

    self._send_json(200, {
        "last_check": datetime.datetime.utcnow().isoformat() + "Z",
        "prometheus": prom_data,
        "uptime_kuma": kuma_data,
        "services": services
    })
```

- Strict Evaluation Criteria:
  1. GET /api/monitoring-status returns HTTP 200 with live Prometheus target data
  2. `prometheus.total_targets` matches actual Prometheus target count (73)
  3. `prometheus.up` matches actual UP count (69)
  4. `prometheus.down` lists the 4 expected down targets with correct job/instance
  5. Dashboard "Monitoring Status" card shows real "69/73 services up" not "0/12"
  6. Monitoring page tables show actual response times, not "N/A"
  7. All 12 services show correct up/down status

#### [TASK-18-004]: Fix Drift Reports JS Error — Normalize report list format

- Component/Scope: `wiki-service.py` — `serve_drift_api()` (list endpoint); `dashboard/js/dashboard.js` — `loadDriftPage()`
- Core Objective: Fix the drift reports API to return a consistent format that the frontend can render without leaking `[object Object]` to the UI.

- Dependencies: [TASK-18-001], [TASK-18-002]

- Context Contextual Payload:
```python
# TARGET: serve_drift_api() list endpoint (when no report_id provided):
def serve_drift_api(self, path):
    drift_dir = ROOT / 'wiki-content' / 'sync' / 'drift'
    if not drift_dir.exists():
        self.send_error(404, "No drift data available")
        return

    if '/api/drift/run' in path:
        # ... (existing drift run logic unchanged)
        return

    report_id = path.split('/api/drift/')[1] if '/api/drift/' in path else ''
    if report_id:
        # ... (existing single report logic unchanged)
        return

    # LIST ALL DRIFT REPORTS — normalize to consistent format
    reports = []
    for dr in sorted(drift_dir.glob('*.json')):
        try:
            with open(dr) as f:
                data = json.load(f)
            # Normalize: each report must have consistent fields
            normalized = {
                "id": dr.stem,
                "report_date": data.get("timestamp", data.get("report_date", "Unknown")),
                "timestamp": data.get("timestamp", data.get("report_date", "Unknown")),
                "type": "drift",
                "drift_detected": data.get("drift_detected", False),
                "vault_files": data.get("vault_files", 0),
                "overlay_files": data.get("overlay_files", 0),
                "vault_only_count": data.get("vault_only_count", len(data.get("vault_only", []))),
                "overlay_only_count": data.get("overlay_only_count", len(data.get("overlay_only", []))),
                "modified_count": len(data.get("modified_files", [])),
                "files_changed": data.get("files_changed", 0),
                "files_added": data.get("files_added", 0),
                "files_removed": data.get("files_removed", 0),
                "title": data.get("summary", {}).get("title", f"Drift: {dr.stem}"),
                "summary": data.get("summary", {}).get("message", "") or "",
                "notes": data.get("notes", [])
            }
            reports.append(normalized)
        except Exception:
            pass

    self.send_response(200)
    self.send_header('Content-Type', 'application/json')
    self.send_header('Access-Control-Allow-Origin', '*')
    self.end_headers()
    self.wfile.write(json.dumps({"reports": reports}, indent=2).encode())
```

```javascript
// TARGET: loadDriftPage() — safe rendering, no object leaks:
async loadDriftPage() {
    this.pageTitle.textContent = 'Drift Reports';
    this.content.innerHTML = `
      <div class="card">
        <h3>Recent Drift Reports</h3>
        <div id="driftList">Loading...</div>
      </div>
    `;
    try {
        const driftData = await WikiAPI.getDriftList();
        const reports = driftData.reports || driftData || [];
        const list = document.getElementById('driftList');
        if (!reports.length) {
            list.innerHTML = '<p>No drift reports found</p>';
            return;
        }
        list.innerHTML = reports.map(r => {
            // SAFETY: convert all values to strings, handle objects
            const date = String(r.report_date || r.timestamp || 'Unknown');
            const driftDetected = r.drift_detected ? 'DRIFT DETECTED' : 'No drift';
            const vaultFiles = Number(r.vault_files || r.files_checked || 0);
            const overlayFiles = Number(r.overlay_files || 0);
            const vaultOnly = Number(r.vault_only_count || r.vault_only?.length || 0);
            const overlayOnly = Number(r.overlay_only_count || r.overlay_only?.length || 0);
            const changed = Number(r.modified_count || r.files_changed || r.changes || 0);
            const summary = String(r.summary || r.title || r.issue || '');
            // Truncate summary safely
            const truncated = summary.length > 150 ? summary.substring(0, 150) + '...' : summary;
            return `
            <div class="wiki-page-item">
                <strong>${date}</strong>
                <span style="margin-left:0.5rem; color: ${r.drift_detected ? '#e74c3c' : '#27ae60'};">${driftDetected}</span>
                <span style="margin-left:0.5rem;">${vaultFiles} vault / ${overlayFiles} overlay</span>
                ${vaultOnly > 0 ? `<span style="margin-left:0.5rem; color:#e67e22;">${vaultOnly} vault-only</span>` : ''}
                ${overlayOnly > 0 ? `<span style="margin-left:0.5rem; color:#3498db;">${overlayOnly} overlay-only</span>` : ''}
                ${changed > 0 ? `<span style="margin-left:0.5rem; color:#e74c3c;">${changed} changed</span>` : ''}
                ${truncated ? `<p style="margin:0.25rem 0 0; font-size:0.85rem; color:#aaa;">${truncated}</p>` : ''}
                <a href="/api/drift/${r.id || date}" target="_blank" style="margin-left:0.5rem;">View</a>
            </div>`;
        }).join('');
    } catch (error) {
        console.error('Error loading drift reports:', error);
        document.getElementById('driftList').innerHTML = '<p class="status-degraded">Unable to load drift reports</p>';
    }
}
```

- Strict Evaluation Criteria:
  1. GET /api/drift returns HTTP 200 with `reports` array containing normalized objects
  2. All drift report fields are strings/numbers (no raw objects)
  3. Drift reports page renders without JavaScript console errors
  4. `[object Object]` no longer appears in UI
  5. All timestamps display as ISO dates, not "Unknown"
  6. "DRIFT DETECTED" items highlighted in red, "No drift" in green

#### [TASK-18-005]: Fix Settings Page — Make read-write with save capability

- Component/Scope: `wiki-service.py` — `_serve_settings()` and new `_update_settings()`; `dashboard/js/api.js` — add `updateSettings()`; `dashboard/settings.html` — add input fields
- Core Objective: Convert the settings page from read-only display to a functional read-write interface with save capability.

- Dependencies: [TASK-18-001], [TASK-18-002], [TASK-18-004]

- Context Contextual Payload:
```python
# ADD to wiki-service.py:
def _update_settings(self):
    """Handle POST /api/settings — update service configuration."""
    content_length = int(self.headers.get('Content-Length', 0))
    body = self.rfile.read(content_length)
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        self.send_error(400, 'Invalid JSON')
        return

    # Validate and update settings
    new_settings = {}
    # Read current settings
    settings_path = ROOT / 'wiki-config.yaml'
    if not settings_path.exists():
        self.send_error(404, 'Config file not found')
        return

    # Update overlay path if provided
    if 'overlay' in data and isinstance(data['overlay'], dict):
        new_settings['overlay'] = data['overlay']
    if 'server' in data and isinstance(data['server'], dict):
        new_settings['server'] = data['server']
    if 'cache' in data and isinstance(data['cache'], dict):
        new_settings['cache'] = data['cache']
    if 'sync' in data and isinstance(data['sync'], dict):
        new_settings['sync'] = data['sync']
    if 'ui' in data and isinstance(data['ui'], dict):
        new_settings['ui'] = data['ui']

    if new_settings:
        # Write to overlay config (non-destructive)
        overlay_config = ROOT / 'wiki-config-overlay.yaml'
        current = {}
        if overlay_config.exists():
            current = yaml.safe_load(overlay_config.read_text()) or {}
        current.update(new_settings)
        overlay_config.write_text(yaml.dump(current, default_flow_style=False))

    self._send_json(200, {"status": "ok", "message": "Settings updated", "settings": current})
```

```javascript
// ADD to dashboard/js/api.js:
static async updateSettings(settings) {
    const response = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
    });
    return await response.json();
}
```

```html
<!-- TARGET: dashboard/settings.html — replace read-only with inputs -->
<!-- Add these input fields inside #settingsContent: -->
<div class="setting-row">
    <label>Theme:</label>
    <select id="settingTheme">
        <option value="light">Light</option>
        <option value="dark">Dark</option>
        <option value="auto">Auto (System)</option>
    </select>
</div>
<div class="setting-row">
    <label>Auto-refresh (seconds):</label>
    <input type="number" id="settingRefresh" min="0" max="3600" value="30">
</div>
<div class="setting-row">
    <label>Wiki Root Path:</label>
    <input type="text" id="settingWikiRoot" value="">
</div>
<div class="setting-row">
    <label>Overlay Path:</label>
    <input type="text" id="settingOverlayPath" value="">
</div>
<button id="saveSettings" class="btn btn-primary">Save Settings</button>
<div id="settingsStatus"></div>
```

- Strict Evaluation Criteria:
  1. GET /api/settings returns full settings object with `ui.theme`, `ui.auto_refresh`, `vault.path`
  2. Settings page displays input fields (not just text) for Theme, Auto-refresh, Language
  3. Vault path shows actual path, not "N/A"
  4. POST /api/settings with valid JSON returns 200 with status "ok"
  5. Changes persist to wiki-config-overlay.yaml
  6. "Save Settings" button shows success/error feedback

#### [TASK-18-006]: Remove TEST-001-check from production kanban

- Component/Scope: `wiki-content/maintenance-active/TEST-001-check.md`
- Core Objective: Remove test data from the production maintenance kanban board.

- Dependencies: None

- Context Contextual Payload:
```bash
# Actions:
rm /Users/tron/grid-network-wiki-tool/wiki-content/maintenance-active/TEST-001-check.md
# Then verify:
ls /Users/tron/grid-network-wiki-tool/wiki-content/maintenance-active/
# Should contain only real maintenance items (MAINT-001, MAINT-002, MAINT-003)
```

- Strict Evaluation Criteria:
  1. TEST-001-check.md file is deleted
  2. GET /api/kanban/maintenance no longer returns TEST-001 in the active list
  3. Maintenance kanban board does not show TEST-001

#### [TASK-18-007]: Add Pagination to Wiki Browser — 20 items per page

- Component/Scope: `dashboard/js/dashboard.js` — `loadWikiBrowser()` method; `wiki-service.py` — add `/api/wiki-index?page=&limit=` support
- Core Objective: Add pagination (20 items/page) and collapsible categories to the wiki browser to handle 96+ pages without infinite scroll.

- Dependencies: [TASK-18-001], [TASK-18-002]

- Context Contextual Payload:
```python
# ADD to wiki-service.py — modify _serve_wiki_index():
def _serve_wiki_index(self):
    """Serve /api/wiki-index with optional pagination."""
    # Parse query params
    page = 1
    limit = 20
    query = self.path.split('?')
    if len(query) > 1:
        params = dict(p.split('=', 1) for p in query[1].split('&') if '=' in p)
        try:
            page = int(params.get('page', 1))
            limit = int(params.get('limit', 20))
        except ValueError:
            pass
        if page < 1: page = 1
        if limit < 1 or limit > 100: limit = 20

    wiki_dir = ROOT / 'wiki-content'
    pages = []
    for md_file in sorted(wiki_dir.glob('**/*.md')):
        # Skip template files and index files
        rel = md_file.relative_to(wiki_dir)
        rel_str = str(rel)
        if rel_str.startswith('wiki-templates/') or rel_str.startswith('wiki-generated/'):
            continue
        if rel_str.startswith('archive/') or rel_str.startswith('raw/') or rel_str.startswith('maintenance/'):
            continue

        try:
            content = md_file.read_text()
            # Extract frontmatter
            title = md_file.stem.replace('-', ' ').replace('_', ' ')
            category = 'general'
            tags = []
            status = 'active'
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    fm = parts[1]
                    for line in fm.split('\n'):
                        if line.startswith('title:'):
                            title = line.split(':', 1)[1].strip().strip('"')
                        elif line.startswith('category:'):
                            category = line.split(':', 1)[1].strip()
                        elif line.startswith('tags:'):
                            tags = line.split(':', 1)[1].strip().strip('[').strip(']').split(',')
                            tags = [t.strip() for t in tags if t.strip()]
                        elif line.startswith('status:'):
                            status = line.split(':', 1)[1].strip()
        except Exception:
            title = md_file.stem
            category = 'general'

        pages.append({
            "slug": rel_str.replace('.md', ''),
            "title": title,
            "path": rel_str,
            "category": category,
            "tags": tags,
            "status": status,
            "last_updated": datetime.datetime.fromtimestamp(md_file.stat().st_mtime).isoformat(),
            "size_bytes": md_file.stat().st_size
        })

    # Pagination
    total = len(pages)
    start = (page - 1) * limit
    end = start + limit
    paginated = pages[start:end]

    self._send_json(200, {
        "pages": paginated,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit if total > 0 else 1,
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z"
    })
```

```javascript
// TARGET: loadWikiBrowser() with pagination:
async loadWikiBrowser(page = 1) {
    this.pageTitle.textContent = 'Wiki Browser';
    this.content.innerHTML = `
      <div class="card">
        <h3>Wiki Pages</h3>
        <input type="text" id="wikiSearch" placeholder="Search wiki..." style="width:100%;padding:0.5rem;margin-bottom:1rem;border:1px solid var(--border-color);border-radius:0.25rem;">
        <div id="wikiCategoryFilters" style="margin-bottom:1rem;"></div>
        <div class="wiki-tree" id="wikiTree">Loading...</div>
        <div id="wikiPagination" style="margin-top:1rem; text-align:center;"></div>
      </div>
    `;
    try {
        const index = await WikiAPI.getWikiIndex();
        const tree = document.getElementById('wikiTree');
        const pages = index.pages || [];
        const total = index.total || pages.length;
        const totalPages = index.total_pages || 1;
        const currentPage = index.page || 1;

        // Category icons map
        const categoryIcons = {
            'infrastructure': '&#128218;',
            'monitoring': '&#128200;',
            'maintenance': '&#128992;',
            'security': '&#128274;',
            'networking': '&#127760;',
            'services': '&#128161;',
            'backup': '&#128190;',
            'planning': '&#128203;',
            'tasks': '&#128203;',
            'template': '&#128196;',
            'general': '&#128196;'
        };

        // Render with category grouping
        const grouped = {};
        pages.forEach(p => {
            if (!grouped[p.category]) grouped[p.category] = [];
            grouped[p.category].push(p);
        });

        let html = '';
        for (const [cat, items] of Object.entries(grouped)) {
            const icon = categoryIcons[cat] || '&#128196;';
            html += `<div class="wiki-category"><strong>${icon} ${cat.charAt(0).toUpperCase() + cat.slice(1)} (${items.length})</strong>`;
            items.forEach(p => {
                html += `<div class="wiki-page-item" style="padding-left:1rem;">
                    <a href="/wiki/${p.slug}.md" target="_blank">${p.title}</a>
                    <span class="status status-${p.status}" style="margin-left:0.5rem;">${p.status}</span>
                </div>`;
            });
            html += '</div>';
        }
        tree.innerHTML = html || '<p>No pages found</p>';

        // Pagination controls
        const pag = document.getElementById('wikiPagination');
        let pagHtml = '';
        if (currentPage > 1) pagHtml += `<a href="#" onclick="dashboard.loadWikiBrowser(${currentPage - 1}); return false;">&laquo; Prev</a> `;
        for (let i = 1; i <= totalPages; i++) {
            if (i === currentPage) {
                pagHtml += `<strong>[${i}]</strong> `;
            } else {
                pagHtml += `<a href="#" onclick="dashboard.loadWikiBrowser(${i}); return false;">${i}</a> `;
            }
        }
        if (currentPage < totalPages) pagHtml += ` <a href="#" onclick="dashboard.loadWikiBrowser(${currentPage + 1}); return false;">Next &raquo;</a>`;
        pagHtml += ` <span style="color:#888;">(${total} total)</span>`;
        pag.innerHTML = pagHtml;

        // Search handler
        const searchInput = document.getElementById('wikiSearch');
        if (searchInput) {
            searchInput.addEventListener('input', async (e) => {
                const query = e.target.value.toLowerCase();
                if (query.length < 2) { this.loadWikiBrowser(); return; }
                const results = await WikiAPI.searchWiki(query);
                // ... (render results similarly)
            });
        }
    } catch (error) {
        console.error('Error loading wiki browser:', error);
        document.getElementById('wikiTree').innerHTML = '<p class="status-degraded">Unable to load wiki pages</p>';
    }
}
```

- Strict Evaluation Criteria:
  1. Wiki browser shows 20 items per page with page numbers
  2. "Next" and "Prev" buttons navigate correctly
  3. Pages are grouped by category with icons
  4. Total page count displayed ("X total")
  5. Search filters within current page results
  6. 96+ pages no longer cause infinite scroll

#### [TASK-18-008]: Add breadcrumb navigation to all sub-pages

- Component/Scope: `dashboard/css/dashboard.css` — add breadcrumb styles; all dashboard HTML pages — add breadcrumb HTML
- Core Objective: Add consistent breadcrumb navigation to every sub-page so users always know their location and can navigate back.

- Dependencies: [TASK-18-001]

- Context Contextual Payload:
```css
/* ADD to dashboard/css/dashboard.css: */
.breadcrumb {
    padding: 0.5rem 1rem;
    background: var(--bg-secondary, #f5f5f5);
    border-bottom: 1px solid var(--border-color, #ddd);
    font-size: 0.875rem;
    color: var(--text-secondary, #666);
}
.breadcrumb a {
    color: var(--text-primary, #333);
    text-decoration: none;
}
.breadcrumb a:hover {
    text-decoration: underline;
    color: var(--accent-color, #007bff);
}
.breadcrumb-separator {
    margin: 0 0.5rem;
    color: var(--text-secondary, #999);
}
.breadcrumb-current {
    color: var(--text-primary, #333);
    font-weight: 600;
}
```

```html
<!-- ADD to every sub-page HTML (after </aside> and <main> opening tag): -->
<nav class="breadcrumb">
    <a href="index.html">Home</a>
    <span class="breadcrumb-separator">/</span>
    <span class="breadcrumb-current">Current Page</span>
</nav>
```

- Strict Evaluation Criteria:
  1. Every sub-page (monitoring, drift, kanban/*, wiki-browser, sites, agents, settings) has a visible breadcrumb
  2. "Home" link navigates to index.html on every page
  3. Current page name is bold in the breadcrumb
  4. Breadcrumb is visible above the content area
  5. No layout shift or CSS conflicts

#### [TASK-18-009]: Add onboarding flow for first-time users

- Component/Scope: `dashboard/js/dashboard.js` — add `showOnboarding()` method; `dashboard/index.html` — add onboarding modal HTML
- Core Objective: Add a "getting started" onboarding flow that appears only on first visit, guiding new users through the dashboard.

- Dependencies: [TASK-18-001], [TASK-18-008]

- Context Contextual Payload:
```javascript
// ADD to dashboard/js/dashboard.js:
async loadDashboardIndex() {
    this.pageTitle.textContent = 'Dashboard';
    this.content.innerHTML = `
      <div class="card">
        <h3>Project Status</h3>
        <div id="projectStatus">Loading...</div>
      </div>
      <div class="card">
        <h3>Goal Progress</h3>
        <div id="goalProgress">Loading...</div>
      </div>
      <div class="card">
        <h3>Active Tasks</h3>
        <div id="activeTasks">Loading...</div>
      </div>
      <div class="card">
        <h3>Monitoring Status</h3>
        <div id="monitoringStatus">Loading...</div>
      </div>
    `;
    await this.loadDashboardData();

    // Show onboarding for first-time users
    if (!localStorage.getItem('grid-wiki-onboarding-complete')) {
        this.showOnboarding();
    }
}

showOnboarding() {
    const overlay = document.createElement('div');
    overlay.id = 'onboarding-overlay';
    overlay.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);display:flex;align-items:center;justify-content:center;z-index:1000;';
    overlay.innerHTML = `
      <div class="card" style="max-width:500px;padding:2rem;">
        <h2>Welcome to GRID Wiki</h2>
        <p>This is your infrastructure intelligence platform. Here's what you can do:</p>
        <ul>
            <li><strong>Dashboard</strong> — Overview of projects, tasks, and monitoring</li>
            <li><strong>Monitoring</strong> — Live status of 69+ services</li>
            <li><strong>Drift Reports</strong> — Vault/overlay sync status</li>
            <li><strong>Kanban Boards</strong> — Change and maintenance tracking</li>
            <li><strong>Wiki Browser</strong> — Browse 96+ documentation pages</li>
            <li><strong>Sites Overview</strong> — GRID and FMSA site status</li>
        </ul>
        <button id="onboarding-dismiss" class="btn btn-primary" style="margin-top:1rem;">Get Started</button>
      </div>
    `;
    document.body.appendChild(overlay);
    document.getElementById('onboarding-dismiss').addEventListener('click', () => {
        overlay.remove();
        localStorage.setItem('grid-wiki-onboarding-complete', '1');
    });
}
```

- Strict Evaluation Criteria:
  1. Onboarding modal appears on first visit to index.html
  2. Clearing localStorage (grid-wiki-onboarding-complete) makes it reappear
  3. Dismissing the modal stores the flag and never shows again
  4. All empty dashboard sections show helpful messages, not "--" or blank
  5. First-time user can find how to navigate within 3 clicks

#### [TASK-18-010]: Fix Monitoring page — Real-time charts with time range selector

- Component/Scope: `dashboard/monitoring.html` — add time range selector; `dashboard/js/dashboard.js` — `loadMonitoringPage()` with chart rendering
- Core Objective: Add real-time monitoring with time range selector (1h, 6h, 24h, 7d) and sparkline charts for each service.

- Dependencies: [TASK-18-001], [TASK-18-002], [TASK-18-003]

- Context Contextual Payload:
```javascript
// TARGET: loadMonitoringPage() with time range selector:
async loadMonitoringPage(timeRange = '24h') {
    this.pageTitle.textContent = 'Monitoring';
    this.content.innerHTML = `
      <div class="card">
        <h3>Service Health</h3>
        <div class="time-range-selector" style="margin-bottom:1rem;">
            <button class="btn btn-sm time-range-btn" data-range="1h">1h</button>
            <button class="btn btn-sm time-range-btn" data-range="6h">6h</button>
            <button class="btn btn-sm time-range-btn" data-range="24h" class="active">24h</button>
            <button class="btn btn-sm time-range-btn" data-range="7d">7d</button>
            <button class="btn btn-sm" id="liveRefreshBtn" style="margin-left:1rem;">&#128260; Live Refresh</button>
        </div>
        <div id="monitoringHealth">Loading...</div>
      </div>
    `;
    try {
        const status = await WikiAPI.getMonitoringStatus();
        const health = document.getElementById('monitoringHealth');
        health.innerHTML = `
          <table>
            <thead>
              <tr><th>Service</th><th>Status</th><th>Last Check</th><th>Response Time</th><th>Sparkline</th></tr>
            </thead>
            <tbody>
              ${status.services?.map(s => `
                <tr>
                  <td>${s.name}</td>
                  <td><span class="status status-${s.status}">${s.status}</span></td>
                  <td>${s.last_check || 'N/A'}</td>
                  <td>${s.response_time_ms ? s.response_time_ms + 'ms' : 'N/A'}</td>
                  <td>${this.renderSparkline(s.name, timeRange)}</td>
                </tr>
              `).join('') || '<tr><td colspan="5">No services found</td></tr>'}
            </tbody>
          </table>
        `;

        // Time range button handlers
        document.querySelectorAll('.time-range-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.time-range-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.loadMonitoringPage(btn.dataset.range);
            });
        });

        // Live refresh
        const liveBtn = document.getElementById('liveRefreshBtn');
        if (liveBtn) {
            liveBtn.addEventListener('click', () => this.loadMonitoringPage(timeRange));
        }
    } catch (error) {
        console.error('Error loading monitoring:', error);
        document.getElementById('monitoringHealth').innerHTML = '<p class="status-degraded">Unable to load monitoring status</p>';
    }
}

renderSparkline(serviceName, timeRange) {
    // Simple sparkline using canvas or SVG
    // For now, return a simple Unicode-based sparkline
    const height = 20;
    const width = 60;
    // Generate mock sparkline data (in production, fetch from Prometheus)
    const data = Array.from({length: width}, () => Math.random() * height);
    const svg = `<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
        <polyline fill="none" stroke="#007bff" stroke-width="1"
            points="${data.map((v, i) => `${i},${height - v}`).join(' ')}" />
    </svg>`;
    return svg;
}
```

- Strict Evaluation Criteria:
  1. Monitoring page shows time range selector (1h, 6h, 24h, 7d)
  2. All 12 services listed with real status from Prometheus
  3. Response times show actual milliseconds, not "N/A"
  4. Sparkline charts render for each service
  5. Live Refresh button reloads current data
  6. Status icons match actual Prometheus target health

#### [TASK-18-011]: Add /api/wiki/<slug> endpoint — Serve individual wiki pages

- Component/Scope: `wiki-service.py` — add new route handler; `dashboard/js/api.js` — add `getWikiPage()` call
- Core Objective: Add a dedicated API endpoint to serve individual wiki page content by slug, enabling in-app page viewing from the wiki browser.

- Dependencies: [TASK-18-001], [TASK-18-002]

- Context Contextual Payload:
```python
# ADD to wiki-service.py do_GET() routing table:
if self.path.startswith('/api/wiki/'):
    slug = self.path[len('/api/wiki/'):].rstrip('/')
    if slug:
        self.serve_wiki_page_by_slug(slug)
    return

# ADD handler method:
def serve_wiki_page_by_slug(self, slug):
    """Serve /api/wiki/<slug> — return markdown content."""
    # Resolve slug to file path (vault-first)
    candidate = self._resolve_wiki_path(slug + '.md')
    if candidate and candidate.is_file():
        content = candidate.read_text()
        self.send_response(200)
        self.send_header('Content-Type', 'text/markdown')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(content.encode())
        return
    self.send_error(404, f'Wiki page not found: {slug}')
```

- Strict Evaluation Criteria:
  1. GET /api/wiki/grid-infrastructure-overview returns HTTP 200 with markdown content
  2. GET /api/wiki/nonexistent returns HTTP 404
  3. Content-Type is text/markdown
  4. Vault-first resolution works (reads from Obsidian vault when available)
  5. Falls back to wiki-content overlay when vault unavailable

#### [TASK-18-012]: Fix Settings page — Display actual vault path from config

- Component/Scope: `wiki-service.py` — `_serve_settings()` method; `dashboard/settings.html` — display logic
- Core Objective: Ensure the Settings page displays the actual vault path from wiki-config.yaml, not "N/A".

- Dependencies: [TASK-18-001], [TASK-18-005]

- Context Contextual Payload:
```python
# FIX: _serve_settings() — ensure vault path is always shown:
def _serve_settings(self):
    """Serve /api/settings — service configuration and settings."""
    # Load config if not already loaded
    if not _CONFIG:
        _load_config()

    # Determine actual vault path
    actual_vault_path = _get_vault_path()
    vault_active = actual_vault_path is not None and actual_vault_path.exists()

    settings = {
        "service": {
            "port": PORT,
            "host": "0.0.0.0",
            "root": str(ROOT),
            "start_time": datetime.datetime.fromtimestamp(start_time).isoformat() if start_time else None,
            "uptime_seconds": int(time.time() - start_time) if start_time else 0,
            "version": "2.0"
        },
        "vault": {
            "enabled": _CONFIG.get('vault', {}).get('enabled', False),
            "path": _CONFIG.get('vault', {}).get('path', str(actual_vault_path)),
            "active": vault_active,
            "effective_path": str(actual_vault_path)
        },
        "overlay": {
            "enabled": _CONFIG.get('overlay', {}).get('enabled', True),
            "path": str(ROOT / 'wiki-content')
        },
        "ui": {
            "theme": "light",
            "auto_refresh": True,
            "refresh_interval_seconds": 30,
            "language": "en",
            "sidebar_collapsed": False
        },
        "cache": {
            "enabled": True,
            "ttl_seconds": 300
        },
        "monitoring": {
            "prometheus_url": "http://10.10.30.120:9090",
            "grafana_url": "https://grafana.grid/",
            "kuma_url": "https://kuma.grid/"
        },
        "sync": {
            "enabled": _CONFIG.get('sync', {}).get('enabled', True),
            "direction": _CONFIG.get('sync', {}).get('direction', 'vault_to_overlay'),
            "last_sync": None
        }
    }
    self._send_json(200, settings)
```

- Strict Evaluation Criteria:
  1. Settings page shows actual vault path (e.g., `/Users/tron/Documents/Obsidian Vault/GRID Network Wiki`)
  2. "Vault Active" indicator shows true/false based on path accessibility
  3. Overlay path is displayed
  4. UI settings (theme, auto-refresh, language) are displayed with editable inputs
  5. Monitoring URLs are shown

#### [TASK-18-013]: Add SSE real-time updates to dashboard

- Component/Scope: `wiki-service-sse.py` — SSE bridge; `dashboard/js/dashboard.js` — SSE client; `dashboard/index.html` — include SSE client
- Core Objective: Add Server-Sent Events support so the dashboard receives real-time updates when monitoring status, drift reports, or kanban data changes.

- Dependencies: [TASK-18-001], [TASK-18-003]

- Context Contextual Payload:
```python
# wiki-service-sse.py — SSE bridge:
#!/usr/bin/env python3
"""SSE bridge for GRID Wiki — pushes real-time updates to connected clients."""
import http.server
import json
import threading
import time
from pathlib import Path

ROOT = Path(__file__).parent
SUBSCRIBERS = []
SUBSCRIBERS_LOCK = threading.Lock()

def broadcast(event, data):
    """Broadcast event to all SSE subscribers."""
    payload = f"event: {event}\ndata: {json.dumps(data)}\n\n"
    with SUBSCRIBERS_LOCK:
        dead = []
        for i, (stream, _) in enumerate(SUBSCRIBERS):
            try:
                stream.write(payload.encode())
                stream.flush()
            except Exception:
                dead.append(i)
        for i in reversed(dead):
            SUBSCRIBERS.pop(i)

def subscribe(stream):
    """Add a client subscriber."""
    with SUBSCRIBERS_LOCK:
        SUBSCRIBERS.append((stream, time.time()))

def unsubscribe(stream):
    """Remove a client subscriber."""
    with SUBSCRIBERS_LOCK:
        SUBSCRIBERS = [(s, t) for s, t in SUBSCRIBERS if s is not stream]

class SSEHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/sse':
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            subscribe(self.wfile)
            try:
                while True:
                    time.sleep(1)  # Keep-alive ping
                    self.wfile.write(b': ping\n\n')
                    self.wfile.flush()
            except Exception:
                pass
            finally:
                unsubscribe(self.wfile)
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        pass  # Suppress log noise

if __name__ == '__main__':
    server = http.server.HTTPServer(('0.0.0.0', 8083), SSEHandler)
    print("SSE bridge running on port 8083")
    server.serve_forever()
```

```javascript
// ADD to dashboard/js/dashboard.js:
initSSE() {
    if (typeof EventSource !== 'undefined') {
        this.sse = new EventSource('/sse');
        this.sse.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'monitoring-update') {
                // Reload monitoring data
                this.loadMonitoringData();
            } else if (data.type === 'drift-update') {
                this.showNotification('Drift report generated', 'info');
            } else if (data.type === 'kanban-update') {
                this.showNotification('Kanban board updated', 'info');
            }
        };
        this.sse.onerror = () => {
            console.warn('SSE connection lost');
        };
    }
}
```

- Strict Evaluation Criteria:
  1. SSE bridge runs on port 8083
  2. Dashboard connects to /sse and receives events
  3. Monitoring updates trigger automatic refresh
  4. Drift report generation triggers notification
  5. Kanban changes trigger notification
  6. Connection drops handled gracefully (no crash)

#### [TASK-18-014]: Add error boundaries and graceful degradation to all pages

- Component/Scope: All dashboard HTML pages; `dashboard/js/dashboard.js` — add error boundary wrapper; `dashboard/css/dashboard.css` — add error state styles
- Core Objective: Ensure every dashboard section shows a clear error message on failure rather than a blank page or spinner forever.

- Dependencies: [TASK-18-001]

- Context Contextual Payload:
```css
/* ADD to dashboard/css/dashboard.css: */
.error-boundary {
    background: #fff3f3;
    border: 1px solid #ffcdd2;
    border-radius: 4px;
    padding: 1rem;
    margin: 0.5rem 0;
}
.error-boundary h4 {
    color: #c62828;
    margin: 0 0 0.5rem 0;
}
.error-boundary p {
    color: #666;
    margin: 0;
    font-size: 0.875rem;
}
.error-boundary button {
    margin-top: 0.5rem;
}
.status-degraded {
    color: #f57c00;
    font-style: italic;
}
.status-healthy {
    color: #2e7d32;
}
```

```javascript
// ADD to dashboard/js/dashboard.js:
renderErrorBoundary(containerId, title, message, onRetry) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = `
        <div class="error-boundary">
            <h4>${title}</h4>
            <p>${message}</p>
            <button class="btn btn-sm" onclick="(${onRetry.toString()})()">Retry</button>
        </div>
    `;
}

// Wrap all data-loading methods:
async loadWithFallback(methodName, containerId, title, fallbackFn, retryFn) {
    try {
        await this[methodName]();
    } catch (error) {
        console.error(`Error in ${methodName}:`, error);
        if (typeof fallbackFn === 'function') {
            fallbackFn();
        } else {
            this.renderErrorBoundary(
                containerId,
                title,
                `Unable to load ${title.toLowerCase()}. ${error.message || 'Check connection.'}`,
                retryFn
            );
        }
    }
}
```

- Strict Evaluation Criteria:
  1. Every dashboard section has error handling (no blank pages)
  2. Error state shows clear "Unable to load X" message with retry button
  3. Degraded state shows "⚠️" icon, not "❌"
  4. Spinner never stays forever (timeout after 10s)
  5. Console shows error details for debugging
  6. No JavaScript uncaught exceptions on any page

#### [TASK-18-015]: Fix Service Status cards — Probe real ports

- Component/Scope: `wiki-service.py` — `serve_service_status()` method; `dashboard/js/dashboard.js` — `loadSitesPage()` or new `loadServiceStatus()` method
- Core Objective: Replace static service status with live port probes for all GRID services.

- Dependencies: [TASK-18-001], [TASK-18-003]

- Context Contextual Payload:
```python
# TARGET: serve_service_status() — probe all GRID services:
def serve_service_status(self):
    """Serve /api/service-status — probe all GRID services."""
    service_targets = [
        {"name": "Prometheus", "url": "http://10.10.30.120:9090", "port": 9090, "type": "http"},
        {"name": "Grafana", "url": "http://10.10.30.120:3000", "port": 3000, "type": "http"},
        {"name": "Uptime Kuma", "url": "http://10.10.30.120:3001", "port": 3001, "type": "http"},
        {"name": "Caddy", "url": "http://10.10.30.120:8080", "port": 8080, "type": "http"},
        {"name": "Portainer", "url": "http://10.10.30.120:9443", "port": 9443, "type": "https"},
        {"name": "Ollama", "url": "http://10.10.30.120:11434", "port": 11434, "type": "http"},
        {"name": "Open WebUI", "url": "http://10.10.30.120:3002", "port": 3002, "type": "http"},
        {"name": "PostgreSQL", "url": "http://10.10.30.120:5432", "port": 5432, "type": "tcp"},
        {"name": "Redis", "url": "http://10.10.30.120:6379", "port": 6379, "type": "tcp"},
        {"name": "Minecraft", "url": "http://10.10.30.120:25565", "port": 25565, "type": "tcp"},
        {"name": "Samba", "url": "http://10.10.30.120:445", "port": 445, "type": "tcp"},
        {"name": "GRID Wiki", "url": "http://10.10.30.131:8082", "port": 8082, "type": "http"},
        {"name": "Omada Controller", "url": "http://10.10.30.120:8043", "port": 8043, "type": "https"},
        {"name": "Honcho", "url": "http://10.10.30.130:8000", "port": 8000, "type": "http"},
        {"name": "OpenConcho", "url": "http://10.10.30.130:8081", "port": 8081, "type": "http"},
    ]

    import threading
    results = {}
    def probe(svc):
        try:
            start = time.time()
            if svc['type'] == 'http':
                req = urllib.request.Request(svc['url'], method='HEAD')
                resp = urllib.request.urlopen(req, timeout=3)
                elapsed = int((time.time() - start) * 1000)
                results[svc['name']] = {
                    "name": svc['name'],
                    "url": svc['url'],
                    "status": "up" if resp.status >= 200 else "down",
                    "response_time_ms": elapsed,
                    "last_check": datetime.datetime.utcnow().isoformat() + "Z",
                    "port": svc['port'],
                    "type": svc['type']
                }
            else:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                start = time.time()
                result = sock.connect_ex((svc['url'].split('//')[1].split(':')[0], svc['port']))
                elapsed = int((time.time() - start) * 1000)
                sock.close()
                results[svc['name']] = {
                    "name": svc['name'],
                    "url": svc['url'],
                    "status": "up" if result == 0 else "down",
                    "response_time_ms": elapsed,
                    "last_check": datetime.datetime.utcnow().isoformat() + "Z",
                    "port": svc['port'],
                    "type": svc['type']
                }
        except Exception:
            results[svc['name']] = {
                "name": svc['name'],
                "url": svc['url'],
                "status": "down",
                "response_time_ms": None,
                "last_check": datetime.datetime.utcnow().isoformat() + "Z",
                "port": svc['port'],
                "type": svc['type']
            }

    threads = [threading.Thread(target=probe, args=(s,)) for s in service_targets]
    for t in threads: t.start()
    for t in threads: t.join(timeout=15)

    services = [results[k] for k in sorted(results.keys())]
    up = sum(1 for s in services if s['status'] == 'up')
    down = len(services) - up

    self._send_json(200, {
        "services": services,
        "summary": {
            "total": len(services),
            "up": up,
            "down": down,
            "last_check": datetime.datetime.utcnow().isoformat() + "Z"
        }
    })
```

- Strict Evaluation Criteria:
  1. GET /api/service-status returns all 15 services with live probe data
  2. Each service shows actual response time in ms
  3. Dashboard "Monitoring Status" card shows "15/15 services up" (or correct count)
  4. Services that are actually down show "down" status (not "healthy")
  5. All probes complete within 15 seconds (parallel execution)
  6. TCP probes work for PostgreSQL, Redis, Samba, Minecraft

#### [TASK-18-016]: Consolidate and deploy — git commit and push

- Component/Scope: Entire local workspace `/Users/tron/grid-network-wiki-tool/`
- Core Objective: Commit all Sprint 18 changes and push to GitHub for backup.

- Dependencies: All previous tasks [TASK-18-001] through [TASK-18-015]

- Context Contextual Payload:
```bash
cd /Users/tron/grid-network-wiki-tool
git add -A
git status
git commit -m "Sprint 18: Adversarial UX Remediation — Fix P0 issues (active-tasks API, goal progress math, monitoring data, drift JS errors, settings read-write), add pagination, breadcrumbs, onboarding, SSE real-time updates, error boundaries, service port probes"
git push origin main
```

- Strict Evaluation Criteria:
  1. All changes committed with descriptive message
  2. Git push succeeds to GitHub (FM-gpt/grid-network-wiki-tool)
  3. No merge conflicts
  4. Git status clean after push

#### [TASK-18-017]: Browser QA — Verify all fixes

- Component/Scope: All dashboard pages via browser
- Core Objective: Systematically verify every fix from the adversarial UX test against the running service.

- Dependencies: [TASK-18-016] (deployed)

- Context Contextual Payload:
```
Verification checklist:

1. Dashboard (index.html):
   - [ ] Active Tasks card shows correct counts (no "Unable to load tasks")
   - [ ] Goal Progress shows max 100% (no "122%")
   - [ ] Monitoring Status shows real "X/Y services up" (not "0/12")
   - [ ] No console errors
   - [ ] Onboarding appears for first-time users

2. Monitoring page (monitoring.html):
   - [ ] All 12+ services show real status (not all "healthy" with "N/A")
   - [ ] Response times show milliseconds (not "N/A")
   - [ ] Last Check shows timestamp (not "N/A")
   - [ ] Time range selector works (1h, 6h, 24h, 7d)
   - [ ] Sparkline charts render
   - [ ] Live Refresh button works

3. Drift Reports (drift.html):
   - [ ] No JavaScript console errors
   - [ ] No "[object Object]" in UI
   - [ ] All timestamps show ISO dates (not "Unknown")
   - [ ] Drift detected items highlighted in red
   - [ ] View links open individual reports

4. Change Kanban (kanban/change.html):
   - [ ] Risk field populated (not "N/A")
   - [ ] IDs sequential (no gaps like CHANGE-002 to CHANGE-010)
   - [ ] Approve/Reject buttons work

5. Maintenance Kanban (kanban/maintenance.html):
   - [ ] No TEST-001-check in production board
   - [ ] Three columns (Open, In Progress, Resolved)

6. Wiki Browser (wiki-browser.html):
   - [ ] Pagination shows 20 items per page
   - [ ] Page numbers displayed
   - [ ] Categories grouped with icons
   - [ ] Search filters results
   - [ ] No infinite scroll

7. Sites Overview (sites.html):
   - [ ] All sites displayed (GRID, FMSA)
   - [ ] Status indicators accurate
   - [ ] Service counts correct

8. Agent Protocol (agents.html):
   - [ ] AGENTS.md content renders correctly

9. Settings (settings.html):
   - [ ] Wiki Root shows actual path (not "N/A")
   - [ ] Input fields for Theme, Auto-refresh, Language
   - [ ] Save button works
   - [ ] Changes persist

10. General:
    - [ ] Sidebar works on ALL pages
    - [ ] Breadcrumbs on all sub-pages
    - [ ] Home button on all pages
    - [ ] Refresh button works
    - [ ] Export button works
```

- Strict Evaluation Criteria:
  1. Every item in the verification checklist passes
  2. Zero JavaScript console errors on any page
  3. All API endpoints return 200 with valid JSON
  4. All links navigate to correct destinations
  5. No visual regressions from Sprint 17

---

## Summary

| Phase | Tasks | Description | Priority |
|-------|-------|-------------|----------|
| P0 — Critical UX Fixes | TASK-18-001 through TASK-18-006 | Fix broken dashboard cards, monitoring data, drift JS errors, settings, remove test data | Immediate |
| P1 — Navigation & Usability | TASK-18-007 through TASK-18-010 | Pagination, breadcrumbs, onboarding, monitoring charts | High |
| P2 — Infrastructure | TASK-18-011 through TASK-18-015 | Wiki page API, service probes, SSE real-time, error boundaries | Medium |
| P3 — Release | TASK-18-016 through TASK-18-017 | Git commit, push, browser QA | Final |

**Total: 17 tasks, ~25-35 hours estimated**
