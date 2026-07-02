# GRID Network Wiki — Global Architecture Specification

**Version:** 2.0
**Status:** Active
**Last Updated:** 2026-06-28
**Author:** AI Project Architect

---

## Executive Summary

GRID Network Wiki is a **self-maintaining, markdown-first knowledge base** that serves as both a human-readable documentation system and an agent-queryable infrastructure monitor. The system runs on CT131 (grid-network-wiki-01) and provides:

- **Wiki Content**: Obsidian vault as canonical source, synced to overlay for container mode
- **Dashboard UI**: Single-page application for browsing, searching, monitoring, and kanban management
- **API Layer**: RESTful endpoints for wiki content, monitoring, kanban, and chatbot integration
- **Agent Protocol**: State-machine workflow for autonomous discovery, maintenance, and change management
- **Real-time Updates**: SSE (Server-Sent Events) for live monitoring and chatbot feedback

**Core Philosophy**: Markdown-first, vault-as-source-of-truth, overlay-fallback for containers, agent-coordinated maintenance.

---

## Target Tech Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: Custom HTTP server (http.server) — no external framework dependencies
- **Data Storage**: Markdown files in Obsidian vault + overlay directory
- **Caching**: In-memory TTL cache (thread-safe dict-based)
- **Search**: Client-side grep + server-side index (wiki-index.json)
- **SSE**: Server-Sent Events for real-time updates
- **MCP Proxy**: Model Context Protocol bridge to Proxmox API

### Frontend
- **Core**: HTML5 + Vanilla JavaScript (no framework dependencies)
- **Styling**: CSS3 with responsive design, dark/light mode support
- **Icons**: SVG inline icons (no external font dependencies)
- **State Management**: localStorage for UI state persistence
- **Routing**: Hash-based routing (no external router library)

### Infrastructure
- **Host**: CT131 (grid-network-wiki-01) on Proxmox host 10.10.30.22
- **Network**: 10.10.30.131 (internal), accessible via Caddy reverse proxy at wiki.grid
- **Storage**: ZFS dataset on CT131, mounted at /srv/grid-wiki/
- **Monitoring**: Prometheus targets, Uptime Kuma monitors, Grafana dashboards
- **Backup**: rsync to local Mac, snapshot before deployments

### Development Environment
- **Local Workspace**: `/Users/tron/grid-network-wiki-tool/` (Mac)
- **Dev Server**: CT121 (grid-dev-01) for rapid iteration
- **Production**: CT131 (grid-network-wiki-01) — never edit directly
- **Deployment**: rsync + systemd restart, verified via browser QA

---

## Directory Structure

```
grid-network-wiki-tool/                          # Local workspace (Mac)
├── wiki-service.py                              # Main HTTP service (port 8082)
├── wiki-service-sse.py                          # SSE bridge (port 8083)
├── wiki-config.yaml                             # Service configuration
├── wiki-content/                                # Overlay wiki root (container mode)
│   ├── wiki/                                    # Wiki markdown files
│   ├── sites/                                   # Multi-site mapping
│   ├── maintenance/                             # Generated maintenance items
│   ├── change-kanban/                           # Generated change cards
│   ├── tasks/                                   # Task files
│   └── raw/                                     # Live state snapshots
├── dashboard/                                   # Dashboard UI
│   ├── index.html                               # Main dashboard
│   ├── monitoring.html                          # Monitoring status
│   ├── drift.html                               # Drift reports
│   ├── agents.html                              # Agent protocol docs
│   ├── wiki-browser.html                        # Wiki file browser
│   ├── site-grid.html                           # Site overview cards
│   ├── site-fmsa.html                           # FMSA site details
│   ├── service.html                             # Service detail view
│   ├── obsidian-html/                           # Obsidian integration
│   │   ├── index.html
│   │   ├── wiki-data.json
│   │   └── app.js
│   ├── css/
│   │   └── dashboard.css                        # Shared styles
│   └── js/
│       ├── api.js                               # API client
│       ├── dashboard.js                         # Main app logic
│       ├── sidebar.js                           # Sidebar navigation
│       └── chatbox.js                           # Chatbot interface
├── tests/                                       # Unit tests
│   ├── server-static.test.js
│   ├── status-adapter.test.js
│   ├── backup-status.test.js
│   ├── hardware-status.test.js
│   ├── tag-filter-ui.test.js
│   ├── status-filter-ui.test.js
│   └── inline-detail-ui.test.js
├── AGENTS.md                                    # Agent protocol (state machine)
├── PROJECT-MANIFEST.md                          # Project brain (current goal, scope)
├── ACTIVE-TASKS.md                              # Development lock (kanban)
├── 00 - GRID Network Wiki Project Plan.md       # Original master plan
├── 11 - Sprint Plan — Adversarial UX Fixes.md   # Current sprint plan
└── scripts/
    ├── deploy-to-grid.sh                        # Deployment script
    └── sync-vault-to-overlay.sh                 # Manual sync trigger

/srv/grid-wiki/                                 # Production directory (CT131)
├── wiki/                                        # Wiki markdown files (SOT)
├── sites/                                       # Multi-site mapping
├── maintenance/                                 # Maintenance kanban state
├── change-kanban/                               # Change kanban state
├── raw/                                         # Live state snapshots
├── wiki-generated/                              # Auto-syntheses
├── maintenance-reports/                         # Health reports
├── sync/                                        # Sync state
├── PROJECT-MANIFEST.md                          # Project brain
├── ACTIVE-TASKS.md                              # Development lock
├── AGENTS.md                                    # Agent protocol
└── dashboard/                                   # Dashboard UI (rsynced)
    ├── index.html
    ├── monitoring.html
    ├── drift.html
    ├── agents.html
    ├── wiki-browser.html
    ├── site-grid.html
    ├── site-fmsa.html
    ├── service.html
    ├── obsidian-html/
    ├── css/
    └── js/
```

