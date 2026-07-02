# GRID Network Nerve Center — Task Manifest (Part 2: Agent Services & Dashboard)

**Tasks:** 19-005 through 19-008
**Scope:** Wiki writer, HTTP service, agent API, knowledge agent interface

---

#### [TASK-19-005]: Create Wiki Writer
- **Component/Scope:** `nerve-center/wiki-writer.py`
- **Core Objective:** Generate wiki documentation from state data — service cards, container docs, server docs, network design.
- **Dependencies:** TASK-19-001 (SQLite state manager)
- **Context:**

```python
# nerve-center/wiki-writer.py
import os, json
from datetime import datetime
from typing import List, Dict, Optional

class WikiWriter:
    def __init__(self, wiki_content_path: str, state_manager):
        self.wiki_path = wiki_content_path
        self.state = state_manager

    def write_service_document(self, service: dict) -> str:
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

    def generate_service_card(self, service: dict) -> str:
        return f"| {service['name']} | {service['type']} | {service.get('port', 'N/A')} | {service.get('status', 'unknown')} | {service.get('url', 'N/A')} |"

    def generate_container_card(self, container: dict) -> str:
        return f"| {container['name']} | {container['vmid']} | {container['type']} | {container.get('status', 'unknown')} | {', '.join(container.get('ip_addresses', []))} |"

    def generate_server_card(self, server: dict) -> str:
        return f"| {server['hostname']} | {server['ip_address']} | {server.get('status', 'unknown')} | {server.get('proxmox_api_url', 'N/A')} |"

    def update_wiki_index(self) -> bool:
        index_path = os.path.join(self.wiki_path, 'wiki-index.json')
        try:
            with open(index_path) as f:
                index = json.load(f)
        except:
            index = {'pages': [], 'generated_at': ''}
        docs = self.state.get_wiki_documents()
        index['pages'] = [{
            'slug': d['slug'], 'title': d['title'], 'category': d['category'],
            'source': d.get('source', 'agent-generated'), 'last_updated': d.get('last_updated')
        } for d in docs]
        index['generated_at'] = datetime.now().isoformat()
        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)
        return True

    def _write_wiki_file(self, slug: str, content: str, category: str, related_id: int = None):
        dir_map = {
            'service': 'services', 'infrastructure': 'infrastructure',
            'design': 'design', 'procedure': 'procedures',
            'troubleshooting': 'troubleshooting'
        }
        dir_name = dir_map.get(category, 'misc')
        dir_path = os.path.join(self.wiki_path, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, f"{slug}.md")
        with open(file_path, 'w') as f:
            f.write(content)
        self.state.create_wiki_document({
            'title': slug.replace('-', ' ').title(), 'slug': slug,
            'category': category, 'content': content,
            'source': 'agent-generated', 'related_service_id': related_id,
            'last_updated': datetime.now().isoformat()
        })

    def _get_container_name(self, container_id: int) -> str:
        if not container_id: return 'N/A'
        container = self.state.get_container(container_id)
        return container['name'] if container else 'N/A'

    def _get_container_ip(self, container_id: int) -> str:
        if not container_id: return 'N/A'
        container = self.state.get_container(container_id)
        return ', '.join(container.get('ip_addresses', [])) if container else 'N/A'

    def _get_container_services_markdown(self, container_id: int) -> str:
        if not container_id: return '- No services discovered\n'
        services = self.state.get_container_services(container_id)
        if not services: return '- No services discovered\n'
        md = ''
        for s in services:
            md += f"- **{s['name']}**: {s['type']}:{s.get('port', 'N/A')} ({s.get('status', 'unknown')})\n"
        return md

    def _get_server_containers_markdown(self, server_id: int) -> str:
        if not server_id: return '- No containers discovered\n'
        containers = self.state.get_server_containers(server_id)
        if not containers: return '- No containers discovered\n'
        md = ''
        for c in containers:
            md += f"- **{c['name']}** (VMID {c['vmid']}): {c['type']} ({c.get('status', 'unknown')})\n"
        return md

    def _get_server_id(self, hostname: str) -> int:
        server = self.state.get_server(hostname)
        return server['id'] if server else None
```

