# GRID Network Nerve Center — Agent-Driven Knowledge Base & Living Infrastructure

**Date:** 2026-06-30  
**Author:** Principal Software Architect (AI)  
**Status:** Specification for automated agent execution  
**Scope:** Replace dead wiki mirror with living nerve center — agent-driven discovery, vector graph knowledge base, SQLite state, live dashboard, wiki documentation as byproduct.

---

## PART 1: GLOBAL ARCHITECTURE SPECIFICATION

### Target Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Backend | Python 3.11+ stdlib only | Zero-deploy, proven pattern from wiki-service |
| Database | SQLite 3 (on-disk, single file) | Lightweight, ACID, agent-writable, no external deps |
| Knowledge | Vector graph via Honcho (CT130:8000) | Cross-session memory, semantic search, agent-native |
| Cache | In-memory TTL dict (thread-safe) | Dashboard performance, no external deps |
| Real-time | SSE via wiki-service-sse.py | Push updates to dashboard without polling |
| Discovery | Proxmox API (REST) | Primary source of truth for LXCs/VMs |
| Monitoring | Prometheus API (REST) | Service health, metrics, targets |
| Routing | Caddy config (file-based) | Network routing, reverse proxy |
| Frontend | Vanilla HTML5 + CSS3 + ES6 JS | No framework deps, works offline |
| Deployment | rsync + systemd on CT131 | Current pattern, proven |
| Reverse Proxy | Caddy on grid-pve | Routes wiki.grid → CT131:8082 |

### Directory Structure

```
grid-network-wiki-tool/                          # Local workspace (Mac)
├── nerve-center/                                # NEW: Nerve center subsystem
│   ├── discoverer.py                            # Proxmox scanner → service map
│   ├── verifier.py                              # Service health checker
│   ├── knowledge.py                             # Vector graph manager (Honcho API)
│   ├── state.py                                 # SQLite state manager
│   ├── wiki-writer.py                           # Markdown doc writer
│   ├── nerve-center.py                          # Main HTTP service (port 8083)
│   ├── nerve-center-config.yaml                 # Configuration
│   ├── nerve-center.db                          # SQLite database (generated)
│   ├── knowledge-graph.json                     # Local vector graph cache
│   └── services/
│       ├── template-card.json                   # Service card template
│       └── discovery-rules.yaml                 # Auto-discovery rules
├── wiki-service.py                              # Existing wiki service (port 8082)
├── wiki-service-sse.py                          # Existing SSE bridge (port 8083)
├── wiki-config.yaml                             # Existing config
├── PROJECT-MANIFEST.md                          # Project brain
├── ACTIVE-TASKS.md                              # Dev lock
├── AGENTS.md                                    # Agent protocol
├── dashboard/
│   ├── index.html                               # Dashboard home (REFACTORED)
│   ├── nerve-center.html                        # NEW: Nerve center view
│   ├── service-card.html                        # NEW: Service detail modal
│   ├── monitoring.html                          # Monitoring status
│   ├── css/
│   │   └── dashboard.css                        # Shared styles (EXTENDED)
│   └── js/
│       ├── api.js                               # API client class (EXTENDED)
│       ├── dashboard.js                         # Main app logic (REFACTORED)
│       ├── nerve-center.js                      # NEW: Nerve center logic
│       ├── sidebar.js                           # Sidebar navigation
│       └── chatbox.js                           # Chatbot interface
├── wiki-content/                                # Overlay wiki root
│   ├── wiki/                                    # Wiki markdown files (BYPRODUCT)
│   ├── sites/                                   # Site info files
│   └── sync/                                    # Sync manifests
├── scripts/
│   ├── discover-proxmox.sh                      # Manual discovery trigger
│   ├── verify-services.sh                       # Manual verification trigger
│   ├── build-knowledge-graph.sh                 # Manual KB rebuild
│   └── deploy-nerve-center.sh                   # Deployment script
├── cron/
│   ├── nerve-discovery.sh                       # Auto-discovery (every 6h)
│   ├── nerve-verify.sh                          # Service verification (every 1h)
│   └── nerve-sync.sh                            # KB sync (every 12h)
├── tests/
│   ├── test-discoverer.py
│   ├── test-verifier.py
│   ├── test-knowledge.py
│   ├── test-state.py
│   └── test-wiki-writer.py
├── docs/
│   ├── 00 - User Documentation.md               # Existing
│   ├── 01 - Architecture.md                     # NEW: Architecture docs
│   └── 02 - API Reference.md                    # NEW: API docs
├── Dockerfile
├── docker-compose.ct131.yml                     # Deployment config
└── caddy/
    └── Caddyfile                                # Caddy config
```

### Data Models / Schema

#### SQLite Database (`nerve-center.db`)

```sql
-- Servers (Proxmox hosts)
CREATE TABLE IF NOT EXISTS servers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hostname TEXT NOT NULL UNIQUE,
    ip_address TEXT NOT NULL,
    proxmox_api_url TEXT NOT NULL,
    proxmox_api_user TEXT NOT NULL,
    proxmox_api_token_name TEXT NOT NULL,
    proxmox_api_token_secret TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'unknown',  -- 'up', 'down', 'unknown'
    last_discovered TEXT,  -- ISO timestamp
    last_verified TEXT,    -- ISO timestamp
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Containers/VMs (LXC on Proxmox)
CREATE TABLE IF NOT EXISTS containers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id INTEGER NOT NULL REFERENCES servers(id),
    vmid INTEGER NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,  -- 'lxc', 'vm'
    status TEXT NOT NULL DEFAULT 'unknown',  -- 'running', 'stopped', 'unknown'
    ip_addresses TEXT NOT NULL DEFAULT '[]',  -- JSON array of IPs
    memory_mb INTEGER,
    cpu_cores INTEGER,
    disk_total_mb INTEGER,
    disk_used_mb INTEGER,
    os TEXT,
    template TEXT,
    last_discovered TEXT,
    last_verified TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(server_id, vmid)
);

-- Services (running on containers)
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    container_id INTEGER NOT NULL REFERENCES containers(id),
    name TEXT NOT NULL,
    type TEXT NOT NULL,  -- 'http', 'https', 'tcp', 'udp', 'ssh', 'database', 'proxy', 'monitoring', 'storage', 'dns', 'mail', 'other'
    port INTEGER,
    protocol TEXT NOT NULL DEFAULT 'tcp',
    url TEXT,  -- Full URL if applicable
    status TEXT NOT NULL DEFAULT 'unknown',  -- 'up', 'down', 'unknown'
    response_time_ms INTEGER,
    last_checked TEXT,
    prometheus_job TEXT,
    prometheus_target TEXT,
    monitoring_configured INTEGER NOT NULL DEFAULT 0,
    caddy_configured INTEGER NOT NULL DEFAULT 0,
    health_check_url TEXT,
    health_check_interval INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Service Relationships (e.g., "Prometheus scrapes Grafana")
CREATE TABLE IF NOT EXISTS service_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_service_id INTEGER NOT NULL REFERENCES services(id),
    target_service_id INTEGER NOT NULL REFERENCES services(id),
    relationship_type TEXT NOT NULL,  -- 'scrapes', 'proxies', 'replicates', 'authenticates', 'depends_on', 'monitors'
    description TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(source_service_id, target_service_id, relationship_type)
);

-- Network Design (canonical network architecture)
CREATE TABLE IF NOT EXISTS network_design (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    version TEXT NOT NULL DEFAULT '1.0',
    description TEXT,
    cidr_blocks TEXT NOT NULL DEFAULT '[]',  -- JSON array of CIDR blocks
    vlan_ids TEXT NOT NULL DEFAULT '[]',  -- JSON array of VLAN IDs
    dns_servers TEXT NOT NULL DEFAULT '[]',  -- JSON array of DNS server IPs
    ntp_servers TEXT NOT NULL DEFAULT '[]',  -- JSON array of NTP server IPs
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Design Rules (validation rules for new services)
CREATE TABLE IF NOT EXISTS design_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    rule_type TEXT NOT NULL,  -- 'port_range', 'required_services', 'forbidden_ports', 'required_monitoring', 'required_backup', 'network_isolation'
    rule_config TEXT NOT NULL,  -- JSON config specific to rule type
    severity TEXT NOT NULL DEFAULT 'warning',  -- 'info', 'warning', 'error'
    created_at TEXT NOT NULL DEFAULT (datetime('new')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Wiki Documents (byproduct of agent actions)
CREATE TABLE IF NOT EXISTS wiki_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,  -- 'infrastructure', 'service', 'network', 'procedure', 'design', 'troubleshooting'
    content TEXT NOT NULL,  -- Markdown content
    source TEXT NOT NULL,  -- 'agent-generated', 'user-edited', 'auto-discovered'
    related_service_id INTEGER REFERENCES services(id),
    related_container_id INTEGER REFERENCES containers(id),
    last_updated TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Agent Actions (audit log)
CREATE TABLE IF NOT EXISTS agent_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    action_type TEXT NOT NULL,  -- 'discover', 'verify', 'create', 'update', 'delete', 'request'
    target_type TEXT NOT NULL,  -- 'container', 'service', 'wiki', 'knowledge'
    target_id INTEGER,
    status TEXT NOT NULL DEFAULT 'pending',  -- 'pending', 'running', 'completed', 'failed'
    details TEXT,  -- JSON details of the action
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- User Requests (user can request new services)
CREATE TABLE IF NOT EXISTS user_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    request_type TEXT NOT NULL,  -- 'create_service', 'modify_service', 'delete_service', 'add_container', 'investigate_issue'
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'pending',  -- 'pending', 'approved', 'in_progress', 'completed', 'rejected'
    assigned_agent_id TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_containers_server ON containers(server_id);
CREATE INDEX IF NOT EXISTS idx_services_container ON services(container_id);
CREATE INDEX IF NOT EXISTS idx_services_status ON services(status);
CREATE INDEX IF NOT EXISTS idx_services_type ON services(type);
CREATE INDEX IF NOT EXISTS idx_wiki_slug ON wiki_documents(slug);
CREATE INDEX IF NOT EXISTS idx_wiki_category ON wiki_documents(category);
CREATE INDEX IF NOT EXISTS idx_agent_actions_status ON agent_actions(status);
CREATE INDEX IF NOT EXISTS idx_agent_actions_type ON agent_actions(action_type);
CREATE INDEX IF NOT EXISTS idx_user_requests_status ON user_requests(status);
```

#### Vector Graph Schema (Honcho Knowledge Base)

The vector graph stores **knowledge** (not state). State lives in SQLite. Knowledge is semantic, queryable, and agent-accessible.

```json
{
  "nodes": [
    {
      "id": "node-001",
      "type": "server",
      "label": "grid-core-01 (CT120)",
      "properties": {
        "hostname": "grid-core-01",
        "ip": "10.10.30.22",
        "proxmox_host": true,
        "os": "Proxmox VE 8.x",
        "role": "production-core"
      },
      "embeddings": [0.1, 0.2, ...],  -- 1024-dim vector
      "metadata": {
        "source": "proxmox-discovery",
        "discovered_at": "2026-06-30T10:00:00Z",
        "confidence": 0.95
      }
    },
    {
      "id": "node-002",
      "type": "service",
      "label": "Prometheus",
      "properties": {
        "name": "Prometheus",
        "type": "monitoring",
        "port": 9090,
        "url": "http://10.10.30.120:9090",
        "status": "up",
        "scrape_interval": "15s",
        "retention": "30d"
      },
      "embeddings": [...],
      "metadata": {
        "source": "prometheus-api",
        "discovered_at": "2026-06-30T10:00:00Z",
        "confidence": 0.98
      }
    },
    {
      "id": "node-003",
      "type": "procedure",
      "label": "How to add a new Proxmox container",
      "properties": {
        "category": "procedure",
        "difficulty": "medium",
        "estimated_time": "30 minutes",
        "prerequisites": ["proxmox-root-access", "iso-image", "network-config"],
        "steps": [
          "1. Login to Proxmox web UI",
          "2. Create new LXC container",
          "3. Assign resources (CPU, RAM, disk)",
          "4. Configure network (IP, gateway, DNS)",
          "5. Install OS template",
          "6. Configure SSH access",
          "7. Verify connectivity",
          "8. Register with monitoring"
        ]
      },
      "embeddings": [...],
      "metadata": {
        "source": "agent-knowledge",
        "created_at": "2026-06-30T10:00:00Z"
      }
    }
  ],
  "edges": [
    {
      "from": "node-001",
      "to": "node-002",
      "type": "hosts",
      "properties": {
        "container_id": 120,
        "service_name": "Prometheus"
      }
    },
    {
      "from": "node-003",
      "to": "node-001",
      "type": "applies_to",
      "properties": {
        "scope": "all-proxmox-hosts"
      }
    }
  ]
}
```

#### Knowledge Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `infrastructure` | Physical/virtual infrastructure | Servers, containers, VMs, storage |
| `service` | Running services | Prometheus, Grafana, PostgreSQL, Caddy |
| `network` | Network architecture | VLANs, subnets, routing, DNS |
| `procedure` | How-to guides | "Add new container", "Restore backup" |
| `design` | Network design docs | "Network topology", "Service naming convention" |
| `troubleshooting` | Known issues & fixes | "Prometheus target down", "Caddy route missing" |
| `monitoring` | Monitoring config | "Prometheus jobs", "Alert rules" |
| `backup` | Backup procedures | "ZFS snapshots", "Cross-site backup" |

### System Boundaries & Contracts

#### API Endpoints