---

## Data Models / Schema

### Wiki Page Frontmatter (YAML)

```yaml
---
title: "Page Title"
type: entity|page|template|summary|maintenance|change
status: active|draft|deprecated|review
last_verified: "2026-06-28T00:00:00Z" | null
confidence: verified-live|verified-source|inferred|stale|blocked
created: "2026-06-23"
tags: [grid, proxmox, infrastructure, agent-relevant]
category: infrastructure|monitoring|maintenance|change|security
audience: [human, agent]
---
```

### Wiki Index (JSON)

```json
{
  "pages": [
    {
      "slug": "grid-infrastructure-overview",
      "title": "GRID Infrastructure Overview",
      "path": "wiki/grid-infrastructure-overview.md",
      "type": "entity",
      "status": "active",
      "tags": ["grid", "infrastructure"],
      "category": "infrastructure",
      "last_updated": "2026-06-28T00:00:00Z"
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
  "tasks": [
    {
      "id": "TASK-01",
      "title": "Sidebar navigation on ALL pages",
      "status": "in_progress",
      "assignee": "SELF",
      "started": "2026-06-23"
    }
  ]
}
```

### Active Tasks (Markdown Table)

```markdown
| Task ID | Description | Status | Assignee |
|---------|-------------|--------|----------|
| TASK-01 | Sidebar navigation on ALL pages | In Progress | SELF |
| TASK-02 | Fix 5 missing API endpoints | Parked | |
```

### Project Manifest (YAML)

```yaml
current_goal: "Sprint 11: Adversarial UX Fixes"
scope_boundaries:
  - Core: Wiki service + dashboard + API
  - In Scope: Discovery, monitoring, kanban, chatbot
  - Out of Scope: External integrations, mobile apps
active_tasks:
  - TASK-01
  - TASK-02
deep_doc_index:
  - DEEP-DOCS/docker-test-env-template.md
  - DEEP-DOCS/agent-workflow.md
```

### Monitoring Status (JSON)

```json
{
  "services": [
    {
      "name": "grid-wiki",
      "type": "http",
      "url": "http://10.10.30.131:8082",
      "status": "up",
      "last_check": "2026-06-28T00:00:00Z",
      "prometheus_job": "grid-wiki",
      "uptime_kuma_monitor": "grid-wiki-uptime"
    }
  ],
  "prometheus_targets": {
    "up": 15,
    "down": 2,
    "missing": 1
  },
  "uptime_kuma_monitors": {
    "configured": 20,
    "down": 3
  }
}
```

### Drift Report (JSON)

```json
{
  "timestamp": "2026-06-28T00:00:00Z",
  "discovery": {
    "containers_scanned": 10,
    "services_discovered": 15,
    "new_services": ["service-x"],
    "stale_services": ["service-y"]
  },
  "drift_detected": {
    "new_containers": 1,
    "ip_changes": 2,
    "port_changes": 1,
    "missing_monitoring": 3
  },
  "pending_changes": 5,
  "maintenance_issues": 3
}
```

