#!/usr/bin/env python3
"""Integration tests for nerve-center/state.py."""
import unittest
import json
import os
import sys
import tempfile
import shutil

# Add parent directory to path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from state import StateManager


class TestStateManager(unittest.TestCase):
    def setUp(self):
        self.db_path = tempfile.mktemp(suffix='.db')
        self.state = StateManager(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    # --- Servers ---

    def test_upsert_server_returns_id(self):
        server = {
            'hostname': 'test-server',
            'ip_address': '10.10.30.99',
            'proxmox_api_url': 'https://10.10.30.99:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'up',
        }
        sid = self.state.upsert_server(server)
        self.assertIsNotNone(sid)
        self.assertIsInstance(sid, int)
        self.assertGreater(sid, 0)

    def test_get_server(self):
        server = {
            'hostname': 'test-server',
            'ip_address': '10.10.30.99',
            'proxmox_api_url': 'https://10.10.30.99:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'up',
        }
        self.state.upsert_server(server)
        retrieved = self.state.get_server('test-server')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['hostname'], 'test-server')
        self.assertEqual(retrieved['status'], 'up')

    def test_get_server_not_found(self):
        retrieved = self.state.get_server('nonexistent')
        self.assertIsNone(retrieved)

    def test_upsert_server_updates(self):
        server = {
            'hostname': 'test-server',
            'ip_address': '10.10.30.99',
            'proxmox_api_url': 'https://10.10.30.99:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'up',
        }
        sid1 = self.state.upsert_server(server)
        server['status'] = 'down'
        server['ip_address'] = '10.10.30.100'
        sid2 = self.state.upsert_server(server)
        self.assertIsNotNone(sid2)
        retrieved = self.state.get_server('test-server')
        self.assertEqual(retrieved['status'], 'down')
        self.assertEqual(retrieved['ip_address'], '10.10.30.100')

    def test_list_servers(self):
        server1 = {
            'hostname': 'beta-server',
            'ip_address': '10.10.30.98',
            'proxmox_api_url': 'https://10.10.30.98:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'up',
        }
        server2 = {
            'hostname': 'alpha-server',
            'ip_address': '10.10.30.97',
            'proxmox_api_url': 'https://10.10.30.97:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'up',
        }
        self.state.upsert_server(server1)
        self.state.upsert_server(server2)
        servers = self.state.list_servers()
        self.assertEqual(len(servers), 2)
        self.assertEqual(servers[0]['hostname'], 'alpha-server')  # sorted by hostname

    # --- Containers ---

    def test_upsert_container_returns_id(self):
        server = {
            'hostname': 'test-server',
            'ip_address': '10.10.30.99',
            'proxmox_api_url': 'https://10.10.30.99:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'up',
        }
        sid = self.state.upsert_server(server)
        container = {
            'server_id': sid,
            'vmid': 9001,
            'name': 'test-container',
            'type': 'lxc',
            'status': 'running',
            'ip_addresses': ['10.10.30.91'],
            'memory_mb': 4096,
            'cpu_cores': 2,
            'disk_total_mb': 10240,
            'disk_used_mb': 2048,
            'os': 'Ubuntu 22.04',
            'template': 'ubuntu-22.04-standard',
        }
        cid = self.state.upsert_container(container)
        self.assertIsNotNone(cid)
        self.assertIsInstance(cid, int)
        self.assertGreater(cid, 0)

    def test_get_container(self):
        server = {
            'hostname': 'test-server',
            'ip_address': '10.10.30.99',
            'proxmox_api_url': 'https://10.10.30.99:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'up',
        }
        sid = self.state.upsert_server(server)
        container = {
            'server_id': sid,
            'vmid': 9001,
            'name': 'test-container',
            'type': 'lxc',
            'status': 'running',
            'ip_addresses': ['10.10.30.91'],
            'memory_mb': 4096,
            'cpu_cores': 2,
            'disk_total_mb': 10240,
            'disk_used_mb': 2048,
            'os': 'Ubuntu 22.04',
            'template': 'ubuntu-22.04-standard',
        }
        self.state.upsert_container(container)
        retrieved = self.state.get_container(9001)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['name'], 'test-container')
        self.assertEqual(retrieved['status'], 'running')

    def test_get_container_not_found(self):
        retrieved = self.state.get_container(9999)
        self.assertIsNone(retrieved)

    def test_list_containers_filtered(self):
        server = {
            'hostname': 'test-server',
            'ip_address': '10.10.30.99',
            'proxmox_api_url': 'https://10.10.30.99:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'up',
        }
        sid = self.state.upsert_server(server)
        container1 = {
            'server_id': sid, 'vmid': 9001, 'name': 'c1', 'type': 'lxc',
            'status': 'running', 'ip_addresses': ['10.10.30.91'],
            'memory_mb': 4096, 'cpu_cores': 2, 'disk_total_mb': 10240,
            'disk_used_mb': 2048, 'os': 'Ubuntu 22.04', 'template': 'ubuntu-22.04',
        }
        container2 = {
            'server_id': sid, 'vmid': 9002, 'name': 'c2', 'type': 'lxc',
            'status': 'stopped', 'ip_addresses': ['10.10.30.92'],
            'memory_mb': 2048, 'cpu_cores': 1, 'disk_total_mb': 5120,
            'disk_used_mb': 1024, 'os': 'Debian 12', 'template': 'debian-12',
        }
        self.state.upsert_container(container1)
        self.state.upsert_container(container2)
        containers = self.state.list_containers(server_id=sid)
        self.assertEqual(len(containers), 2)
        containers_stopped = self.state.list_containers(server_id=sid)
        self.assertEqual(len(containers_stopped), 2)

    # --- Services ---

    def test_upsert_service_returns_id(self):
        server = {
            'hostname': 'test-server',
            'ip_address': '10.10.30.99',
            'proxmox_api_url': 'https://10.10.30.99:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'up',
        }
        sid = self.state.upsert_server(server)
        container = {
            'server_id': sid, 'vmid': 9001, 'name': 'test-container',
            'type': 'lxc', 'status': 'running', 'ip_addresses': ['10.10.30.91'],
            'memory_mb': 4096, 'cpu_cores': 2, 'disk_total_mb': 10240,
            'disk_used_mb': 2048, 'os': 'Ubuntu 22.04', 'template': 'ubuntu-22.04',
        }
        cid = self.state.upsert_container(container)
        service = {
            'container_id': cid, 'name': 'test-service', 'type': 'http',
            'port': 8080, 'protocol': 'tcp', 'url': 'http://10.10.30.91:8080',
            'status': 'up', 'response_time_ms': 5,
            'last_checked': '2026-06-30T10:00:00',
            'prometheus_job': 'test-service',
            'prometheus_target': 'http://10.10.30.91:8080/metrics',
            'monitoring_configured': 1, 'caddy_configured': 1,
        }
        sid = self.state.upsert_service(service)
        self.assertIsNotNone(sid)
        self.assertIsInstance(sid, int)
        self.assertGreater(sid, 0)

    def test_get_service(self):
        server = {
            'hostname': 'test-server',
            'ip_address': '10.10.30.99',
            'proxmox_api_url': 'https://10.10.30.99:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'up',
        }
        sid_s = self.state.upsert_server(server)
        container = {
            'server_id': sid_s, 'vmid': 9001, 'name': 'test-container',
            'type': 'lxc', 'status': 'running', 'ip_addresses': ['10.10.30.91'],
            'memory_mb': 4096, 'cpu_cores': 2, 'disk_total_mb': 10240,
            'disk_used_mb': 2048, 'os': 'Ubuntu 22.04', 'template': 'ubuntu-22.04',
        }
        cid = self.state.upsert_container(container)
        service = {
            'container_id': cid, 'name': 'test-service', 'type': 'http',
            'port': 8080, 'protocol': 'tcp', 'url': 'http://10.10.30.91:8080',
            'status': 'up', 'response_time_ms': 5,
            'last_checked': '2026-06-30T10:00:00',
            'prometheus_job': 'test-service',
            'prometheus_target': 'http://10.10.30.91:8080/metrics',
            'monitoring_configured': 1, 'caddy_configured': 1,
        }
        svc_id = self.state.upsert_service(service)
        retrieved = self.state.get_service(svc_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['name'], 'test-service')
        self.assertEqual(retrieved['status'], 'up')

    def test_update_service_status(self):
        server = {
            'hostname': 'test-server',
            'ip_address': '10.10.30.99',
            'proxmox_api_url': 'https://10.10.30.99:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'up',
        }
        sid_s = self.state.upsert_server(server)
        container = {
            'server_id': sid_s, 'vmid': 9001, 'name': 'test-container',
            'type': 'lxc', 'status': 'running', 'ip_addresses': ['10.10.30.91'],
            'memory_mb': 4096, 'cpu_cores': 2, 'disk_total_mb': 10240,
            'disk_used_mb': 2048, 'os': 'Ubuntu 22.04', 'template': 'ubuntu-22.04',
        }
        cid = self.state.upsert_container(container)
        service = {
            'container_id': cid, 'name': 'test-service', 'type': 'http',
            'port': 8080, 'protocol': 'tcp', 'url': 'http://10.10.30.91:8080',
            'status': 'up', 'response_time_ms': 5,
            'last_checked': '2026-06-30T10:00:00',
            'prometheus_job': 'test-service',
            'prometheus_target': 'http://10.10.30.91:8080/metrics',
            'monitoring_configured': 1, 'caddy_configured': 1,
        }
        svc_id = self.state.upsert_service(service)
        result = self.state.update_service_status(svc_id, 'down', 0)
        self.assertTrue(result)
        retrieved = self.state.get_service(svc_id)
        self.assertEqual(retrieved['status'], 'down')

    def test_list_services_filtered(self):
        server = {
            'hostname': 'test-server',
            'ip_address': '10.10.30.99',
            'proxmox_api_url': 'https://10.10.30.99:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'up',
        }
        sid_s = self.state.upsert_server(server)
        container = {
            'server_id': sid_s, 'vmid': 9001, 'name': 'test-container',
            'type': 'lxc', 'status': 'running', 'ip_addresses': ['10.10.30.91'],
            'memory_mb': 4096, 'cpu_cores': 2, 'disk_total_mb': 10240,
            'disk_used_mb': 2048, 'os': 'Ubuntu 22.04', 'template': 'ubuntu-22.04',
        }
        cid = self.state.upsert_container(container)
        service1 = {
            'container_id': cid, 'name': 'http-svc', 'type': 'http',
            'port': 8080, 'protocol': 'tcp', 'url': 'http://10.10.30.91:8080',
            'status': 'up', 'response_time_ms': 5,
            'last_checked': '2026-06-30T10:00:00',
            'prometheus_job': None, 'prometheus_target': None,
            'monitoring_configured': 0, 'caddy_configured': 0,
        }
        service2 = {
            'container_id': cid, 'name': 'ssh-svc', 'type': 'ssh',
            'port': 22, 'protocol': 'tcp', 'url': None,
            'status': 'up', 'response_time_ms': 3,
            'last_checked': '2026-06-30T10:00:00',
            'prometheus_job': None, 'prometheus_target': None,
            'monitoring_configured': 0, 'caddy_configured': 0,
        }
        self.state.upsert_service(service1)
        self.state.upsert_service(service2)
        http_services = self.state.list_services(container_id=cid, type='http')
        self.assertEqual(len(http_services), 1)
        self.assertEqual(http_services[0]['name'], 'http-svc')
        all_services = self.state.list_services(container_id=cid)
        self.assertEqual(len(all_services), 2)

    # --- Wiki Documents ---

    def test_create_wiki_document(self):
        doc = {
            'title': 'Test Service',
            'slug': 'test-service',
            'category': 'service',
            'content': '# Test Service\n\nThis is a test service.',
            'source': 'agent-generated',
            'last_updated': '2026-06-30T10:00:00',
        }
        doc_id = self.state.create_wiki_document(doc)
        self.assertIsNotNone(doc_id)
        self.assertIsInstance(doc_id, int)
        self.assertGreater(doc_id, 0)

    def test_get_wiki_document_by_slug(self):
        doc = {
            'title': 'Test Service',
            'slug': 'test-service',
            'category': 'service',
            'content': '# Test Service\n\nThis is a test service.',
            'source': 'agent-generated',
            'last_updated': '2026-06-30T10:00:00',
        }
        self.state.create_wiki_document(doc)
        retrieved = self.state.get_wiki_document_by_slug('test-service')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['title'], 'Test Service')
        self.assertEqual(retrieved['category'], 'service')

    def test_get_wiki_document_not_found(self):
        retrieved = self.state.get_wiki_document_by_slug('nonexistent')
        self.assertIsNone(retrieved)

    def test_get_wiki_documents_filtered(self):
        doc1 = {
            'title': 'Service Doc', 'slug': 'svc-doc',
            'category': 'service', 'content': '# Service',
            'source': 'agent-generated',
            'last_updated': '2026-06-30T10:00:00',
        }
        doc2 = {
            'title': 'Infra Doc', 'slug': 'infra-doc',
            'category': 'infrastructure', 'content': '# Infra',
            'source': 'agent-generated',
            'last_updated': '2026-06-30T10:00:00',
        }
        self.state.create_wiki_document(doc1)
        self.state.create_wiki_document(doc2)
        service_docs = self.state.get_wiki_documents(category='service')
        self.assertEqual(len(service_docs), 1)
        self.assertEqual(service_docs[0]['category'], 'service')
        all_docs = self.state.get_wiki_documents()
        self.assertEqual(len(all_docs), 2)

    # --- Agent Actions ---

    def test_create_agent_action(self):
        action = {
            'agent_id': 'test-agent',
            'action_type': 'discover',
            'target_type': 'all',
            'status': 'completed',
            'details': {'servers': 1, 'containers': 1, 'services': 1},
        }
        action_id = self.state.create_agent_action(action)
        self.assertIsNotNone(action_id)
        self.assertIsInstance(action_id, int)
        self.assertGreater(action_id, 0)

    def test_get_agent_actions_filtered(self):
        action1 = {
            'agent_id': 'test-agent',
            'action_type': 'discover',
            'target_type': 'all',
            'status': 'completed',
            'details': {},
        }
        action2 = {
            'agent_id': 'test-agent',
            'action_type': 'verify',
            'target_type': 'services',
            'status': 'pending',
            'details': {},
        }
        self.state.create_agent_action(action1)
        self.state.create_agent_action(action2)
        completed = self.state.get_agent_actions(status='completed')
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0]['action_type'], 'discover')
        all_actions = self.state.get_agent_actions()
        self.assertEqual(len(all_actions), 2)

    # --- User Requests ---

    def test_create_user_request(self):
        request = {
            'user_id': 'test-user',
            'request_type': 'create_service',
            'title': 'Test Service Request',
            'description': 'Create a new test service',
        }
        request_id = self.state.create_user_request(request)
        self.assertIsNotNone(request_id)
        self.assertIsInstance(request_id, int)
        self.assertGreater(request_id, 0)

    def test_user_request_default_status(self):
        request = {
            'user_id': 'test-user',
            'request_type': 'create_service',
            'title': 'Test Service Request',
            'description': 'Create a new test service',
        }
        self.state.create_user_request(request)
        requests = self.state.get_user_requests()
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0]['status'], 'pending')

    def test_get_user_requests_filtered(self):
        req1 = {
            'user_id': 'test-user', 'request_type': 'create_service',
            'title': 'Req 1', 'description': 'Desc 1',
        }
        req2 = {
            'user_id': 'test-user', 'request_type': 'modify_service',
            'title': 'Req 2', 'description': 'Desc 2',
        }
        self.state.create_user_request(req1)
        self.state.create_user_request(req2)
        pending = self.state.get_user_requests(status='pending')
        self.assertEqual(len(pending), 2)

    def test_update_user_request(self):
        request = {
            'user_id': 'test-user', 'request_type': 'create_service',
            'title': 'Test Service Request', 'description': 'Desc',
        }
        rid = self.state.create_user_request(request)
        result = self.state.update_user_request(rid, 'approved', {'routed_to': 'test-agent'})
        self.assertTrue(result)
        requests = self.state.get_user_requests()
        self.assertEqual(requests[0]['status'], 'approved')

    # --- Relationships ---

    def test_create_relationship(self):
        server = {
            'hostname': 'test-server', 'ip_address': '10.10.30.99',
            'proxmox_api_url': 'https://10.10.30.99:8006/api2/json',
            'proxmox_api_user': 'root@pam', 'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test', 'status': 'up',
        }
        sid_s = self.state.upsert_server(server)
        container = {
            'server_id': sid_s, 'vmid': 9001, 'name': 'test-container',
            'type': 'lxc', 'status': 'running', 'ip_addresses': ['10.10.30.91'],
            'memory_mb': 4096, 'cpu_cores': 2, 'disk_total_mb': 10240,
            'disk_used_mb': 2048, 'os': 'Ubuntu 22.04', 'template': 'ubuntu-22.04',
        }
        cid = self.state.upsert_container(container)
        svc1 = {
            'container_id': cid, 'name': 'svc1', 'type': 'http',
            'port': 8080, 'protocol': 'tcp', 'url': 'http://10.10.30.91:8080',
            'status': 'up', 'response_time_ms': 5, 'last_checked': '2026-06-30T10:00:00',
            'prometheus_job': None, 'prometheus_target': None,
            'monitoring_configured': 0, 'caddy_configured': 0,
        }
        svc2 = {
            'container_id': cid, 'name': 'svc2', 'type': 'http',
            'port': 9090, 'protocol': 'tcp', 'url': 'http://10.10.30.91:9090',
            'status': 'up', 'response_time_ms': 5, 'last_checked': '2026-06-30T10:00:00',
            'prometheus_job': None, 'prometheus_target': None,
            'monitoring_configured': 0, 'caddy_configured': 0,
        }
        id1 = self.state.upsert_service(svc1)
        id2 = self.state.upsert_service(svc2)
        rel_id = self.state.create_relationship(id1, id2, 'scrapes')
        self.assertIsNotNone(rel_id)
        relationships = self.state.get_service_relationships(id1)
        self.assertEqual(len(relationships), 1)
        self.assertEqual(relationships[0]['relationship_type'], 'scrapes')

    def test_delete_relationship(self):
        server = {
            'hostname': 'test-server', 'ip_address': '10.10.30.99',
            'proxmox_api_url': 'https://10.10.30.99:8006/api2/json',
            'proxmox_api_user': 'root@pam', 'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test', 'status': 'up',
        }
        sid_s = self.state.upsert_server(server)
        container = {
            'server_id': sid_s, 'vmid': 9001, 'name': 'test-container',
            'type': 'lxc', 'status': 'running', 'ip_addresses': ['10.10.30.91'],
            'memory_mb': 4096, 'cpu_cores': 2, 'disk_total_mb': 10240,
            'disk_used_mb': 2048, 'os': 'Ubuntu 22.04', 'template': 'ubuntu-22.04',
        }
        cid = self.state.upsert_container(container)
        svc1 = {
            'container_id': cid, 'name': 'svc1', 'type': 'http',
            'port': 8080, 'protocol': 'tcp', 'url': 'http://10.10.30.91:8080',
            'status': 'up', 'response_time_ms': 5, 'last_checked': '2026-06-30T10:00:00',
            'prometheus_job': None, 'prometheus_target': None,
            'monitoring_configured': 0, 'caddy_configured': 0,
        }
        svc2 = {
            'container_id': cid, 'name': 'svc2', 'type': 'http',
            'port': 9090, 'protocol': 'tcp', 'url': 'http://10.10.30.91:9090',
            'status': 'up', 'response_time_ms': 5, 'last_checked': '2026-06-30T10:00:00',
            'prometheus_job': None, 'prometheus_target': None,
            'monitoring_configured': 0, 'caddy_configured': 0,
        }
        id1 = self.state.upsert_service(svc1)
        id2 = self.state.upsert_service(svc2)
        self.state.create_relationship(id1, id2, 'scrapes')
        result = self.state.delete_relationship(id1, id2, 'scrapes')
        self.assertTrue(result)
        relationships = self.state.get_service_relationships(id1)
        self.assertEqual(len(relationships), 0)


if __name__ == '__main__':
    unittest.main()
