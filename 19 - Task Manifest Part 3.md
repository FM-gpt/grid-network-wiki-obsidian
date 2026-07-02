# GRID Network Nerve Center — Task Manifest (Part 3: Dashboard & Integration)

**Tasks:** 19-009 through 19-012
**Scope:** Dashboard HTML/JS, agent API, request handler, integration tests, deployment

---

#### [TASK-19-009]: Create Nerve Center Dashboard
- **Component/Scope:** `nerve-center/nerve-center.html` + `nerve-center/js/nerve-center.js` + `nerve-center/css/nerve-center.css`
- **Core Objective:** User-facing nerve center dashboard showing servers → containers → services → everything.
- **Dependencies:** TASK-19-006 (HTTP service)
- **Context:**

```html
<!-- nerve-center/nerve-center.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GRID Network Nerve Center</title>
  <link rel="stylesheet" href="css/nerve-center.css">
</head>
<body>
  <div class="nerve-center" id="nerveCenter">
    <header>
      <h1>GRID Network Nerve Center</h1>
      <div id="statusBar">
        <span id="sseStatus" class="status-indicator disconnected">SSE: disconnected</span>
        <span id="lastUpdate">Last update: --</span>
        <button id="refreshBtn">Refresh</button>
        <button id="discoverBtn">Discover</button>
        <button id="verifyBtn">Verify</button>
      </div>
    </header>

    <!-- Search -->
    <div class="search-box">
      <input type="text" id="searchInput" placeholder="Search knowledge base..." />
      <div id="searchResults" class="search-results hidden"></div>
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

    <!-- Service Detail Modal -->
    <div id="serviceModal" class="modal hidden">
      <div class="modal-content">
        <span class="close-modal" id="closeModal">&times;</span>
        <div id="modalBody"></div>
      </div>
    </div>
  </div>
  <script src="js/nerve-center.js"></script>
</body>
</html>
```

```css
/* nerve-center/css/nerve-center.css */
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; color: #333; }
.nerve-center { max-width: 1400px; margin: 0 auto; padding: 1rem; }
header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem; }
header h1 { font-size: 1.5rem; }
#statusBar { display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; }
.status-indicator { padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; }
.status-indicator.connected { background: #4caf50; color: white; }
.status-indicator.disconnected { background: #f44336; color: white; }
button { padding: 0.5rem 1rem; border: none; border-radius: 4px; cursor: pointer; background: #2196f3; color: white; }
button:hover { background: #1976d2; }
.search-box { margin: 1rem 0; position: relative; }
.search-box input { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; }
.search-results { position: absolute; top: 100%; left: 0; right: 0; background: white; border: 1px solid #ddd; border-radius: 4px; max-height: 300px; overflow-y: auto; z-index: 100; }
.search-results.hidden { display: none; }
.search-result-item { padding: 0.5rem 1rem; cursor: pointer; border-bottom: 1px solid #eee; }
.search-result-item:hover { background: #f0f0f0; }
.tabs { display: flex; gap: 0.25rem; margin-bottom: 1rem; border-bottom: 2px solid #ddd; }
.tab { padding: 0.75rem 1.5rem; border: none; background: none; color: #666; cursor: pointer; font-size: 1rem; border-bottom: 2px solid transparent; margin-bottom: -2px; }
.tab.active { color: #2196f3; border-bottom-color: #2196f3; }
.tab-content { display: none; }
.tab-content.active { display: block; }
.server-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
.server-card { background: white; border: 1px solid #ddd; border-radius: 8px; padding: 1rem; cursor: pointer; transition: box-shadow 0.2s; }
.server-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.server-card.up { border-left: 4px solid #4caf50; }
.server-card.down { border-left: 4px solid #f44336; }
.server-card h3 { margin-bottom: 0.5rem; }
.server-card p { font-size: 0.9rem; color: #666; }
.container-list, .service-list, .knowledge-results, .wiki-docs { background: white; border: 1px solid #ddd; border-radius: 8px; overflow: hidden; }
.container-item, .service-item, .knowledge-item, .wiki-doc-item { padding: 0.75rem 1rem; border-bottom: 1px solid #eee; }
.container-item:hover, .service-item:hover, .wiki-doc-item:hover { background: #f5f5f5; cursor: pointer; }
.status-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 0.5rem; }
.status-dot.up { background: #4caf50; }
.status-dot.down { background: #f44336; }
.status-dot.unknown { background: #9e9e9e; }
.request-form { background: white; border: 1px solid #ddd; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; }
.request-form input, .request-form select, .request-form textarea { width: 100%; padding: 0.5rem; margin: 0.25rem 0; border: 1px solid #ddd; border-radius: 4px; }
.request-form textarea { min-height: 80px; resize: vertical; }
.request-item { background: white; border: 1px solid #ddd; border-radius: 4px; padding: 0.5rem 1rem; margin-bottom: 0.5rem; }
.modal { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal.hidden { display: none; }
.modal-content { background: white; border-radius: 8px; padding: 2rem; max-width: 800px; width: 90%; max-height: 80vh; overflow-y: auto; position: relative; }
.close-modal { position: absolute; top: 1rem; right: 1rem; font-size: 1.5rem; cursor: pointer; }
</style>
```