### Kanban Card (Markdown)

```markdown
---
title: "Change Summary"
type: change
status: pending|approved|rejected|merged
submitted: "2026-06-28T00:00:00Z"
reviewed: null
risk: low|medium|high
---
```

---

## System Boundaries & Contracts

### API Endpoints

#### Wiki Content

```
GET  /api/wiki-index        - List all wiki pages with metadata
GET  /api/wiki/<slug>       - Get wiki page content by slug
POST /api/wiki/search       - Search wiki pages (query, limit)
GET  /api/wiki-export       - Export wiki as tar.gz
```

#### Active Tasks

```
GET  /api/active-tasks      - Get active tasks (parse ACTIVE-TASKS.md)
```

#### Sites

```
GET  /api/sites-index       - Get sites overview (list sites/)
GET  /api/sites/<site-name> - Get site-specific data
```

#### Monitoring

```
GET  /api/monitoring-status - Get monitoring status (Prometheus, Uptime Kuma)
GET  /api/prometheus-targets - Get Prometheus targets status
GET  /api/uptime-kuma-monitors - Get Uptime Kuma monitors
```

#### Drift

```
GET  /api/drift/<date>      - Get drift report for specific date
GET  /api/drift/latest      - Get latest drift report
```

#### Kanban

```
GET  /api/kanban/changes    - Get pending change cards
POST /api/kanban/changes/<id>/approve - Approve change
POST /api/kanban/changes/<id>/reject  - Reject change
GET  /api/kanban/maintenance - Get open maintenance cards
POST /api/kanban/maintenance/<id>/resolve - Resolve maintenance
```

#### Chatbot

```
POST /api/chat/query        - Query chatbot (bridge to Honcho)
POST /api/chat/action       - Create kanban item from chat
```

#### Settings

```
GET  /api/settings          - Get service configuration
```

#### Sync

```
POST /api/sync/run          - Trigger manual sync (vault -> overlay)
GET  /api/sync-status       - Get last sync status
```

### Internal Module Interfaces

#### Wiki Service (wiki-service.py)

```python
class WikiService:
    def __init__(self, port: int, root: Path):
        """Initialize HTTP server with wiki root and config."""

    def start(self):
        """Start HTTP server on configured port."""

    def stop(self):
        """Stop HTTP server gracefully."""

    def get_wiki_index(self) -> dict:
        """Generate wiki index from wiki-content/."""

    def get_wiki_page(self, slug: str) -> str:
        """Get wiki page content by slug."""

    def search_wiki(self, query: str, limit: int = 10) -> list:
        """Search wiki pages (client-side grep)."""

    def get_active_tasks(self) -> list:
        """Parse ACTIVE-TASKS.md and return task list."""

    def get_sites_index(self) -> dict:
        """Get sites overview from sites/ directory."""

    def get_monitoring_status(self) -> dict:
        """Query Prometheus and Uptime Kuma for status."""

    def get_drift_report(self, date: str) -> dict:
        """Get drift report for specific date."""

    def get_kanban_changes(self) -> list:
        """Get pending change cards from change-kanban/."""

    def get_kanban_maintenance(self) -> list:
        """Get open maintenance cards from maintenance/."""

    def approve_change(self, card_id: str) -> bool:
        """Approve change and move to approved/."""

    def reject_change(self, card_id: str) -> bool:
        """Reject change and move to rejected/."""

    def resolve_maintenance(self, card_id: str) -> bool:
        """Resolve maintenance card and move to resolved/."""

    def chat_query(self, message: str) -> str:
        """Query chatbot via Honcho API."""

    def chat_action(self, message: str) -> dict:
        """Create kanban item from chat message."""

    def sync_vault_to_overlay(self) -> dict:
        """Sync Obsidian vault to overlay directory."""

    def get_settings(self) -> dict:
        """Get service configuration from wiki-config.yaml."""

    def export_wiki(self) -> bytes:
        """Export wiki as tar.gz archive."""
```

#### SSE Bridge (wiki-service-sse.py)

