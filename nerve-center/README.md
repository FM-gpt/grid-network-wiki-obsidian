# GRID Network Nerve Center

Autonomous infrastructure discovery, monitoring, and knowledge management system.

## Architecture

```
                    ┌─────────────────────────────────────┐
                    │       GRID Network Nerve Center      │
┌──────────┐       │                                      │
│ Proxmox  │──────▶│  Discoverer                          │
│ Cluster  │       │  └─ discovers servers, containers,   │
└──────────┘       │    services, and network endpoints   │
                   │                                      │
                   │  ┌─ Knowledge Graph Manager          │
                   │  │  └─ entity/relationship storage   │
                   │  └─────────────────────────────────┘ │
                   │                                      │
                   │  ┌─ Service Verifier                 │
                   │  │  └─ health checks & alerts        │
                   │  └─────────────────────────────────┘ │
                   │                                      │
                   │  ┌─ Wiki Writer                      │
                   │  │  └─ documentation generation      │
                   │  └─────────────────────────────────┘ │
                   │                                      │
                   │  ┌─ Discovery Pipeline               │
                   │  │  └─ orchestrate discover→verify   │
                   │  │    →analyze→document→alert        │
                   │  └─────────────────────────────────┘ │
                   │                                      │
                   │  ┌─ Knowledge Agent Interface        │
                   │  │  └─ unified agent API             │
                   │  └─────────────────────────────────┘ │
                   │                                      │
                   │  ┌─ HTTP Services                    │
                   │  │  ├── Nerve Center API (8765)      │
                   │  │  └── Agent API (8766)            │
                   │  └─────────────────────────────────┘ │
                   │                                      │
                   │  ┌─ Dashboard                        │
                   │  │  └─ web UI (dashboard.html)       │
                   │  └─────────────────────────────────┘ │
                   └──────────────────────────────────────┘
```

## Components

| Component | File | Description |
|-----------|------|-------------|
| State Manager | `state.py` | SQLite CRUD for servers, containers, services, wiki docs |
| Schema | `schema.sql` | Database schema (7 tables, 10+ indexes) |
| Discoverer | `discoverer.py` | Proxmox API integration for infrastructure discovery |
| Knowledge Graph | `knowledge_graph.py` | Entity/relationship graph with semantic search |
| Service Verifier | `service_verifier.py` | Service health checks and alert generation |
| Wiki Writer | `wiki_writer.py` | Documentation generation with change tracking |
| Discovery Pipeline | `discovery_pipeline.py` | 5-stage pipeline with hooks |
| Knowledge Agent | `knowledge_agent.py` | Unified agent interface |
| Nerve Center API | `http_service.py` | REST API (port 8765) |
| Agent API | `agent_api.py` | Agent-facing REST API (port 8766) |
| Dashboard | `dashboard.html` | Web UI (dark theme, responsive) |
| Entry Point | `run.py` | CLI entry point |

## Quick Start

```bash
# 1. Install dependencies
pip install -r nerve-center/requirements.txt

# 2. Configure
cp nerve-center/config.yaml .
# Edit config.yaml with your Proxmox credentials

# 3. Run (both services)
python nerve-center/run.py

# Or run individual services:
python nerve-center/run.py --nerve-only  # Port 8765
python nerve-center/run.py --agent-only  # Port 8766

# 4. Health check
python nerve-center/run.py --health
```

## Docker

```bash
# Build
docker build -t nerve-center -f nerve-center/Dockerfile .

# Run
docker run -d \
  --name nerve-center \
  -p 8765:8765 \
  -p 8766:8766 \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -v nerve-center-data:/app/data \
  -v nerve-center-logs:/app/logs \
  nerve-center

# Stop
docker stop nerve-center && docker rm nerve-center
```

## API Endpoints