```javascript
// nerve-center/js/nerve-center.js
class NerveCenter {
  constructor() {
    this.apiBase = '/api/nerve';
    this.sse = null;
    this.currentTab = 'servers';
    this._init();
  }

  _init() {
    this._setupTabs();
    this._setupSearch();
    this._setupRequestForm();
    this._setupModal();
    this._loadTab('servers');
    this._subscribeToSSE();
  }

  _setupTabs() {
    document.querySelectorAll('.tab').forEach(tab => {
      tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById(tab.dataset.tab).classList.add('active');
        this.currentTab = tab.dataset.tab;
        this._loadTab(tab.dataset.tab);
      });
    });
  }

  _setupSearch() {
    const input = document.getElementById('searchInput');
    let debounceTimer;
    input.addEventListener('input', (e) => {
      clearTimeout(debounceTimer);
      const query = e.target.value.trim();
      if (query.length >= 2) {
        debounceTimer = setTimeout(() => this._searchKnowledge(query), 300);
      } else {
        document.getElementById('searchResults').classList.add('hidden');
      }
    });
  }

  _setupRequestForm() {
    document.getElementById('submitRequest').addEventListener('click', async () => {
      const title = document.getElementById('requestTitle').value;
      const type = document.getElementById('requestType').value;
      const description = document.getElementById('requestDescription').value;
      if (!title) { alert('Title is required'); return; }
      try {
        const resp = await fetch(`${this.apiBase}/requests`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: 'user', request_type: type, title, description })
        });
        const data = await resp.json();
        alert(`Request created: ${data.id}`);
        document.getElementById('requestTitle').value = '';
        document.getElementById('requestDescription').value = '';
        this._loadTab('requests');
      } catch (e) {
        alert(`Error: ${e.message}`);
      }
    });
  }

  _setupModal() {
    document.getElementById('closeModal').addEventListener('click', () => {
      document.getElementById('serviceModal').classList.add('hidden');
    });
    document.getElementById('serviceModal').addEventListener('click', (e) => {
      if (e.target.id === 'serviceModal') {
        document.getElementById('serviceModal').classList.add('hidden');
      }
    });
  }

  async _loadTab(tabId) {
    switch (tabId) {
      case 'servers': await this._loadServers(); break;
      case 'containers': await this._loadContainers(); break;
      case 'services': await this._loadServices(); break;
      case 'knowledge': break;
      case 'requests': await this._loadRequests(); break;
      case 'wiki': await this._loadWikiDocs(); break;
    }
    document.getElementById('lastUpdate').textContent = `Last update: ${new Date().toLocaleTimeString()}`;
  }

  async _loadServers() {
    const grid = document.getElementById('serverGrid');
    grid.innerHTML = '<p>Loading...</p>';
    try {
      const resp = await fetch(`${this.apiBase}/servers`);
      const data = await resp.json();
      grid.innerHTML = '';
      for (const server of data.servers) {
        const card = document.createElement('div');
        card.className = `server-card ${server.status}`;
        card.innerHTML = `
          <h3>${server.hostname}</h3>
          <p>IP: ${server.ip_address}</p>
          <p>Status: <span class="status-dot ${server.status}"></span> ${server.status}</p>
          <p>Containers: ${server.containers?.length || 0}</p>
        `;
        card.addEventListener('click', () => this._loadContainersForServer(server.id));
        grid.appendChild(card);
      }
    } catch (e) {
      grid.innerHTML = `<p class="error">Error loading servers: ${e.message}</p>`;
    }
  }

  async _loadContainersForServer(serverId) {
    const list = document.getElementById('containerList');
    list.innerHTML = '<p>Loading...</p>';
    try {
      const resp = await fetch(`${this.apiBase}/containers`);
      const data = await resp.json();
      list.innerHTML = '';
      const containers = data.containers.filter(c => c.server_id === serverId);
      for (const c of containers) {
        const item = document.createElement('div');
        item.className = 'container-item';
        item.innerHTML = `
          <strong>${c.name}</strong> <span class="status-dot ${c.status}"></span>
          <span>VMID: ${c.vmid} | Type: ${c.type}</span>
          <p>IP: ${c.ip_addresses?.join(', ') || 'N/A'}</p>
          <p>Services: ${c.services?.length || 0}</p>
        `;
        item.addEventListener('click', () => this._showContainerDetail(c));
        list.appendChild(item);
      }
    } catch (e) {
      list.innerHTML = `<p class="error">Error: ${e.message}</p>`;
    }
  }

  async _loadContainers() {
    const list = document.getElementById('containerList');
    list.innerHTML = '<p>Loading...</p>';
    try {
      const resp = await fetch(`${this.apiBase}/containers`);
      const data = await resp.json();
      list.innerHTML = '';
      for (const c of data.containers) {
        const item = document.createElement('div');
        item.className = 'container-item';
        item.innerHTML = `
          <strong>${c.name}</strong> <span class="status-dot ${c.status}"></span>
          <span>VMID: ${c.vmid} | Type: ${c.type}</span>
          <p>IP: ${c.ip_addresses?.join(', ') || 'N/A'}</p>
          <p>Services: ${c.services?.length || 0}</p>
        `;
        item.addEventListener('click', () => this._showContainerDetail(c));
        list.appendChild(item);
      }
    } catch (e) {
      list.innerHTML = `<p class="error">Error: ${e.message}</p>`;
    }
  }

  async _loadServices() {
    const list = document.getElementById('serviceList');
    list.innerHTML = '<p>Loading...</p>';
    try {
      const resp = await fetch(`${this.apiBase}/services`);
      const data = await resp.json();
      list.innerHTML = '';
      for (const s of data.services) {
        const item = document.createElement('div');
        item.className = 'service-item';
        item.innerHTML = `
          <span class="status-dot ${s.status}"></span>
          <strong>${s.name}</strong> <span>(${s.type}:${s.port})</span>
          <span>${s.status}</span>
          <span>${s.url || 'N/A'}</span>
        `;
        item.addEventListener('click', () => this._showServiceDetail(s.id));
        list.appendChild(item);
      }
    } catch (e) {
      list.innerHTML = `<p class="error">Error: ${e.message}</p>`;
    }
  }

  async _searchKnowledge(query) {
    const results = document.getElementById('searchResults');
    try {
      const resp = await fetch(`${this.apiBase}/knowledge?q=${encodeURIComponent(query)}&limit=10`);
      const data = await resp.json();
      results.innerHTML = '';
      if (data.results.length === 0) {
        results.innerHTML = '<div class="search-result-item">No results</div>';
      } else {
        for (const node of data.results) {
          const item = document.createElement('div');
          item.className = 'search-result-item';
          item.innerHTML = `<strong>${node.label}</strong> <span>(${node.type})</span>`;
          results.appendChild(item);
        }
      }
      results.classList.remove('hidden');
    } catch (e) {
      results.innerHTML = `<div class="search-result-item">Error: ${e.message}</div>`;
      results.classList.remove('hidden');
    }
  }

  async _showServiceDetail(serviceId) {
    try {
      const resp = await fetch(`${this.apiBase}/services/${serviceId}`);
      const data = await resp.json();
      const modal = document.getElementById('serviceModal');
      const body = document.getElementById('modalBody');
      body.innerHTML = `
        <h2>${data.name}</h2>
        <p><strong>Type:</strong> ${data.type}</p>
        <p><strong>Port:</strong> ${data.port}</p>
        <p><strong>URL:</strong> ${data.url || 'N/A'}</p>
        <p><strong>Status:</strong> <span class="status-dot ${data.status}"></span> ${data.status}</p>
        <p><strong>Container:</strong> ${data.container?.name || 'N/A'}</p>
        <p><strong>Prometheus:</strong> ${data.monitoring_configured ? 'Configured' : 'Not configured'}</p>
        <p><strong>Caddy:</strong> ${data.caddy_configured ? 'Configured' : 'Not configured'}</p>
        <h3>Relationships</h3>
        <ul>${(data.relationships || []).map(r => `<li>${r.relationship_type}: ${r.target_name} (${r.target_type})</li>`).join('')}</ul>
        <h3>Wiki Documents</h3>
        <ul>${(data.wiki_docs || []).map(d => `<li>${d.title} (${d.category})</li>`).join('')}</ul>
      `;
      modal.classList.remove('hidden');
    } catch (e) {
      alert(`Error: ${e.message}`);
    }
  }

  async _showContainerDetail(container) {
    try {
      const resp = await fetch(`${this.apiBase}/containers/${container.vmid}`);
      const data = await resp.json();
      const modal = document.getElementById('serviceModal');
      const body = document.getElementById('modalBody');
      body.innerHTML = `
        <h2>${data.name} (VMID ${data.vmid})</h2>
        <p><strong>Type:</strong> ${data.type}</p>
        <p><strong>Status:</strong> <span class="status-dot ${data.status}"></span> ${data.status}</p>
        <p><strong>IP:</strong> ${data.ip_addresses?.join(', ') || 'N/A'}</p>
        <p><strong>Memory:</strong> ${data.memory_mb} MB</p>
        <p><strong>CPU:</strong> ${data.cpu_cores} cores</p>
        <h3>Services</h3>
        <ul>${(data.services || []).map(s => `<li><span class="status-dot ${s.status}"></span> ${s.name} (${s.type}:${s.port})</li>`).join('')}</ul>
      `;
      modal.classList.remove('hidden');
    } catch (e) {
      alert(`Error: ${e.message}`);
    }
  }

  async _loadRequests() {
    const list = document.getElementById('requestList');
    list.innerHTML = '<p>Loading...</p>';
    try {
      const resp = await fetch(`${this.apiBase}/requests`);
      const data = await resp.json();
      list.innerHTML = '';
      for (const req of data.requests) {
        const item = document.createElement('div');
        item.className = 'request-item';
        item.innerHTML = `<strong>${req.title}</strong> <span>(${req.request_type})</span> <span class="status-dot ${req.status === 'completed' ? 'up' : req.status === 'rejected' ? 'down' : 'unknown'}"></span> ${req.status}`;
        list.appendChild(item);
      }
    } catch (e) {
      list.innerHTML = `<p class="error">Error: ${e.message}</p>`;
    }
  }

  async _loadWikiDocs() {
    const list = document.getElementById('wikiDocs');
    list.innerHTML = '<p>Loading...</p>';
    try {
      const resp = await fetch(`${this.apiBase}/wiki/documents`);
      const data = await resp.json();
      list.innerHTML = '';
      for (const doc of data.documents) {
        const item = document.createElement('div');
        item.className = 'wiki-doc-item';
        item.innerHTML = `<strong>${doc.title}</strong> <span>(${doc.category})</span>`;
        list.appendChild(item);
      }
    } catch (e) {
      list.innerHTML = `<p class="error">Error: ${e.message}</p>`;
    }
  }

  _subscribeToSSE() {
    this.sse = new EventSource('/sse');
    this.sse.addEventListener('connected', (event) => {
      const el = document.getElementById('sseStatus');
      el.textContent = 'SSE: connected';
      el.className = 'status-indicator connected';
    });
    this.sse.addEventListener('discovery-complete', (event) => {
      const data = JSON.parse(event.data);
      console.log('Discovery complete:', data);
      this._loadTab(this.currentTab);
    });
    this.sse.addEventListener('verification-complete', (event) => {
      const data = JSON.parse(event.data);
      console.log('Verification complete:', data);
      this._loadTab(this.currentTab);
    });
    this.sse.addEventListener('service-status-change', (event) => {
      const data = JSON.parse(event.data);
      console.log('Service changed:', data);
    });
    this.sse.addEventListener('knowledge-update', (event) => {
      const data = JSON.parse(event.data);
      console.log('Knowledge updated:', data);
    });
    this.sse.addEventListener('request-created', (event) => {
      const data = JSON.parse(event.data);
      console.log('Request created:', data);
      this._loadTab('requests');
    });
    this.sse.addEventListener('agent-action', (event) => {
      const data = JSON.parse(event.data);
      console.log('Agent action:', data);
    });
    this.sse.addEventListener('discovery-error', (event) => {
      const data = JSON.parse(event.data);
      alert(`Discovery error: ${data.error}`);
    });
    this.sse.addEventListener('verification-error', (event) => {
      const data = JSON.parse(event.data);
      alert(`Verification error: ${data.error}`);
    });
    this.sse.onerror = (error) => {
      const el = document.getElementById('sseStatus');
      el.textContent = 'SSE: disconnected';
      el.className = 'status-indicator disconnected';
    };
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.nerveCenter = new NerveCenter();
});
```