```python
class SSEBridge:
    def __init__(self, port: int, wiki_service: WikiService):
        """Initialize SSE server with wiki service reference."""

    def start(self):
        """Start SSE server on configured port."""

    def stop(self):
        """Stop SSE server gracefully."""

    def broadcast(self, event: str, data: dict):
        """Broadcast event to all connected clients."""

    def subscribe(self, callback):
        """Subscribe client to events."""

    def unsubscribe(self, callback):
        """Unsubscribe client from events."""

    def trigger_monitoring_update(self):
        """Trigger monitoring status update."""

    def trigger_drift_update(self):
        """Trigger drift report update."""

    def trigger_kanban_update(self):
        """Trigger kanban board update."""

    def trigger_chat_update(self):
        """Trigger chatbot message update."""
```

#### Dashboard JavaScript Modules

```javascript
// api.js
class WikiAPI {
    static async getWikiIndex() { /* ... */ }
    static async getWikiPage(slug) { /* ... */ }
    static async searchWiki(query, limit) { /* ... */ }
    static async getActiveTasks() { /* ... */ }
    static async getMonitoringStatus() { /* ... */ }
    static async getDriftReport(date) { /* ... */ }
    static async getKanbanChanges() { /* ... */ }
    static async getKanbanMaintenance() { /* ... */ }
    static async approveChange(cardId) { /* ... */ }
    static async rejectChange(cardId) { /* ... */ }
    static async resolveMaintenance(cardId) { /* ... */ }
    static async chatQuery(message) { /* ... */ }
    static async chatAction(message) { /* ... */ }
    static async syncVaultToOverlay() { /* ... */ }
    static async getSettings() { /* ... */ }
    static async exportWiki() { /* ... */ }
}

// dashboard.js
class Dashboard {
    constructor() {
        this.state = {
            currentView: 'index',
            sidebarOpen: true,
            onboardingComplete: false
        };
    }

    init() {
        this.loadState();
        this.renderSidebar();
        this.renderCurrentView();
        this.setupEventListeners();
    }

    loadState() { /* ... */ }
    saveState() { /* ... */ }
    renderSidebar() { /* ... */ }
    renderCurrentView() { /* ... */ }
    navigateTo(view) { /* ... */ }
    setupEventListeners() { /* ... */ }
}

// sidebar.js
class Sidebar {
    constructor() {
        this.links = [
            { id: 'index', label: 'Dashboard', icon: '📊' },
            { id: 'monitoring', label: 'Monitoring', icon: '📈' },
            { id: 'drift', label: 'Drift Reports', icon: '🔍' },
            { id: 'kanban', label: 'Kanban Boards', icon: '📋' },
            { id: 'wiki', label: 'Wiki Browser', icon: '📖' },
            { id: 'sites', label: 'Sites Overview', icon: '🌐' },
            { id: 'agents', label: 'Agent Protocol', icon: '🤖' },
            { id: 'settings', label: 'Settings', icon: '⚙️' }
        ];
    }

    render() { /* ... */ }
    toggle() { /* ... */ }
    setActive(viewId) { /* ... */ }
}

// chatbox.js
class Chatbox {
    constructor() {
        this.messages = [];
        this.connected = false;
    }

    init() {
        this.connect();
        this.setupEventListeners();
    }

    connect() { /* ... */ }
    disconnect() { /* ... */ }
    sendMessage(message) { /* ... */ }
    receiveMessage(message) { /* ... */ }
    setupEventListeners() { /* ... */ }
}
```

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        OPERATOR LAYER                            │
│  Dashboard UI (https://wiki.grid/)  <->  Wiki on CT131           │
│        ^                                              ^          │
│        | Sites Overview (cards for each site)       |          │
│        | Drill-down into per-site details           |          │
│        | **Full Wiki Viewer** (browse/view raw MD)  |          │
│        | **Download Wiki** (export .md package)     |          │
│        | **Kanban Boards** (change/maintenance)     |          │
│        | **Chatbot** (query Honcho)                 |          │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      SERVER LAYER (CT131)                        │
│  /srv/grid-wiki/     - Wiki markdown files (SOT)                 │
│  /srv/grid-wiki/sites/ - Multi-site mapping & index             │
│  /srv/grid-wiki/raw/ - Raw evidence (snapshots, logs)           │
│  /srv/grid-wiki/wiki-generated/ - Auto-syntheses                │
│  grid-wiki-service/  - Wiki API + dashboard app                 │
│  grid-wiki-sse/      - SSE bridge for real-time updates         │
│  grid-wiki-mcp/      - MCP proxy for Proxmox API                │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                  AGENT / CRON LAYER (1am-6am)                    │
│  1. Discovery scan (Proxmox, Docker, Prometheus, Uptime)        │
│  2. Drift detection vs wiki                                     │
│  3. New service detection + auto-monitor setup                  │
│  4. Maintenance kanban worker (investigate errors)              │
│  5. Wiki generation/update                                     │
│  6. Multi-site inventory mapping (grid, fmsa, etc.)             │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                   EXTERNAL INTEGRATIONS                          │
│  - Obsidian Vault (/Users/tron/Documents/Obsidian Vault/...)     │
│  - Proxmox API (via MCP proxy)                                  │
│  - Prometheus (metrics collection)                              │
│  - Uptime Kuma (monitoring)                                     │
│  - Grafana (dashboards)                                         │
│  - Honcho (memory & reasoning)                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Design Principles

1. **Markdown-First**: All content stored as `.md` files, exportable and human-readable
2. **Vault as Source of Truth**: Obsidian vault is canonical source, overlay is fallback
3. **Overlay for Containers**: In container mode (CT131), overlay becomes primary wiki root
4. **Agent-Coordinated**: Hermes agents use state machine workflow for maintenance
5. **Real-Time Updates**: SSE bridge for live monitoring and chatbot feedback
6. **Container-Aware**: Service detects vault accessibility and switches modes
7. **Zero Database**: No SQL/NoSQL database, just files on disk
8. **API-First**: All functionality exposed via RESTful API endpoints
9. **Client-Side Search**: Wiki search via client-side grep (no backend search index)
10. **State Persistence**: localStorage for UI state, file-based for wiki state

---

## Security Considerations

- **Authentication**: Dashboard requires basic auth (configurable)
- **API Keys**: MCP proxy uses pre-shared keys for Proxmox API
- **File Permissions**: Wiki files readable by service, writable by agents
- **CORS**: Configured for trusted origins (wiki.grid, localhost)
- **Input Validation**: All API inputs validated before processing
- **XSS Protection**: Content sanitized before rendering in HTML
- **CSRF Protection**: Token-based CSRF protection for state-changing actions

---

## Performance Considerations

- **Caching**: In-memory TTL cache (5 minutes default) for API responses
- **Lazy Loading**: Dashboard views loaded on-demand (not all at once)
- **Client-Side Search**: Wiki search via client-side grep (fast, no backend)
- **SSE Optimization**: Event batching for monitoring updates
- **File System**: Wiki files stored on ZFS for fast reads
- **Compression**: Gzip encoding for API responses
- **CDN**: Static assets cached via Caddy reverse proxy

---

## Deployment Strategy

1. **Local Development**: Edit files in `/Users/tron/grid-network-wiki-tool/`
2. **Verification**: Run tests, build, browser QA on local Mac
3. **Staging**: Deploy to CT121 (grid-dev-01) for rapid iteration
4. **Production**: Deploy to CT131 (grid-network-wiki-01) after verification
5. **Rollback**: Snapshot before deployment, restore if issues arise
6. **Monitoring**: Verify health endpoint, Prometheus targets, Uptime Kuma monitors

---

## Maintenance & Operations

- **Daily**: Discovery scan (1am-6am), drift detection, maintenance worker
- **Weekly**: Wiki sync, backup, health report generation
- **Monthly**: Review drift reports, update documentation, optimize cache
- **Quarterly**: Audit monitoring setup, update best-practice rules
- **Annually**: Major version upgrade, security audit, performance review

---

## Success Metrics

- **Wiki Coverage**: 100% of GRID infrastructure documented
- **Discovery Accuracy**: 95%+ of services discovered and documented
- **Drift Detection**: 100% of changes detected within 24 hours
- **Monitoring Coverage**: 90%+ of services have Prometheus + Uptime Kuma
- **Agent Coordination**: Zero duplicate work (ACTIVE-TASKS.md lock)
- **User Satisfaction**: Adversarial UX test passes (first-time user can accomplish core task)
- **Uptime**: 99.9%+ availability (monitored by Uptime Kuma)
- **Response Time**: API endpoints < 500ms (cached), < 2s (uncached)

---

## Future Enhancements (Out of Scope)

- Mobile app for on-the-go monitoring
- Advanced search with full-text indexing (Elasticsearch)
- Multi-language support
- Role-based access control (RBAC)
- Audit logging for all agent actions
- Webhook integrations for external systems
- Machine learning for anomaly detection
- Advanced visualization (graphs, charts)
- Collaborative editing (real-time sync)
- Offline mode for operators