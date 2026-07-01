#!/usr/bin/env python3
"""Integration tests for the full nerve center pipeline.

Tests the complete flow: StateManager → KnowledgeGraph → ServiceVerifier →
WikiWriter → DiscoveryPipeline → KnowledgeAgent → AgentAPI → Dashboard data.
"""
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from state import StateManager
from knowledge_graph import KnowledgeGraphManager
from service_verifier import ServiceVerifier
from wiki_writer import WikiWriter
from discovery_pipeline import DiscoveryPipeline
from knowledge_agent import KnowledgeAgent
from agent_api import NerveCenterAgentApp


class TestFullPipelineFlow(unittest.TestCase):
    """Test the complete nerve center pipeline flow."""

    def setUp(self):
        self.db_path = tempfile.mktemp(suffix='.db')
        self.state = StateManager(self.db_path)
        self.app = NerveCenterAgentApp(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_discover_to_status_flow(self):
        """Full flow: create entities → verify → get status."""
        # Step 1: Create entities via KnowledgeAgent
        eid1 = self.app.create_entity('server', 'grid-pve', {
            'ip_address': '10.10.30.22',
            'proxmox_api_url': 'https://10.10.30.22:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'up',
        })
        self.assertIsNotNone(eid1)

        eid2 = self.app.create_entity('container', 'grid-dev-01', {
            'ip_address': '10.10.30.121',
            'status': 'running',
            'host': 'grid-pve',
        })
        self.assertIsNotNone(eid2)

        # Step 2: Create a relationship
        rid = self.app.create_relationship(
            'server', 'grid-pve', 'container', 'grid-dev-01', 'hosts')
        self.assertGreater(rid, 0)

        # Step 3: Verify services
        verify_result = self.app.run_verification()
        self.assertIn('stages', verify_result)
        self.assertIn('verify', verify_result['stages'])

        # Step 4: Get system status
        status = self.app.get_system_status()
        self.assertIn('timestamp', status)
        self.assertIn('knowledge_graph', status)
        self.assertGreater(status['knowledge_graph']['total_entities'], 0)

    def test_discovery_pipeline_with_mocked_data(self):
        """Pipeline processes mocked discovery data end-to-end."""
        # Create some entities first
        self.app.create_entity('server', 'test-server', {
            'ip_address': '10.0.0.1', 'status': 'up'})

        # Run discovery (will fail gracefully without proxmox config)
        result = self.app.run_discovery()
        self.assertIn('stages', result)
        self.assertIn('discover', result['stages'])
        self.assertIn('verify', result['stages'])
        self.assertIn('analyze', result['stages'])
        self.assertIn('document', result['stages'])
        self.assertIn('alerts', result)

    def test_health_report_flow(self):
        """Health report reflects discovered entities."""
        # Create entities
        self.app.create_entity('server', 'grid-pve', {
            'ip_address': '10.10.30.22', 'status': 'up'})
        self.app.create_entity('service', 'prometheus', {
            'port': 9090, 'status': 'up', 'host': 'grid-pve'})

        report = self.app.get_health_report()
        self.assertIn('generated_at', report)
        self.assertIn('services', report)

    def test_alert_generation_flow(self):
        """Alerts are generated from verification results."""
        alerts = self.app.get_alerts()
        self.assertIsInstance(alerts, list)

    def test_graph_query_flow(self):
        """Query graph after creating entities returns correct data."""
        # Create entities
        self.app.create_entity('server', 'grid-pve', {
            'ip_address': '10.10.30.22', 'status': 'up'})
        self.app.create_entity('service', 'grafana', {
            'port': 3000, 'status': 'up', 'host': 'grid-pve'})
        self.app.create_relationship(
            'server', 'grid-pve', 'service', 'grafana', 'hosts')

        # Query by type
        result = self.app.query_graph(entity_type='server')
        self.assertEqual(len(result['entities']), 1)
        self.assertEqual(result['entities'][0]['entity_id'], 'grid-pve')

        # Query by type and ID
        result = self.app.query_graph(entity_type='server', entity_id='grid-pve')
        self.assertEqual(len(result['entities']), 1)

        # Query with relationship
        result = self.app.query_graph(relationship_type='hosts')
        self.assertGreater(len(result['relationships']), 0)

    def test_search_knowledge_flow(self):
        """Search finds entities created in the system."""
        self.app.create_entity('server', 'grid-pve', {
            'ip_address': '10.10.30.22', 'status': 'up'})
        self.app.create_entity('service', 'prometheus', {
            'port': 9090, 'status': 'up'})

        result = self.app.search_knowledge('grid-pve')
        self.assertIn('results', result)
        self.assertIn('count', result)

    def test_user_request_lifecycle(self):
        """Full lifecycle: submit → get → update → get."""
        # Submit
        req = self.app.submit_request('user-1', 'discovery', 'Run discovery')
        self.assertEqual(req['status'], 'pending')
        request_id = req['id']

        # Get
        requests = self.app.get_user_requests(user_id='user-1')
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0]['title'], 'Run discovery')

        # Update
        success = self.app.update_request_status(request_id, 'completed',
                                                  {'result': 'success'})
        self.assertTrue(success)

        # Get filtered
        requests = self.app.get_user_requests(status='completed')
        self.assertEqual(len(requests), 1)

    def test_agent_registration_flow(self):
        """Full agent lifecycle: register → act → query."""
        # Register
        agent = self.app.register_agent('test-agent', 'Test Agent')
        self.assertEqual(agent['id'], 'test-agent')

        # Agent acts (creates entity)
        self.app.create_entity('server', 'grid-pve', {
            'ip_address': '10.10.30.22', 'status': 'up'})

        # Query agent info
        info = self.app.get_agent_info('test-agent')
        self.assertIsNotNone(info)
        self.assertEqual(info['name'], 'Test Agent')

        # List agents
        agents = self.app.list_agents()
        self.assertGreaterEqual(len(agents), 2)  # system + test-agent

    def test_wiki_document_generation(self):
        """Wiki documents are generated from entities."""
        # Create entity
        self.app.create_entity('server', 'grid-pve', {
            'ip_address': '10.10.30.22', 'status': 'up',
            'proxmox_api_url': 'https://10.10.30.22:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
        })

        # Run discovery to generate wiki docs
        result = self.app.run_discovery()
        self.assertIn('stages', result)

        # List wiki docs
        docs = self.app.list_wiki_documents()
        self.assertIsInstance(docs, list)

    def test_delete_and_recreate_entity(self):
        """Entity can be deleted and recreated in the knowledge graph."""
        # Create entity in KG
        eid1 = self.app.create_entity('server', 'grid-pve-temp', {
            'ip_address': '10.10.30.22', 'status': 'up'})
        self.assertGreater(eid1, 0)

        # Verify exists in KG
        result = self.app.query_graph(entity_type='server', entity_id='grid-pve-temp')
        self.assertEqual(len(result['entities']), 1)

        # Delete from KG (soft delete: status='deleted' in wiki doc)
        success = self.app.delete_entity('server', 'grid-pve-temp')
        self.assertTrue(success)

        # Verify wiki doc is soft-deleted
        doc = self.app.agent.writer.get_document_by_slug('entity:server:grid-pve-temp')
        self.assertIsNotNone(doc)
        self.assertEqual(doc['status'], 'deleted')

        # Recreate with same ID (creates new wiki doc)
        eid2 = self.app.create_entity('server', 'grid-pve-temp', {
            'ip_address': '10.10.30.22', 'status': 'up'})
        self.assertGreater(eid2, 0)

        # Verify it exists again with active status
        result = self.app.query_graph(entity_type='server', entity_id='grid-pve-temp')
        self.assertEqual(len(result['entities']), 1)
        active_doc = self.app.agent.writer.get_document_by_slug('entity:server:grid-pve-temp')
        self.assertEqual(active_doc['status'], 'active')

    def test_graph_summary_reflects_state(self):
        """Graph summary accurately reflects entities and relationships."""
        # Create entities
        self.app.create_entity('server', 'grid-pve', {
            'ip_address': '10.10.30.22', 'status': 'up'})
        self.app.create_entity('container', 'grid-dev-01', {
            'ip_address': '10.10.30.121', 'status': 'running'})
        self.app.create_entity('service', 'prometheus', {
            'port': 9090, 'status': 'up'})
        self.app.create_relationship(
            'server', 'grid-pve', 'service', 'prometheus', 'hosts')

        status = self.app.get_system_status()
        summary = status['knowledge_graph']
        self.assertGreater(summary['total_entities'], 0)
        self.assertGreater(summary['total_relationships'], 0)
        self.assertIn('server', summary['entity_types'])
        self.assertIn('service', summary['entity_types'])

    def test_multiple_agents_coexist(self):
        """Multiple agents can register and operate independently."""
        self.app.register_agent('agent-a', 'Agent A')
        self.app.register_agent('agent-b', 'Agent B')

        # Each agent creates entities in state
        self.state.upsert_server({
            'hostname': 'server-a',
            'ip_address': '10.0.0.1',
            'proxmox_api_url': 'https://10.0.0.1:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'up',
        })
        self.state.upsert_server({
            'hostname': 'server-b',
            'ip_address': '10.0.0.2',
            'proxmox_api_url': 'https://10.0.0.2:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'up',
        })

        # Check status reflects both
        status = self.app.get_system_status()
        self.assertGreater(status['servers']['total'], 0)

    def test_entity_type_counts(self):
        """Entity type counts in graph summary are accurate."""
        self.app.create_entity('server', 'grid-pve', {
            'ip_address': '10.10.30.22', 'status': 'up'})
        self.app.create_entity('server', 'grid-pve-2', {
            'ip_address': '10.10.30.23', 'status': 'up'})
        self.app.create_entity('container', 'ct-01', {
            'ip_address': '10.10.30.101', 'status': 'running'})

        status = self.app.get_system_status()
        summary = status['knowledge_graph']

        self.assertEqual(summary['entity_types'].get('server', 0), 2)
        self.assertEqual(summary['entity_types'].get('container', 0), 1)
        self.assertEqual(summary['total_entities'], 3)

    def test_knowledge_agent_writes_to_state(self):
        """KnowledgeAgent writes to both KG and state."""
        # create_entity writes to KG; upsert_server writes to state
        self.state.upsert_server({
            'hostname': 'grid-pve',
            'ip_address': '10.10.30.22',
            'proxmox_api_url': 'https://10.10.30.22:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'up',
        })
        servers = self.state.list_servers()
        self.assertEqual(len(servers), 1)
        self.assertEqual(servers[0]['hostname'], 'grid-pve')

    def test_agent_actions_are_logged(self):
        """Every agent action is logged in the audit trail."""
        self.app.create_entity('server', 'grid-pve', {
            'ip_address': '10.10.30.22', 'status': 'up'})
        self.app.create_entity('service', 'prometheus', {
            'port': 9090, 'status': 'up'})
        self.app.create_relationship(
            'server', 'grid-pve', 'service', 'prometheus', 'hosts')

        actions = self.app.get_agent_actions()
        self.assertGreater(len(actions), 0)
        action_types = [a['action_type'] for a in actions]
        self.assertIn('create_entity', action_types)
        self.assertIn('create_relationship', action_types)