| Method | Endpoint | Handler | Purpose | Response Format |
|--------|----------|---------|---------|-----------------|
| GET | `/api/nerve/health` | `serve_health_check` | Health check | `{status, uptime_seconds, service_name, started_at}` |
| GET | `/api/nerve/servers` | `serve_servers` | List all servers | `{servers: [{id, hostname, ip, status, containers}]}` |
| GET | `/api/nerve/containers` | `serve_containers` | List all containers | `{containers: [{id, server_id, name, type, status, services}]}` |
| GET | `/api/nerve/containers/<vmid>` | `serve_container_detail` | Container detail | Full container + services + docs |
| GET | `/api/nerve/services` | `serve_services` | List all services | `{services: [{id, name, type, port, status, url, container}]}` |
| GET | `/api/nerve/services/<id>` | `serve_service_detail` | Service detail | Full service + relationships + docs + monitoring |
| GET | `/api/nerve/knowledge` | `serve_knowledge` | Knowledge search | `{results: [{id, type, label, properties, score}], total}` |
| GET | `/api/nerve/knowledge/<id>` | `serve_knowledge_detail` | Knowledge item | Full knowledge node + related items |
| POST | `/api/nerve/knowledge` | `create_knowledge` | Add knowledge | `{id, status, message}` |
| GET | `/api/nerve/requests` | `serve_requests` | List user requests | `{requests: [{id, type, title, status, created_at}]}` |
| POST | `/api/nerve/requests` | `create_request` | Create request | `{id, status, message}` |
| GET | `/api/nerve/agent/actions` | `serve_agent_actions` | Agent action log | `{actions: [{id, agent, type, status, details}]}` |
| POST | `/api/nerve/discover` | `trigger_discovery` | Trigger discovery | `{status, job_id, message}` |
| POST | `/api/nerve/verify` | `trigger_verification` | Trigger verification | `{status, job_id, message}` |
| GET | `/api/nerve/sync-status` | `serve_sync_status` | KB sync status | `{last_sync, status, files_synced}` |
| GET | `/api/nerve/design` | `serve_network_design` | Network design | `{design, rules}` |
| GET | `/api/nerve/wiki/documents` | `serve_wiki_docs` | Wiki documents | `{documents: [{id, title, slug, category}]}` |
| GET | `/api/nerve/wiki/<slug>` | `serve_wiki_doc` | Wiki document | `{title, content, slug, category}` |
| GET | `/sse` | `_handle_sse` | SSE endpoint | `text/event-stream` |

#### SSE Events

| Event | Data | Description |
|-------|------|-------------|
| `connected` | `{status: "connected", timestamp: ...}` | SSE connection established |
| `discovery-start` | `{job_id: ..., started_at: ...}` | Discovery job started |
| `discovery-progress` | `{job_id: ..., progress: ..., servers_found: ..., containers_found: ...}` | Discovery progress |
| `discovery-complete` | `{job_id: ..., servers_found: ..., containers_found: ..., services_found: ...}` | Discovery complete |
| `verification-start` | `{job_id: ..., started_at: ...}` | Verification job started |
| `verification-complete` | `{job_id: ..., services_checked: ..., services_up: ..., services_down: ...}` | Verification complete |
| `knowledge-update` | `{id: ..., type: ..., label: ...}` | Knowledge item updated |
| `service-status-change` | `{service_id: ..., name: ..., new_status: ..., old_status: ...}` | Service status changed |
| `request-created` | `{id: ..., type: ..., title: ...}` | New user request created |
| `agent-action` | `{id: ..., agent: ..., type: ..., status: ...}` | Agent action completed |

#### Internal Module Interfaces

```python
# nerve-center/discoverer.py
class ProxmoxDiscoverer:
    def __init__(self, proxmox_api_url, api_user, api_token_name, api_token_secret)
    def discover_servers(self) -> list[dict]  # Returns list of server dicts
    def discover_containers(self, server_id) -> list[dict]  # Returns list of container dicts
    def discover_services(self, container) -> list[dict]  # Returns list of service dicts
    def verify_server(self, server) -> str  # Returns 'up', 'down', 'unknown'
    def verify_container(self, container) -> str  # Returns 'running', 'stopped', 'unknown'
    def verify_service(self, service) -> dict  # Returns {status, response_time_ms, ...}
    def map_relationships(self, services) -> list[dict]  # Returns list of relationship dicts

# nerve-center/verifier.py
class ServiceVerifier:
    def __init__(self, db, knowledge_graph)
    def verify_all_services(self) -> dict  # Returns {checked, up, down, errors}
    def verify_service(self, service) -> dict  # Returns {status, response_time_ms, ...}
    def check_prometheus(self, service) -> bool  # Returns True if Prometheus is configured
    def check_caddy(self, service) -> bool  # Returns True if Caddy routing is configured
    def check_health(self, service) -> dict  # Returns health check result
    def detect_anomalies(self, service) -> list[dict]  # Returns list of anomalies

# nerve-center/knowledge.py
class KnowledgeGraph:
    def __init__(self, honcho_url, local_cache_path)
    def add_node(self, node: dict) -> str  # Returns node_id
    def add_edge(self, edge: dict) -> str  # Returns edge_id
    def search(self, query: str, limit: int = 10) -> list[dict]  # Returns knowledge results
    def get_node(self, node_id: str) -> dict  # Returns knowledge node
    def get_related(self, node_id: str, relationship_type: str) -> list[dict]  # Returns related nodes
    def update_node(self, node_id: str, properties: dict) -> bool  # Returns True on success
    def delete_node(self, node_id: str) -> bool  # Returns True on success
    def sync_to_honcho(self) -> bool  # Returns True on success
    def rebuild_local_cache(self) -> bool  # Returns True on success

# nerve-center/state.py
class StateManager:
    def __init__(self, db_path)
    def get_server(self, hostname) -> dict  # Returns server dict or None
    def get_container(self, vmid) -> dict  # Returns container dict or None
    def get_service(self, id) -> dict  # Returns service dict or None
    def list_servers(self) -> list[dict]  # Returns all servers
    def list_containers(self, server_id=None) -> list[dict]  # Returns all containers
    def list_services(self, container_id=None, type=None, status=None) -> list[dict]  # Returns services
    def upsert_server(self, server: dict) -> int  # Returns server_id
    def upsert_container(self, container: dict) -> int  # Returns container_id
    def upsert_service(self, service: dict) -> int  # Returns service_id
    def update_service_status(self, service_id, status, response_time_ms) -> bool
    def create_relationship(self, source_id, target_id, relationship_type) -> int
    def delete_relationship(self, source_id, target_id, relationship_type) -> bool
    def get_service_relationships(self, service_id) -> list[dict]
    def get_container_services(self, container_id) -> list[dict]
    def get_server_containers(self, server_id) -> list[dict]
    def create_wiki_document(self, doc: dict) -> int  # Returns doc_id
    def get_wiki_documents(self, category=None, related_service_id=None) -> list[dict]
    def get_wiki_document_by_slug(self, slug) -> dict
    def create_agent_action(self, action: dict) -> int  # Returns action_id
    def get_agent_actions(self, status=None, type=None) -> list[dict]
    def create_user_request(self, request: dict) -> int  # Returns request_id
    def get_user_requests(self, status=None) -> list[dict]
    def update_user_request(self, request_id, status, details) -> bool

# nerve-center/wiki-writer.py
class WikiWriter:
    def __init__(self, wiki_content_path, state_manager)
    def write_service_document(self, service) -> str  # Returns file path
    def write_container_document(self, container) -> str  # Returns file path
    def write_server_document(self, server) -> str  # Returns file path
    def write_network_design_document(self, design) -> str  # Returns file path
    def write_procedure_document(self, procedure) -> str  # Returns file path
    def write_troubleshooting_document(self, issue) -> str  # Returns file path
    def generate_service_card(self, service) -> str  # Returns markdown card
    def generate_container_card(self, container) -> str  # Returns markdown card
    def generate_server_card(self, server) -> str  # Returns markdown card
    def update_wiki_index(self) -> bool  # Returns True on success

# nerve-center/nerve-center.py — HTTP service
class NerveCenterHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self)
    def do_POST(self)
    def do_OPTIONS(self)
    def _send_cors_headers()
    def _send_json(code, data)
    def _serve_file(path, ct)

    # API handlers
    def serve_health_check(self) -> dict
    def serve_servers(self) -> dict
    def serve_containers(self) -> dict
    def serve_container_detail(self, vmid) -> dict
    def serve_services(self) -> dict
    def serve_service_detail(self, service_id) -> dict
    def serve_knowledge(self) -> dict
    def serve_knowledge_detail(self, node_id) -> dict
    def create_knowledge(self) -> dict
    def serve_requests(self) -> dict
    def create_request(self) -> dict
    def serve_agent_actions(self) -> dict
    def trigger_discovery(self) -> dict
    def trigger_verification(self) -> dict
    def serve_sync_status(self) -> dict
    def serve_network_design(self) -> dict
    def serve_wiki_docs(self) -> dict
    def serve_wiki_doc(self, slug) -> dict
    def _handle_sse(self)

# dashboard/js/nerve-center.js
class NerveCenter {
    constructor()
    init()
    loadServerView()
    loadContainerView()
    loadServiceView()
    loadKnowledgeView()
    loadRequestView()
    loadAgentActionView()
    loadWikiView()
    searchKnowledge(query)
    createRequest(title, description, type)
    refreshData()
    showServiceDetail(service_id)
    showContainerDetail(container_id)
    showServerDetail(server_id)
    subscribeToSSE()
}
```

---

## PART 2: ATOMIC TASK MANIFEST

### Phase 1: Core Infrastructure

#### [TASK-19-001]: Create SQLite Schema and State Manager

**Component/Scope:** `nerve-center/state.py` + `nerve-center/schema.sql`  
**Core Objective:** Create the SQLite database schema and Python state manager for all nerve center data.

**Dependencies:** None

**Context:**

The SQLite database is the operational state store. It holds servers, containers, services, relationships, wiki documents, agent actions, and user requests. The schema is defined in `schema.sql` and created/initialized by `state.py`.

**Schema file:** `nerve-center/schema.sql` (see above)

**Implementation:**

```python
# nerve-center/state.py
import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

class StateManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'nerve-center.db')
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database from schema.sql."""
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path) as f:
            schema = f.read()
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema)
            conn.commit()

    # --- Servers ---
    def get_server(self, hostname: str) -> Optional[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute("SELECT * FROM servers WHERE hostname = ?", (hostname,))
            row = cur.fetchone()
            return dict(row) if row else None

    def upsert_server(self, server: dict) -> int:
        """Insert or update server. Returns server_id."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                INSERT OR REPLACE INTO servers (hostname, ip_address, proxmox_api_url,
                    proxmox_api_user, proxmox_api_token_name, proxmox_api_token_secret,
                    status, last_discovered, last_verified, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                RETURNING id
            """, (
                server['hostname'],
                server['ip_address'],
                server.get('proxmox_api_url', ''),
                server.get('proxmox_api_user', ''),
                server.get('proxmox_api_token_name', ''),
                server.get('proxmox_api_token_secret', ''),
                server.get('status', 'unknown'),
                server.get('last_discovered'),
                server.get('last_verified'),
                datetime.now().isoformat()
            ))
            conn.commit()
            return cur.fetchone()[0]

    def list_servers(self) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute("SELECT * FROM servers ORDER BY hostname")
            return [dict(r) for r in cur.fetchall()]

    # --- Containers ---
    def get_container(self, vmid: int) -> Optional[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute("SELECT * FROM containers WHERE vmid = ?", (vmid,))
            row = cur.fetchone()
            return dict(row) if row else None

    def upsert_container(self, container: dict) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                INSERT OR REPLACE INTO containers (server_id, vmid, name, type, status,
                    ip_addresses, memory_mb, cpu_cores, disk_total_mb, disk_used_mb,
                    os, template, last_discovered, last_verified, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                RETURNING id
            """, (
                container['server_id'],
                container['vmid'],
                container['name'],
                container['type'],
                container.get('status', 'unknown'),
                json.dumps(container.get('ip_addresses', [])),
                container.get('memory_mb'),
                container.get('cpu_cores'),
                container.get('disk_total_mb'),
                container.get('disk_used_mb'),
                container.get('os'),
                container.get('template'),
                container.get('last_discovered'),
                container.get('last_verified'),
                datetime.now().isoformat()
            ))
            conn.commit()
            return cur.fetchone()[0]

    def list_containers(self, server_id: int = None) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if server_id:
                cur = conn.execute("SELECT * FROM containers WHERE server_id = ? ORDER BY vmid", (server_id,))
            else:
                cur = conn.execute("SELECT * FROM containers ORDER BY server_id, vmid")
            return [dict(r) for r in cur.fetchall()]

    def get_server_containers(self, server_id: int) -> List[dict]:
        return self.list_containers(server_id)

    # --- Services ---
    def get_service(self, service_id: int) -> Optional[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute("SELECT * FROM services WHERE id = ?", (service_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def upsert_service(self, service: dict) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                INSERT OR REPLACE INTO services (container_id, name, type, port, protocol,
                    url, status, response_time_ms, last_checked, prometheus_job,
                    prometheus_target, monitoring_configured, caddy_configured,
                    health_check_url, health_check_interval, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                RETURNING id
            """, (
                service['container_id'],
                service['name'],
                service['type'],
                service.get('port'),
                service.get('protocol', 'tcp'),
                service.get('url'),
                service.get('status', 'unknown'),
                service.get('response_time_ms'),
                service.get('last_checked'),
                service.get('prometheus_job'),
                service.get('prometheus_target'),
                service.get('monitoring_configured', 0),
                service.get('caddy_configured', 0),
                service.get('health_check_url'),
                service.get('health_check_interval'),
                datetime.now().isoformat()
            ))
            conn.commit()
            return cur.fetchone()[0]

    def list_services(self, container_id: int = None, type: str = None, status: str = None) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT * FROM services WHERE 1=1"
            params = []
            if container_id:
                query += " AND container_id = ?"
                params.append(container_id)
            if type:
                query += " AND type = ?"
                params.append(type)
            if status:
                query += " AND status = ?"
                params.append(status)
            query += " ORDER BY name"
            cur = conn.execute(query, params)
            return [dict(r) for r in cur.fetchall()]

    def update_service_status(self, service_id: int, status: str, response_time_ms: int = None) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE services SET status = ?, response_time_ms = ?, last_checked = ?, updated_at = ?
                WHERE id = ?
            """, (status, response_time_ms, datetime.now().isoformat(), datetime.now().isoformat(), service_id))
            conn.commit()
            return True

    def get_container_services(self, container_id: int) -> List[dict]:
        return self.list_services(container_id=container_id)

    def get_service_relationships(self, service_id: int) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute("""
                SELECT sr.*, s.name as target_name, s.type as target_type
                FROM service_relationships sr
                JOIN services s ON sr.target_service_id = s.id
                WHERE sr.source_service_id = ?
                UNION ALL
                SELECT sr.*, s.name as target_name, s.type as target_type
                FROM service_relationships sr
                JOIN services s ON sr.source_service_id = s.id
                WHERE sr.target_service_id = ?
            """, (service_id, service_id))
            return [dict(r) for r in cur.fetchall()]

    def create_relationship(self, source_id: int, target_id: int, relationship_type: str) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                INSERT OR IGNORE INTO service_relationships (source_service_id, target_service_id, relationship_type)
                VALUES (?, ?, ?)
                RETURNING id
            """, (source_id, target_id, relationship_type))
            conn.commit()
            row = cur.fetchone()
            return row[0] if row else None

    def delete_relationship(self, source_id: int, target_id: int, relationship_type: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                DELETE FROM service_relationships
                WHERE source_service_id = ? AND target_service_id = ? AND relationship_type = ?
            """, (source_id, target_id, relationship_type))
            conn.commit()
            return True

    # --- Wiki Documents ---
    def create_wiki_document(self, doc: dict) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                INSERT INTO wiki_documents (title, slug, category, content, source,
                    related_service_id, related_container_id, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                RETURNING id
            """, (
                doc['title'], doc['slug'], doc['category'], doc['content'],
                doc.get('source', 'agent-generated'),
                doc.get('related_service_id'), doc.get('related_container_id'),
                doc.get('last_updated', datetime.now().isoformat())
            ))
            conn.commit()
            return cur.fetchone()[0]

    def get_wiki_documents(self, category: str = None, related_service_id: int = None) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT id, title, slug, category, source, related_service_id, last_updated FROM wiki_documents WHERE 1=1"
            params = []
            if category:
                query += " AND category = ?"
                params.append(category)
            if related_service_id:
                query += " AND related_service_id = ?"
                params.append(related_service_id)
            query += " ORDER BY last_updated DESC"
            cur = conn.execute(query, params)
            return [dict(r) for r in cur.fetchall()]

    def get_wiki_document_by_slug(self, slug: str) -> Optional[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute("SELECT * FROM wiki_documents WHERE slug = ?", (slug,))
            row = cur.fetchone()
            return dict(row) if row else None

    # --- Agent Actions ---
    def create_agent_action(self, action: dict) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                INSERT INTO agent_actions (agent_id, action_type, target_type, target_id,
                    status, details, started_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                RETURNING id
            """, (
                action['agent_id'], action['action_type'], action['target_type'],
                action.get('target_id'), action.get('status', 'pending'),
                json.dumps(action.get('details', {})),
                action.get('started_at', datetime.now().isoformat())
            ))
            conn.commit()
            return cur.fetchone()[0]

    def get_agent_actions(self, status: str = None, type: str = None) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT * FROM agent_actions WHERE 1=1"
            params = []
            if status:
                query += " AND status = ?"
                params.append(status)
            if type:
                query += " AND action_type = ?"
                params.append(type)
            query += " ORDER BY created_at DESC LIMIT 100"
            cur = conn.execute(query, params)
            return [dict(r) for r in cur.fetchall()]

    # --- User Requests ---
    def create_user_request(self, request: dict) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                INSERT INTO user_requests (user_id, request_type, title, description, status)
                VALUES (?, ?, ?, ?, ?)
                RETURNING id
            """, (
                request['user_id'], request['request_type'], request['title'],
                request.get('description', ''), 'pending'
            ))
            conn.commit()
            return cur.fetchone()[0]

    def get_user_requests(self, status: str = None) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT * FROM user_requests WHERE 1=1"
            params = []
            if status:
                query += " AND status = ?"
                params.append(status)
            query += " ORDER BY created_at DESC"
            cur = conn.execute(query, params)
            return [dict(r) for r in cur.fetchall()]

    def update_user_request(self, request_id: int, status: str, details: dict = None) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE user_requests SET status = ?, updated_at = ?
                WHERE id = ?
            """, (status, datetime.now().isoformat(), request_id))
            if details:
                conn.execute("UPDATE user_requests SET details = ? WHERE id = ?",
                           (json.dumps(details), request_id))
            conn.commit()
            return True
```