### Nerve Center API (port 8765)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/nerve-center/status` | System status |
| GET | `/api/nerve-center/graph` | Query knowledge graph |
| GET | `/api/nerve-center/graph?type=X&id=Y` | Query specific entity |
| GET | `/api/nerve-center/search?q=QUERY` | Search knowledge |
| GET | `/api/nerve-center/wiki` | List wiki documents |
| GET | `/api/nerve-center/wiki/slug` | Get wiki document |
| GET | `/api/nerve-center/health-report` | Health report |
| GET | `/api/nerve-center/alerts` | Current alerts |
| POST | `/api/nerve-center/discovery` | Run discovery |
| POST | `/api/nerve-center/verification` | Run verification |
| POST | `/api/nerve-center/agents/register` | Register agent |

### Agent API (port 8766)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/agent/status` | System status |
| GET | `/api/agent/graph?type=X&id=Y` | Query knowledge graph |
| GET | `/api/agent/search?q=QUERY` | Search knowledge |
| GET | `/api/agent/wiki/slug` | Get wiki document |
| GET | `/api/agent/wiki` | List wiki documents |
| GET | `/api/agent/requests` | Get user requests |
| GET | `/api/agent/agents` | List agents |
| GET | `/api/agent/agents/ID` | Get agent info |
| GET | `/api/agent/actions` | Get agent actions |
| GET | `/api/agent/alerts` | Get alerts |
| GET | `/api/agent/health-report` | Get health report |
| POST | `/api/agent/discovery` | Run discovery |
| POST | `/api/agent/verification` | Run verification |
| POST | `/api/agent/request` | Submit user request |
| POST | `/api/agent/agents/register` | Register agent |
| POST | `/api/agent/entity` | Create entity |
| POST | `/api/agent/relationship` | Create relationship |
| PUT | `/api/agent/request/ID/status` | Update request status |
| DELETE | `/api/agent/entity/TYPE/ID` | Delete entity |

## Dashboard

Access the web dashboard at `http://localhost:8765/dashboard.html`

Features:
- Real-time status overview (servers, containers, services, wiki docs)
- 7 tabs: Overview, Servers, Containers, Services, Alerts, Agents, Knowledge Graph
- Interactive knowledge graph visualization
- Discovery modal with one-click pipeline execution
- Dark theme, responsive layout
- Auto-refresh (30s interval)

## Testing

```bash
cd nerve-center/tests

# Run all tests
python3 test_*.py

# Run specific test file
python3 test_state.py
python3 test_integration.py
```

Test coverage: 311 tests across 11 files.

## Configuration

See `config.yaml` for all configuration options:

- **database**: SQLite path and schema
- **proxmox**: Proxmox cluster API credentials
- **discovery**: Pipeline interval and settings
- **verification**: Service check interval and thresholds
- **alerts**: Alert rules and notification
- **wiki**: Auto-generation settings
- **http**: Service host/port configuration
- **knowledge_graph**: Graph settings
- **logging**: Log level and format

## Deployment to CT120 (Proxmox)

```bash
# 1. Clone to CT120 (grid-core-01)
ssh grid-pve "pct exec 120 -- bash -c 'git clone /path/to/GRID-Network-Wiki-Tool.git'"

# 2. Install dependencies
ssh grid-pve "pct exec 120 -- bash -c 'pip install -r GRID-Network-Wiki-Tool/nerve-center/requirements.txt'"

# 3. Configure
ssh grid-pve "pct exec 120 -- bash -c 'cp GRID-Network-Wiki-Tool/nerve-center/config.yaml /opt/nerve-center/config.yaml'"

# 4. Start
ssh grid-pve "pct exec 120 -- bash -c 'cd /opt/nerve-center && python run.py &'"
```

## Knowledge Graph Schema

### Entities
- **server**: Proxmox hosts, standalone servers
- **container**: LXC/Docker containers
- **service**: Network services (HTTP, SSH, etc.)
- **network**: Network segments, VLANs
- **agent**: Registered agents

### Relationships
- **hosts**: server → container
- **hosts**: server → service
- **depends_on**: service → service
- **monitors**: service → service
- **manages**: agent → server/container/service

## Development

```bash
# Type check
pyright nerve-center/

# Run linting
flake8 nerve-center/

# Format
black nerve-center/
```

## License

Internal use — GRID Network.