- **Strict Evaluation Criteria:**
  1. `WikiWriter('/tmp/test-wiki', state).write_service_document({'name': 'test-service', 'type': 'http', 'port': 80, 'url': 'http://10.0.0.1:80', 'status': 'up', ...})` returns `'service-test-service'`
  2. File `/tmp/test-wiki/services/service-test-service.md` is created with correct markdown content
  3. `WikiWriter('/tmp/test-wiki', state).write_container_document({'name': 'test-container', 'vmid': 100, 'type': 'lxc', 'status': 'running', 'ip_addresses': ['10.0.0.2'], ...})` returns `'container-test-container'`
  4. File `/tmp/test-wiki/infrastructure/container-test-container.md` is created
  5. `WikiWriter('/tmp/test-wiki', state).write_server_document({'hostname': 'test-server', 'ip_address': '10.0.0.1', 'status': 'up', 'proxmox_api_url': 'https://10.0.0.1:8006/api2/json', ...})` returns `'server-test-server'`
  6. `WikiWriter('/tmp/test-wiki', state).update_wiki_index()` returns `True` and creates `wiki-index.json`
  7. `wiki-index.json` contains pages from state manager
  8. `generate_service_card()` returns correctly formatted markdown table row
  9. `generate_container_card()` returns correctly formatted markdown table row
  10. `generate_server_card()` returns correctly formatted markdown table row

---

#### [TASK-19-006]: Create Nerve Center HTTP Service
- **Component/Scope:** `nerve-center/nerve-center.py`
- **Core Objective:** HTTP service that serves the nerve center API, dashboard, and bridges all subsystems.
- **Dependencies:** TASK-19-001 through 19-005
- **Context:**