- **Strict Evaluation Criteria:**
  1. `nerve-center.html` loads in browser without JS errors
  2. Servers tab displays server cards with status dots
  3. Clicking a server card loads containers for that server
  4. Containers tab displays all containers with status
  5. Services tab displays all services with status
  6. Clicking a service opens detail modal with full info
  7. Clicking a container opens detail modal with full info
  8. Knowledge tab shows search results
  9. Requests tab shows user requests
  10. Wiki tab shows wiki documents
  11. SSE connection establishes and shows connected status
  12. Search input debounces (300ms) before querying
  13. Submit request form creates a request via API
  14. Refresh button reloads current tab
  15. Discover button triggers discovery via API
  16. Verify button triggers verification via API
  17. Modal closes when clicking X or outside modal content
  18. Error states show error messages instead of blank

---

#### [TASK-19-010]: Create Agent API & Request Handler
- **Component/Scope:** `nerve-center/agent-api.py` + `nerve-center/request-handler.py`
- **Core Objective:** Agent API for querying/updating state, and user request handler for service requests.
- **Dependencies:** TASK-19-001 through 19-006
- **Context:**

```python
# nerve-center/agent-api.py
import json, os, sys
from typing import Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nerve_center.state import StateManager
from nerve_center.discoverer import ProxmoxDiscoverer
from nerve_center.verifier import ServiceVerifier
from nerve_center.knowledge import KnowledgeGraph
from nerve_center.wiki_writer import WikiWriter

class AgentAPI:
    def __init__(self, state, knowledge, discoverer, verifier, wiki_writer):
        self.state = state
        self.knowledge = knowledge
        self.discoverer = discoverer
        self.verifier = verifier
        self.wiki_writer = wiki_writer

    def query_state(self, query_type: str, filters: dict = None) -> dict:
        if query_type == 'servers':
            servers = self.state.list_servers()
            if filters and 'status' in filters:
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
            if filters and 'category' in filters:
                docs = [d for d in docs if d['category'] == filters['category']]
            return {'documents': docs}
        elif query_type == 'agent_actions':
            actions = self.state.get_agent_actions()
            if filters and 'status' in filters:
                actions = [a for a in actions if a['status'] == filters['status']]
            return {'actions': actions}
        elif query_type == 'user_requests':
            requests = self.state.get_user_requests()
            if filters and 'status' in filters:
                requests = [r for r in requests if r['status'] == filters['status']]
            return {'requests': requests}
        return {'error': f'Unknown query type: {query_type}'}

    def update_state(self, update_type: str, data: dict) -> dict:
        if update_type == 'create_service':
            service_id = self.state.upsert_service(data)
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
        if action_type == 'discover':
            result = self.discoverer.discover_all()
            action_id = self.state.create_agent_action({
                'agent_id': 'agent', 'action_type': 'discover',
                'target_type': 'all', 'status': 'completed', 'details': result
            })
            return {'status': 'completed', 'action_id': action_id, 'result': result}
        elif action_type == 'verify':
            result = self.verifier.verify_all()
            action_id = self.state.create_agent_action({
                'agent_id': 'agent', 'action_type': 'verify',
                'target_type': 'services', 'status': 'completed', 'details': result
            })
            return {'status': 'completed', 'action_id': action_id, 'result': result}
        elif action_type == 'write_wiki':
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
        results = self.knowledge.search(query, limit)
        return {'results': results, 'total': len(results)}

# nerve-center/request-handler.py
class RequestHandler:
    def __init__(self, state, agent_api):
        self.state = state
        self.agent_api = agent_api

    def create_request(self, user_id, request_type, title, description):
        request_id = self.state.create_user_request({
            'user_id': user_id, 'request_type': request_type,
            'title': title, 'description': description
        })
        self._route_request(request_id, request_type)
        return request_id

    def _route_request(self, request_id, request_type):
        routing = {
            'create_service': 'service-creation-agent',
            'modify_service': 'service-modification-agent',
            'delete_service': 'service-deletion-agent',
            'add_container': 'container-creation-agent',
            'investigate_issue': 'investigation-agent'
        }
        agent = routing.get(request_type, 'general-agent')
        self.state.update_user_request(request_id, 'approved', {'routed_to': agent})

    def get_request(self, request_id):
        return self.state.get_user_requests()

    def update_request_status(self, request_id, status, details=None):
        return self.state.update_user_request(request_id, status, details)
```

