#!/usr/bin/env python3
"""Tests for nerve-center/knowledge_agent.py."""
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from state import StateManager
from knowledge_agent import KnowledgeAgent, KnowledgeAgentResponse


class TestKnowledgeAgent(unittest.TestCase):
    def setUp(self):
        self.db_path = tempfile.mktemp(suffix='.db')
        self.state = StateManager(self.db_path)
        self.agent = KnowledgeAgent(self.state)

    def tearDown(self):
        self.agent.pipeline.stop()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    # --- Initialization ---

    def test_init_with_state(self):
        self.assertIsNotNone(self.agent.state)
        self.assertIsNotNone(self.agent.kgm)
        self.assertIsNotNone(self.agent.writer)
        self.assertIsNotNone(self.agent.verifier)
        self.assertIsNotNone(self.agent.pipeline)

    def test_init_creates_system_agent(self):
        self.assertIn('system', self.agent._agents)
        self.assertEqual(self.agent._agents['system']['status'], 'active')

    def test_init_with_config(self):
        config = {
            'proxmox': {
                'api_url': 'https://10.10.30.22:8006/api2/json',
                'api_user': 'root@pam',
                'api_token_name': 'test-token',
                'api_token_secret': 'test-secret',
            }
        }
        agent = KnowledgeAgent(self.state, config)
        self.assertIsNotNone(agent.pipeline.discoverer)

    # --- Agent management ---

    def test_register_agent(self):
        result = self.agent.register_agent('test-agent', 'Test Agent')
        self.assertEqual(result['id'], 'test-agent')
        self.assertEqual(result['name'], 'Test Agent')
        self.assertEqual(result['status'], 'active')

    def test_get_agent_info(self):
        info = self.agent.get_agent_info('system')
        self.assertIsNotNone(info)
        self.assertEqual(info['id'], 'system')

    def test_get_agent_info_not_found(self):
        info = self.agent.get_agent_info('nonexistent')
        self.assertIsNone(info)

    def test_list_agents(self):
        self.agent.register_agent('agent-1')
        self.agent.register_agent('agent-2')
        agents = self.agent.list_agents()
        self.assertEqual(len(agents), 3)  # system + 2 new

    def test_agent_action_count_increases(self):
        # First call creates the 'agent' entry
        self.agent.create_entity('server', 'grid-pve-1', {'ip': '10.10.30.23'})
        initial_count = self.agent._agents['agent']['action_count']
        # Second call should increase it
        self.agent.create_entity('server', 'grid-pve-2', {'ip': '10.10.30.24'})
        new_count = self.agent._agents['agent']['action_count']
        self.assertGreater(new_count, initial_count)

    # --- Knowledge queries ---

    def test_query_graph_all_entities(self):
        result = self.agent.query_graph()
        self.assertIn('entities', result)
        self.assertIn('relationships', result)
        self.assertIn('summary', result)

    def test_query_graph_by_type(self):
        result = self.agent.query_graph(entity_type='server')
        self.assertIn('entities', result)

    def test_query_graph_by_type_and_id(self):
        result = self.agent.query_graph(entity_type='server', entity_id='grid-pve')
        self.assertIn('entities', result)

    def test_query_graph_with_relationship(self):
        result = self.agent.query_graph(relationship_type='hosts')
        self.assertIn('relationships', result)

    def test_search_knowledge(self):
        result = self.agent.search_knowledge('grid-pve')
        self.assertIn('results', result)
        self.assertIn('count', result)

    def test_search_knowledge_filtered(self):
        result = self.agent.search_knowledge('grid-pve', entity_type='server')
        self.assertIn('results', result)

    def test_get_wiki_document(self):
        doc = self.agent.get_wiki_document('nonexistent')
        self.assertIsNone(doc)

    def test_list_wiki_documents(self):
        docs = self.agent.list_wiki_documents()
        self.assertIsInstance(docs, list)

    def test_list_wiki_documents_filtered(self):
        docs = self.agent.list_wiki_documents(category='server')
        self.assertIsInstance(docs, list)

    # --- Service actions ---

    def test_request_discovery(self):
        result = self.agent.request_discovery()
        self.assertIn('stages', result)
        self.assertIn('discover', result['stages'])

    def test_request_verification(self):
        result = self.agent.request_verification()
        self.assertIn('stages', result)
        self.assertIn('verify', result['stages'])

    def test_request_health_report(self):
        result = self.agent.request_health_report()
        self.assertIn('generated_at', result)

    def test_get_alerts(self):
        alerts = self.agent.get_alerts()
        self.assertIsInstance(alerts, list)

    # --- User requests ---

    def test_submit_request(self):
        result = self.agent.submit_request(
            'user-1', 'discovery', 'Run discovery')
        self.assertIn('id', result)
        self.assertEqual(result['status'], 'pending')
        self.assertEqual(result['user_id'], 'user-1')

    def test_get_user_requests(self):
        self.agent.submit_request('user-1', 'discovery', 'Test request')
        requests = self.agent.get_user_requests(user_id='user-1')
        self.assertEqual(len(requests), 1)

    def test_get_user_requests_filtered(self):
        self.agent.submit_request('user-1', 'discovery', 'Test request')
        requests = self.agent.get_user_requests(status='pending')
        self.assertEqual(len(requests), 1)

    def test_update_request_status(self):
        req_id = self.agent.submit_request(
            'user-1', 'discovery', 'Test request')['id']
        result = self.agent.update_request_status(req_id, 'completed')
        self.assertTrue(result)

    # --- Knowledge graph operations ---

    def test_create_entity(self):
        eid = self.agent.create_entity('server', 'grid-pve',
                                       {'ip': '10.10.30.22'})
        self.assertIsNotNone(eid)
        self.assertGreater(eid, 0)

    def test_create_relationship(self):
        self.agent.create_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        self.agent.create_entity('service', 'prometheus', {'port': 9090})
        rid = self.agent.create_relationship(
            'server', 'grid-pve', 'service', 'prometheus', 'hosts')
        self.assertIsNotNone(rid)
        self.assertGreater(rid, 0)

    def test_delete_entity(self):
        self.agent.create_entity('server', 'grid-pve', {'ip': '10.10.30.22'})
        result = self.agent.delete_entity('server', 'grid-pve')
        self.assertTrue(result)

    # --- System status ---

    def test_get_system_status(self):
        status = self.agent.get_system_status()
        self.assertIn('timestamp', status)
        self.assertIn('agents', status)
        self.assertIn('knowledge_graph', status)
        self.assertIn('servers', status)
        self.assertIn('containers', status)
        self.assertIn('services', status)
        self.assertIn('wiki_documents', status)
        self.assertIn('alerts', status)

    def test_system_status_reflects_state(self):
        self.state.upsert_server({
            'hostname': 'grid-pve',
            'ip_address': '10.10.30.22',
            'proxmox_api_url': 'https://10.10.30.22:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'up',
        })
        status = self.agent.get_system_status()
        self.assertEqual(status['servers']['total'], 1)