```python
# nerve-center/nerve-center.py
#!/usr/bin/env python3
"""GRID Network Nerve Center HTTP Service."""
import http.server, json, os, sys, time, socketserver, threading, yaml
import urllib.request, urllib.error
from datetime import datetime
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nerve_center.state import StateManager
from nerve_center.discoverer import ProxmoxDiscoverer
from nerve_center.verifier import ServiceVerifier
from nerve_center.knowledge import KnowledgeGraph
from nerve_center.wiki_writer import WikiWriter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8083
start_time = time.time()

_state = None
_discoverer = None
_verifier = None
_knowledge = None
_wiki_writer = None
_sse_subscribers = []
_sse_lock = threading.Lock()

CONFIG = yaml.safe_load(open(os.path.join(ROOT, 'nerve-center-config.yaml'))) if os.path.exists(os.path.join(ROOT, 'nerve-center-config.yaml')) else {}

def _send_json(handler, code, data):
    handler.send_response(code)
    handler.send_header('Content-Type', 'application/json')
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.end_headers()
    handler.wfile.write(json.dumps(data, indent=2).encode())

class NerveCenterHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format, *args):
        print(f"[nerve-center] {self.address_string()} - {format % args}", flush=True)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api/nerve/health':
            _send_json(self, 200, {'status': 'healthy', 'service': 'nerve-center', 'version': '1.0.0', 'timestamp': datetime.now().isoformat(), 'uptime': time.time() - start_time})
            return

        if path == '/api/nerve/servers':
            servers = _state.list_servers()
            for server in servers:
                server['containers'] = _state.get_server_containers(server['id'])
            _send_json(self, 200, {'servers': servers})
            return

        if path == '/api/nerve/containers':
            containers = _state.list_containers()
            for c in containers:
                c['services'] = _state.get_container_services(c['id'])
            _send_json(self, 200, {'containers': containers})
            return

        if path.startswith('/api/nerve/containers/'):
            vmid = path.split('/')[-1]
            container = _state.get_container(int(vmid))
            if container:
                container['services'] = _state.get_container_services(container['id'])
                _send_json(self, 200, container)
            else:
                _send_json(self, 404, {'error': 'Container not found'})
            return

        if path == '/api/nerve/services':
            services = _state.list_services()
            for s in services:
                s['container'] = _state.get_container(s['container_id'])
                s['relationships'] = _state.get_service_relationships(s['id'])
            _send_json(self, 200, {'services': services})
            return

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

        if path.startswith('/api/nerve/knowledge/'):
            node_id = path.split('/')[-1]
            node = _knowledge.get_node(node_id)
            if node:
                related = _knowledge.get_related(node_id)
                _send_json(self, 200, {'node': node, 'related': related})
            else:
                _send_json(self, 404, {'error': 'Knowledge node not found'})
            return

        if path == '/api/nerve/requests':
            params = parse_qs(parsed.query)
            status = params.get('status', [None])[0]
            requests = _state.get_user_requests(status=status)
            _send_json(self, 200, {'requests': requests})
            return

        if path == '/api/nerve/agent/actions':
            params = parse_qs(parsed.query)
            status = params.get('status', [None])[0]
            actions = _state.get_agent_actions(status=status)
            _send_json(self, 200, {'actions': actions})
            return

        if path == '/api/nerve/sync-status':
            _send_json(self, 200, {'last_sync': datetime.now().isoformat(), 'status': 'running', 'files_synced': 0})
            return

        if path == '/api/nerve/design':
            design = CONFIG.get('network_design', {})
            rules = CONFIG.get('design_rules', [])
            _send_json(self, 200, {'design': design, 'rules': rules})
            return

        if path == '/api/nerve/wiki/documents':
            params = parse_qs(parsed.query)
            category = params.get('category', [None])[0]
            docs = _state.get_wiki_documents(category=category)
            _send_json(self, 200, {'documents': docs})
            return

        if path.startswith('/api/nerve/wiki/'):
            slug = path.split('/')[-1]
            doc = _state.get_wiki_document_by_slug(slug)
            if doc:
                _send_json(self, 200, doc)
            else:
                _send_json(self, 404, {'error': 'Document not found'})
            return

        if path == '/sse':
            self._handle_sse()
            return

        if path == '/nerve-center.html':
            filepath = os.path.join(ROOT, 'nerve-center', 'nerve-center.html')
            with open(filepath) as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(content.encode())
            return

        _send_json(self, 404, {'error': f'Not found: {path}'})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api/nerve/knowledge':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)
            node_id = _knowledge.add_node(data)
            _send_json(self, 200, {'id': node_id, 'status': 'created'})
            return

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

        if path == '/api/nerve/discover':
            job_id = f"discover-{int(time.time())}"
            threading.Thread(target=self._run_discovery, args=(job_id,), daemon=True).start()
            _send_json(self, 200, {'status': 'started', 'job_id': job_id, 'message': 'Discovery started'})
            return

        if path == '/api/nerve/verify':
            job_id = f"verify-{int(time.time())}"
            threading.Thread(target=self._run_verification, args=(job_id,), daemon=True).start()
            _send_json(self, 200, {'status': 'started', 'job_id': job_id, 'message': 'Verification started'})
            return

        _send_json(self, 405, {'error': 'Method not allowed'})

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()

    def _handle_sse(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        with _sse_lock:
            _sse_subscribers.append(self.wfile)
        self.wfile.write(f"event: connected\ndata: {json.dumps({'status': 'connected', 'timestamp': time.time()})}\n\n".encode())
        self.wfile.flush()
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

    def _broadcast(self, event, data):
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

    def _run_discovery(self, job_id):
        self._broadcast('discovery-start', {'job_id': job_id, 'started_at': datetime.now().isoformat()})
        try:
            result = _discoverer.discover_all()
            for i, server in enumerate(result['servers']):
                self._broadcast('discovery-progress', {'job_id': job_id, 'progress': i / len(result['servers']) if result['servers'] else 0, 'servers_found': i + 1, 'containers_found': len(result['containers']), 'services_found': len(result['services'])})
            self._broadcast('discovery-complete', {'job_id': job_id, 'servers_found': len(result['servers']), 'containers_found': len(result['containers']), 'services_found': len(result['services'])})
            for service in result['services']:
                _wiki_writer.write_service_document(service)
            for container in result['containers']:
                _wiki_writer.write_container_document(container)
            _wiki_writer.update_wiki_index()
        except Exception as e:
            self._broadcast('discovery-error', {'job_id': job_id, 'error': str(e)})

    def _run_verification(self, job_id):
        self._broadcast('verification-start', {'job_id': job_id, 'started_at': datetime.now().isoformat()})
        try:
            result = _verifier.verify_all()
            self._broadcast('verification-complete', {'job_id': job_id, 'services_checked': result['checked'], 'services_up': result['up'], 'services_down': result['down']})
        except Exception as e:
            self._broadcast('verification-error', {'job_id': job_id, 'error': str(e)})

def main():
    global _state, _discoverer, _verifier, _knowledge, _wiki_writer
    _state = StateManager()
    _knowledge = KnowledgeGraph()
    _wiki_writer = WikiWriter(os.path.join(ROOT, 'wiki-content'), _state)
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
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), NerveCenterHandler) as httpd:
        print(f"NERVE CENTER running at http://0.0.0.0:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.shutdown()

if __name__ == '__main__':
    main()
```