**Edge Cases:**
- SQLite concurrent writes: Use WAL mode (`PRAGMA journal_mode=WAL`) for better concurrency
- Database migration: If schema changes, detect version and run migrations
- Large result sets: Use pagination for `list_*` methods (limit 100, offset)

**Verification:**
```python
# Test state manager
sm = StateManager('/tmp/test-nerve.db')
assert sm.get_server('grid-core-01') is None
sid = sm.upsert_server({'hostname': 'grid-core-01', 'ip_address': '10.10.30.22', 'proxmox_api_url': 'https://10.10.30.22:8006/api2/json', 'proxmox_api_user': 'root@pam', 'proxmox_api_token_name': 'nerve-center', 'proxmox_api_token_secret': 'test', 'status': 'up'})
assert sid is not None
s = sm.get_server('grid-core-01')
assert s['hostname'] == 'grid-core-01'
assert s['status'] == 'up'
```

---

#### [TASK-19-002]: Create Proxmox Discoverer

**Component/Scope:** `nerve-center/discoverer.py`  
**Core Objective:** Scan Proxmox API to discover servers, containers, VMs, and running services.

**Dependencies:** TASK-19-001 (SQLite state manager)

**Context:**

The discoverer reads the Proxmox API to build the live state of the network. It discovers:
1. **Servers** (Proxmox hosts) — hostname, IP, API URL, credentials
2. **Containers/VMs** (LXCs on Proxmox) — vmid, name, type, status, IP, resources
3. **Services** (running on containers) — ports, protocols, URLs, health

**Implementation:**

```python
# nerve-center/discoverer.py
import json
import urllib.request
import urllib.error
import ssl
import socket
import time
from datetime import datetime
from typing import List, Dict, Optional

class ProxmoxDiscoverer:
    def __init__(self, state_manager, api_url, api_user, api_token_name, api_token_secret):
        self.state = state_manager
        self.api_url = api_url.rstrip('/')
        self.api_user = api_user
        self.api_token_name = api_token_name
        self.api_token_secret = api_token_secret
        self._verify_ssl = False  # Self-signed certs on Proxmox

    def _api_get(self, path: str) -> dict:
        """Make authenticated GET request to Proxmox API."""
        url = f"{self.api_url}/api2/json/{path}"
        req = urllib.request.Request(url)
        req.add_header('Authorization', f'PVEAPIToken={self.api_token_name}!{self.api_token_secret}')
        req.add_header('Content-Type', 'application/json')

        ctx = ssl.create_default_context()
        if not self._verify_ssl:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        try:
            with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            raise Exception(f"Proxmox API error: {e.code} {e.reason}")
        except socket.timeout:
            raise Exception("Proxmox API timeout")

    def discover_servers(self) -> List[dict]:
        """Discover all Proxmox hosts."""
        servers = []
        try:
            data = self._api_get('nodes')
            for node in data.get('data', []):
                hostname = node.get('node', '')
                ip = node.get('ip', '')
                status = 'up' if node.get('online') else 'down'
                server = {
                    'hostname': hostname,
                    'ip_address': ip,
                    'proxmox_api_url': f"https://{ip}:8006/api2/json",
                    'proxmox_api_user': self.api_user,
                    'proxmox_api_token_name': self.api_token_name,
                    'proxmox_api_token_secret': self.api_token_secret,
                    'status': status,
                    'last_discovered': datetime.now().isoformat(),
                    'last_verified': datetime.now().isoformat()
                }
                sid = self.state.upsert_server(server)
                servers.append({**server, 'id': sid})
        except Exception as e:
            print(f"Error discovering servers: {e}")
        return servers

    def discover_containers(self, server_hostname: str) -> List[dict]:
        """Discover all containers/VMs on a Proxmox host."""
        containers = []
        try:
            # Get all nodes (LXC)
            lxc_data = self._api_get(f"nodes/{server_hostname}/lxc")
            for lxc in lxc_data.get('data', []):
                vmid = lxc.get('vmid', 0)
                name = lxc.get('name', f'vm-{vmid}')
                status = 'running' if lxc.get('status') == 'running' else 'stopped'
                ip_addrs = []
                try:
                    net_data = self._api_get(f"nodes/{server_hostname}/lxc/{vmid}/config")
                    net_conf = net_data.get('data', {}).get('net', '')
                    if net_conf:
                        for iface in net_conf.split(','):
                            if 'ip=' in iface:
                                ip = iface.split('=')[1].split('/')[0]
                                ip_addrs.append(ip)
                except:
                    pass

                # Get resource info
                res_data = self._api_get(f"nodes/{server_hostname}/lxc/{vmid}/status/current")
                res = res_data.get('data', {})

                server = self.state.get_server(server_hostname)
                server_id = server['id'] if server else None

                container = {
                    'server_id': server_id,
                    'vmid': vmid,
                    'name': name,
                    'type': 'lxc',
                    'status': status,
                    'ip_addresses': ip_addrs,
                    'memory_mb': res.get('maxmem', 0),
                    'cpu_cores': res.get('maxcpu', 0),
                    'disk_total_mb': res.get('maxdisk', 0) // (1024 * 1024),
                    'disk_used_mb': res.get('disk', 0) // (1024 * 1024),
                    'os': None,  # Will be populated from config
                    'template': None,
                    'last_discovered': datetime.now().isoformat(),
                    'last_verified': datetime.now().isoformat()
                }
                cid = self.state.upsert_container(container)
                containers.append({**container, 'id': cid})
        except Exception as e:
            print(f"Error discovering containers on {server_hostname}: {e}")
        return containers

    def discover_services(self, container: dict) -> List[dict]:
        """Discover services running on a container."""
        services = []
        # Known service port mappings
        service_map = [
            ('http', 80, 'HTTP'),
            ('https', 443, 'HTTPS'),
            ('ssh', 22, 'SSH'),
            ('postgresql', 5432, 'PostgreSQL'),
            ('mysql', 3306, 'MySQL'),
            ('redis', 6379, 'Redis'),
            ('prometheus', 9090, 'Prometheus'),
            ('grafana', 3000, 'Grafana'),
            ('caddy', 8080, 'Caddy'),
            ('portainer', 9443, 'Portainer'),
            ('minecraft', 19132, 'Minecraft'),
            ('samba', 445, 'Samba'),
            ('ollama', 11434, 'Ollama'),
            ('open-webui', 3002, 'Open WebUI'),
            ('omada', 8043, 'Omada Controller'),
            ('proxmox', 8006, 'Proxmox API'),
        ]

        for proto, port, name in service_map:
            # Check if port is open via TCP probe
            is_open = self._check_port_open(container['ip_addresses'], port)
            if is_open:
                url = f"http://{container['ip_addresses'][0]}:{port}" if proto in ('http', 'https') else None
                service = {
                    'container_id': container['id'],
                    'name': name,
                    'type': proto,
                    'port': port,
                    'protocol': 'tcp',
                    'url': url,
                    'status': 'up' if is_open else 'down',
                    'response_time_ms': 0,
                    'last_checked': datetime.now().isoformat(),
                    'prometheus_job': None,
                    'prometheus_target': None,
                    'monitoring_configured': 0,
                    'caddy_configured': 0,
                    'health_check_url': None,
                    'health_check_interval': None
                }
                sid = self.state.upsert_service(service)
                services.append({**service, 'id': sid})
        return services

    def _check_port_open(self, ip_addresses: List[str], port: int, timeout: int = 3) -> bool:
        """Check if a TCP port is open on any of the given IPs."""
        for ip in ip_addresses:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((ip, port))
                sock.close()
                if result == 0:
                    return True
            except:
                pass
        return False

    def verify_server(self, server: dict) -> str:
        """Verify server is reachable."""
        try:
            self._api_get('version')
            return 'up'
        except:
            return 'down'

    def verify_container(self, container: dict) -> str:
        """Verify container is running."""
        try:
            data = self._api_get(f"nodes/{container['server_hostname']}/lxc/{container['vmid']}/status/current")
            return 'running' if data.get('data', {}).get('status') == 'running' else 'stopped'
        except:
            return 'unknown'

    def verify_service(self, service: dict) -> dict:
        """Verify service health."""
        if not service.get('url'):
            return {'status': 'unknown', 'response_time_ms': None}

        start = time.time()
        try:
            req = urllib.request.Request(service['url'])
            ctx = ssl.create_default_context()
            if not self._verify_ssl:
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
                elapsed = (time.time() - start) * 1000
                return {'status': 'up', 'response_time_ms': round(elapsed, 1)}
        except:
            elapsed = (time.time() - start) * 1000
            return {'status': 'down', 'response_time_ms': None}

    def discover_all(self) -> dict:
        """Full discovery: servers → containers → services."""
        result = {
            'servers': [],
            'containers': [],
            'services': [],
            'errors': []
        }

        # Discover servers
        servers = self.discover_servers()
        result['servers'] = servers

        # Discover containers on each server
        for server in servers:
            if server['status'] != 'up':
                continue
            containers = self.discover_containers(server['hostname'])
            result['containers'].extend(containers)

            # Discover services on each container
            for container in containers:
                if container['status'] != 'running':
                    continue
                services = self.discover_services(container)
                result['services'].extend(services)

        return result
```

**Edge Cases:**
- Proxmox API rate limiting: Add 1s delay between API calls
- Self-signed certs: Disable SSL verification for Proxmox
- Large container counts: Paginate API calls (limit 100)
- Network unreachable containers: Mark as 'unknown' status

---

#### [TASK-19-003]: Create Knowledge Graph Manager

**Component/Scope:** `nerve-center/knowledge.py`  
**Core Objective:** Manage the vector knowledge graph — store, search, and retrieve network knowledge via Honcho API.

**Dependencies:** None (Honcho is external, CT130:8000)

**Context:**