- **Strict Evaluation Criteria:**
  1. `AgentAPI(state, kg, disc, ver, wiki).query_state('servers')` returns `{'servers': [...]}`
  2. `AgentAPI(...).query_state('services', {'type': 'http'})` returns only HTTP services
  3. `AgentAPI(...).update_state('create_service', {...})` returns `{'status': 'created', 'service_id': N, 'wiki_slug': '...'}`
  4. `AgentAPI(...).trigger_action('discover')` returns `{'status': 'completed', ...}`
  5. `AgentAPI(...).trigger_action('verify')` returns `{'status': 'completed', ...}`
  6. `AgentAPI(...).trigger_action('sync_knowledge')` returns `{'status': 'synced'}` or `{'status': 'failed'}`
  7. `AgentAPI(...).search_knowledge('test')` returns `{'results': [...], 'total': N}`
  8. `RequestHandler(state, api).create_request('user', 'create_service', 'Test', 'Desc')` returns request_id
  9. Request is routed to correct agent based on type
  10. `RequestHandler(...).update_request_status(1, 'completed')` returns `True`

---

#### [TASK-19-011]: Create Integration Tests
- **Component/Scope:** `tests/test-integration.py`
- **Core Objective:** Test all nerve center components end-to-end.
- **Dependencies:** All previous tasks
- **Context:**