- **Strict Evaluation Criteria:**
  1. `python3 nerve-center.py` starts and listens on port 8083
  2. `curl http://127.0.0.1:8083/api/nerve/health` returns `{"status": "healthy", ...}`
  3. `curl http://127.0.0.1:8083/api/nerve/servers` returns `{"servers": [...]}` (empty list if no Proxmox)
  4. `curl http://127.0.0.1:8083/api/nerve/containers` returns `{"containers": [...]}`
  5. `curl http://127.0.0.1:8083/api/nerve/services` returns `{"services": [...]}`
  6. `curl http://127.0.0.1:8083/api/nerve/knowledge?q=test` returns `{"results": [...], "total": N}`
  7. `curl -X POST http://127.0.0.1:8083/api/nerve/knowledge` with valid JSON body returns `{"id": "...", "status": "created"}`
  8. `curl -X POST http://127.0.0.1:8083/api/nerve/requests` with valid body returns `{"id": N, "status": "created"}`
  9. `curl -X POST http://127.0.0.1:8083/api/nerve/discover` returns `{"status": "started", "job_id": "discover-..."}`
  10. `curl http://127.0.0.1:8083/api/nerve/requests` returns `{"requests": [...]}`
  11. `curl http://127.0.0.1:8083/api/nerve/agent/actions` returns `{"actions": [...]}`
  12. `curl http://127.0.0.1:8083/api/nerve/wiki/documents` returns `{"documents": [...]}`
  13. `curl http://127.0.0.1:8083/api/nerve/wiki/test-service` returns wiki document or 404
  14. `curl http://127.0.0.1:8083/api/nerve/design` returns `{"design": {...}, "rules": [...]}`
  15. `curl http://127.0.0.1:8083/api/nerve/sync-status` returns sync status
  16. `curl http://127.0.0.1:8083/sse` establishes SSE connection and receives `connected` event
  17. `curl http://127.0.0.1:8083/nerve-center.html` returns HTML content
  18. Invalid endpoints return 404 JSON
  19. `OPTIONS` requests return CORS headers
  20. `POST` to GET-only endpoints returns 405

---

#### [TASK-19-007]: Create Agent-Driven Discovery Pipeline
- **Component/Scope:** `scripts/discover-proxmox.sh` + `cron/nerve-discovery.sh`
- **Core Objective:** Agent-driven pipeline that discovers new containers/services when added, verifies them, updates knowledge graph, and writes wiki docs.
- **Dependencies:** TASK-19-006 (HTTP service)
- **Context:**

```bash
#!/bin/bash
# scripts/discover-proxmox.sh
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== GRID Network Nerve Center - Discovery Pipeline ==="
echo "Started: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"

# Step 1: Trigger discovery
echo "Step 1: Triggering discovery..."
DISCOVERY_RESULT=$(curl -s --max-time 30 http://127.0.0.1:8083/api/nerve/discover)
echo "Discovery triggered: $DISCOVERY_RESULT"

# Step 2: Wait for completion (poll agent actions)
echo "Step 2: Waiting for discovery to complete..."
MAX_WAIT=300
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
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

# Step 5: Sync knowledge graph
echo "Step 5: Syncing knowledge graph..."
curl -s --max-time 30 http://127.0.0.1:8083/api/nerve/sync-status

# Step 6: Write wiki docs
echo "Step 6: Writing wiki documentation..."
curl -s --max-time 30 http://127.0.0.1:8083/api/nerve/wiki/documents > /dev/null

echo "=== Discovery pipeline complete ==="
echo "Finished: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
```

