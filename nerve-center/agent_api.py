"""nerve-center/agent_api.py — Agent-facing API for nerve center.

Provides REST endpoints for agents to:
- Query the knowledge graph
- Search wiki documents
- Request service actions (discovery, verification, health reports)
- Submit and manage user requests
- Register and manage agents
- Get system status

This is the primary interface through which agents interact with the nerve center.
"""

import json
import threading
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Optional, Any

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state import StateManager
from knowledge_agent import KnowledgeAgent, KnowledgeAgentResponse


class NerveCenterAgentApp:
    """Application wiring KnowledgeAgent with agent-specific operations."""

    def __init__(self, db_path: str, config: dict = None) -> None:
        self.db_path = db_path
        self.config = config or {}
        self.agent = KnowledgeAgent(StateManager(db_path), self.config)

    # --- Discovery ---

    def run_discovery(self) -> dict:
        """Run full discovery pipeline."""
        return self.agent.request_discovery()

    def run_verification(self) -> dict:
        """Run service verification."""
        return self.agent.request_verification()

    def get_health_report(self) -> dict:
        """Get health report."""
        return self.agent.request_health_report()

    def get_alerts(self) -> list:
        """Get current alerts."""
        return self.agent.get_alerts()

    # --- Knowledge queries ---

    def query_graph(self, entity_type: str = None,
                    entity_id: str = None,
                    relationship_type: str = None) -> dict:
        """Query the knowledge graph."""
        return self.agent.query_graph(entity_type, entity_id, relationship_type)

    def search_knowledge(self, query: str,
                         entity_type: str = None) -> dict:
        """Search knowledge base."""
        return self.agent.search_knowledge(query, entity_type)

    def get_wiki_document(self, slug: str) -> Optional[dict]:
        """Get wiki document by slug."""
        return self.agent.get_wiki_document(slug)

    def list_wiki_documents(self, category: str = None) -> list:
        """List wiki documents."""
        return self.agent.list_wiki_documents(category)

    # --- User requests ---

    def submit_request(self, user_id: str, request_type: str,
                       title: str, description: str = None) -> dict:
        """Submit a user request."""
        return self.agent.submit_request(user_id, request_type, title, description)

    def get_user_requests(self, user_id: str = None,
                          status: str = None) -> list:
        """Get user requests."""
        return self.agent.get_user_requests(user_id, status)

    def update_request_status(self, request_id: int,
                              status: str,
                              details: dict = None) -> bool:
        """Update request status."""
        return self.agent.update_request_status(request_id, status, details)

    # --- Agent management ---

    def register_agent(self, agent_id: str,
                       name: str = None) -> dict:
        """Register an agent."""
        return self.agent.register_agent(agent_id, name)

    def get_agent_info(self, agent_id: str) -> Optional[dict]:
        """Get agent info."""
        return self.agent.get_agent_info(agent_id)

    def list_agents(self) -> list:
        """List all agents."""
        return self.agent.list_agents()

    def get_agent_actions(self, agent_id: str = None,
                          status: str = None,
                          action_type: str = None) -> list:
        """Get agent actions."""
        return self.agent.get_agent_actions(agent_id, status, action_type)

    # --- Knowledge graph operations ---

    def create_entity(self, entity_type: str, entity_id: str,
                      properties: dict,
                      source: str = 'agent') -> int:
        """Create entity in knowledge graph."""
        return self.agent.create_entity(entity_type, entity_id, properties, source)

    def create_relationship(self, source_type: str, source_id: str,
                            target_type: str, target_id: str,
                            rel_type: str,
                            properties: dict = None) -> int:
        """Create relationship."""
        return self.agent.create_relationship(
            source_type, source_id, target_type, target_id, rel_type, properties)

    def delete_entity(self, entity_type: str, entity_id: str) -> bool:
        """Delete entity."""
        return self.agent.delete_entity(entity_type, entity_id)

    # --- System status ---

    def get_system_status(self) -> dict:
        """Get comprehensive system status."""
        return self.agent.get_system_status()


class AgentAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the Agent API.

    Routes:
        GET  /api/agent/status              - System status
        GET  /api/agent/graph               - Query graph
        GET  /api/agent/graph?type=X&id=Y  - Query specific entity
        GET  /api/agent/search?q=QUERY     - Search knowledge
        GET  /api/agent/wiki/slug          - Get wiki doc
        GET  /api/agent/wiki               - List wiki docs
        POST /api/agent/discovery           - Run discovery
        POST /api/agent/verification        - Run verification
        POST /api/agent/health-report       - Get health report
        POST /api/agent/alerts              - Get alerts
        POST /api/agent/request             - Submit user request
        GET  /api/agent/requests            - Get user requests
        PUT  /api/agent/request/ID/status   - Update request
        POST /api/agent/agents/register     - Register agent
        GET  /api/agent/agents              - List agents
        GET  /api/agent/agents/ID           - Get agent info
        GET  /api/agent/actions             - Get agent actions
        POST /api/agent/entity              - Create entity
        POST /api/agent/relationship        - Create relationship
        DELETE /api/agent/entity/TYPE/ID    - Delete entity
    """

    app: Optional[NerveCenterAgentApp] = None

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

    def _send_json(self, data: dict, status: int = 200) -> None:
        """Send JSON response."""
        body = json.dumps(data, indent=2, default=str).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> dict:
        """Read and parse JSON request body."""
        length = int(self.headers.get('Content-Length', 0))
        if length == 0:
            return {}
        body = self.rfile.read(length)
        return json.loads(body.decode('utf-8'))

    def _parse_path(self):
        """Parse URL path and query parameters."""
        parsed = urlparse(self.path)
        return parsed.path.rstrip('/'), parse_qs(parsed.query)

    # --- GET ---

    def do_GET(self):
        path, params = self._parse_path()

        try:
            if path == '/api/agent/status':
                self._handle_status()
            elif path == '/api/agent/graph':
                self._handle_graph_query(params)
            elif path.startswith('/api/agent/graph/'):
                self._handle_graph_entity(path)
            elif path == '/api/agent/search':
                self._handle_search(params)
            elif path.startswith('/api/agent/wiki/'):
                slug = path.split('/wiki/')[-1]
                self._handle_get_wiki_doc(slug)
            elif path == '/api/agent/wiki':
                category = params.get('category', [None])[0]
                docs = self.app.list_wiki_documents(category)
                self._send_json({'documents': docs})
            elif path == '/api/agent/requests':
                user_id = params.get('user_id', [None])[0]
                status = params.get('status', [None])[0]
                requests = self.app.get_user_requests(user_id, status)
                self._send_json({'requests': requests})
            elif path == '/api/agent/agents':
                agents = self.app.list_agents()
                self._send_json({'agents': agents})
            elif path.startswith('/api/agent/agents/'):
                agent_id = path.split('/agents/')[-1]
                info = self.app.get_agent_info(agent_id)
                if info:
                    self._send_json({'agent': info})
                else:
                    self._send_json({'error': 'Agent not found'}, 404)
            elif path == '/api/agent/actions':
                agent_id = params.get('agent_id', [None])[0]
                status = params.get('status', [None])[0]
                action_type = params.get('type', [None])[0]
                actions = self.app.get_agent_actions(agent_id, status, action_type)
                self._send_json({'actions': actions})
            elif path == '/api/agent/alerts':
                alerts = self.app.get_alerts()
                self._send_json({'alerts': alerts})
            elif path == '/api/agent/health-report':
                report = self.app.get_health_report()
                self._send_json(report)
            else:
                self._send_json({'error': 'Not found'}, 404)
        except Exception as e:
            self._send_json({'error': str(e)}, 500)

    # --- POST ---

    def do_POST(self):
        path, params = self._parse_path()

        try:
            if path == '/api/agent/discovery':
                result = self.app.run_discovery()
                self._send_json(result)
            elif path == '/api/agent/verification':
                result = self.app.run_verification()
                self._send_json(result)
            elif path == '/api/agent/request':
                body = self._read_body()
                result = self.app.submit_request(
                    body.get('user_id', 'unknown'),
                    body.get('request_type', 'general'),
                    body.get('title', ''),
                    body.get('description', ''),
                )
                self._send_json(result)
            elif path.startswith('/api/agent/agents/register'):
                body = self._read_body()
                agent_id = body.get('agent_id', body.get('id', ''))
                name = body.get('name', None)
                if not agent_id:
                    self._send_json({'error': 'agent_id required'}, 400)
                    return
                result = self.app.register_agent(agent_id, name)
                self._send_json(result)
            elif path == '/api/agent/entity':
                body = self._read_body()
                entity_type = body.get('entity_type', body.get('type', ''))
                entity_id = body.get('entity_id', body.get('id', ''))
                properties = body.get('properties', {})
                source = body.get('source', 'agent')
                if not entity_type or not entity_id:
                    self._send_json({'error': 'entity_type and entity_id required'}, 400)
                    return
                eid = self.app.create_entity(entity_type, entity_id, properties, source)
                self._send_json({'id': eid, 'entity_type': entity_type, 'entity_id': entity_id})
            elif path == '/api/agent/relationship':
                body = self._read_body()
                rid = self.app.create_relationship(
                    body.get('source_type', ''),
                    body.get('source_id', ''),
                    body.get('target_type', ''),
                    body.get('target_id', ''),
                    body.get('relationship_type', body.get('rel_type', '')),
                    body.get('properties', {}),
                )
                self._send_json({'id': rid})
            else:
                self._send_json({'error': 'Not found'}, 404)
        except json.JSONDecodeError:
            self._send_json({'error': 'Invalid JSON'}, 400)
        except Exception as e:
            self._send_json({'error': str(e)}, 500)

    # --- PUT ---

    def do_PUT(self):
        path, params = self._parse_path()

        try:
            if path.startswith('/api/agent/request/') and path.endswith('/status'):
                request_id = int(path.split('/request/')[1].split('/')[0])
                body = self._read_body()
                status = body.get('status', '')
                details = body.get('details', {})
                success = self.app.update_request_status(request_id, status, details)
                if success:
                    self._send_json({'success': True, 'id': request_id})
                else:
                    self._send_json({'error': 'Update failed'}, 500)
            else:
                self._send_json({'error': 'Not found'}, 404)
        except (ValueError, IndexError):
            self._send_json({'error': 'Invalid request ID'}, 400)
        except Exception as e:
            self._send_json({'error': str(e)}, 500)

    # --- DELETE ---

    def do_DELETE(self):
        path, params = self._parse_path()

        try:
            if path.startswith('/api/agent/entity/') and path.count('/') >= 4:
                parts = path.split('/entity/')[-1].split('/')
                entity_type = parts[0]
                entity_id = parts[1]
                success = self.app.delete_entity(entity_type, entity_id)
                if success:
                    self._send_json({'success': True, 'entity_type': entity_type, 'entity_id': entity_id})
                else:
                    self._send_json({'error': 'Delete failed'}, 500)
            else:
                self._send_json({'error': 'Not found'}, 404)
        except Exception as e:
            self._send_json({'error': str(e)}, 500)

    # --- Handler methods ---

    def _handle_status(self):
        status = self.app.get_system_status()
        self._send_json(status)

    def _handle_graph_query(self, params):
        entity_type = params.get('type', [None])[0]
        entity_id = params.get('id', [None])[0]
        relationship_type = params.get('relationship', [None])[0]
        result = self.app.query_graph(entity_type, entity_id, relationship_type)
        self._send_json(result)

    def _handle_graph_entity(self, path):
        parts = path.split('/graph/')[-1].split('/')
        entity_type = parts[0]
        entity_id = parts[1]
        result = self.app.query_graph(entity_type=entity_type, entity_id=entity_id)
        self._send_json(result)

    def _handle_search(self, params):
        query = params.get('q', [''])[0]
        entity_type = params.get('type', [None])[0]
        result = self.app.search_knowledge(query, entity_type)
        self._send_json(result)

    def _handle_get_wiki_doc(self, slug):
        doc = self.app.get_wiki_document(slug)
        if doc:
            self._send_json(doc)
        else:
            self._send_json({'error': 'Document not found'}, 404)


class AgentAPIServer:
    """HTTP server wrapper for the Agent API."""

    def __init__(self, db_path: str, config: dict = None,
                 host: str = '0.0.0.0', port: int = 8766) -> None:
        self.db_path = db_path
        self.config = config or {}
        self.host = host
        self.port = port
        self.server: Optional[HTTPServer] = None

    def start(self) -> None:
        """Start the HTTP server."""
        NerveCenterAgentApp.__init__.__globals__['sys'] = sys
        self.app = NerveCenterAgentApp(self.db_path, self.config)
        AgentAPIHandler.app = self.app
        self.server = HTTPServer((self.host, self.port), AgentAPIHandler)
        print(f"Agent API server starting on {self.host}:{self.port}")
        self.server.serve_forever()

    def stop(self) -> None:
        """Stop the HTTP server."""
        if self.server:
            self.server.shutdown()

    def get_status(self) -> dict:
        """Get server status without starting."""
        return {
            'host': self.host,
            'port': self.port,
            'db_path': self.db_path,
        }