The knowledge graph stores **knowledge** (not state). It uses Honcho (CT130:8000) for vector storage and semantic search. A local JSON cache mirrors the graph for fast access.

**Implementation:**

```python
# nerve-center/knowledge.py
import json
import os
import urllib.request
import urllib.error
from typing import List, Dict, Optional

class KnowledgeGraph:
    def __init__(self, honcho_url: str = 'http://10.10.30.130:8000', local_cache_path: str = None):
        self.honcho_url = honcho_url.rstrip('/')
        self.local_cache_path = local_cache_path or os.path.join(os.path.dirname(__file__), 'knowledge-graph.json')
        self._cache = self._load_cache()

    def _load_cache(self) -> dict:
        """Load local knowledge cache."""
        if os.path.exists(self.local_cache_path):
            with open(self.local_cache_path) as f:
                return json.load(f)
        return {'nodes': [], 'edges': []}

    def _save_cache(self):
        """Save local knowledge cache."""
        with open(self.local_cache_path, 'w') as f:
            json.dump(self._cache, f, indent=2)

    def add_node(self, node: dict) -> str:
        """Add a knowledge node to the graph."""
        node_id = node.get('id', f"node-{len(self._cache['nodes']) + 1}")
        node['id'] = node_id

        # Add to local cache
        existing = next((n for n in self._cache['nodes'] if n['id'] == node_id), None)
        if existing:
            existing.update(node)
        else:
            self._cache['nodes'].append(node)

        # Sync to Honcho
        self._sync_to_honcho(node)
        self._save_cache()
        return node_id

    def add_edge(self, edge: dict) -> str:
        """Add an edge between two knowledge nodes."""
        edge_id = f"edge-{len(self._cache['edges']) + 1}"
        edge['id'] = edge_id
        self._cache['edges'].append(edge)
        self._save_cache()
        return edge_id

    def search(self, query: str, limit: int = 10) -> List[dict]:
        """Search knowledge graph for relevant nodes."""
        # Try Honcho first for semantic search
        try:
            url = f"{self.honcho_url}/api/search?q={urllib.parse.quote(query)}&limit={limit}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                return data.get('results', [])
        except:
            pass

        # Fallback to local keyword search
        results = []
        query_lower = query.lower()
        for node in self._cache['nodes']:
            score = 0
            label = node.get('label', '').lower()
            props = json.dumps(node.get('properties', {})).lower()
            if query_lower in label:
                score += 10
            if query_lower in props:
                score += 5
            if score > 0:
                results.append({'node': node, 'score': score})

        results.sort(key=lambda x: x['score'], reverse=True)
        return [r['node'] for r in results[:limit]]

    def get_node(self, node_id: str) -> Optional[dict]:
        """Get a knowledge node by ID."""
        return next((n for n in self._cache['nodes'] if n['id'] == node_id), None)

    def get_related(self, node_id: str, relationship_type: str = None) -> List[dict]:
        """Get nodes related to a given node."""
        related = []
        for edge in self._cache['edges']:
            if edge.get('from') == node_id or edge.get('to') == node_id:
                if relationship_type is None or edge.get('type') == relationship_type:
                    target_id = edge.get('to') if edge.get('from') == node_id else edge.get('from')
                    node = self.get_node(target_id)
                    if node:
                        related.append(node)
        return related

    def update_node(self, node_id: str, properties: dict) -> bool:
        """Update a knowledge node's properties."""
        node = self.get_node(node_id)
        if not node:
            return False
        node['properties'].update(properties)
        self._save_cache()
        return True

    def delete_node(self, node_id: str) -> bool:
        """Delete a knowledge node."""
        node = self.get_node(node_id)
        if not node:
            return False
        self._cache['nodes'] = [n for n in self._cache['nodes'] if n['id'] != node_id]
        self._save_cache()
        return True

    def _sync_to_honcho(self, node: dict):
        """Sync node to Honcho (external)."""
        try:
            url = f"{self.honcho_url}/api/node"
            data = json.dumps(node).encode()
            req = urllib.request.Request(url, data=data, method='POST')
            req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp.read()
        except:
            pass  # Honcho unavailable, keep local

    def sync_to_honcho(self) -> bool:
        """Sync entire local cache to Honcho."""
        try:
            for node in self._cache['nodes']:
                self._sync_to_honcho(node)
            return True
        except:
            return False

    def rebuild_local_cache(self) -> bool:
        """Rebuild local cache from Honcho."""
        try:
            url = f"{self.honcho_url}/api/graph"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                self._cache = data
                self._save_cache()
                return True
        except:
            return False
```

**Edge Cases:**
- Honcho unavailable: Fall back to local keyword search
- Large graphs: Paginate Honcho queries
- Network partitions: Keep local cache operational

---

#### [TASK-19-004]: Create Service Verifier

**Component/Scope:** `nerve-center/verifier.py`  
**Core Objective:** Verify service health, check Prometheus/Caddy configuration, detect anomalies.

**Dependencies:** TASK-19-001 (SQLite state manager), TASK-19-003 (Knowledge graph)

**Context:**

The verifier checks each service for:
1. **Health**: Is the service responding? (HTTP/TCP probe)
2. **Prometheus**: Is it being scraped? (Query Prometheus API)
3. **Caddy**: Is it routed? (Check Caddy config)
4. **Anomalies**: Port conflicts, missing docs, unmonitored services

**Implementation:**

```python
# nerve-center/verifier.py
import json
import socket
import time
import urllib.request
import urllib.error
import ssl
from datetime import datetime
from typing import List, Dict, Optional

class ServiceVerifier:
    def __init__(self, state_manager, knowledge_graph):
        self.state = state_manager
        self.kg = knowledge_graph

    def verify_all_services(self) -> dict:
        """Verify all services. Returns summary."""
        services = self.state.list_services()
        result = {'checked': 0, 'up': 0, 'down': 0, 'errors': []}

        for service in services:
            try:
                health = self.verify_service(service)
                self.state.update_service_status(service['id'], health['status'], health.get('response_time_ms'))
                result['checked'] += 1
                if health['status'] == 'up':
                    result['up'] += 1
                else:
                    result['down'] += 1
            except Exception as e:
                result['errors'].append({'service_id': service['id'], 'error': str(e)})

        return result

    def verify_service(self, service: dict) -> dict:
        """Verify a single service."""
        if not service.get('url'):
            return {'status': 'unknown', 'response_time_ms': None}

        start = time.time()
        try:
            req = urllib.request.Request(service['url'])
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
                elapsed = (time.time() - start) * 1000
                return {'status': 'up', 'response_time_ms': round(elapsed, 1)}
        except:
            elapsed = (time.time() - start) * 1000
            return {'status': 'down', 'response_time_ms': None}

    def check_prometheus(self, service: dict) -> bool:
        """Check if service is configured in Prometheus."""
        try:
            url = "http://10.10.30.120:9090/api/v1/targets"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                targets = data.get('data', {}).get('activeTargets', [])
                for target in targets:
                    if target.get('scrapeUrl') == service.get('url'):
                        return True
                return False
        except:
            return False

    def check_caddy(self, service: dict) -> bool:
        """Check if service is routed via Caddy."""
        # Check Caddy config file
        caddy_config_path = '/etc/caddy/Caddyfile'
        try:
            with open(caddy_config_path) as f:
                config = f.read()
                if service.get('url') and service['url'] in config:
                    return True
                # Check by port
                if service.get('port') and f":{service['port']}" in config:
                    return True
                return False
        except:
            return False

    def detect_anomalies(self, service: dict) -> List[dict]:
        """Detect anomalies for a service."""
        anomalies = []

        # Check for port conflicts
        other_services = self.state.list_services(port=service.get('port'))
        if len(other_services) > 1:
            anomalies.append({
                'type': 'port_conflict',
                'severity': 'error',
                'message': f"Port {service['port']} used by {len(other_services)} services"
            })

        # Check if monitoring is configured
        if not self.check_prometheus(service):
            anomalies.append({
                'type': 'missing_monitoring',
                'severity': 'warning',
                'message': f"Service {service['name']} not monitored by Prometheus"
            })

        # Check if Caddy routing is configured
        if not self.check_caddy(service):
            anomalies.append({
                'type': 'missing_caddy_route',
                'severity': 'info',
                'message': f"Service {service['name']} not routed via Caddy"
            })

        # Check if wiki document exists
        wiki_docs = self.state.get_wiki_documents(related_service_id=service['id'])
        if not wiki_docs:
            anomalies.append({
                'type': 'missing_documentation',
                'severity': 'info',
                'message': f"Service {service['name']} has no wiki documentation"
            })

        return anomalies

    def verify_all(self) -> dict:
        """Full verification: services, Prometheus, Caddy, anomalies."""
        services = self.state.list_services()
        result = {
            'services': [],
            'prometheus_targets': [],
            'caddy_routes': [],
            'anomalies': []
        }

        for service in services:
            health = self.verify_service(service)
            prometheus = self.check_prometheus(service)
            caddy = self.check_caddy(service)
            anomalies = self.detect_anomalies(service)

            result['services'].append({
                **service,
                'health': health,
                'prometheus_configured': prometheus,
                'caddy_configured': caddy
            })
            result['anomalies'].extend(anomalies)

        # Get Prometheus targets
        try:
            url = "http://10.10.30.120:9090/api/v1/targets"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                result['prometheus_targets'] = data.get('data', {}).get('activeTargets', [])
        except:
            pass

        return result
```

**Edge Cases:**
- Prometheus unreachable: Mark as 'unknown'
- Caddy config not on CT131: Skip Caddy check
- Large service lists: Batch verification

---

#### [TASK-19-005]: Create Wiki Writer

**Component/Scope:** `nerve-center/wiki-writer.py`  
**Core Objective:** Generate wiki documentation from state data — service cards, container docs, server docs, network design.

**Dependencies:** TASK-19-001 (SQLite state manager)

**Context:**

The wiki writer generates markdown documentation as a byproduct of agent actions. It writes to `wiki-content/` and updates the wiki index.

**Implementation:**

