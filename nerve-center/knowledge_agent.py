"""nerve-center/knowledge_agent.py — Agent interface for knowledge base interaction."""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state import StateManager
from knowledge_graph import KnowledgeGraphManager
from wiki_writer import WikiWriter
from service_verifier import ServiceVerifier
from discovery_pipeline import DiscoveryPipeline


class KnowledgeAgent:
    """Agent interface for knowledge base interaction.

    Provides a unified API for agents to:
    - Query the knowledge graph
    - Search wiki documents
    - Request service actions (discover, verify, etc.)
    - Submit user requests
    - Receive agent responses
    """

    def __init__(self, state_manager: StateManager,
                 config: dict = None) -> None:
        self.state = state_manager
        self.config = config or {}
        self.kgm = KnowledgeGraphManager(self.state)
        self.writer = WikiWriter(self.state, self.kgm)
        self.verifier = ServiceVerifier(self.state, self.kgm)
        self.pipeline = DiscoveryPipeline(self.state, self.config)
        self._agents: Dict[str, dict] = {}
        self._init_agent('system')

    def _init_agent(self, agent_id: str) -> None:
        """Initialize a known agent."""
        if agent_id not in self._agents:
            self._agents[agent_id] = {
                'id': agent_id,
                'name': agent_id.replace('_', ' ').title(),
                'status': 'active',
                'last_seen': datetime.now().isoformat(),
                'action_count': 0,
            }

    def _record_action(self, agent_id: str, action_type: str,
                       target_type: str, target_id: int = None,
                       details: dict = None) -> int:
        """Record an agent action in the audit log."""
        self._init_agent(agent_id)
        action = {
            'agent_id': agent_id,
            'action_type': action_type,
            'target_type': target_type,
            'target_id': target_id,
            'status': 'completed',
            'details': details or {},
            'started_at': datetime.now().isoformat(),
            'completed_at': datetime.now().isoformat(),
        }
        action_id = self.state.create_agent_action(action)
        self._agents[agent_id]['action_count'] += 1
        self._agents[agent_id]['last_seen'] = datetime.now().isoformat()
        return action_id

    # --- Knowledge queries ---

    def query_graph(self, entity_type: str = None,
                    entity_id: str = None,
                    relationship_type: str = None) -> dict:
        """Query the knowledge graph."""
        result = {
            'query': {
                'entity_type': entity_type,
                'entity_id': entity_id,
                'relationship_type': relationship_type,
            },
            'entities': [],
            'relationships': [],
            'summary': self.kgm.get_graph_summary(),
        }

        # Get entities
        if entity_type and entity_id:
            entity = self.kgm.get_entity(entity_type, entity_id)
            if entity:
                result['entities'].append(entity)
        elif entity_type:
            entities = self.kgm.list_entities(entity_type=entity_type)
            result['entities'].extend(entities)
        else:
            entities = self.kgm.list_entities()
            result['entities'].extend(entities)

        # Get relationships
        if relationship_type:
            rels = self.kgm.get_relationships(relationship_type=relationship_type)
            result['relationships'].extend(rels)
        elif entity_type and entity_id:
            neighbors = self.kgm.get_neighbors(entity_type, entity_id)
            result['relationships'].extend(neighbors)
        else:
            rels = self.kgm.get_relationships()
            result['relationships'].extend(rels)

        return result

    def search_knowledge(self, query: str,
                         entity_type: str = None) -> dict:
        """Search knowledge base for entities matching a query."""
        results = self.kgm.search_entities(query, entity_type)
        return {
            'query': query,
            'entity_type': entity_type,
            'results': results,
            'count': len(results),
        }

    def get_wiki_document(self, slug: str) -> Optional[dict]:
        """Get a wiki document by slug."""
        return self.writer.get_document_by_slug(slug)

    def list_wiki_documents(self, category: str = None) -> List[dict]:
        """List wiki documents, optionally filtered by category."""
        return self.writer.get_generated_docs(category)

    # --- Service actions ---

    def request_discovery(self) -> dict:
        """Request a full discovery run."""
        action_id = self._record_action('agent', 'discovery', 'system')
        result = self.pipeline.run()
        self._record_action('agent', 'discovery_complete', 'system',
                          details={'servers': len(result.get('stages', {}).get('discover', {}).get('servers', []))})
        return result

    def request_verification(self) -> dict:
        """Request service verification."""
        action_id = self._record_action('agent', 'verification', 'system')
        result = self.pipeline.run()
        self._record_action('agent', 'verification_complete', 'system',
                          details={'services_checked': result.get('stages', {}).get('verify', {}).get('total', 0)})
        return result

    def request_health_report(self) -> dict:
        """Request a health report."""
        action_id = self._record_action('agent', 'health_report', 'system')
        report = self.verifier.generate_health_report()
        return report

    def get_alerts(self) -> List[dict]:
        """Get current alerts."""
        report = self.verifier.generate_health_report()
        return self.verifier.check_alerts(report)

    # --- User requests ---

    def submit_request(self, user_id: str, request_type: str,
                       title: str, description: str = None) -> dict:
        """Submit a user request."""
        request = {
            'user_id': user_id,
            'request_type': request_type,
            'title': title,
            'description': description or '',
        }
        request_id = self.state.create_user_request(request)
        return {
            'id': request_id,
            'status': 'pending',
            'user_id': user_id,
            'request_type': request_type,
            'title': title,
        }

    def get_user_requests(self, user_id: str = None,
                          status: str = None) -> List[dict]:
        """Get user requests, optionally filtered."""
        return self.state.get_user_requests(status=status)

    def update_request_status(self, request_id: int,
                              status: str,
                              details: dict = None) -> bool:
        """Update a user request's status."""
        return self.state.update_user_request(request_id, status, details)

    # --- Agent management ---

    def register_agent(self, agent_id: str,
                       name: str = None) -> dict:
        """Register a new agent."""
        self._init_agent(agent_id)
        if name:
            self._agents[agent_id]['name'] = name
        return self._agents[agent_id]

    def get_agent_info(self, agent_id: str) -> Optional[dict]:
        """Get information about an agent."""
        return self._agents.get(agent_id)

    def list_agents(self) -> List[dict]:
        """List all registered agents."""
        return list(self._agents.values())

    def get_agent_actions(self, agent_id: str = None,
                          status: str = None,
                          action_type: str = None) -> List[dict]:
        """Get agent actions, optionally filtered."""
        return self.state.get_agent_actions(status=status, type=action_type)

    # --- Knowledge graph operations ---

    def create_entity(self, entity_type: str, entity_id: str,
                      properties: dict,
                      source: str = 'agent') -> int:
        """Create or update an entity in the knowledge graph."""
        eid = self.kgm.upsert_entity(entity_type, entity_id, properties, source)
        self._record_action('agent', 'create_entity', entity_type,
                          details={'entity_id': entity_id})
        return eid

    def create_relationship(self, source_type: str, source_id: str,
                            target_type: str, target_id: str,
                            rel_type: str,
                            properties: dict = None) -> int:
        """Create a relationship between entities."""
        rid = self.kgm.create_relationship(
            source_type, source_id, target_type, target_id, rel_type, properties)
        self._record_action('agent', 'create_relationship', 'relationship',
                          details={'source': f'{source_type}:{source_id}',
                                   'target': f'{target_type}:{target_id}',
                                   'type': rel_type})
        return rid

    def delete_entity(self, entity_type: str, entity_id: str) -> bool:
        """Delete an entity from the knowledge graph."""
        result = self.kgm.delete_entity(entity_type, entity_id)
        self._record_action('agent', 'delete_entity', entity_type,
                          details={'entity_id': entity_id})
        return result

    # --- System status ---

    def get_system_status(self) -> dict:
        """Get comprehensive system status."""
        return {
            'timestamp': datetime.now().isoformat(),
            'agents': {
                'total': len(self._agents),
                'list': self.list_agents(),
            },
            'knowledge_graph': self.kgm.get_graph_summary(),
            'servers': {
                'total': len(self.state.list_servers()),
                'up': sum(1 for s in self.state.list_servers() if s.get('status') == 'up'),
                'down': sum(1 for s in self.state.list_servers() if s.get('status') == 'down'),
            },
            'containers': {
                'total': len(self.state.list_containers()),
                'running': sum(1 for c in self.state.list_containers() if c.get('status') == 'running'),
                'stopped': sum(1 for c in self.state.list_containers() if c.get('status') == 'stopped'),
            },
            'services': {
                'total': len(self.state.list_services()),
                'up': sum(1 for s in self.state.list_services() if s.get('status') == 'up'),
                'down': sum(1 for s in self.state.list_services() if s.get('status') == 'down'),
            },
            'wiki_documents': {
                'total': len(self.writer.get_generated_docs()),
            },
            'alerts': self.get_alerts(),
        }


class KnowledgeAgentResponse:
    """Standardized response format for agent interactions."""

    def __init__(self, success: bool, data: dict = None,
                 error: str = None, agent_id: str = None) -> None:
        self.success = success
        self.data = data or {}
        self.error = error
        self.agent_id = agent_id
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'agent_id': self.agent_id,
            'timestamp': self.timestamp,
        }

    @classmethod
    def success_response(cls, data: dict = None,
                         agent_id: str = None) -> 'KnowledgeAgentResponse':
        return cls(success=True, data=data, agent_id=agent_id)

    @classmethod
    def error_response(cls, error: str,
                       agent_id: str = None) -> 'KnowledgeAgentResponse':
        return cls(success=False, data={}, error=error, agent_id=agent_id)