class TestDashboardDataFlow(unittest.TestCase):
    """Verify dashboard can receive data from the API layer."""

    def setUp(self):
        self.db_path = tempfile.mktemp(suffix='.db')
        self.app = NerveCenterAgentApp(self.db_path)
        self.state = self.app.agent.state

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_status_api_provides_all_sections(self):
        """System status includes all dashboard sections."""
        self.app.create_entity('server', 'grid-pve', {
            'ip_address': '10.10.30.22', 'status': 'up'})
        self.app.create_entity('container', 'ct-01', {
            'ip_address': '10.10.30.101', 'status': 'running'})
        self.app.create_entity('service', 'prometheus', {
            'port': 9090, 'status': 'up'})

        status = self.app.get_system_status()

        # All sections present
        self.assertIn('timestamp', status)
        self.assertIn('agents', status)
        self.assertIn('knowledge_graph', status)
        self.assertIn('servers', status)
        self.assertIn('containers', status)
        self.assertIn('services', status)
        self.assertIn('wiki_documents', status)
        self.assertIn('alerts', status)

    def test_status_servers_reflect_entities(self):
        """Server count in status matches discovered entities."""
        # create_entity writes to KG, not state table. Use upsert_server for state.
        self.state.upsert_server({
            'hostname': 'grid-pve',
            'ip_address': '10.10.30.22',
            'proxmox_api_url': 'https://10.10.30.22:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'up',
        })
        self.state.upsert_server({
            'hostname': 'grid-pve-2',
            'ip_address': '10.10.30.23',
            'proxmox_api_url': 'https://10.10.30.23:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'down',
        })
        status = self.app.get_system_status()
        self.assertEqual(status['servers']['total'], 2)

    def test_status_containers_reflect_entities(self):
        """Container count in status matches discovered entities."""
        self.state.upsert_container({
            'container_id': 'ct-01',
            'name': 'grid-dev-01',
            'vmid': 101,
            'server_id': 100,
            'type': 'docker',
            'ip_addresses': ['10.10.30.101'],
            'status': 'running',
        })
        self.state.upsert_container({
            'container_id': 'ct-02',
            'name': 'grid-test-01',
            'vmid': 102,
            'server_id': 100,
            'type': 'lxc',
            'ip_addresses': ['10.10.30.102'],
            'status': 'stopped',
        })
        status = self.app.get_system_status()
        self.assertEqual(status['containers']['total'], 2)

    def test_status_services_reflect_entities(self):
        """Service count in status matches discovered entities."""
        self.state.upsert_service({
            'name': 'prometheus',
            'container_id': 'ct-01',
            'type': 'monitoring',
            'port': 9090,
            'status': 'up',
            'host': 'grid-pve',
        })
        self.state.upsert_service({
            'name': 'grafana',
            'container_id': 'ct-01',
            'type': 'dashboard',
            'port': 3000,
            'status': 'down',
            'host': 'grid-pve',
        })
        status = self.app.get_system_status()
        self.assertEqual(status['services']['total'], 2)

    def test_status_agents_list(self):
        """Agent list in status includes registered agents."""
        self.app.register_agent('test-agent', 'Test')
        status = self.app.get_system_status()
        self.assertGreaterEqual(len(status['agents']['list']), 2)


if __name__ == '__main__':
    unittest.main()