```python
# nerve-center/wiki-writer.py
import os
import json
from datetime import datetime
from typing import List, Dict, Optional

class WikiWriter:
    def __init__(self, wiki_content_path: str, state_manager):
        self.wiki_path = wiki_content_path
        self.state = state_manager

    def write_service_document(self, service: dict) -> str:
        """Write service documentation."""
        slug = f"service-{service['name'].lower().replace(' ', '-')}"
        content = f"""---
title: "{service['name']}"
type: service
status: {"active" if service.get('status') == 'up' else "down"}
last_updated: "{datetime.now().isoformat()}"
tags: [{service['type']}, {service.get('name', '')}]
---

# {service['name']}

## Overview
- **Type:** {service['type']}
- **Port:** {service.get('port', 'N/A')}
- **Protocol:** {service.get('protocol', 'tcp')}
- **URL:** {service.get('url', 'N/A')}
- **Status:** {service.get('status', 'unknown')}
- **Response Time:** {service.get('response_time_ms', 'N/A')}ms

## Container
- **Name:** {self._get_container_name(service.get('container_id'))}
- **IP:** {self._get_container_ip(service.get('container_id'))}

## Monitoring
- **Prometheus:** {"Configured" if service.get('monitoring_configured') else "Not configured"}
- **Health Check:** {service.get('health_check_url', 'N/A')}

## Documentation
Generated automatically by the Network Nerve Center agent.
"""
        self._write_wiki_file(slug, content, 'service', service.get('id'))
        return slug

    def write_container_document(self, container: dict) -> str:
        """Write container documentation."""
        slug = f"container-{container['name'].lower().replace(' ', '-')}"
        content = f"""---
title: "{container['name']}"
type: container
status: {"active" if container.get('status') == 'running' else "stopped"}
last_updated: "{datetime.now().isoformat()}"
tags: [{container['type']}, {container.get('name', '')}]
---

# {container['name']}

## Overview
- **VMID:** {container['vmid']}
- **Type:** {container['type']}
- **Status:** {container.get('status', 'unknown')}
- **IP Addresses:** {', '.join(container.get('ip_addresses', []))}

## Resources
- **Memory:** {container.get('memory_mb', 'N/A')} MB
- **CPU:** {container.get('cpu_cores', 'N/A')} cores
- **Disk Total:** {container.get('disk_total_mb', 'N/A')} MB
- **Disk Used:** {container.get('disk_used_mb', 'N/A')} MB

## OS
- **OS:** {container.get('os', 'N/A')}
- **Template:** {container.get('template', 'N/A')}

## Services
{self._get_container_services_markdown(container.get('id'))}

## Documentation
Generated automatically by the Network Nerve Center agent.
"""
        self._write_wiki_file(slug, content, 'infrastructure', container.get('id'))
        return slug

    def write_server_document(self, server: dict) -> str:
        """Write server documentation."""
        slug = f"server-{server['hostname'].lower().replace('-', '-')}"
        content = f"""---
title: "{server['hostname']}"
type: server
status: {"active" if server.get('status') == 'up' else "down"}
last_updated: "{datetime.now().isoformat()}"
tags: [proxmox, {server.get('hostname', '')}]
---

# {server['hostname']}

## Overview
- **IP Address:** {server['ip_address']}
- **Status:** {server.get('status', 'unknown')}
- **Proxmox API:** {server.get('proxmox_api_url', 'N/A')}

## Containers
{self._get_server_containers_markdown(self._get_server_id(server['hostname']))}

## Documentation
Generated automatically by the Network Nerve Center agent.
"""
        self._write_wiki_file(slug, content, 'infrastructure', None)
        return slug

    def write_network_design_document(self, design: dict) -> str:
        """Write network design documentation."""
        slug = "network-design"
        content = f"""---
title: "Network Design"
type: design
status: active
last_updated: "{datetime.now().isoformat()}"
tags: [network, design]
---

# Network Design

## Network Architecture
{json.dumps(design, indent=2)}

## Documentation
Generated automatically by the Network Nerve Center agent.
"""
        self._write_wiki_file(slug, content, 'design', None)
        return slug

    def write_procedure_document(self, procedure: dict) -> str:
        """Write procedure documentation."""
        slug = f"procedure-{procedure['name'].lower().replace(' ', '-')}"
        content = f"""---
title: "{procedure['name']}"
type: procedure
status: active
last_updated: "{datetime.now().isoformat()}"
tags: [procedure, {procedure.get('category', '')}]
---

# {procedure['name']}

## Description
{procedure.get('description', '')}

## Steps
{procedure.get('steps', [])}

## Documentation
Generated automatically by the Network Nerve Center agent.
"""
        self._write_wiki_file(slug, content, 'procedure', None)
        return slug

    def write_troubleshooting_document(self, issue: dict) -> str:
        """Write troubleshooting documentation."""
        slug = f"troubleshooting-{issue['title'].lower().replace(' ', '-')}"
        content = f"""---
title: "{issue['title']}"
type: troubleshooting
status: active
last_updated: "{datetime.now().isoformat()}"
tags: [troubleshooting, {issue.get('category', '')}]
---

# {issue['title']}

## Description
{issue.get('description', '')}

## Resolution
{issue.get('resolution', '')}

## Documentation
Generated automatically by the Network Nerve Center agent.
"""
        self._write_wiki_file(slug, content, 'troubleshooting', None)
        return slug

    def generate_service_card(self, service: dict) -> str:
        """Generate a service card markdown."""
        return f"""
| Service | Type | Port | Status | URL |
|---------|------|------|--------|-----|
| {service['name']} | {service['type']} | {service.get('port', 'N/A')} | {service.get('status', 'unknown')} | {service.get('url', 'N/A')} |
"""

    def generate_container_card(self, container: dict) -> str:
        """Generate a container card markdown."""
        return f"""
| Container | VMID | Type | Status | IP |
|-----------|------|------|--------|----|
| {container['name']} | {container['vmid']} | {container['type']} | {container.get('status', 'unknown')} | {', '.join(container.get('ip_addresses', []))} |
"""

    def generate_server_card(self, server: dict) -> str:
        """Generate a server card markdown."""
        return f"""
| Server | IP | Status | Proxmox API |
|--------|-----|--------|-------------|
| {server['hostname']} | {server['ip_address']} | {server.get('status', 'unknown')} | {server.get('proxmox_api_url', 'N/A')} |
"""

    def update_wiki_index(self) -> bool:
        """Update wiki index."""
        # Read existing index or create new one
        index_path = os.path.join(self.wiki_path, 'wiki-index.json')
        try:
            with open(index_path) as f:
                index = json.load(f)
        except:
            index = {'pages': [], 'generated_at': ''}

        # Add all wiki documents
        docs = self.state.get_wiki_documents()
        index['pages'] = [{
            'slug': d['slug'],
            'title': d['title'],
            'category': d['category'],
            'source': d.get('source', 'agent-generated'),
            'last_updated': d.get('last_updated')
        } for d in docs]
        index['generated_at'] = datetime.now().isoformat()

        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)
        return True

    # --- Helpers ---
    def _write_wiki_file(self, slug: str, content: str, category: str, related_id: int = None):
        """Write a wiki file."""
        # Determine directory
        if category == 'service':
            dir_path = os.path.join(self.wiki_path, 'services')
        elif category == 'infrastructure':
            dir_path = os.path.join(self.wiki_path, 'infrastructure')
        elif category == 'design':
            dir_path = os.path.join(self.wiki_path, 'design')
        elif category == 'procedure':
            dir_path = os.path.join(self.wiki_path, 'procedures')
        elif category == 'troubleshooting':
            dir_path = os.path.join(self.wiki_path, 'troubleshooting')
        else:
            dir_path = os.path.join(self.wiki_path, 'misc')

        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, f"{slug}.md")

        with open(file_path, 'w') as f:
            f.write(content)

        # Update state
        self.state.create_wiki_document({
            'title': slug.replace('-', ' ').title(),
            'slug': slug,
            'category': category,
            'content': content,
            'source': 'agent-generated',
            'related_service_id': related_id,
            'last_updated': datetime.now().isoformat()
        })

    def _get_container_name(self, container_id: int) -> str:
        """Get container name by ID."""
        if not container_id:
            return 'N/A'
        container = self.state.get_container(container_id)
        return container['name'] if container else 'N/A'

    def _get_container_ip(self, container_id: int) -> str:
        """Get container IP by ID."""
        if not container_id:
            return 'N/A'
        container = self.state.get_container(container_id)
        return ', '.join(container.get('ip_addresses', [])) if container else 'N/A'

    def _get_container_services_markdown(self, container_id: int) -> str:
        """Get services markdown for a container."""
        if not container_id:
            return '- No services discovered\n'
        services = self.state.get_container_services(container_id)
        if not services:
            return '- No services discovered\n'
        md = ''
        for s in services:
            md += f"- **{s['name']}**: {s['type']}:{s.get('port', 'N/A')} ({s.get('status', 'unknown')})\n"
        return md

    def _get_server_containers_markdown(self, server_id: int) -> str:
        """Get containers markdown for a server."""
        if not server_id:
            return '- No containers discovered\n'
        containers = self.state.get_server_containers(server_id)
        if not containers:
            return '- No containers discovered\n'
        md = ''
        for c in containers:
            md += f"- **{c['name']}** (VMID {c['vmid']}): {c['type']} ({c.get('status', 'unknown')})\n"
        return md

    def _get_server_id(self, hostname: str) -> int:
        """Get server ID by hostname."""
        server = self.state.get_server(hostname)
        return server['id'] if server else None
```

**Edge Cases:**
- Wiki path doesn't exist: Create it
- File conflicts: Use unique slugs
- Large documents: Truncate content

---

#### [TASK-19-006]: Create Nerve Center HTTP Service

**Component/Scope:** `nerve-center/nerve-center.py`  
**Core Objective:** HTTP service that serves the nerve center API, dashboard, and serves as the bridge between all subsystems.

**Dependencies:** TASK-19-001 through 19-005

**Context:**

The nerve center service runs on port 8083 (separate from wiki-service 8082). It provides:
1. API endpoints for all nerve center data
2. Dashboard HTML pages
3. SSE real-time updates
4. Integration with discovery, verification, knowledge, and wiki writer

**Implementation:**

```python
# nerve-center/nerve-center.py
#!/usr/bin/env python3
"""GRID Network Nerve Center HTTP Service."""

import http.server
import json
import os
import sys
import time
import socketserver
import threading
import yaml
import urllib.request
import urllib.error
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nerve_center.state import StateManager
from nerve_center.discoverer import ProxmoxDiscoverer
from nerve_center.verifier import ServiceVerifier
from nerve_center.knowledge import KnowledgeGraph
from nerve_center.wiki_writer import WikiWriter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8083
start_time = time.time()

# Global state
_state = None
_discoverer = None
_verifier = None
_knowledge = None
_wiki_writer = None
_sse_subscribers = []
_sse_lock = threading.Lock()

def _load_config():
    """Load nerve-center config."""
    config_path = os.path.join(ROOT, 'nerve-center-config.yaml')
    if os.path.exists(config_path):
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {}

CONFIG = _load_config()

def _get_content_type(path):
    """Get content type for file."""
    if path.endswith('.html'):
        return 'text/html'
    elif path.endswith('.css'):
        return 'text/css'
    elif path.endswith('.js'):
        return 'application/javascript'
    elif path.endswith('.json'):
        return 'application/json'
    elif path.endswith('.md'):
        return 'text/markdown'
    elif path.endswith('.png'):
        return 'image/png'
    elif path.endswith('.jpg') or path.endswith('.jpeg'):
        return 'image/jpeg'
    elif path.endswith('.svg'):
        return 'image/svg+xml'
    else:
        return 'application/octet-stream'

def _serve_file(handler, filename, content_type='application/octet-stream'):
    """Serve a static file."""
    filepath = os.path.join(ROOT, filename)
    try:
        data = filepath.read_bytes()
    except FileNotFoundError:
        handler.send_error(404, f"File not found: {filename}")
        return
    handler.send_response(200)
    handler.send_header('Content-Type', content_type)
    handler.send_header('Access-Control-Allow-Origin', '*')
    if 'html' in content_type:
        handler.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        handler.send_header('Pragma', 'no-cache')
        handler.send_header('Expires', '0')
    handler.end_headers()
    handler.wfile.write(data)

def _send_json(handler, code, data):
    """Send JSON response."""
    handler.send_response(code)
    handler.send_header('Content-Type', 'application/json')
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.end_headers()
    handler.wfile.write(json.dumps(data, indent=2).encode())

class NerveCenterHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for nerve center."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / 'nerve-center'), **kwargs)

    def log_message(self, format, *args):
        print(f"[nerve-center] {self.address_string()} - {format % args}", flush=True)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Health check
        if path == '/api/health':
            uptime = time.time() - start_time
            _send_json(self, 200, {
                'status': 'healthy',
                'service': 'nerve-center',
                'version': '1.0.0',
                'timestamp': datetime.now().isoformat(),
                'uptime': uptime
            })
            return

        # Servers
        if path == '/api/nerve/servers':
            servers = _state.list_servers()
            # Add containers to each server
            for server in servers:
                server['containers'] = _state.get_server_containers(server['id'])
            _send_json(self, 200, {'servers': servers})
            return

        # Containers
        if path == '/api/nerve/containers':
            containers = _state.list_containers()
            for c in containers:
                c['services'] = _state.get_container_services(c['id'])
            _send_json(self, 200, {'containers': containers})
            return

        # Container detail
        if path.startswith('/api/nerve/containers/'):
            vmid = path.split('/')[-1]
            container = _state.get_container(int(vmid))
            if container:
                container['services'] = _state.get_container_services(container['id'])
                _send_json(self, 200, container)
            else:
                _send_json(self, 404, {'error': 'Container not found'})
            return

        # Services
        if path == '/api/nerve/services':
            services = _state.list_services()
            for s in services:
                s['container'] = _state.get_container(s['container_id'])
                s['relationships'] = _state.get_service_relationships(s['id'])
            _send_json(self, 200, {'services': services})
            return

        # Service detail
        if path.startswith('/api/nerve/services/'):
            service_id = path.split('/')[-1]
            service = _state.get_service(int(service_id))
            if service:
                service['container'] = _state.get_container(service['container_id'])
                service['relationships'] = _state.get_service_relationships(service['id'])
                service['wiki_docs'] = _state.get_wiki_documents(related_service_id=service['id'])
                _send_json(self, 200, service)
            else:
                _send_json(self, 404, {'error': 'Service not found'})
            return

        # Knowledge search
        if path == '/api/nerve/knowledge':
            params = parse_qs(parsed.query)
            query = params.get('q', [''])[0]
            limit = int(params.get('limit', ['10'])[0])
            if query:
                results = _knowledge.search(query, limit)
                _send_json(self, 200, {'results': results, 'total': len(results)})
            else:
                _send_json(self, 400, {'error': 'Query parameter q is required'})
            return

        # Knowledge item
        if path.startswith('/api/nerve/knowledge/'):
            node_id = path.split('/')[-1]
            node = _knowledge.get_node(node_id)
            if node:
                related = _knowledge.get_related(node_id)
                _send_json(self, 200, {'node': node, 'related': related})
            else:
                _send_json(self, 404, {'error': 'Knowledge node not found'})
            return

        # User requests
        if path == '/api/nerve/requests':
            params = parse_qs(parsed.query)
            status = params.get('status', [None])[0]
            requests = _state.get_user_requests(status=status)
            _send_json(self, 200, {'requests': requests})
            return

        # Agent actions
        if path == '/api/nerve/agent/actions':
            params = parse_qs(parsed.query)
            status = params.get('status', [None])[0]
            actions = _state.get_agent_actions(status=status)
            _send_json(self, 200, {'actions': actions})
            return

        # Sync status
        if path == '/api/nerve/sync-status':
            _send_json(self, 200, {
                'last_sync': datetime.now().isoformat(),
                'status': 'running',
                'files_synced': 0
            })
            return

        # Network design
        if path == '/api/nerve/design':
            design = CONFIG.get('network_design', {})
            rules = CONFIG.get('design_rules', [])
            _send_json(self, 200, {'design': design, 'rules': rules})
            return

        # Wiki documents
        if path == '/api/nerve/wiki/documents':
            params = parse_qs(parsed.query)
            category = params.get('category', [None])[0]
            docs = _state.get_wiki_documents(category=category)
            _send_json(self, 200, {'documents': docs})
            return

        # Wiki document
        if path.startswith('/api/nerve/wiki/'):
            slug = path.split('/')[-1]
            doc = _state.get_wiki_document_by_slug(slug)
            if doc:
                _send_json(self, 200, doc)
            else:
                _send_json(self, 404, {'error': 'Document not found'})
            return

        # SSE endpoint
        if path == '/sse':
            self._handle_sse()
            return

        # Serve dashboard HTML
        if path == '/nerve-center.html' or path == '/nerve-center':
            _serve_file(self, 'nerve-center/nerve-center.html', 'text/html')
            return

        # Serve service card
        if path == '/service-card.html' or path == '/service-card':
            _serve_file(self, 'nerve-center/service-card.html', 'text/html')
            return

        # Serve static assets
        if path.startswith('/nerve-center/css/') or path.startswith('/nerve-center/js/'):
            _serve_file(self, f'nerve-center{path}', _get_content_type(path))
            return

        # Default: 404
        _send_json(self, 404, {'error': f'Not found: {path}'})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Create knowledge
        if path == '/api/nerve/knowledge':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)
            node_id = _knowledge.add_node(data)
            _send_json(self, 200, {'id': node_id, 'status': 'created'})
            return

        # Create user request
        if path == '/api/nerve/requests':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)
            request_id = _state.create_user_request({
                'user_id': data.get('user_id', 'anonymous'),
                'request_type': data['request_type'],
                'title': data['title'],
                'description': data.get('description', '')
            })
            _send_json(self, 200, {'id': request_id, 'status': 'created'})
            return

        # Trigger discovery
        if path == '/api/nerve/discover':
            job_id = f"discover-{int(time.time())}"
            # Start discovery in background
            threading.Thread(target=self._run_discovery, args=(job_id,), daemon=True).start()
            _send_json(self, 200, {'status': 'started', 'job_id': job_id, 'message': 'Discovery started'})
            return

        # Trigger verification
        if path == '/api/nerve/verify':
            job_id = f"verify-{int(time.time())}"
            threading.Thread(target=self._run_verification, args=(job_id,), daemon=True).start()
            _send_json(self, 200, {'status': 'started', 'job_id': job_id, 'message': 'Verification started'})
            return

        # Default: 405
        _send_json(self, 405, {'error': 'Method not allowed'})

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()

    def _handle_sse(self):
        """Handle SSE connection."""
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        # Register subscriber
        with _sse_lock:
            _sse_subscribers.append(self.wfile)

        # Send connected event
        self.wfile.write(f"event: connected\ndata: {json.dumps({'status': 'connected', 'timestamp': time.time()})}\n\n".encode())
        self.wfile.flush()

        # Keep connection alive
        try:
            while True:
                time.sleep(30)
                self.wfile.write(f": heartbeat\n\n".encode())
                self.wfile.flush()
        except:
            pass
        finally:
            with _sse_lock:
                if self.wfile in _sse_subscribers:
                    _sse_subscribers.remove(self.wfile)

    def _run_discovery(self, job_id):
        """Run discovery in background."""
        # Broadcast start
        self._broadcast('discovery-start', {'job_id': job_id, 'started_at': datetime.now().isoformat()})

        try:
            result = _discoverer.discover_all()
            # Broadcast progress
            for i, server in enumerate(result['servers']):
                self._broadcast('discovery-progress', {
                    'job_id': job_id,
                    'progress': i / len(result['servers']) if result['servers'] else 0,
                    'servers_found': i + 1,
                    'containers_found': len(result['containers']),
                    'services_found': len(result['services'])
                })
            # Broadcast complete
            self._broadcast('discovery-complete', {
                'job_id': job_id,
                'servers_found': len(result['servers']),
                'containers_found': len(result['containers']),
                'services_found': len(result['services'])
            })
            # Write wiki docs
            for service in result['services']:
                _wiki_writer.write_service_document(service)
            for container in result['containers']:
                _wiki_writer.write_container_document(container)
            _wiki_writer.update_wiki_index()
        except Exception as e:
            self._broadcast('discovery-error', {'job_id': job_id, 'error': str(e)})

    def _run_verification(self, job_id):
        """Run verification in background."""
        self._broadcast('verification-start', {'job_id': job_id, 'started_at': datetime.now().isoformat()})
        try:
            result = _verifier.verify_all()
            self._broadcast('verification-complete', {
                'job_id': job_id,
                'services_checked': result['checked'],
                'services_up': result['up'],
                'services_down': result['down']
            })
        except Exception as e:
            self._broadcast('verification-error', {'job_id': job_id, 'error': str(e)})

    def _broadcast(self, event, data):
        """Broadcast SSE event to all subscribers."""
        with _sse_lock:
            dead = []
            for wfile in _sse_subscribers:
                try:
                    wfile.write(f"event: {event}\ndata: {json.dumps(data)}\n\n".encode())
                    wfile.flush()
                except:
                    dead.append(wfile)
            for d in dead:
                if d in _sse_subscribers:
                    _sse_subscribers.remove(d)

def main():
    global _state, _discoverer, _verifier, _knowledge, _wiki_writer

    # Initialize subsystems
    _state = StateManager()
    _knowledge = KnowledgeGraph()
    _wiki_writer = WikiWriter(os.path.join(ROOT, 'wiki-content'), _state)

    # Initialize discoverer
    proxmox_config = CONFIG.get('proxmox', {})
    _discoverer = ProxmoxDiscoverer(
        state_manager=_state,
        api_url=proxmox_config.get('api_url', 'https://10.10.30.22:8006/api2/json'),
        api_user=proxmox_config.get('api_user', 'root@pam'),
        api_token_name=proxmox_config.get('api_token_name', 'nerve-center'),
        api_token_secret=proxmox_config.get('api_token_secret', '')
    )

    _verifier = ServiceVerifier(_state, _knowledge)

    print(f"Starting GRID Network Nerve Center on port {PORT}...")
    print(f"Serving from: {ROOT}")
    print(f"Knowledge graph: {_knowledge.honcho_url}")
    print(f"Wiki content: {_wiki_writer.wiki_path}")
    print("-" * 60)

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), NerveCenterHandler) as httpd:
        print(f"NERVE CENTER running at http://0.0.0.0:{PORT}")
        print(f"Dashboard: http://localhost:{PORT}/nerve-center.html")
        print(f"API: http://localhost:{PORT}/api/nerve/servers")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")
            httpd.shutdown()

if __name__ == '__main__':
    main()
```