```python
#!/usr/bin/env python3
"""Integration tests for GRID Network Nerve Center."""
import unittest, json, os, sys, tempfile, shutil
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nerve_center.state import StateManager
from nerve_center.discoverer import ProxmoxDiscoverer
from nerve_center.verifier import ServiceVerifier
from nerve_center.knowledge import KnowledgeGraph
from nerve_center.wiki_writer import WikiWriter
from nerve_center.agent_api import AgentAPI
from nerve_center.request_handler import RequestHandler

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.db_path = '/tmp/test-nerve-integration.db'
        self.state = StateManager(self.db_path)
        self.knowledge = KnowledgeGraph(local_cache_path='/tmp/test-knowledge.json')
        self.wiki_writer = WikiWriter('/tmp/test-wiki', self.state)
        self.agent_api = AgentAPI(self.state, self.knowledge, None, None, self.wiki_writer)
        self.request_handler = RequestHandler(self.state, self.agent_api)

    def tearDown(self):
        for path in [self.db_path, '/tmp/test-knowledge.json']:
            if os.path.exists(path):
                os.remove(path)
        if os.path.exists('/tmp/test-wiki'):
            shutil.rmtree('/tmp/test-wiki')

    def test_server_crud(self):
        server = {'hostname': 'test-server', 'ip_address': '10.10.30.99',
                   'proxmox_api_url': 'https://10.10.30.99:8006/api2/json',
                   'proxmox_api_user': 'root@pam', 'proxmox_api_token_name': 'test',
                   'proxmox_api_token_secret': 'test', 'status': 'up'}
        sid = self.state.upsert_server(server)
        self.assertIsNotNone(sid)
        retrieved = self.state.get_server('test-server')
        self.assertEqual(retrieved['hostname'], 'test-server')
        self.assertEqual(retrieved['status'], 'up')
        servers = self.state.list_servers()
        self.assertEqual(len(servers), 1)

    def test_container_crud(self):
        server = {'hostname': 'test-server', 'ip_address': '10.10.30.99',
                   'proxmox_api_url': 'https://10.10.30.99:8006/api2/json',
                   'proxmox_api_user': 'root@pam', 'proxmox_api_token_name': 'test',
                   'proxmox_api_token_secret': 'test', 'status': 'up'}
        sid = self.state.upsert_server(server)
        container = {'server_id': sid, 'vmid': 9001, 'name': 'test-container',
                      'type': 'lxc', 'status': 'running', 'ip_addresses': ['10.10.30.91'],
                      'memory_mb': 4096, 'cpu_cores': 2, 'disk_total_mb': 10240,
                      'disk_used_mb': 2048, 'os': 'Ubuntu 22.04', 'template': 'ubuntu-22.04'}
        cid = self.state.upsert_container(container)
        self.assertIsNotNone(cid)
        retrieved = self.state.get_container(9001)
        self.assertEqual(retrieved['name'], 'test-container')
        self.assertEqual(retrieved['status'], 'running')

    def test_service_crud(self):
        server = {'hostname': 'test-server', 'ip_address': '10.10.30.99',
                   'proxmox_api_url': 'https://10.10.30.99:8006/api2/json',
                   'proxmox_api_user': 'root@pam', 'proxmox_api_token_name': 'test',
                   'proxmox_api_token_secret': 'test', 'status': 'up'}
        sid = self.state.upsert_server(server)
        container = {'server_id': sid, 'vmid': 9001, 'name': 'test-container',
                      'type': 'lxc', 'status': 'running', 'ip_addresses': ['10.10.30.91'],
                      'memory_mb': 4096, 'cpu_cores': 2, 'disk_total_mb': 10240,
                      'disk_used_mb': 2048, 'os': 'Ubuntu 22.04', 'template': 'ubuntu-22.04'}
        cid = self.state.upsert_container(container)
        service = {'container_id': cid, 'name': 'test-service', 'type': 'http', 'port': 8080,
                    'protocol': 'tcp', 'url': 'http://10.10.30.91:8080', 'status': 'up',
                    'response_time_ms': 5, 'last_checked': '2026-06-30T10:00:00',
                    'prometheus_job': 'test-service', 'prometheus_target': 'http://10.10.30.91:8080/metrics',
                    'monitoring_configured': 1, 'caddy_configured': 1}
        sid = self.state.upsert_service(service)
        self.assertIsNotNone(sid)
        retrieved = self.state.get_service(sid)
        self.assertEqual(retrieved['name'], 'test-service')
        self.assertEqual(retrieved['status'], 'up')
        services = self.state.list_services(container_id=cid)
        self.assertEqual(len(services), 1)

    def test_wiki_document(self):
        doc = {'title': 'Test Service', 'slug': 'test-service', 'category': 'service',
                'content': '# Test Service\n\nThis is a test service.',
                'source': 'agent-generated', 'last_updated': '2026-06-30T10:00:00'}
        doc_id = self.state.create_wiki_document(doc)
        self.assertIsNotNone(doc_id)
        retrieved = self.state.get_wiki_document_by_slug('test-service')
        self.assertEqual(retrieved['title'], 'Test Service')
        self.assertEqual(retrieved['category'], 'service')

    def test_agent_action(self):
        action = {'agent_id': 'test-agent', 'action_type': 'discover', 'target_type': 'all',
                   'status': 'completed', 'details': {'servers': 1, 'containers': 1, 'services': 1}}
        action_id = self.state.create_agent_action(action)
        self.assertIsNotNone(action_id)
        actions = self.state.get_agent_actions(status='completed')
        self.assertEqual(len(actions), 1)

    def test_user_request(self):
        request = {'user_id': 'test-user', 'request_type': 'create_service',
                    'title': 'Test Service Request', 'description': 'Create a new test service'}
        request_id = self.state.create_user_request(request)
        self.assertIsNotNone(request_id)
        requests = self.state.get_user_requests()
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0]['status'], 'pending')

    def test_knowledge_graph(self):
        node = {'id': 'test-node', 'type': 'service', 'label': 'Test Service',
                 'properties': {'name': 'test', 'status': 'up'},
                 'embeddings': [0.1] * 10, 'metadata': {'source': 'test'}}
        node_id = self.knowledge.add_node(node)
        self.assertEqual(node_id, 'test-node')
        retrieved = self.knowledge.get_node('test-node')
        self.assertEqual(retrieved['label'], 'Test Service')
        results = self.knowledge.search('test', limit=10)
        self.assertGreater(len(results), 0)

    def test_wiki_writer(self):
        service = {'container_id': 1, 'name': 'test-service', 'type': 'http', 'port': 8080,
                    'protocol': 'tcp', 'url': 'http://10.10.30.91:8080', 'status': 'up',
                    'response_time_ms': 5, 'last_checked': '2026-06-30T10:00:00',
                    'prometheus_job': 'test-service', 'prometheus_target': 'http://10.10.30.91:8080/metrics',
                    'monitoring_configured': 1, 'caddy_configured': 1}
        slug = self.wiki_writer.write_service_document(service)
        self.assertEqual(slug, 'service-test-service')
        file_path = os.path.join('/tmp/test-wiki', 'services', 'service-test-service.md')
        self.assertTrue(os.path.exists(file_path))
        with open(file_path) as f:
            content = f.read()
        self.assertIn('test-service', content.lower())

    def test_agent_api(self):
        server = {'hostname': 'test-server', 'ip_address': '10.10.30.99',
                   'proxmox_api_url': 'https://10.10.30.99:8006/api2/json',
                   'proxmox_api_user': 'root@pam', 'proxmox_api_token_name': 'test',
                   'proxmox_api_token_secret': 'test', 'status': 'up'}
        self.state.upsert_server(server)
        result = self.agent_api.query_state('servers')
        self.assertIn('servers', result)
        self.assertEqual(len(result['servers']), 1)

    def test_request_handler(self):
        request_id = self.request_handler.create_request('test-user', 'create_service', 'Test', 'Desc')
        self.assertIsNotNone(request_id)
        requests = self.state.get_user_requests()
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0]['status'], 'approved')

if __name__ == '__main__':
    unittest.main()
```

