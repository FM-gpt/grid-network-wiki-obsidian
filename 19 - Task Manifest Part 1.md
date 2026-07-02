# GRID Network Nerve Center — Task Manifest (Part 1: Core Infrastructure)

**Tasks:** 19-001 through 19-004
**Scope:** SQLite state manager, Proxmox discoverer, knowledge graph, service verifier

---

#### [TASK-19-001]: Create SQLite Schema and State Manager
- **Component/Scope:** `nerve-center/schema.sql` + `nerve-center/state.py`
- **Core Objective:** Create the SQLite database schema and Python state manager for all nerve center data (servers, containers, services, wiki docs, agent actions, user requests).
- **Dependencies:** None
- **Context:**

```sql
-- nerve-center/schema.sql
-- Servers (Proxmox hosts)
CREATE TABLE IF NOT EXISTS servers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hostname TEXT NOT NULL UNIQUE,
    ip_address TEXT NOT NULL,
    proxmox_api_url TEXT NOT NULL,
    proxmox_api_user TEXT NOT NULL,
    proxmox_api_token_name TEXT NOT NULL,
    proxmox_api_token_secret TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'unknown',
    last_discovered TEXT,
    last_verified TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Containers/VMs (LXC on Proxmox)
CREATE TABLE IF NOT EXISTS containers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id INTEGER NOT NULL REFERENCES servers(id),
    vmid INTEGER NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'unknown',
    ip_addresses TEXT NOT NULL DEFAULT '[]',
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
    type TEXT NOT NULL,
    port INTEGER,
    protocol TEXT NOT NULL DEFAULT 'tcp',
    url TEXT,
    status TEXT NOT NULL DEFAULT 'unknown',
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

-- Service Relationships
CREATE TABLE IF NOT EXISTS service_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_service_id INTEGER NOT NULL REFERENCES services(id),
    target_service_id INTEGER NOT NULL REFERENCES services(id),
    relationship_type TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(source_service_id, target_service_id, relationship_type)
);

-- Wiki Documents (byproduct of agent actions)
CREATE TABLE IF NOT EXISTS wiki_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT NOT NULL,
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
    action_type TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id INTEGER,
    status TEXT NOT NULL DEFAULT 'pending',
    details TEXT,
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- User Requests
CREATE TABLE IF NOT EXISTS user_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    request_type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    assigned_agent_id TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Indexes
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

```python
# nerve-center/state.py (key methods)
import sqlite3, json, os
from datetime import datetime
from typing import Optional, List, Dict, Any

class StateManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'nerve-center.db')
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
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
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                INSERT OR REPLACE INTO servers (hostname, ip_address, proxmox_api_url,
                    proxmox_api_user, proxmox_api_token_name, proxmox_api_token_secret,
                    status, last_discovered, last_verified, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                RETURNING id
            """, (
                server['hostname'], server['ip_address'],
                server.get('proxmox_api_url', ''), server.get('proxmox_api_user', ''),
                server.get('proxmox_api_token_name', ''), server.get('proxmox_api_token_secret', ''),
                server.get('status', 'unknown'),
                server.get('last_discovered'), server.get('last_verified'),
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
                container['server_id'], container['vmid'], container['name'],
                container['type'], container.get('status', 'unknown'),
                json.dumps(container.get('ip_addresses', [])),
                container.get('memory_mb'), container.get('cpu_cores'),
                container.get('disk_total_mb'), container.get('disk_used_mb'),
                container.get('os'), container.get('template'),
                container.get('last_discovered'), container.get('last_verified'),
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
                service['container_id'], service['name'], service['type'],
                service.get('port'), service.get('protocol', 'tcp'),
                service.get('url'), service.get('status', 'unknown'),
                service.get('response_time_ms'), service.get('last_checked'),
                service.get('prometheus_job'), service.get('prometheus_target'),
                service.get('monitoring_configured', 0), service.get('caddy_configured', 0),
                service.get('health_check_url'), service.get('health_check_interval'),
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
                query += " AND container_id = ?"; params.append(container_id)
            if type:
                query += " AND type = ?"; params.append(type)
            if status:
                query += " AND status = ?"; params.append(status)
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
                query += " AND category = ?"; params.append(category)
            if related_service_id:
                query += " AND related_service_id = ?"; params.append(related_service_id)
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
                query += " AND status = ?"; params.append(status)
            if type:
                query += " AND action_type = ?"; params.append(type)
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
                query += " AND status = ?"; params.append(status)
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

- **Strict Evaluation Criteria:**
  1. `StateManager('/tmp/test.db').upsert_server({'hostname': 'test', 'ip_address': '10.0.0.1', ...})` returns non-zero ID
  2. `StateManager('/tmp/test.db').get_server('test')` returns the inserted server dict
  3. `StateManager('/tmp/test.db').list_servers()` returns list containing the inserted server
  4. `StateManager('/tmp/test.db').upsert_container({'server_id': sid, 'vmid': 100, ...})` returns non-zero ID
  5. `StateManager('/tmp/test.db').get_container(100)` returns the inserted container dict
  6. `StateManager('/tmp/test.db').upsert_service({'container_id': cid, 'name': 'test', 'type': 'http', 'port': 80, ...})` returns non-zero ID
  7. `StateManager('/tmp/test.db').get_service(sid)` returns the inserted service dict
  8. `StateManager('/tmp/test.db').create_wiki_document({'title': 'Test', 'slug': 'test', 'category': 'service', 'content': '# Test', 'source': 'agent'})` returns non-zero ID
  9. `StateManager('/tmp/test.db').get_wiki_document_by_slug('test')` returns the inserted doc
  10. `StateManager('/tmp/test.db').create_agent_action({'agent_id': 'test', 'action_type': 'discover', 'target_type': 'all', 'status': 'completed', 'details': {}})` returns non-zero ID
  11. `StateManager('/tmp/test.db').create_user_request({'user_id': 'test', 'request_type': 'create_service', 'title': 'Test'})` returns non-zero ID
  12. All `list_*` methods handle None filters correctly (return all rows)
  13. SQLite WAL mode enabled for concurrency (`PRAGMA journal_mode=WAL`)

---

#### [TASK-19-002]: Create Proxmox Discoverer
- **Component/Scope:** `nerve-center/discoverer.py`
- **Core Objective:** Scan Proxmox API to discover servers, containers, VMs, and running services.
- **Dependencies:** TASK-19-001 (SQLite state manager)
- **Context:**

```python
# nerve-center/discoverer.py
import json, urllib.request, urllib.error, ssl, socket, time
from datetime import datetime
from typing import List, Dict, Optional

class ProxmoxDiscoverer:
    def __init__(self, state_manager, api_url, api_user, api_token_name, api_token_secret):
        self.state = state_manager
        self.api_url = api_url.rstrip('/')
        self.api_user = api_user
        self.api_token_name = api_token_name
        self.api_token_secret = api_token_secret
        self._verify_ssl = False

    def _api_get(self, path: str) -> dict:
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
        servers = []
        try:
            data = self._api_get('nodes')
            for node in data.get('data', []):
                hostname = node.get('node', '')
                ip = node.get('ip', '')
                status = 'up' if node.get('online') else 'down'
                server = {
                    'hostname': hostname, 'ip_address': ip,
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
        containers = []
        try:
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
                res_data = self._api_get(f"nodes/{server_hostname}/lxc/{vmid}/status/current")
                res = res_data.get('data', {})
                server = self.state.get_server(server_hostname)
                server_id = server['id'] if server else None
                container = {
                    'server_id': server_id, 'vmid': vmid, 'name': name,
                    'type': 'lxc', 'status': status, 'ip_addresses': ip_addrs,
                    'memory_mb': res.get('maxmem', 0), 'cpu_cores': res.get('maxcpu', 0),
                    'disk_total_mb': res.get('maxdisk', 0) // (1024 * 1024),
                    'disk_used_mb': res.get('disk', 0) // (1024 * 1024),
                    'os': None, 'template': None,
                    'last_discovered': datetime.now().isoformat(),
                    'last_verified': datetime.now().isoformat()
                }
                cid = self.state.upsert_container(container)
                containers.append({**container, 'id': cid})
        except Exception as e:
            print(f"Error discovering containers on {server_hostname}: {e}")
        return containers

    def discover_services(self, container: dict) -> List[dict]:
        services = []
        service_map = [
            ('http', 80, 'HTTP'), ('https', 443, 'HTTPS'), ('ssh', 22, 'SSH'),
            ('postgresql', 5432, 'PostgreSQL'), ('mysql', 3306, 'MySQL'),
            ('redis', 6379, 'Redis'), ('prometheus', 9090, 'Prometheus'),
            ('grafana', 3000, 'Grafana'), ('caddy', 8080, 'Caddy'),
            ('portainer', 9443, 'Portainer'), ('minecraft', 19132, 'Minecraft'),
            ('samba', 445, 'Samba'), ('ollama', 11434, 'Ollama'),
            ('open-webui', 3002, 'Open WebUI'), ('omada', 8043, 'Omada Controller'),
            ('proxmox', 8006, 'Proxmox API'),
        ]
        for proto, port, name in service_map:
            is_open = self._check_port_open(container['ip_addresses'], port)
            if is_open:
                url = f"http://{container['ip_addresses'][0]}:{port}" if proto in ('http', 'https') else None
                service = {
                    'container_id': container['id'], 'name': name, 'type': proto,
                    'port': port, 'protocol': 'tcp', 'url': url,
                    'status': 'up', 'response_time_ms': 0,
                    'last_checked': datetime.now().isoformat(),
                    'prometheus_job': None, 'prometheus_target': None,
                    'monitoring_configured': 0, 'caddy_configured': 0,
                    'health_check_url': None, 'health_check_interval': None
                }
                sid = self.state.upsert_service(service)
                services.append({**service, 'id': sid})
        return services

    def _check_port_open(self, ip_addresses: List[str], port: int, timeout: int = 3) -> bool:
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
        try:
            self._api_get('version')
            return 'up'
        except:
            return 'down'

    def verify_container(self, container: dict) -> str:
        try:
            data = self._api_get(f"nodes/{container['server_hostname']}/lxc/{container['vmid']}/status/current")
            return 'running' if data.get('data', {}).get('status') == 'running' else 'stopped'
        except:
            return 'unknown'

    def verify_service(self, service: dict) -> dict:
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

    def discover_all(self) -> dict:
        result = {'servers': [], 'containers': [], 'services': [], 'errors': []}
        servers = self.discover_servers()
        result['servers'] = servers
        for server in servers:
            if server['status'] != 'up':
                continue
            containers = self.discover_containers(server['hostname'])
            result['containers'].extend(containers)
            for container in containers:
                if container['status'] != 'running':
                    continue
                services = self.discover_services(container)
                result['services'].extend(services)
        return result
```

- **Strict Evaluation Criteria:**
  1. `ProxmoxDiscoverer` initializes with valid state manager and API credentials
  2. `discover_servers()` returns list of server dicts with `id` from state manager
  3. `discover_containers(hostname)` returns list of container dicts with `id` from state manager
  4. `discover_services(container)` returns list of service dicts with `id` from state manager
  5. `_check_port_open(['127.0.0.1'], 22)` returns `True` if SSH is running, `False` otherwise
  6. `verify_service({'url': 'http://127.0.0.1:8082', ...})` returns `{'status': 'up', 'response_time_ms': N}` if service is reachable
  7. `discover_all()` returns dict with `servers`, `containers`, `services` lists populated
  8. Proxmox API errors are caught and logged, not raised to caller
  9. Self-signed SSL is handled (cert verification disabled)

---

#### [TASK-19-003]: Create Knowledge Graph Manager
- **Component/Scope:** `nerve-center/knowledge.py`
- **Core Objective:** Manage the vector knowledge graph — store, search, and retrieve network knowledge via Honcho API.
- **Dependencies:** None (Honcho is external, CT130:8000)
- **Context:**

```python
# nerve-center/knowledge.py
import json, os, urllib.request, urllib.parse, urllib.error
from typing import List, Dict, Optional

class KnowledgeGraph:
    def __init__(self, honcho_url: str = 'http://10.10.30.130:8000', local_cache_path: str = None):
        self.honcho_url = honcho_url.rstrip('/')
        self.local_cache_path = local_cache_path or os.path.join(os.path.dirname(__file__), 'knowledge-graph.json')
        self._cache = self._load_cache()

    def _load_cache(self) -> dict:
        if os.path.exists(self.local_cache_path):
            with open(self.local_cache_path) as f:
                return json.load(f)
        return {'nodes': [], 'edges': []}

    def _save_cache(self):
        with open(self.local_cache_path, 'w') as f:
            json.dump(self._cache, f, indent=2)

    def add_node(self, node: dict) -> str:
        node_id = node.get('id', f"node-{len(self._cache['nodes']) + 1}")
        node['id'] = node_id
        existing = next((n for n in self._cache['nodes'] if n['id'] == node_id), None)
        if existing:
            existing.update(node)
        else:
            self._cache['nodes'].append(node)
        self._sync_to_honcho(node)
        self._save_cache()
        return node_id

    def add_edge(self, edge: dict) -> str:
        edge_id = f"edge-{len(self._cache['edges']) + 1}"
        edge['id'] = edge_id
        self._cache['edges'].append(edge)
        self._save_cache()
        return edge_id

    def search(self, query: str, limit: int = 10) -> List[dict]:
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
        return next((n for n in self._cache['nodes'] if n['id'] == node_id), None)

    def get_related(self, node_id: str, relationship_type: str = None) -> List[dict]:
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
        node = self.get_node(node_id)
        if not node:
            return False
        node['properties'].update(properties)
        self._save_cache()
        return True

    def delete_node(self, node_id: str) -> bool:
        node = self.get_node(node_id)
        if not node:
            return False
        self._cache['nodes'] = [n for n in self._cache['nodes'] if n['id'] != node_id]
        self._save_cache()
        return True

    def _sync_to_honcho(self, node: dict):
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
        try:
            for node in self._cache['nodes']:
                self._sync_to_honcho(node)
            return True
        except:
            return False

    def rebuild_local_cache(self) -> bool:
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

- **Strict Evaluation Criteria:**
  1. `KnowledgeGraph(local_cache_path='/tmp/test-kg.json').add_node({'id': 'test', 'type': 'service', 'label': 'Test', 'properties': {'name': 'test'}})` returns `'test'`
  2. `KnowledgeGraph(local_cache_path='/tmp/test-kg.json').get_node('test')` returns the inserted node dict
  3. `KnowledgeGraph(local_cache_path='/tmp/test-kg.json').search('test', limit=10)` returns list containing the inserted node
  4. `KnowledgeGraph(local_cache_path='/tmp/test-kg.json').update_node('test', {'status': 'up'})` returns `True`
  5. `KnowledgeGraph(local_cache_path='/tmp/test-kg.json').update_node('nonexistent', {'status': 'up'})` returns `False`
  6. `KnowledgeGraph(local_cache_path='/tmp/test-kg.json').delete_node('test')` returns `True`
  7. `KnowledgeGraph(local_cache_path='/tmp/test-kg.json').get_node('test')` returns `None` after deletion
  8. `KnowledgeGraph(local_cache_path='/tmp/test-kg.json').sync_to_honcho()` returns `True` if Honcho is reachable, `False` otherwise
  9. Honcho unavailability does not crash the system (graceful fallback)

---

#### [TASK-19-004]: Create Service Verifier
- **Component/Scope:** `nerve-center/verifier.py`
- **Core Objective:** Verify service health, check Prometheus/Caddy configuration, detect anomalies.
- **Dependencies:** TASK-19-001 (SQLite state manager), TASK-19-003 (Knowledge graph)
- **Context:**

```python
# nerve-center/verifier.py
import json, socket, time, urllib.request, urllib.error, ssl
from datetime import datetime
from typing import List, Dict, Optional

class ServiceVerifier:
    def __init__(self, state_manager, knowledge_graph):
        self.state = state_manager
        self.kg = knowledge_graph

    def verify_all_services(self) -> dict:
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
        caddy_config_path = '/etc/caddy/Caddyfile'
        try:
            with open(caddy_config_path) as f:
                config = f.read()
                if service.get('url') and service['url'] in config:
                    return True
                if service.get('port') and f":{service['port']}" in config:
                    return True
                return False
        except:
            return False

    def detect_anomalies(self, service: dict) -> List[dict]:
        anomalies = []
        # Check for port conflicts
        other_services = self.state.list_services(port=service.get('port'))
        if len(other_services) > 1:
            anomalies.append({
                'type': 'port_conflict', 'severity': 'error',
                'message': f"Port {service['port']} used by {len(other_services)} services"
            })
        # Check if monitoring is configured
        if not self.check_prometheus(service):
            anomalies.append({
                'type': 'missing_monitoring', 'severity': 'warning',
                'message': f"Service {service['name']} not monitored by Prometheus"
            })
        # Check if Caddy routing is configured
        if not self.check_caddy(service):
            anomalies.append({
                'type': 'missing_caddy_route', 'severity': 'info',
                'message': f"Service {service['name']} not routed via Caddy"
            })
        # Check if wiki document exists
        wiki_docs = self.state.get_wiki_documents(related_service_id=service['id'])
        if not wiki_docs:
            anomalies.append({
                'type': 'missing_documentation', 'severity': 'info',
                'message': f"Service {service['name']} has no wiki documentation"
            })
        return anomalies

    def verify_all(self) -> dict:
        services = self.state.list_services()
        result = {'services': [], 'prometheus_targets': [], 'caddy_routes': [], 'anomalies': []}
        for service in services:
            health = self.verify_service(service)
            prometheus = self.check_prometheus(service)
            caddy = self.check_caddy(service)
            anomalies = self.detect_anomalies(service)
            result['services'].append({
                **service, 'health': health,
                'prometheus_configured': prometheus, 'caddy_configured': caddy
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

- **Strict Evaluation Criteria:**
  1. `ServiceVerifier(state, kg).verify_all_services()` returns dict with `checked`, `up`, `down`, `errors` keys
  2. `verify_service({'url': 'http://127.0.0.1:8082'})` returns `{'status': 'up', 'response_time_ms': N}` if service is reachable
  3. `check_prometheus({'url': 'http://10.10.30.120:9090'})` returns `True` if service is in Prometheus targets, `False` otherwise
  4. `check_caddy({'port': 8080})` returns `True` if `:8080` is in Caddy config, `False` otherwise
  5. `detect_anomalies({'name': 'test', 'port': 8080, 'id': 1})` returns list of anomaly dicts
  6. Port conflict detection: if two services use same port, returns `port_conflict` anomaly
  7. Missing monitoring detection: if service not in Prometheus, returns `missing_monitoring` anomaly
  8. Missing documentation detection: if no wiki doc for service, returns `missing_documentation` anomaly
  9. `verify_all()` returns dict with `services`, `prometheus_targets`, `caddy_routes`, `anomalies` keys