**Edge Cases:**
- Proxmox API unavailable: Mark servers as 'unknown'
- Knowledge graph unavailable: Use local cache
- Large discovery results: Stream progress via SSE

---

### Phase 2: Agent-Driven Discovery Pipeline

#### [TASK-19-007]: Create Agent-Driven Discovery Pipeline

**Component/Scope:** `scripts/discover-proxmox.sh` + `cron/nerve-discovery.sh`  
**Core Objective:** Agent-driven pipeline that discovers new containers/services when added, verifies them, updates the knowledge graph, and writes wiki docs.

**Dependencies:** TASK-19-001 through 19-006

**Context:**

When a new container is added to Proxmox, the agent pipeline:
1. Discovers the new container via Proxmox API
2. Verifies its services (port probes, health checks)
3. Checks against network design rules (port conflicts, required monitoring)
4. Updates the knowledge graph with the new node
5. Writes wiki documentation for the container and its services
6. Updates the SQLite state
7. Pushes updates via SSE to the dashboard

**Implementation:**

```bash
#!/bin/bash
# scripts/discover-proxmox.sh
# Agent-driven discovery pipeline

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== GRID Network Nerve Center - Discovery Pipeline ==="
echo "Started: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo

# Step 1: Trigger discovery via API
echo "Step 1: Triggering discovery..."
DISCOVERY_RESULT=$(curl -s --max-time 30 http://127.0.0.1:8083/api/nerve/discover)
echo "Discovery triggered: $DISCOVERY_RESULT"

# Step 2: Wait for discovery to complete (poll SSE)
echo "Step 2: Waiting for discovery to complete..."
MAX_WAIT=300
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    # Check if discovery is still running
    ACTIONS=$(curl -s --max-time 10 http://127.0.0.1:8083/api/nerve/agent/actions?status=running)
    if [ -z "$ACTIONS" ] || echo "$ACTIONS" | grep -q '"actions": \[\]'; then
        echo "Discovery complete."
        break
    fi
    sleep 5
    WAITED=$((WAITED + 5))
done

# Step 3: Check results
echo "Step 3: Checking results..."
SERVERS=$(curl -s --max-time 10 http://127.0.0.1:8083/api/nerve/servers)
CONTAINERS=$(curl -s --max-time 10 http://127.0.0.1:8083/api/nerve/containers)
SERVICES=$(curl -s --max-time 10 http://127.0.0.1:8083/api/nerve/services)

SERVER_COUNT=$(echo "$SERVERS" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('servers', [])))" 2>/dev/null || echo "0")
CONTAINER_COUNT=$(echo "$CONTAINERS" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('containers', [])))" 2>/dev/null || echo "0")
SERVICE_COUNT=$(echo "$SERVICES" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('services', [])))" 2>/dev/null || echo "0")

echo "Servers found: $SERVER_COUNT"
echo "Containers found: $CONTAINER_COUNT"
echo "Services found: $SERVICE_COUNT"

# Step 4: Run verification
echo "Step 4: Running verification..."
VERIFY_RESULT=$(curl -s --max-time 30 http://127.0.0.1:8083/api/nerve/verify)
echo "Verification triggered: $VERIFY_RESULT"

# Step 5: Update knowledge graph
echo "Step 5: Updating knowledge graph..."
# Sync local cache to Honcho
curl -s --max-time 30 http://127.0.0.1:8083/api/nerve/sync-status

# Step 6: Write wiki docs
echo "Step 6: Writing wiki documentation..."
curl -s --max-time 30 http://127.0.0.1:8083/api/nerve/wiki/documents > /dev/null

echo
echo "=== Discovery pipeline complete ==="
echo "Finished: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
```

**Cron job:** `cron/nerve-discovery.sh` — runs every 6 hours (1am-6am window).

**Edge Cases:**
- Proxmox API down: Skip discovery, log error
- Network partition: Continue with cached state
- Large discovery: Stream progress via SSE

---

### Phase 3: Knowledge Base

#### [TASK-19-008]: Create Knowledge Base Agent Interface

**Component/Scope:** `nerve-center/knowledge-agent.py` + `nerve-center/knowledge-rules.yaml`  
**Core Objective:** Agent interface for querying and updating the knowledge graph. Agents can search, add, update, and delete knowledge nodes.

**Dependencies:** TASK-19-003 (Knowledge graph)

**Context:**

The knowledge base agent provides:
1. **Query interface**: Agents can search knowledge by semantic query
2. **Update interface**: Agents can add/update/delete knowledge nodes
3. **Rule engine**: Knowledge rules define how agents should behave (e.g., "always verify Prometheus config before adding a service")
4. **Relationship mapping**: Agents can discover relationships between nodes (e.g., "Prometheus scrapes Grafana")

**Implementation:**

```python
# nerve-center/knowledge-agent.py
import json
import os
import yaml
from typing import List, Dict, Optional
from nerve_center.knowledge import KnowledgeGraph

class KnowledgeAgent:
    def __init__(self, knowledge_graph: KnowledgeGraph, rules_path: str = None):
        self.kg = knowledge_graph
        self.rules = self._load_rules(rules_path)

    def _load_rules(self, rules_path: str) -> List[dict]:
        """Load knowledge rules."""
        if rules_path and os.path.exists(rules_path):
            with open(rules_path) as f:
                return yaml.safe_load(f)
        return []

    def query(self, query: str, limit: int = 10) -> List[dict]:
        """Query knowledge graph for relevant nodes."""
        results = self.kg.search(query, limit)

        # Apply rules to filter/enrich results
        for rule in self.rules:
            if rule.get('type') == 'filter':
                results = self._apply_filter(rule, results)
            elif rule.get('type') == 'enrich':
                results = self._apply_enrichment(rule, results)

        return results

    def add_knowledge(self, node: dict) -> str:
        """Add knowledge node with rule validation."""
        # Validate against rules
        for rule in self.rules:
            if rule.get('type') == 'validate':
                if not self._validate_rule(rule, node):
                    raise Exception(f"Knowledge validation failed: {rule.get('name')}")

        return self.kg.add_node(node)

    def update_knowledge(self, node_id: str, properties: dict) -> bool:
        """Update knowledge node with rule validation."""
        return self.kg.update_node(node_id, properties)

    def delete_knowledge(self, node_id: str) -> bool:
        """Delete knowledge node."""
        return self.kg.delete_node(node_id)

    def get_related(self, node_id: str, relationship_type: str = None) -> List[dict]:
        """Get related knowledge nodes."""
        return self.kg.get_related(node_id, relationship_type)

    def discover_relationships(self, service_id: int) -> List[dict]:
        """Discover relationships between services."""
        # Use state manager to find relationships
        from nerve_center.state import StateManager
        state = StateManager()
        return state.get_service_relationships(service_id)

    def _apply_filter(self, rule: dict, results: List[dict]) -> List[dict]:
        """Apply filter rule to results."""
        if rule.get('type') == 'filter' and rule.get('exclude_types'):
            return [r for r in results if r.get('type') not in rule['exclude_types']]
        return results

    def _apply_enrichment(self, rule: dict, results: List[dict]) -> List[dict]:
        """Apply enrichment rule to results."""
        if rule.get('type') == 'enrich' and rule.get('add_properties'):
            for r in results:
                r.update(rule['add_properties'])
        return results

    def _validate_rule(self, rule: dict, node: dict) -> bool:
        """Validate node against rule."""
        if rule.get('type') == 'validate' and rule.get('required_fields'):
            for field in rule['required_fields']:
                if field not in node.get('properties', {}):
                    return False
        return True
```

**Knowledge Rules (knowledge-rules.yaml):**

```yaml
rules:
  - name: "required-service-fields"
    type: "validate"
    required_fields: ["name", "type", "status"]
    severity: "error"

  - name: "exclude-deprecated"
    type: "filter"
    exclude_types: ["deprecated"]

  - name: "enrich-with-monitoring"
    type: "enrich"
    add_properties:
      monitoring_status: "unknown"

  - name: "required-monitoring"
    type: "validate"
    condition: "if type == 'service' then monitoring_configured must be true"
    severity: "warning"
```

**Edge Cases:**
- Knowledge graph unavailable: Return empty results
- Rule validation failures: Log warning, don't block

---

### Phase 4: Nerve Center Dashboard

#### [TASK-19-009]: Create Nerve Center Dashboard

**Component/Scope:** `nerve-center/nerve-center.html` + `nerve-center/js/nerve-center.js`  
**Core Objective:** User-facing nerve center dashboard showing servers → containers → services → everything.

**Dependencies:** TASK-19-006 (HTTP service)

**Context:**

The nerve center dashboard is a single-page application that shows:
1. **Server view**: List of all Proxmox hosts with status
2. **Container view**: All containers on a server with services
3. **Service view**: All services with health status, ports, URLs
4. **Knowledge view**: Searchable knowledge base
5. **Request view**: User service requests
6. **Wiki view**: Generated wiki documents

**Implementation:**