- **Strict Evaluation Criteria:**
  1. `python3 tests/test-integration.py` runs all 10 tests
  2. All tests pass (exit code 0)
  3. `test_server_crud` verifies server upsert, get, list
  4. `test_container_crud` verifies container upsert, get
  5. `test_service_crud` verifies service upsert, get, list
  6. `test_wiki_document` verifies wiki doc creation and retrieval
  7. `test_agent_action` verifies agent action logging
  8. `test_user_request` verifies request creation
  9. `test_knowledge_graph` verifies KG add, get, search
  10. `test_wiki_writer` verifies wiki file creation and content
  11. `test_agent_api` verifies agent API query
  12. `test_request_handler` verifies request creation and routing
  13. Cleanup removes all temp files after each test

---

#### [TASK-19-012]: Create Configuration & Deployment
- **Component/Scope:** `nerve-center/nerve-center-config.yaml` + `scripts/deploy-nerve-center.sh` + `cron/nerve-discovery.sh` + `cron/nerve-verify.sh` + `cron/nerve-sync.sh`
- **Core Objective:** Configuration file and deployment scripts for the nerve center service.
- **Dependencies:** All previous tasks
- **Context:**

```yaml
# nerve-center/nerve-center-config.yaml
proxmox:
  api_url: "https://10.10.30.22:8006/api2/json"
  api_user: "root@pam"
  api_token_name: "nerve-center"
  api_token_secret: "<replace_with_actual_token>"

wiki_content_path: "/srv/grid-wiki-tool/wiki-content"

network_design:
  name: "GRID Network"
  version: "1.0"
  description: "GRID infrastructure network design"
  cidr_blocks: ["10.10.30.0/24", "10.70.2.0/24"]
  vlan_ids: [10, 20, 30, 40, 50]
  dns_servers: ["10.10.30.22", "10.10.30.129"]
  ntp_servers: ["10.10.30.22"]

design_rules:
  - name: "allowed_ports"
    type: "port_range"
    rule_config:
      min: 1
      max: 65535
      reserved: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 53, 80, 443, 8080, 8443, 9090, 3000, 3001, 3002, 5432, 6379, 8006, 11434, 19132, 445, 9443, 8043]

  - name: "required_monitoring"
    type: "required_services"
    rule_config:
      required: ["prometheus", "grafana"]
      severity: "warning"

  - name: "required_backup"
    type: "required_backup"
    rule_config:
      severity: "warning"
      description: "All production services must have backup"

  - name: "network_isolation"
    type: "network_isolation"
    rule_config:
      production_vlans: [10, 20]
      management_vlans: [30, 40]
      guest_vlans: [50]
```

