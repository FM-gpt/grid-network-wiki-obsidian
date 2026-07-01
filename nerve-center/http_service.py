"""nerve-center/http_service.py — HTTP API server for GRID Network Nerve Center."""

import json
import threading
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from typing import Dict, Optional, Any

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state import StateManager
from discoverer import ProxmoxDiscoverer
from knowledge_graph import KnowledgeGraphManager
from service_verifier import ServiceVerifier
from wiki_writer import WikiWriter


class NerveCenterApp:
    """Full nerve center application wiring all components."""

    def __init__(self, db_path: str, config: Optional[dict] = None) -> None:
        self.db_path = db_path
        self.config = config or {}
        self.state = StateManager(db_path)
        self.kgm = KnowledgeGraphManager(self.state)
        self.verifier = ServiceVerifier(self.state, self.kgm)
        self.writer = WikiWriter(self.state, self.kgm)
        self._discoverer: Optional[ProxmoxDiscoverer] = None
        self._discovery_thread: Optional[threading.Thread] = None
        self._running = False
        self._init_discoverer()

    def _init_discoverer(self) -> None:
        """Initialize Proxmox discoverer from config."""
        proxmox = self.config.get('proxmox', {})
        if proxmox.get('api_url'):
            self._discoverer = ProxmoxDiscoverer(
                state_manager=self.state,
                api_url=proxmox['api_url'],
                api_user=proxmox.get('api_user', ''),
                api_token_name=proxmox.get('api_token_name', ''),
                api_token_secret=proxmox.get('api_token_secret', ''),
            )

    def discover(self, blocking: bool = False) -> dict:
        """Run full discovery pipeline."""
        if not self._discoverer:
            return {'error': 'Proxmox discoverer not configured'}
        result = self._discoverer.discover_all()
        # Generate wiki docs for discovered items
        self.writer.generate_bulk('server', result.get('servers', []))
        self.writer.generate_bulk('container', result.get('containers', []))
        self.writer.generate_bulk('service', result.get('services', []))
        # Generate discovery summary
        self.writer.generate_document('discovery_summary', result)
        return result

    def verify_all(self) -> dict:
        """Verify all services."""
        return self.verifier.verify_all_services()

    def health_report(self) -> dict:
        """Generate health report."""
        return self.verifier.generate_health_report()

    def get_alerts(self) -> list:
        """Get current alerts."""
        report = self.health_report()
        return self.verifier.check_alerts(report)

    def start_discovery(self) -> Optional[threading.Thread]:
        """Start discovery in background thread."""
        if not self._discoverer:
            return None
        self._running = True
        thread = threading.Thread(target=self._discovery_loop, daemon=True)
        thread.start()
        self._discovery_thread = thread
        return thread

    def _discovery_loop(self) -> None:
        """Background discovery loop."""
        interval = self.config.get('discovery_interval', 300)
        while self._running:
            try:
                self.discover()
            except Exception as e:
                print(f"Discovery error: {e}")
            # Sleep in small increments to allow stopping
            for _ in range(interval * 10):
                if not self._running:
                    break
                threading.Event().wait(0.1)

    def stop_discovery(self) -> None:
        """Stop background discovery."""
        self._running = False

    def get_wiki_docs(self, category: str = None) -> list:
        """Get wiki documents."""
        if category:
            return self.writer.get_generated_docs(category)
        return self.writer.get_generated_docs()

    def get_wiki_doc_by_slug(self, slug: str) -> Optional[dict]:
        """Get wiki document by slug."""
        return self.writer.get_document_by_slug(slug)

    def get_graph_summary(self) -> dict:
        """Get knowledge graph summary."""
        return self.kgm.get_graph_summary()

    def get_neighbors(self, entity_type: str, entity_id: str,
                      direction: str = 'both') -> list:
        """Get graph neighbors."""
        return self.kgm.get_neighbors(entity_type, entity_id, direction)

    def search_entities(self, query: str, entity_type: str = None) -> list:
        """Search entities."""
        return self.kgm.search_entities(query, entity_type)

    def get_servers(self) -> list:
        """Get all servers."""
        return self.state.list_servers()

    def get_server(self, hostname: str) -> Optional[dict]:
        """Get server by hostname."""
        return self.state.get_server(hostname)

    def get_containers(self) -> list:
        """Get all containers."""
        return self.state.list_containers()

    def get_services(self) -> list:
        """Get all services."""
        return self.state.list_services()

    def get_service(self, service_id: int) -> Optional[dict]:
        """Get service by ID."""
        return self.state.get_service(service_id)


class NerveCenterHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Nerve Center API."""

    app: Optional[NerveCenterApp] = None  # Set by server

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

    def _send_json(self, data: Any, status: int = 200) -> None:
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _read_body(self) -> dict:
        length = int(self.headers.get('Content-Length', 0))
        if length == 0:
            return {}
        body = self.rfile.read(length)
        return json.loads(body.decode())

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        params = parse_qs(parsed.query)

        try:
            # Health check
            if path == '/api/health' or path == '/api/health/':
                self._send_json({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
                return

            # Root API info
            if path == '/api' or path == '/api/':
                self._send_json({
                    'name': 'GRID Network Nerve Center',
                    'version': '1.0.0',
                    'endpoints': {
                        'GET /api/health': 'Health check',
                        'GET /api/servers': 'List all servers',
                        'GET /api/servers/{hostname}': 'Get server by hostname',
                        'GET /api/containers': 'List all containers',
                        'GET /api/services': 'List all services',
                        'GET /api/services/{id}': 'Get service by ID',
                        'GET /api/wiki': 'List wiki documents',
                        'GET /api/wiki/{slug}': 'Get wiki document by slug',
                        'GET /api/graph/summary': 'Knowledge graph summary',
                        'GET /api/graph/neighbors/{type}/{id}': 'Get graph neighbors',
                        'GET /api/search?q=query': 'Search entities',
                        'GET /api/alerts': 'Get current alerts',
                        'GET /api/health-report': 'Full health report',
                        'GET /api/discovery': 'Run discovery',
                        'GET /api/verify': 'Verify all services',
                    }
                })
                return

            # Servers
            if path.startswith('/api/servers/'):
                hostname = path.split('/api/servers/')[-1]
                server = self.app.get_server(hostname)
                if server:
                    self._send_json(server)
                else:
                    self._send_json({'error': 'Server not found'}, 404)
                return

            if path == '/api/servers' or path == '/api/servers/':
                self._send_json({'servers': self.app.get_servers()})
                return

            # Containers
            if path == '/api/containers' or path == '/api/containers/':
                self._send_json({'containers': self.app.get_containers()})
                return

            # Services
            if path.startswith('/api/services/'):
                service_id = int(path.split('/api/services/')[-1])
                service = self.app.get_service(service_id)
                if service:
                    self._send_json(service)
                else:
                    self._send_json({'error': 'Service not found'}, 404)
                return

            if path == '/api/services' or path == '/api/services/':
                self._send_json({'services': self.app.get_services()})
                return

            # Wiki documents
            if path.startswith('/api/wiki/'):
                slug = path.split('/api/wiki/')[-1]
                doc = self.app.get_wiki_doc_by_slug(slug)
                if doc:
                    self._send_json(doc)
                else:
                    self._send_json({'error': 'Document not found'}, 404)
                return

            if path == '/api/wiki' or path == '/api/wiki/':
                category = params.get('category', [None])[0]
                docs = self.app.get_wiki_docs(category)
                self._send_json({'documents': docs, 'count': len(docs)})
                return

            # Knowledge graph
            if path == '/api/graph/summary' or path == '/api/graph/summary/':
                self._send_json(self.app.get_graph_summary())
                return

            if path.startswith('/api/graph/neighbors/'):
                parts = path.split('/api/graph/neighbors/')[-1].split('/')
                if len(parts) >= 2:
                    entity_type, entity_id = parts[0], parts[1]
                    direction = params.get('direction', ['both'])[0]
                    neighbors = self.app.get_neighbors(entity_type, entity_id, direction)
                    self._send_json({'neighbors': neighbors, 'count': len(neighbors)})
                else:
                    self._send_json({'error': 'Missing entity type or id'}, 400)
                return

            # Search
            if path == '/api/search' or path == '/api/search/':
                query = params.get('q', [''])[0]
                entity_type = params.get('entity_type', [None])[0]
                results = self.app.search_entities(query, entity_type)
                self._send_json({'results': results, 'count': len(results)})
                return

            # Alerts
            if path == '/api/alerts' or path == '/api/alerts/':
                alerts = self.app.get_alerts()
                self._send_json({'alerts': alerts, 'count': len(alerts)})
                return

            # Health report
            if path == '/api/health-report' or path == '/api/health-report/':
                report = self.app.health_report()
                self._send_json(report)
                return

            # Discovery
            if path == '/api/discovery' or path == '/api/discovery/':
                result = self.app.discover()
                self._send_json(result)
                return

            # Verify
            if path == '/api/verify' or path == '/api/verify/':
                result = self.app.verify_all()
                self._send_json(result)
                return

            self._send_json({'error': 'Not found'}, 404)

        except Exception as e:
            self._send_json({'error': str(e), 'traceback': traceback.format_exc()}, 500)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        try:
            body = self._read_body()

            # Run discovery
            if path == '/api/discovery' or path == '/api/discovery/':
                blocking = body.get('blocking', False)
                if blocking:
                    result = self.app.discover(blocking=True)
                    self._send_json(result)
                else:
                    thread = self.app.start_discovery()
                    self._send_json({'status': 'discovery started', 'thread': str(thread)})
                return

            # Run verification
            if path == '/api/verify' or path == '/api/verify/':
                result = self.app.verify_all()
                self._send_json(result)
                return

            # Create user request
            if path == '/api/requests' or path == '/api/requests/':
                request_id = self.app.state.create_user_request(body)
                self._send_json({'id': request_id, 'status': 'pending'}, 201)
                return

            # Update user request
            if path.startswith('/api/requests/'):
                request_id = int(path.split('/api/requests/')[-1])
                status = body.get('status', 'pending')
                details = body.get('details', {})
                self.app.state.update_user_request(request_id, status, details)
                self._send_json({'id': request_id, 'status': status})
                return

            # Search
            if path == '/api/search' or path == '/api/search/':
                query = body.get('q', '')
                entity_type = body.get('entity_type')
                results = self.app.search_entities(query, entity_type)
                self._send_json({'results': results, 'count': len(results)})
                return

            self._send_json({'error': 'Not found'}, 404)

        except json.JSONDecodeError:
            self._send_json({'error': 'Invalid JSON'}, 400)
        except Exception as e:
            self._send_json({'error': str(e), 'traceback': traceback.format_exc()}, 500)


def create_app(db_path: str, config: dict = None) -> NerveCenterApp:
    """Create and return the nerve center application."""
    return NerveCenterApp(db_path, config)


def create_server(app: NerveCenterApp, host: str = '0.0.0.0',
                  port: int = 8082) -> HTTPServer:
    """Create and return the HTTP server."""
    NerveCenterHandler.app = app
    server = HTTPServer((host, port), NerveCenterHandler)
    return server


def run_server(db_path: str, host: str = '0.0.0.0', port: int = 8082,
               config: dict = None) -> None:
    """Run the nerve center HTTP server."""
    app = create_app(db_path, config)
    server = create_server(app, host, port)
    print(f"Nerve Center listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()