```html
<!-- nerve-center/nerve-center.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GRID Network Nerve Center</title>
  <link rel="stylesheet" href="../css/dashboard.css">
  <style>
    .nerve-center { padding: 2rem; }
    .server-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
    .server-card { border: 1px solid #ddd; border-radius: 8px; padding: 1rem; }
    .server-card.up { border-left: 4px solid #4caf50; }
    .server-card.down { border-left: 4px solid #f44336; }
    .container-list { margin-top: 1rem; }
    .container-item { padding: 0.5rem; border-bottom: 1px solid #eee; }
    .service-list { margin-top: 0.5rem; }
    .service-item { display: flex; align-items: center; gap: 0.5rem; padding: 0.25rem 0; }
    .status-dot { width: 10px; height: 10px; border-radius: 50%; }
    .status-dot.up { background: #4caf50; }
    .status-dot.down { background: #f44336; }
    .status-dot.unknown { background: #9e9e9e; }
    .search-box { margin: 1rem 0; }
    .search-box input { width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; }
    .knowledge-results { margin-top: 1rem; }
    .knowledge-item { padding: 0.5rem; border-bottom: 1px solid #eee; }
    .request-form { margin: 1rem 0; }
    .request-form input, .request-form select, .request-form textarea { width: 100%; padding: 0.5rem; margin: 0.25rem 0; border: 1px solid #ddd; border-radius: 4px; }
    .wiki-docs { margin: 1rem 0; }
    .wiki-doc-item { padding: 0.5rem; border-bottom: 1px solid #eee; cursor: pointer; }
    .wiki-doc-item:hover { background: #f5f5f5; }
  </style>
</head>
<body>
  <div class="nerve-center" id="nerveCenter">
    <h1>GRID Network Nerve Center</h1>

    <!-- Search -->
    <div class="search-box">
      <input type="text" id="searchInput" placeholder="Search knowledge base..." />
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button class="tab active" data-tab="servers">Servers</button>
      <button class="tab" data-tab="containers">Containers</button>
      <button class="tab" data-tab="services">Services</button>
      <button class="tab" data-tab="knowledge">Knowledge</button>
      <button class="tab" data-tab="requests">Requests</button>
      <button class="tab" data-tab="wiki">Wiki</button>
    </div>

    <!-- Server View -->
    <div class="tab-content active" id="servers">
      <div class="server-grid" id="serverGrid"></div>
    </div>

    <!-- Container View -->
    <div class="tab-content" id="containers">
      <div class="container-list" id="containerList"></div>
    </div>

    <!-- Service View -->
    <div class="tab-content" id="services">
      <div class="service-list" id="serviceList"></div>
    </div>

    <!-- Knowledge View -->
    <div class="tab-content" id="knowledge">
      <div class="knowledge-results" id="knowledgeResults"></div>
    </div>

    <!-- Request View -->
    <div class="tab-content" id="requests">
      <div class="request-form">
        <h3>Create Service Request</h3>
        <input type="text" id="requestTitle" placeholder="Title" />
        <select id="requestType">
          <option value="create_service">Create Service</option>
          <option value="modify_service">Modify Service</option>
          <option value="delete_service">Delete Service</option>
          <option value="add_container">Add Container</option>
          <option value="investigate_issue">Investigate Issue</option>
        </select>
        <textarea id="requestDescription" placeholder="Description"></textarea>
        <button id="submitRequest">Submit Request</button>
      </div>
      <div id="requestList"></div>
    </div>

    <!-- Wiki View -->
    <div class="tab-content" id="wiki">
      <div class="wiki-docs" id="wikiDocs"></div>
    </div>
  </div>

  <script src="../js/nerve-center.js"></script>
</body>
</html>
```

```javascript
// nerve-center/js/nerve-center.js
class NerveCenter {
  constructor() {
    this.apiBase = '/api/nerve';
    this.sse = null;
    this.currentTab = 'servers';
  }

  init() {
    this.setupTabs();
    this.setupSearch();
    this.setupRequestForm();
    this.loadServers();
    this.subscribeToSSE();
  }

  setupTabs() {
    document.querySelectorAll('.tab').forEach(tab => {
      tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        tab.classList.add('active');
        const tabId = tab.dataset.tab;
        document.getElementById(tabId).classList.add('active');
        this.currentTab = tabId;
        this.loadTab(tabId);
      });
    });
  }

  setupSearch() {
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', (e) => {
      const query = e.target.value.trim();
      if (query.length >= 2) {
        this.searchKnowledge(query);
      }
    });
  }

  setupRequestForm() {
    document.getElementById('submitRequest').addEventListener('click', () => {
      const title = document.getElementById('requestTitle').value;
      const type = document.getElementById('requestType').value;
      const description = document.getElementById('requestDescription').value;
      if (!title) { alert('Title is required'); return; }
      this.createRequest(title, type, description);
    });
  }

  async loadServers() {
    const response = await fetch(`${this.apiBase}/servers`);
    const data = await response.json();
    const grid = document.getElementById('serverGrid');
    grid.innerHTML = '';
    for (const server of data.servers) {
      const card = document.createElement('div');
      card.className = `server-card ${server.status}`;
      card.innerHTML = `
        <h3>${server.hostname}</h3>
        <p>IP: ${server.ip_address}</p>
        <p>Status: ${server.status}</p>
        <p>Containers: ${server.containers?.length || 0}</p>
      `;
      card.addEventListener('click', () => this.loadContainersForServer(server.id));
      grid.appendChild(card);
    }
  }

  async loadContainersForServer(serverId) {
    const response = await fetch(`${this.apiBase}/containers`);
    const data = await response.json();
    const list = document.getElementById('containerList');
    list.innerHTML = '';
    const containers = data.containers.filter(c => c.server_id === serverId);
    for (const container of containers) {
      const item = document.createElement('div');
      item.className = 'container-item';
      item.innerHTML = `
        <strong>${container.name}</strong> (VMID ${container.vmid})
        <span class="status-dot ${container.status}"></span>
        <p>IP: ${container.ip_addresses?.join(', ')}</p>
        <p>Services: ${container.services?.length || 0}</p>
      `;
      item.addEventListener('click', () => this.loadServiceDetail(container.id));
      list.appendChild(item);
    }
  }

  async loadServiceDetail(containerId) {
    // Show service detail modal
    console.log('Loading service detail for container:', containerId);
  }

  async searchKnowledge(query) {
    const response = await fetch(`${this.apiBase}/knowledge?q=${encodeURIComponent(query)}&limit=10`);
    const data = await response.json();
    const results = document.getElementById('knowledgeResults');
    results.innerHTML = '';
    for (const node of data.results) {
      const item = document.createElement('div');
      item.className = 'knowledge-item';
      item.innerHTML = `<strong>${node.label}</strong> (${node.type})<br>${JSON.stringify(node.properties).substring(0, 100)}...`;
      results.appendChild(item);
    }
  }

  async createRequest(title, type, description) {
    const response = await fetch(`${this.apiBase}/requests`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: 'user', request_type: type, title, description })
    });
    const data = await response.json();
    alert(`Request created: ${data.id}`);
  }

  async loadTab(tabId) {
    switch (tabId) {
      case 'servers': await this.loadServers(); break;
      case 'containers': await this.loadContainersForServer(null); break;
      case 'services': await this.loadServices(); break;
      case 'knowledge': break; // Search handles this
      case 'requests': await this.loadRequests(); break;
      case 'wiki': await this.loadWikiDocs(); break;
    }
  }

  async loadServices() {
    const response = await fetch(`${this.apiBase}/services`);
    const data = await response.json();
    const list = document.getElementById('serviceList');
    list.innerHTML = '';
    for (const service of data.services) {
      const item = document.createElement('div');
      item.className = 'service-item';
      item.innerHTML = `
        <span class="status-dot ${service.status}"></span>
        <strong>${service.name}</strong> (${service.type}:${service.port})
        <span>${service.status}</span>
      `;
      list.appendChild(item);
    }
  }

  async loadRequests() {
    const response = await fetch(`${this.apiBase}/requests`);
    const data = await response.json();
    const list = document.getElementById('requestList');
    list.innerHTML = '';
    for (const req of data.requests) {
      const item = document.createElement('div');
      item.className = 'container-item';
      item.innerHTML = `<strong>${req.title}</strong> (${req.request_type}) - ${req.status}`;
      list.appendChild(item);
    }
  }

  async loadWikiDocs() {
    const response = await fetch(`${this.apiBase}/wiki/documents`);
    const data = await response.json();
    const list = document.getElementById('wikiDocs');
    list.innerHTML = '';
    for (const doc of data.documents) {
      const item = document.createElement('div');
      item.className = 'wiki-doc-item';
      item.innerHTML = `<strong>${doc.title}</strong> (${doc.category})`;
      list.appendChild(item);
    }
  }

  subscribeToSSE() {
    this.sse = new EventSource('/sse');
    this.sse.addEventListener('connected', (event) => {
      console.log('SSE connected:', JSON.parse(event.data));
    });
    this.sse.addEventListener('discovery-complete', (event) => {
      const data = JSON.parse(event.data);
      console.log('Discovery complete:', data);
      this.loadServers();
    });
    this.sse.addEventListener('verification-complete', (event) => {
      const data = JSON.parse(event.data);
      console.log('Verification complete:', data);
      this.loadServices();
    });
    this.sse.addEventListener('service-status-change', (event) => {
      const data = JSON.parse(event.data);
      console.log('Service status changed:', data);
    });
    this.sse.addEventListener('knowledge-update', (event) => {
      const data = JSON.parse(event.data);
      console.log('Knowledge updated:', data);
    });
    this.sse.addEventListener('request-created', (event) => {
      const data = JSON.parse(event.data);
      console.log('Request created:', data);
      this.loadRequests();
    });
    this.sse.addEventListener('agent-action', (event) => {
      const data = JSON.parse(event.data);
      console.log('Agent action:', data);
    });
    this.sse.onerror = (error) => {
      console.error('SSE error:', error);
    };
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  const nc = new NerveCenter();
  nc.init();
});
```

**Edge Cases:**
- SSE connection lost: Reconnect with exponential backoff
- Large data sets: Paginate results
- Browser compatibility: Check EventSource support

---

### Phase 5: Agent API & User Request Handler

#### [TASK-19-010]: Create Agent API & User Request Handler

**Component/Scope:** `nerve-center/agent-api.py` + `nerve-center/request-handler.py`  
**Core Objective:** Agent API for querying/updating state, and user request handler for service requests.

**Dependencies:** All previous tasks

**Context:**

The agent API provides:
1. **Query interface**: Agents can query state, knowledge, wiki
2. **Update interface**: Agents can create/update/delete state
3. **Action interface**: Agents can trigger discovery, verification, wiki writes

The user request handler:
1. **Receives requests**: Users can request new services, modifications, investigations
2. **Routes to agents**: Requests are routed to appropriate agents
3. **Tracks status**: Requests have status (pending, approved, in_progress, completed, rejected)

**Implementation:**

```python
# nerve-center/agent-api.py
import json
import os
import sys
import time
import socketserver
import threading
import yaml
import urllib.request
import urllib.error
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nerve_center.state import StateManager
from nerve_center.discoverer import ProxmoxDiscoverer
from nerve_center.verifier import ServiceVerifier
from nerve_center.knowledge import KnowledgeGraph
from nerve_center.wiki_writer import WikiWriter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class AgentAPI:
    def __init__(self, state, knowledge, discoverer, verifier, wiki_writer):
        self.state = state
        self.knowledge = knowledge
        self.discoverer = discoverer
        self.verifier = verifier
        self.wiki_writer = wiki_writer

    def query_state(self, query_type: str, filters: dict = None) -> dict:
        """Query state by type."""
        if query_type == 'servers':
            servers = self.state.list_servers()
            if filters:
                if 'status' in filters:
                    servers = [s for s in servers if s['status'] == filters['status']]
            return {'servers': servers}
        elif query_type == 'containers':
            containers = self.state.list_containers()
            if filters:
                if 'server_id' in filters:
                    containers = [c for c in containers if c['server_id'] == filters['server_id']]
                if 'status' in filters:
                    containers = [c for c in containers if c['status'] == filters['status']]
            return {'containers': containers}
        elif query_type == 'services':
            services = self.state.list_services()
            if filters:
                if 'container_id' in filters:
                    services = [s for s in services if s['container_id'] == filters['container_id']]
                if 'type' in filters:
                    services = [s for s in services if s['type'] == filters['type']]
                if 'status' in filters:
                    services = [s for s in services if s['status'] == filters['status']]
            return {'services': services}
        elif query_type == 'wiki_documents':
            docs = self.state.get_wiki_documents()
            if filters:
                if 'category' in filters:
                    docs = [d for d in docs if d['category'] == filters['category']]
            return {'documents': docs}
        elif query_type == 'agent_actions':
            actions = self.state.get_agent_actions()
            if filters:
                if 'status' in filters:
                    actions = [a for a in actions if a['status'] == filters['status']]
            return {'actions': actions}
        elif query_type == 'user_requests':
            requests = self.state.get_user_requests()
            if filters:
                if 'status' in filters:
                    requests = [r for r in requests if r['status'] == filters['status']]
            return {'requests': requests}
        return {'error': f'Unknown query type: {query_type}'}

    def update_state(self, update_type: str, data: dict) -> dict:
        """Update state."""
        if update_type == 'create_service':
            service_id = self.state.upsert_service(data)
            # Write wiki doc
            slug = self.wiki_writer.write_service_document(data)
            return {'status': 'created', 'service_id': service_id, 'wiki_slug': slug}
        elif update_type == 'create_container':
            container_id = self.state.upsert_container(data)
            slug = self.wiki_writer.write_container_document(data)
            return {'status': 'created', 'container_id': container_id, 'wiki_slug': slug}
        elif update_type == 'create_server':
            server_id = self.state.upsert_server(data)
            slug = self.wiki_writer.write_server_document(data)
            return {'status': 'created', 'server_id': server_id, 'wiki_slug': slug}
        elif update_type == 'create_knowledge':
            node_id = self.knowledge.add_node(data)
            return {'status': 'created', 'node_id': node_id}
        elif update_type == 'update_knowledge':
            success = self.knowledge.update_node(data['id'], data['properties'])
            return {'status': 'updated' if success else 'failed'}
        elif update_type == 'delete_knowledge':
            success = self.knowledge.delete_node(data['id'])
            return {'status': 'deleted' if success else 'failed'}
        return {'error': f'Unknown update type: {update_type}'}

    def trigger_action(self, action_type: str, params: dict = None) -> dict:
        """Trigger an action."""
        if action_type == 'discover':
            result = self.discoverer.discover_all()
            # Create agent action
            action_id = self.state.create_agent_action({
                'agent_id': 'agent',
                'action_type': 'discover',
                'target_type': 'all',
                'status': 'completed',
                'details': result
            })
            return {'status': 'completed', 'action_id': action_id, 'result': result}
        elif action_type == 'verify':
            result = self.verifier.verify_all()
            action_id = self.state.create_agent_action({
                'agent_id': 'agent',
                'action_type': 'verify',
                'target_type': 'services',
                'status': 'completed',
                'details': result
            })
            return {'status': 'completed', 'action_id': action_id, 'result': result}
        elif action_type == 'write_wiki':
            # Write all wiki docs
            services = self.state.list_services()
            for service in services:
                self.wiki_writer.write_service_document(service)
            containers = self.state.list_containers()
            for container in containers:
                self.wiki_writer.write_container_document(container)
            self.wiki_writer.update_wiki_index()
            return {'status': 'completed'}
        elif action_type == 'sync_knowledge':
            success = self.knowledge.sync_to_honcho()
            return {'status': 'synced' if success else 'failed'}
        return {'error': f'Unknown action type: {action_type}'}

    def search_knowledge(self, query: str, limit: int = 10) -> dict:
        """Search knowledge base."""
        results = self.knowledge.search(query, limit)
        return {'results': results, 'total': len(results)}

# nerve-center/request-handler.py
class RequestHandler:
    def __init__(self, state, agent_api):
        self.state = state
        self.agent_api = agent_api

    def create_request(self, user_id, request_type, title, description):
        """Create a user request."""
        request_id = self.state.create_user_request({
            'user_id': user_id,
            'request_type': request_type,
            'title': title,
            'description': description
        })
        # Route to appropriate agent
        self._route_request(request_id, request_type)
        return request_id

    def _route_request(self, request_id, request_type):
        """Route request to appropriate agent."""
        if request_type == 'create_service':
            # Agent will handle service creation
            self.state.update_user_request(request_id, 'approved', {'routed_to': 'service-creation-agent'})
        elif request_type == 'modify_service':
            self.state.update_user_request(request_id, 'approved', {'routed_to': 'service-modification-agent'})
        elif request_type == 'delete_service':
            self.state.update_user_request(request_id, 'pending', {'routed_to': 'service-deletion-agent'})
        elif request_type == 'add_container':
            self.state.update_user_request(request_id, 'approved', {'routed_to': 'container-creation-agent'})
        elif request_type == 'investigate_issue':
            self.state.update_user_request(request_id, 'approved', {'routed_to': 'investigation-agent'})

    def get_request(self, request_id):
        """Get a user request."""
        return self.state.get_user_requests()  # Simplified

    def update_request_status(self, request_id, status, details=None):
        """Update request status."""
        return self.state.update_user_request(request_id, status, details)
```