class TestKnowledgeAgentResponse(unittest.TestCase):
    def test_success_response(self):
        resp = KnowledgeAgentResponse.success_response({'key': 'value'}, 'agent-1')
        self.assertTrue(resp.success)
        self.assertEqual(resp.data['key'], 'value')
        self.assertEqual(resp.agent_id, 'agent-1')
        self.assertIsNone(resp.error)

    def test_error_response(self):
        resp = KnowledgeAgentResponse.error_response('fail', 'agent-1')
        self.assertFalse(resp.success)
        self.assertEqual(resp.error, 'fail')
        self.assertEqual(resp.agent_id, 'agent-1')
        self.assertEqual(resp.data, {})

    def test_to_dict(self):
        resp = KnowledgeAgentResponse.success_response({'data': 123}, 'agent-1')
        d = resp.to_dict()
        self.assertTrue(d['success'])
        self.assertEqual(d['data'], {'data': 123})
        self.assertEqual(d['agent_id'], 'agent-1')
        self.assertIn('timestamp', d)

    def test_to_dict_error(self):
        resp = KnowledgeAgentResponse.error_response('fail', 'agent-1')
        d = resp.to_dict()
        self.assertFalse(d['success'])
        self.assertEqual(d['error'], 'fail')


if __name__ == '__main__':
    unittest.main()