```bash
#!/bin/bash
# scripts/deploy-nerve-center.sh
set -e

CT131="grid-pve"
CT131_WIKI_DIR="/srv/grid-wiki-tool"

echo "=== Deploying GRID Network Nerve Center to CT131 ==="

# Copy nerve-center files
echo "Copying nerve-center files..."
rsync -av --delete nerve-center/ grid-pve:"$CT131_WIKI_DIR/nerve-center/"

# Copy config
echo "Copying config..."
scp nerve-center-config.yaml grid-pve:"$CT131_WIKI_DIR/nerve-center/"

# Restart service
echo "Restarting nerve-center service..."
ssh grid-pve "pct exec 131 -- bash -c 'systemctl restart nerve-center || (cd /srv/grid-wiki-tool/nerve-center && python3 -u nerve-center.py &)'"

# Verify
echo "Verifying deployment..."
sleep 5
HEALTH=$(curl -s --max-time 10 http://127.0.0.1:8083/api/nerve/health 2>/dev/null || echo '{"status":"unreachable"}')
STATUS=$(echo "$HEALTH" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))" 2>/dev/null || echo "unknown")
echo "Service status: $STATUS"

if [ "$STATUS" = "healthy" ]; then
    echo "=== Deployment successful ==="
else
    echo "=== Deployment may have issues - check service manually ==="
    echo "SSH to CT131: ssh grid-pve"
    echo "Check service: pct exec 131 -- cat /var/log/nerve-center.log"
fi
```