**Edge Cases:**
- Agent unavailable: Queue request, retry later
- Invalid request: Return error with reason
- Duplicate request: Check for existing, return ID

---

### Phase 6: Wiki Writer & Documentation

#### [TASK-19-011]: Create Wiki Writer & Documentation Generator

**Component/Scope:** `nerve-center/wiki-writer.py` (already defined in TASK-19-005) + `nerve-center/docs-generator.py`  
**Core Objective:** Generate comprehensive wiki documentation from state data.

**Dependencies:** TASK-19-005 (Wiki writer)

**Context:**

The docs generator creates:
1. **Service documentation**: For each service (overview, ports, config, monitoring)
2. **Container documentation**: For each container (resources, services, status)
3. **Server documentation**: For each server (containers, services, status)
4. **Network design documentation**: Network topology, VLANs, subnets
5. **Procedure documentation**: How-to guides for common tasks
6. **Troubleshooting documentation**: Known issues and fixes

**Implementation:** (Already defined in TASK-19-005. This task focuses on integration with the nerve center service and cron jobs.)

---

### Phase 7: Integration & Testing

#### [TASK-19-012]: Integration Testing

**Component/Scope:** `tests/` + `scripts/deploy-nerve-center.sh`  
**Core Objective:** Test all nerve center components end-to-end.

**Dependencies:** All previous tasks

**Context:**

Integration tests verify:
1. Discovery pipeline: Proxmox → SQLite → Knowledge graph → Wiki
2. Verification pipeline: Services → Health checks → Prometheus → Caddy
3. Knowledge graph: Search, add, update, delete nodes
4. User requests: Create, route, update status
5. Dashboard: Load servers, containers, services, knowledge, wiki
6. SSE: Real-time updates to dashboard

**Test script:** `tests/test-integration.py`

```python
#!/usr/bin/env python3
"""Integration tests for GRID Network Nerve Center."""

import unittest
import json
import os
import sys
import tempfile
import urllib.request
import urllib.error

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nerve_center.state import StateManager
from nerve_center.discoverer import ProxmoxDiscoverer
from nerve_center.verifier import ServiceVerifier
from nerve_center.knowledge import KnowledgeGraph
from nerve_center.wiki_writer import WikiWriter

class TestIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.db_path = '/tmp/test-nerve-integration.db'
        self.state = StateManager(self.db_path)
        self.knowledge = KnowledgeGraph(local_cache_path='/tmp/test-knowledge.json')
        self.wiki_writer = WikiWriter('/tmp/test-wiki', self.state)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        for path in [self.db_path, '/tmp/test-knowledge.json']:
            if os.path.exists(path):
                os.remove(path)
        if os.path.exists('/tmp/test-wiki'):
            shutil.rmtree('/tmp/test-wiki')

    def test_server_crud(self):
        """Test server create/read/update/delete."""
        server = {
            'hostname': 'test-server',
            'ip_address': '10.10.30.99',
            'proxmox_api_url': 'https://10.10.30.99:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'up'
        }
        sid = self.state.upsert_server(server)
        self.assertIsNotNone(sid)

        retrieved = self.state.get_server('test-server')
        self.assertEqual(retrieved['hostname'], 'test-server')
        self.assertEqual(retrieved['status'], 'up')

        servers = self.state.list_servers()
        self.assertEqual(len(servers), 1)

    def test_container_crud(self):
        """Test container create/read/update/delete."""
        server = {
            'hostname': 'test-server',
            'ip_address': '10.10.30.99',
            'proxmox_api_url': 'https://10.10.30.99:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'up'
        }
        sid = self.state.upsert_server(server)

        container = {
            'server_id': sid,
            'vmid': 9001,
            'name': 'test-container',
            'type': 'lxc',
            'status': 'running',
            'ip_addresses': ['10.10.30.91'],
            'memory_mb': 4096,
            'cpu_cores': 2,
            'disk_total_mb': 10240,
            'disk_used_mb': 2048,
            'os': 'Ubuntu 22.04',
            'template': 'ubuntu-22.04-standard'
        }
        cid = self.state.upsert_container(container)
        self.assertIsNotNone(cid)

        retrieved = self.state.get_container(9001)
        self.assertEqual(retrieved['name'], 'test-container')
        self.assertEqual(retrieved['status'], 'running')

    def test_service_crud(self):
        """Test service create/read/update/delete."""
        server = {
            'hostname': 'test-server',
            'ip_address': '10.10.30.99',
            'proxmox_api_url': 'https://10.10.30.99:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'up'
        }
        sid = self.state.upsert_server(server)

        container = {
            'server_id': sid,
            'vmid': 9001,
            'name': 'test-container',
            'type': 'lxc',
            'status': 'running',
            'ip_addresses': ['10.10.30.91'],
            'memory_mb': 4096,
            'cpu_cores': 2,
            'disk_total_mb': 10240,
            'disk_used_mb': 2048,
            'os': 'Ubuntu 22.04',
            'template': 'ubuntu-22.04-standard'
        }
        cid = self.state.upsert_container(container)

        service = {
            'container_id': cid,
            'name': 'test-service',
            'type': 'http',
            'port': 8080,
            'protocol': 'tcp',
            'url': 'http://10.10.30.91:8080',
            'status': 'up',
            'response_time_ms': 5,
            'last_checked': '2026-06-30T10:00:00',
            'prometheus_job': 'test-service',
            'prometheus_target': 'http://10.10.30.91:8080/metrics',
            'monitoring_configured': 1,
            'caddy_configured': 1
        }
        sid = self.state.upsert_service(service)
        self.assertIsNotNone(sid)

        retrieved = self.state.get_service(sid)
        self.assertEqual(retrieved['name'], 'test-service')
        self.assertEqual(retrieved['status'], 'up')

        services = self.state.list_services(container_id=cid)
        self.assertEqual(len(services), 1)

    def test_wiki_document(self):
        """Test wiki document creation."""
        doc = {
            'title': 'Test Service',
            'slug': 'test-service',
            'category': 'service',
            'content': '# Test Service\n\nThis is a test service.',
            'source': 'agent-generated',
            'last_updated': '2026-06-30T10:00:00'
        }
        doc_id = self.state.create_wiki_document(doc)
        self.assertIsNotNone(doc_id)

        retrieved = self.state.get_wiki_document_by_slug('test-service')
        self.assertEqual(retrieved['title'], 'Test Service')
        self.assertEqual(retrieved['category'], 'service')

    def test_agent_action(self):
        """Test agent action logging."""
        action = {
            'agent_id': 'test-agent',
            'action_type': 'discover',
            'target_type': 'all',
            'status': 'completed',
            'details': {'servers': 1, 'containers': 1, 'services': 1}
        }
        action_id = self.state.create_agent_action(action)
        self.assertIsNotNone(action_id)

        actions = self.state.get_agent_actions(status='completed')
        self.assertEqual(len(actions), 1)

    def test_user_request(self):
        """Test user request creation."""
        request = {
            'user_id': 'test-user',
            'request_type': 'create_service',
            'title': 'Test Service Request',
            'description': 'Create a new test service'
        }
        request_id = self.state.create_user_request(request)
        self.assertIsNotNone(request_id)

        requests = self.state.get_user_requests()
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0]['status'], 'pending')

    def test_knowledge_graph(self):
        """Test knowledge graph operations."""
        node = {
            'id': 'test-node',
            'type': 'service',
            'label': 'Test Service',
            'properties': {'name': 'test', 'status': 'up'},
            'embeddings': [0.1] * 10,
            'metadata': {'source': 'test'}
        }
        node_id = self.knowledge.add_node(node)
        self.assertEqual(node_id, 'test-node')

        retrieved = self.knowledge.get_node('test-node')
        self.assertEqual(retrieved['label'], 'Test Service')

        # Search
        results = self.knowledge.search('test', limit=10)
        self.assertGreater(len(results), 0)

    def test_wiki_writer(self):
        """Test wiki writer."""
        service = {
            'container_id': 1,
            'name': 'test-service',
            'type': 'http',
            'port': 8080,
            'protocol': 'tcp',
            'url': 'http://10.10.30.91:8080',
            'status': 'up',
            'response_time_ms': 5,
            'last_checked': '2026-06-30T10:00:00',
            'prometheus_job': 'test-service',
            'prometheus_target': 'http://10.10.30.91:8080/metrics',
            'monitoring_configured': 1,
            'caddy_configured': 1
        }
        slug = self.wiki_writer.write_service_document(service)
        self.assertEqual(slug, 'service-test-service')

        # Check file exists
        file_path = os.path.join('/tmp/test-wiki', 'services', 'service-test-service.md')
        self.assertTrue(os.path.exists(file_path))

        # Check content
        with open(file_path) as f:
            content = f.read()
        self.assertIn('test-service', content.lower())

if __name__ == '__main__':
    unittest.main()
```

**Deployment script:** `scripts/deploy-nerve-center.sh`

```bash
#!/bin/bash
# Deploy nerve center to CT131

set -e

CT131="grid-pve"
CT131_WIKI_DIR="/srv/grid-wiki-tool"

echo "=== Deploying GRID Network Nerve Center to CT131 ==="

# Copy nerve-center files
echo "Copying nerve-center files..."
scp -r nerve-center/ grid-pve:"$CT131_WIKI_DIR/"

# Restart service
echo "Restarting nerve-center service..."
ssh grid-pve "pct exec 131 -- bash -c 'systemctl restart nerve-center'"

# Verify
echo "Verifying deployment..."
sleep 5
curl -s --max-time 10 http://127.0.0.1:8083/api/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Status: {d[\"status\"]}')"

echo "=== Deployment complete ==="
```

---

## PART 3: RISK MITIGATION & EDGE CASES

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Proxmox API down | No discovery | Use cached state, retry with exponential backoff |
| Knowledge graph unavailable | No semantic search | Fall back to local keyword search |
| SQLite corruption | Data loss | WAL mode, regular backups, checksums |
| Large discovery results | Memory overflow | Stream results, paginate API calls |
| Network partition | Inconsistent state | Eventual consistency, conflict resolution |
| Agent errors | Stale data | Health checks, alerts, manual override |
| Wiki path conflicts | Duplicate docs | Unique slugs, checksums, deduplication |

### Bottlenecks

| Bottleneck | Impact | Mitigation |
|------------|--------|------------|
| Proxmox API rate limits | Slow discovery | Cache, batch requests, throttle |
| Large knowledge graph | Slow search | Indexing, caching, pagination |
| SQLite concurrent writes | Data corruption | WAL mode, connection pooling |
| SSE connection limits | Missed updates | Queue events, reconnect logic |
| Wiki file I/O | Slow doc generation | Async writes, batching |

### Verification Checklist

- [ ] SQLite schema creates correctly
- [ ] Proxmox discoverer connects and scans
- [ ] Service verifier checks health, Prometheus, Caddy
- [ ] Knowledge graph stores and searches nodes
- [ ] Wiki writer generates docs correctly
- [ ] Nerve center service responds to all API endpoints
- [ ] Dashboard loads and displays data
- [ ] SSE pushes real-time updates
- [ ] Agent API queries and updates state
- [ ] User requests create and route correctly
- [ ] Integration tests pass
- [ ] Cron jobs run on schedule
- [ ] Deployment script works

---

*End of specification.*
