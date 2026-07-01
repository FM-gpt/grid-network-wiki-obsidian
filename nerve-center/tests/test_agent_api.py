#!/usr/bin/env python3
"""Tests for nerve-center/agent_api.py."""
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from state import StateManager
from agent_api import NerveCenterAgentApp, AgentAPIHandler, AgentAPIServer


class TestNerveCenterAgentApp(unittest.TestCase):
    def setUp(self):
        self.db_path = tempfile.mktemp(suffix='.db')
        self.app = NerveCenterAgentApp(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    # --- Initialization ---

    def test_init_with_db_path(self):
        self.assertIsNotNone(self.app.agent)
        self.assertIsNotNone(self.app.agent.state)
        self.assertEqual(self.app.db_path, self.db_path)

    def test_init_with_config(self):
        config = {
            'proxmox': {
                'api_url': 'https://10.10.30.22:8006/api2/json',
                'api_user': 'root@pam',
                'api_token_name': 'test-token',
                'api_token_secret': 'test-secret',
            }
        }
        app = NerveCenterAgentApp(self.db_path, config)
        self.assertIsNotNone(app.agent.pipeline.discoverer)

    def test_init_default_config(self):
        app = NerveCenterAgentApp(self.db_path)
        self.assertEqual(app.config, {})

    # --- Discovery ---

    def test_run_discovery(self):
        result = self.app.run_discovery()
        self.assertIn('stages', result)
        self.assertIn('discover', result['stages'])

    def test_run_discovery_no_discoverer(self):
        # Without proxmox config, discoverer is None
        # Pipeline should handle this gracefully
        result = self.app.run_discovery()
        self.assertIn('stages', result)

    def test_run_verification(self):
        result = self.app.run_verification()
        self.assertIn('stages', result)
        self.assertIn('verify', result['stages'])

    def test_get_health_report(self):
        report = self.app.get_health_report()
        self.assertIn('generated_at', report)

    def test_get_alerts(self):
        alerts = self.app.get_alerts()
        self.assertIsInstance(alerts, list)

    # --- Knowledge queries ---

    def test_query_graph_all(self):
        result = self.app.query_graph()
        self.assertIn('entities', result)
        self.assertIn('relationships', result)
        self.assertIn('summary', result)

    def test_query_graph_by_type(self):
        result = self.app.query_graph(entity_type='server')
        self.assertIn('entities', result)

    def test_query_graph_by_type_and_id(self):
        result = self.app.query_graph(entity_type='server', entity_id='grid-pve')
        self.assertIn('entities', result)

    def test_search_knowledge(self):
        result = self.app.search_knowledge('grid-pve')
        self.assertIn('results', result)
        self.assertIn('count', result)

    def test_search_knowledge_filtered(self):
        result = self.app.search_knowledge('grid-pve', entity_type='server')
        self.assertIn('results', result)

    def test_get_wiki_document(self):
        doc = self.app.get_wiki_document('nonexistent')
        self.assertIsNone(doc)

    def test_list_wiki_documents(self):
        docs = self.app.list_wiki_documents()
        self.assertIsInstance(docs, list)

    def test_list_wiki_documents_filtered(self):
        docs = self.app.list_wiki_documents(category='server')
        self.assertIsInstance(docs, list)

    # --- User requests ---

    def test_submit_request(self):
        result = self.app.submit_request('user-1', 'discovery', 'Test request')
        self.assertIn('id', result)
        self.assertEqual(result['status'], 'pending')
        self.assertEqual(result['user_id'], 'user-1')

    def test_get_user_requests(self):
        self.app.submit_request('user-1', 'discovery', 'Test request')
        requests = self.app.get_user_requests(user_id='user-1')
        self.assertEqual(len(requests), 1)

    def test_get_user_requests_filtered(self):
        self.app.submit_request('user-1', 'discovery', 'Test request')
        requests = self.app.get_user_requests(status='pending')
        self.assertEqual(len(requests), 1)

    def test_update_request_status(self):
        req_id = self.app.submit_request('user-1', 'discovery', 'Test request')['id']
        result = self.app.update_request_status(req_id, 'completed')
        self.assertTrue(result)

    # --- Agent management ---

    def test_register_agent(self):
        result = self.app.register_agent('test-agent', 'Test Agent')
        self.assertEqual(result['id'], 'test-agent')
        self.assertEqual(result['name'], 'Test Agent')
        self.assertEqual(result['status'], 'active')

    def test_get_agent_info(self):
        info = self.app.get_agent_info('system')
        self.assertIsNotNone(info)
        self.assertEqual(info['id'], 'system')

    def test_get_agent_info_not_found(self):
        info = self.app.get_agent_info('nonexistent')
        self.assertIsNone(info)

    def test_list_agents(self):
        self.app.register_agent('agent-1')
        self.app.register_agent('agent-2')
        agents = self.app.list_agents()
        self.assertGreaterEqual(len(agents), 3)  # system + 2 new

    def test_get_agent_actions(self):
        # First create an action by doing something
        self.app.create_entity('server', 'test-server', {'ip': '10.0.0.1'})
        actions = self.app.get_agent_actions()
        self.assertIsInstance(actions, list)

    # --- Knowledge graph operations ---

    def test_create_entity(self):
        eid = self.app.create_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        self.assertIsNotNone(eid)
        self.assertGreater(eid, 0)

    def test_create_relationship(self):
        self.app.create_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        self.app.create_entity('service', 'prometheus', {'port': 9090})
        rid = self.app.create_relationship(
            'server', 'grid-pve', 'service', 'prometheus', 'hosts')
        self.assertIsNotNone(rid)
        self.assertGreater(rid, 0)

    def test_delete_entity(self):
        self.app.create_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        result = self.app.delete_entity('server', 'grid-pve')
        self.assertTrue(result)

    # --- System status ---

    def test_get_system_status(self):
        status = self.app.get_system_status()
        self.assertIn('timestamp', status)
        self.assertIn('agents', status)
        self.assertIn('knowledge_graph', status)
        self.assertIn('servers', status)
        self.assertIn('containers', status)
        self.assertIn('services', status)
        self.assertIn('wiki_documents', status)
        self.assertIn('alerts', status)

    def test_system_status_reflects_state(self):
        self.app.create_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        status = self.app.get_system_status()
        self.assertGreater(status['knowledge_graph']['total_entities'], 0)


class TestAgentAPIServer(unittest.TestCase):
    def setUp(self):
        self.db_path = tempfile.mktemp(suffix='.db')
        self.server = AgentAPIServer(self.db_path, host='127.0.0.1', port=18766)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_init(self):
        self.assertEqual(self.server.host, '127.0.0.1')
        self.assertEqual(self.server.port, 18766)
        self.assertIsNone(self.server.server)

    def test_get_status(self):
        status = self.server.get_status()
        self.assertEqual(status['host'], '127.0.0.1')
        self.assertEqual(status['port'], 18766)
        self.assertEqual(status['db_path'], self.db_path)


if __name__ == '__main__':
    unittest.main()