```bash
#!/bin/bash
# cron/nerve-discovery.sh — runs every 6 hours
cd /srv/grid-wiki-tool
python3 -u scripts/discover-proxmox.sh >> /var/log/nerve-discovery.log 2>&1
```

```bash
#!/bin/bash
# cron/nerve-verify.sh — runs every 1 hour
cd /srv/grid-wiki-tool
python3 -u scripts/verify-services.sh >> /var/log/nerve-verify.log 2>&1
```

```bash
#!/bin/bash
# cron/nerve-sync.sh — runs every 12 hours
cd /srv/grid-wiki-tool
curl -s --max-time 30 http://127.0.0.1:8083/api/nerve/knowledge > /dev/null
curl -s --max-time 30 http://127.0.0.1:8083/api/nerve/wiki/documents > /dev/null
```

- **Strict Evaluation Criteria:**
  1. `nerve-center-config.yaml` is valid YAML with all required sections
  2. `proxmox.api_url` points to correct Proxmox host
  3. `deploy-nerve-center.sh` copies files to CT131 via rsync/SCP
  4. `deploy-nerve-center.sh` restarts the service on CT131
  5. `deploy-nerve-center.sh` verifies health endpoint after deployment
  6. `nerve-discovery.sh` runs discovery pipeline
  7. `nerve-verify.sh` runs verification pipeline
  8. `nerve-sync.sh` syncs knowledge graph
  9. All cron jobs log to `/var/log/nerve-*.log`
  10. Config has `network_design` and `design_rules` sections
