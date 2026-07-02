# GRID Network Nerve Center — Architecture Specification

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
│   ├── agent-api.py                             # Agent query/update API
│   ├── request-handler.py                       # User request router
│   ├── nerve-center.py                          # Main HTTP service (port 8083)
│   ├── nerve-center-config.yaml                 # Configuration
│   ├── nerve-center.db                          # SQLite database (generated)
│   ├── knowledge-graph.json                     # Local vector graph cache
│   ├── knowledge-rules.yaml                     # Knowledge validation rules
│   ├── schema.sql                               # Database schema
│   ├── docs-generator.py                        # Wiki doc generator
│   ├── nerve-center.html                        # Dashboard HTML
│   ├── service-card.html                        # Service detail modal
│   ├── services/
│   │   └── template-card.json                   # Service card template
│   ├── css/
│   │   └── nerve-center.css                     # Dashboard styles
│   └── js/
│       └── nerve-center.js                      # Dashboard logic
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
│   ├── services/                                # Service docs (auto-generated)
│   ├── infrastructure/                          # Server/container docs (auto-generated)
│   ├── design/                                  # Network design docs (auto-generated)
│   ├── procedures/                              # Procedure docs (auto-generated)
│   ├── troubleshooting/                         # Troubleshooting docs (auto-generated)
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
│   ├── test-wiki-writer.py
│   └── test-integration.py
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

See `nerve-center/schema.sql` for full SQL schema.

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
| GET | `/nerve-center.html` | (static) | Dashboard HTML | `text/html` |

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
# nerve-center/state.py
class StateManager:
    def __init__(self, db_path: str = None)
    def get_server(self, hostname: str) -> Optional[dict]
    def upsert_server(self, server: dict) -> int
    def list_servers(self) -> List[dict]
    def get_container(self, vmid: int) -> Optional[dict]
    def upsert_container(self, container: dict) -> int
    def list_containers(self, server_id: int = None) -> List[dict]
    def get_server_containers(self, server_id: int) -> List[dict]
    def get_service(self, service_id: int) -> Optional[dict]
    def upsert_service(self, service: dict) -> int
    def list_services(self, container_id: int = None, type: str = None, status: str = None) -> List[dict]
    def update_service_status(self, service_id: int, status: str, response_time_ms: int = None) -> bool
    def get_container_services(self, container_id: int) -> List[dict]
    def get_service_relationships(self, service_id: int) -> List[dict]
    def create_relationship(self, source_id: int, target_id: int, relationship_type: str) -> int
    def delete_relationship(self, source_id: int, target_id: int, relationship_type: str) -> bool
    def create_wiki_document(self, doc: dict) -> int
    def get_wiki_documents(self, category: str = None, related_service_id: int = None) -> List[dict]
    def get_wiki_document_by_slug(self, slug: str) -> Optional[dict]
    def create_agent_action(self, action: dict) -> int
    def get_agent_actions(self, status: str = None, type: str = None) -> List[dict]
    def create_user_request(self, request: dict) -> int
    def get_user_requests(self, status: str = None) -> List[dict]
    def update_user_request(self, request_id: int, status: str, details: dict = None) -> bool

# nerve-center/discoverer.py
class ProxmoxDiscoverer:
    def __init__(self, state_manager, api_url, api_user, api_token_name, api_token_secret)
    def discover_servers(self) -> List[dict]
    def discover_containers(self, server_hostname: str) -> List[dict]
    def discover_services(self, container: dict) -> List[dict]
    def verify_server(self, server: dict) -> str
    def verify_container(self, container: dict) -> str
    def verify_service(self, service: dict) -> dict
    def discover_all(self) -> dict

# nerve-center/verifier.py
class ServiceVerifier:
    def __init__(self, state_manager, knowledge_graph)
    def verify_all_services(self) -> dict
    def verify_service(self, service: dict) -> dict
    def check_prometheus(self, service: dict) -> bool
    def check_caddy(self, service: dict) -> bool
    def detect_anomalies(self, service: dict) -> List[dict]
    def verify_all(self) -> dict

# nerve-center/knowledge.py
class KnowledgeGraph:
    def __init__(self, honcho_url: str = 'http://10.10.30.130:8000', local_cache_path: str = None)
    def add_node(self, node: dict) -> str
    def add_edge(self, edge: dict) -> str
    def search(self, query: str, limit: int = 10) -> List[dict]
    def get_node(self, node_id: str) -> Optional[dict]
    def get_related(self, node_id: str, relationship_type: str = None) -> List[dict]
    def update_node(self, node_id: str, properties: dict) -> bool
    def delete_node(self, node_id: str) -> bool
    def sync_to_honcho(self) -> bool
    def rebuild_local_cache(self) -> bool

# nerve-center/wiki-writer.py
class WikiWriter:
    def __init__(self, wiki_content_path: str, state_manager)
    def write_service_document(self, service: dict) -> str
    def write_container_document(self, container: dict) -> str
    def write_server_document(self, server: dict) -> str
    def write_network_design_document(self, design: dict) -> str
    def write_procedure_document(self, procedure: dict) -> str
    def write_troubleshooting_document(self, issue: dict) -> str
    def generate_service_card(self, service: dict) -> str
    def generate_container_card(self, container: dict) -> str
    def generate_server_card(self, server: dict) -> str
    def update_wiki_index(self) -> bool

# nerve-center/agent-api.py
class AgentAPI:
    def __init__(self, state, knowledge, discoverer, verifier, wiki_writer)
    def query_state(self, query_type: str, filters: dict = None) -> dict
    def update_state(self, update_type: str, data: dict) -> dict
    def trigger_action(self, action_type: str, params: dict = None) -> dict
    def search_knowledge(self, query: str, limit: int = 10) -> dict

# nerve-center/request-handler.py
class RequestHandler:
    def __init__(self, state, agent_api)
    def create_request(self, user_id, request_type, title, description)
    def _route_request(self, request_id, request_type)
    def get_request(self, request_id)
    def update_request_status(self, request_id, status, details=None)

# nerve-center/nerve-center.py — HTTP service
class NerveCenterHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self)
    def do_POST(self)
    def do_OPTIONS(self)
    def _send_cors_headers()
    def _send_json(code, data)
    def _serve_file(path, ct)
    def serve_health_check() -> dict
    def serve_servers() -> dict
    def serve_containers() -> dict
    def serve_container_detail(vmid) -> dict
    def serve_services() -> dict
    def serve_service_detail(service_id) -> dict
    def serve_knowledge() -> dict
    def serve_knowledge_detail(node_id) -> dict
    def create_knowledge() -> dict
    def serve_requests() -> dict
    def create_request() -> dict
    def serve_agent_actions() -> dict
    def trigger_discovery() -> dict
    def trigger_verification() -> dict
    def serve_sync_status() -> dict
    def serve_network_design() -> dict
    def serve_wiki_docs() -> dict
    def serve_wiki_doc(slug) -> dict
    def _handle_sse()

# dashboard/js/nerve-center.js
class NerveCenter {
    constructor()
    init()
    loadServerView()
    loadContainerView()
    loadServiceView()
    loadKnowledgeView()
    loadRequestView()
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
