#!/usr/bin/env python3
"""Tests for nerve-center/http_service.py."""
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from state import StateManager
from http_service import NerveCenterApp, NerveCenterHandler, create_app


class TestNerveCenterApp(unittest.TestCase):
    def setUp(self):
        self.db_path = tempfile.mktemp(suffix='.db')
        self.app = NerveCenterApp(self.db_path)

    def tearDown(self):
        self.app.stop_discovery()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_init_without_config(self):
        app = NerveCenterApp(self.db_path)
        self.assertIsNotNone(app.state)
        self.assertIsNotNone(app.kgm)
        self.assertIsNotNone(app.verifier)
        self.assertIsNotNone(app.writer)
        self.assertIsNone(app._discoverer)

    def test_init_with_config(self):
        config = {
            'proxmox': {
                'api_url': 'https://10.10.30.22:8006/api2/json',
                'api_user': 'root@pam',
                'api_token_name': 'test-token',
                'api_token_secret': 'test-secret',
            }
        }
        app = NerveCenterApp(self.db_path, config)
        self.assertIsNotNone(app._discoverer)
        self.assertEqual(app._discoverer.api_url, 'https://10.10.30.22:8006/api2/json')

    def test_discover_without_discoverer(self):
        result = self.app.discover()
        self.assertIn('error', result)

    def test_discover_with_discoverer(self):
        config = {
            'proxmox': {
                'api_url': 'https://10.10.30.22:8006/api2/json',
                'api_user': 'root@pam',
                'api_token_name': 'test-token',
                'api_token_secret': 'test-secret',
            }
        }
        app = NerveCenterApp(self.db_path, config)
        with patch.object(app._discoverer, 'discover_all', return_value={
            'servers': [], 'containers': [], 'services': [], 'errors': [],
        }):
            result = app.discover()
            self.assertEqual(len(result['servers']), 0)

    def test_verify_all_empty(self):
        result = self.app.verify_all()
        self.assertEqual(result['total'], 0)

    def test_health_report(self):
        report = self.app.health_report()
        self.assertIn('generated_at', report)
        self.assertIn('servers', report)

    def test_get_alerts_empty(self):
        self.assertEqual(len(self.app.get_alerts()), 0)

    def test_get_wiki_docs_empty(self):
        self.assertEqual(len(self.app.get_wiki_docs()), 0)

    def test_get_wiki_docs_filtered(self):
        self.assertEqual(len(self.app.get_wiki_docs('server')), 0)

    def test_get_wiki_doc_by_slug_not_found(self):
        self.assertIsNone(self.app.get_wiki_doc_by_slug('nonexistent'))

    def test_get_graph_summary(self):
        summary = self.app.get_graph_summary()
        self.assertIn('total_entities', summary)
        self.assertIn('total_relationships', summary)
        self.assertIn('connected_components', summary)

    def test_get_neighbors_empty(self):
        self.assertEqual(len(self.app.get_neighbors('server', 'nonexistent')), 0)

    def test_search_entities_empty(self):
        self.assertEqual(len(self.app.search_entities('test')), 0)

    def test_get_servers_empty(self):
        self.assertEqual(len(self.app.get_servers()), 0)

    def test_get_server_not_found(self):
        self.assertIsNone(self.app.get_server('nonexistent'))

    def test_get_containers_empty(self):
        self.assertEqual(len(self.app.get_containers()), 0)

    def test_get_services_empty(self):
        self.assertEqual(len(self.app.get_services()), 0)

    def test_get_service_not_found(self):
        self.assertIsNone(self.app.get_service(9999))

    def test_start_discovery_no_config(self):
        self.assertIsNone(self.app.start_discovery())

    def test_start_discovery_with_config(self):
        config = {
            'proxmox': {
                'api_url': 'https://10.10.30.22:8006/api2/json',
                'api_user': 'root@pam',
                'api_token_name': 'test-token',
                'api_token_secret': 'test-secret',
            },
            'discovery_interval': 1,
        }
        app = NerveCenterApp(self.db_path, config)
        thread = app.start_discovery()
        self.assertIsNotNone(thread)
        self.assertTrue(thread.is_alive())
        app.stop_discovery()