- **Strict Evaluation Criteria:**
  1. `bash scripts/discover-proxmox.sh` executes without errors
  2. Discovery API is called and returns `{"status": "started"}`
  3. Script waits for discovery to complete (polls agent actions)
  4. Result counts are printed (servers, containers, services)
  5. Verification is triggered and completes
  6. Knowledge graph sync is attempted
  7. Wiki documents endpoint is called
  8. Script exits with code 0 on success
  9. Cron job `cron/nerve-discovery.sh` runs the same pipeline
  10. Cron job is scheduled to run every 6 hours (1am-6am window)

---

#### [TASK-19-008]: Create Knowledge Agent Interface
- **Component/Scope:** `nerve-center/knowledge-agent.py` + `nerve-center/knowledge-rules.yaml`
- **Core Objective:** Agent interface for querying/updating knowledge graph with rule validation.
- **Dependencies:** TASK-19-003 (Knowledge graph)
- **Context:**

```python
# nerve-center/knowledge-agent.py
import json, os, yaml
from typing import List, Dict, Optional
from nerve_center.knowledge import KnowledgeGraph

class KnowledgeAgent:
    def __init__(self, knowledge_graph: KnowledgeGraph, rules_path: str = None):
        self.kg = knowledge_graph
        self.rules = self._load_rules(rules_path)

    def _load_rules(self, rules_path: str) -> List[dict]:
        if rules_path and os.path.exists(rules_path):
            with open(rules_path) as f:
                return yaml.safe_load(f)
        return []

    def query(self, query: str, limit: int = 10) -> List[dict]:
        results = self.kg.search(query, limit)
        for rule in self.rules:
            if rule.get('type') == 'filter':
                results = self._apply_filter(rule, results)
            elif rule.get('type') == 'enrich':
                results = self._apply_enrichment(rule, results)
        return results

    def add_knowledge(self, node: dict) -> str:
        for rule in self.rules:
            if rule.get('type') == 'validate':
                if not self._validate_rule(rule, node):
                    raise Exception(f"Knowledge validation failed: {rule.get('name')}")
        return self.kg.add_node(node)

    def update_knowledge(self, node_id: str, properties: dict) -> bool:
        return self.kg.update_node(node_id, properties)

    def delete_knowledge(self, node_id: str) -> bool:
        return self.kg.delete_node(node_id)

    def get_related(self, node_id: str, relationship_type: str = None) -> List[dict]:
        return self.kg.get_related(node_id, relationship_type)

    def _apply_filter(self, rule: dict, results: List[dict]) -> List[dict]:
        if rule.get('type') == 'filter' and rule.get('exclude_types'):
            return [r for r in results if r.get('type') not in rule['exclude_types']]
        return results

    def _apply_enrichment(self, rule: dict, results: List[dict]) -> List[dict]:
        if rule.get('type') == 'enrich' and rule.get('add_properties'):
            for r in results:
                r.update(rule['add_properties'])
        return results

    def _validate_rule(self, rule: dict, node: dict) -> bool:
        if rule.get('type') == 'validate' and rule.get('required_fields'):
            for field in rule['required_fields']:
                if field not in node.get('properties', {}):
                    return False
        return True

# nerve-center/knowledge-rules.yaml
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

- **Strict Evaluation Criteria:**
  1. `KnowledgeAgent(kg).add_knowledge({'id': 'test', 'type': 'service', 'label': 'Test', 'properties': {'name': 'test', 'type': 'http', 'status': 'up'}})` returns `'test'`
  2. `KnowledgeAgent(kg).add_knowledge({'id': 'test2', 'type': 'service', 'label': 'Test2', 'properties': {'name': 'test2'}})` raises `Exception` (missing 'type' and 'status')
  3. `KnowledgeAgent(kg).query('test', limit=10)` returns list containing the inserted node
  4. `KnowledgeAgent(kg).update_knowledge('test', {'status': 'down'})` returns `True`
  5. `KnowledgeAgent(kg).delete_knowledge('test')` returns `True`
  6. `KnowledgeAgent(kg).get_related('test')` returns related nodes
  7. Rules are loaded from `knowledge-rules.yaml`
  8. Knowledge graph unavailability does not crash the agent (graceful fallback)