class TestNerveCenterAppWithState(unittest.TestCase):
    def setUp(self):
        self.db_path = tempfile.mktemp(suffix='.db')
        self.state = StateManager(self.db_path)
        self.app = NerveCenterApp(self.db_path)
        self.state.upsert_server({
            'hostname': 'grid-pve',
            'ip_address': '10.10.30.22',
            'proxmox_api_url': 'https://10.10.30.22:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'up',
        })
        self.state.upsert_service({
            'container_id': 1,
            'name': 'prometheus',
            'type': 'http',
            'port': 9090,
            'url': 'http://10.10.30.120:9090',
            'status': 'up',
        })

    def tearDown(self):
        self.app.stop_discovery()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_get_servers_with_data(self):
        servers = self.app.get_servers()
        self.assertEqual(len(servers), 1)
        self.assertEqual(servers[0]['hostname'], 'grid-pve')

    def test_get_server_by_hostname(self):
        server = self.app.get_server('grid-pve')
        self.assertIsNotNone(server)
        self.assertEqual(server['hostname'], 'grid-pve')

    def test_get_server_by_hostname_not_found(self):
        self.assertIsNone(self.app.get_server('nonexistent'))

    def test_get_services_with_data(self):
        services = self.app.get_services()
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0]['name'], 'prometheus')

    def test_get_service_by_id(self):
        services = self.app.get_services()
        service = self.app.get_service(services[0]['id'])
        self.assertIsNotNone(service)
        self.assertEqual(service['name'], 'prometheus')


class TestNerveCenterHandlerAppLogic(unittest.TestCase):
    """Test handler by verifying it routes to app methods correctly."""

    def setUp(self):
        self.db_path = tempfile.mktemp(suffix='.db')
        self.app = NerveCenterApp(self.db_path)
        NerveCenterHandler.app = self.app
        self.state = self.app.state
        self.state.upsert_server({
            'hostname': 'grid-pve',
            'ip_address': '10.10.30.22',
            'proxmox_api_url': 'https://10.10.30.22:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'up',
        })
        self.state.upsert_service({
            'container_id': 1,
            'name': 'prometheus',
            'type': 'http',
            'port': 9090,
            'url': 'http://10.10.30.120:9090',
            'status': 'up',
        })

    def tearDown(self):
        NerveCenterHandler.app = None
        self.app.stop_discovery()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_handler_class_exists(self):
        self.assertTrue(hasattr(NerveCenterHandler, 'do_GET'))
        self.assertTrue(hasattr(NerveCenterHandler, 'do_POST'))
        self.assertTrue(hasattr(NerveCenterHandler, '_send_json'))

    def test_handler_app_is_set(self):
        self.assertIsNotNone(NerveCenterHandler.app)
        self.assertIsInstance(NerveCenterHandler.app, NerveCenterApp)

    def test_health_check_routes_correctly(self):
        result = self.app.health_report()
        self.assertIn('generated_at', result)

    def test_get_servers_routes_correctly(self):
        servers = self.app.get_servers()
        self.assertEqual(len(servers), 1)
        self.assertEqual(servers[0]['hostname'], 'grid-pve')

    def test_get_server_by_hostname_routes_correctly(self):
        server = self.app.get_server('grid-pve')
        self.assertIsNotNone(server)
        self.assertEqual(server['hostname'], 'grid-pve')

    def test_get_containers_routes_correctly(self):
        containers = self.app.get_containers()
        self.assertIsInstance(containers, list)

    def test_get_services_routes_correctly(self):
        services = self.app.get_services()
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0]['name'], 'prometheus')

    def test_get_graph_summary_routes_correctly(self):
        summary = self.app.get_graph_summary()
        self.assertIn('total_entities', summary)

    def test_get_alerts_routes_correctly(self):
        alerts = self.app.get_alerts()
        self.assertIsInstance(alerts, list)

    def test_health_report_routes_correctly(self):
        report = self.app.health_report()
        self.assertIn('generated_at', report)

    def test_search_entities_routes_correctly(self):
        results = self.app.search_entities('grid-pve')
        self.assertIsInstance(results, list)

    def test_get_wiki_routes_correctly(self):
        docs = self.app.get_wiki_docs()
        self.assertIsInstance(docs, list)

    def test_post_create_request_routes_correctly(self):
        rid = self.app.state.create_user_request({
            'user_id': 'test-user',
            'request_type': 'discovery',
            'title': 'Test request',
        })
        self.assertIsNotNone(rid)
        self.assertGreater(rid, 0)

    def test_post_discovery_routes_correctly(self):
        result = self.app.discover()
        # Without discoverer configured, discover returns error
        self.assertIn('error', result)

    def test_post_verify_routes_correctly(self):
        result = self.app.verify_all()
        self.assertIn('total', result)


class TestCreateApp(unittest.TestCase):
    def test_create_app(self):
        db_path = tempfile.mktemp(suffix='.db')
        try:
            app = create_app(db_path)
            self.assertIsNotNone(app.state)
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_create_app_with_config(self):
        db_path = tempfile.mktemp(suffix='.db')
        try:
            config = {
                'proxmox': {
                    'api_url': 'https://10.10.30.22:8006/api2/json',
                    'api_user': 'root@pam',
                    'api_token_name': 'test-token',
                    'api_token_secret': 'test-secret',
                }
            }
            app = create_app(db_path, config)
            self.assertIsNotNone(app._discoverer)
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)


if __name__ == '__main__':
    unittest.main()
