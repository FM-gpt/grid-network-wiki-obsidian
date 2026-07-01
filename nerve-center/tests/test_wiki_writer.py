#!/usr/bin/env python3
"""Tests for nerve-center/wiki_writer.py."""
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from state import StateManager
from wiki_writer import WikiWriter


class TestWikiWriter(unittest.TestCase):
    def setUp(self):
        self.db_path = tempfile.mktemp(suffix='.db')
        self.state = StateManager(self.db_path)
        self.writer = WikiWriter(state_manager=self.state)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    # --- generate_document ---

    def test_generate_server_doc(self):
        """Generating a server doc creates a wiki document."""
        data = {
            'id': 1,
            'hostname': 'grid-pve',
            'ip_address': '10.10.30.22',
            'proxmox_api_url': 'https://10.10.30.22:8006/api2/json',
            'status': 'up',
        }
        doc_id = self.writer.generate_document('server', data)
        self.assertIsNotNone(doc_id)
        doc = self.state.get_wiki_document_by_slug(
            f"generated:server:{data['id']}"
        )
        self.assertIsNotNone(doc)
        self.assertEqual(doc['title'], 'Server: grid-pve')
        body = json.loads(doc['content'])
        self.assertEqual(body['hostname'], 'grid-pve')
        self.assertEqual(body['status'], 'up')

    def test_generate_container_doc(self):
        """Generating a container doc creates a wiki document."""
        data = {
            'id': 100,
            'name': 'grid-core-01',
            'vmid': 120,
            'type': 'lxc',
            'status': 'running',
            'ip_addresses': ['10.10.30.120'],
            'memory_mb': 8589934592,
            'cpu_cores': 4,
            'disk_total_mb': 102400,
            'disk_used_mb': 20480,
            'server_id': 1,
        }
        doc_id = self.writer.generate_document('container', data)
        self.assertIsNotNone(doc_id)
        doc = self.state.get_wiki_document_by_slug(
            f"generated:container:{data['id']}"
        )
        self.assertIsNotNone(doc)
        self.assertEqual(doc['title'], f"Container: {data['name']} (VMID: {data['vmid']})")
        body = json.loads(doc['content'])
        self.assertEqual(body['name'], 'grid-core-01')
        self.assertEqual(body['vmid'], 120)
        self.assertEqual(body['status'], 'running')

    def test_generate_service_doc(self):
        """Generating a service doc creates a wiki document."""
        data = {
            'id': 1,
            'name': 'prometheus',
            'type': 'http',
            'port': 9090,
            'protocol': 'tcp',
            'url': 'http://10.10.30.120:9090',
            'status': 'up',
            'response_time_ms': 12.5,
            'container_id': 100,
            'prometheus_job': 'prometheus',
            'prometheus_target': '10.10.30.120:9090',
            'monitoring_configured': 1,
            'caddy_configured': 1,
            'last_checked': datetime.now().isoformat(),
        }
        doc_id = self.writer.generate_document('service', data)
        self.assertIsNotNone(doc_id)
        doc = self.state.get_wiki_document_by_slug(
            f"generated:service:{data['id']}"
        )
        self.assertIsNotNone(doc)
        self.assertEqual(doc['title'], f"Service: {data['name']} ({data['type']}:{data['port']})")
        body = json.loads(doc['content'])
        self.assertEqual(body['name'], 'prometheus')
        self.assertEqual(body['port'], 9090)
        self.assertEqual(body['status'], 'up')

    def test_generate_health_report_doc(self):
        """Generating a health report doc creates a wiki document."""
        data = {
            'id': 1,
            'generated_at': datetime.now().isoformat(),
            'servers': {'up': 2, 'down': 0, 'total': 2},
            'containers': {'running': 5, 'stopped': 1, 'total': 6},
            'services': {'up': 10, 'down': 1, 'degraded': 0, 'unknown': 0, 'total': 11},
            'service_details': [],
            'ssl_certificates': [],
            'connected_components': 1,
        }
        doc_id = self.writer.generate_document('health_report', data)
        self.assertIsNotNone(doc_id)
        doc = self.state.get_wiki_document_by_slug(
            f"generated:health_report:{data['id']}"
        )
        self.assertIsNotNone(doc)
        body = json.loads(doc['content'])
        self.assertIn('summary', body)
        self.assertEqual(body['summary']['servers_up'], 2)
        self.assertEqual(body['summary']['containers_running'], 5)
        self.assertEqual(body['summary']['services_up'], 10)

    def test_generate_relationship_doc(self):
        """Generating a relationship doc creates a wiki document."""
        data = {
            'id': 1,
            'source_type': 'server',
            'source_id': 'grid-pve',
            'target_type': 'service',
            'target_id': 'prometheus',
            'relationship_type': 'hosts',
            'properties': {'interval': '15s'},
            'created_at': datetime.now().isoformat(),
        }
        doc_id = self.writer.generate_document('relationship', data)
        self.assertIsNotNone(doc_id)
        doc = self.state.get_wiki_document_by_slug(
            f"generated:relationship:{data['id']}"
        )
        self.assertIsNotNone(doc)
        body = json.loads(doc['content'])
        self.assertEqual(body['source_id'], 'grid-pve')
        self.assertEqual(body['target_id'], 'prometheus')
        self.assertEqual(body['relationship_type'], 'hosts')

    def test_generate_discovery_summary_doc(self):
        """Generating a discovery summary doc creates a wiki document."""
        data = {
            'id': 1,
            'servers': [
                {'hostname': 'grid-pve', 'status': 'up'},
                {'hostname': 'grid-pve-2', 'status': 'down'},
            ],
            'containers': [
                {'name': 'grid-core-01', 'status': 'running', 'vmid': 120},
            ],
            'services': [
                {'name': 'prometheus', 'port': 9090, 'status': 'up'},
            ],
            'errors': [],
        }
        doc_id = self.writer.generate_document('discovery_summary', data)
        self.assertIsNotNone(doc_id)
        doc = self.state.get_wiki_document_by_slug(
            f"generated:discovery_summary:{data['id']}"
        )
        self.assertIsNotNone(doc)
        body = json.loads(doc['content'])
        self.assertEqual(body['summary']['servers_discovered'], 2)
        self.assertEqual(body['summary']['containers_discovered'], 1)
        self.assertEqual(body['summary']['services_discovered'], 1)

    def test_generate_document_unknown_type(self):
        """Generating with unknown doc type raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.writer.generate_document('unknown_type', {'id': 1})
        self.assertIn('unknown_type', str(ctx.exception))

    def test_generate_document_update_existing(self):
        """Updating an existing doc returns the same ID."""
        data = {'id': 1, 'hostname': 'grid-pve', 'ip_address': '10.10.30.22', 'status': 'up'}
        doc_id1 = self.writer.generate_document('server', data)
        data['ip_address'] = '10.10.30.23'
        doc_id2 = self.writer.generate_document('server', data)
        self.assertEqual(doc_id1, doc_id2)
        doc = self.state.get_wiki_document_by_slug(f"generated:server:{data['id']}")
        self.assertIsNotNone(doc)
        body = json.loads(doc['content'])
        self.assertEqual(body['ip_address'], '10.10.30.23')

    # --- generate_bulk ---

    def test_generate_bulk(self):
        """Bulk generation creates multiple docs."""
        items = [
            {'id': 1, 'hostname': 'grid-pve', 'ip_address': '10.10.30.22', 'status': 'up'},
            {'id': 2, 'hostname': 'grid-pve-2', 'ip_address': '10.10.30.23', 'status': 'down'},
        ]
        doc_ids = self.writer.generate_bulk('server', items)
        self.assertEqual(len(doc_ids), 2)
        self.assertEqual(len(self.writer.get_generated_docs('server')), 2)

    def test_generate_bulk_partial_failure(self):
        """Bulk generation handles partial failures gracefully."""
        items = [
            {'id': 1, 'hostname': 'grid-pve', 'ip_address': '10.10.30.22', 'status': 'up'},
            {'id': 2, 'hostname': 'grid-pve-2', 'ip_address': '10.10.30.23', 'status': 'down'},
        ]
        doc_ids = self.writer.generate_bulk('server', items)
        self.assertEqual(len(doc_ids), 2)

    # --- list_templates ---

    def test_list_templates(self):
        """List templates returns all registered types."""
        templates = self.writer.list_templates()
        self.assertIn('server', templates)
        self.assertIn('container', templates)
        self.assertIn('service', templates)
        self.assertIn('health_report', templates)
        self.assertIn('relationship', templates)
        self.assertIn('discovery_summary', templates)

    def test_register_template(self):
        """Registering a custom template makes it available."""
        def custom_gen(data):
            return {'title': f"Custom: {data.get('name', '')}", 'body': data}
        self.writer.register_template('custom', custom_gen)
        templates = self.writer.list_templates()
        self.assertIn('custom', templates)

        data = {'id': 1, 'name': 'test'}
        doc_id = self.writer.generate_document('custom', data)
        self.assertIsNotNone(doc_id)

    # --- get_generated_docs ---

    def test_get_generated_docs_all(self):
        """Getting all generated docs returns all types."""
        self.writer.generate_document('server', {'id': 1, 'hostname': 'grid-pve', 'ip_address': '10.10.30.22', 'status': 'up'})
        self.writer.generate_document('container', {'id': 100, 'name': 'grid-core-01', 'vmid': 120, 'type': 'lxc', 'status': 'running', 'ip_addresses': ['10.10.30.120'], 'memory_mb': 0, 'cpu_cores': 0, 'disk_total_mb': 0, 'disk_used_mb': 0, 'server_id': 1})
        docs = self.writer.get_generated_docs()
        self.assertEqual(len(docs), 2)

    def test_get_generated_docs_filtered(self):
        """Getting generated docs filtered by type works."""
        self.writer.generate_document('server', {'id': 1, 'hostname': 'grid-pve', 'ip_address': '10.10.30.22', 'status': 'up'})
        self.writer.generate_document('server', {'id': 2, 'hostname': 'grid-pve-2', 'ip_address': '10.10.30.23', 'status': 'down'})
        docs = self.writer.get_generated_docs('server')
        self.assertEqual(len(docs), 2)

    def test_get_document_by_slug(self):
        """Getting a document by slug returns it."""
        self.writer.generate_document('server', {'id': 1, 'hostname': 'grid-pve', 'ip_address': '10.10.30.22', 'status': 'up'})
        doc = self.writer.get_document_by_slug('generated:server:1')
        self.assertIsNotNone(doc)
        self.assertEqual(doc['title'], 'Server: grid-pve')

    def test_get_document_by_slug_not_found(self):
        """Getting a non-existent document by slug returns None."""
        doc = self.writer.get_document_by_slug('generated:server:nonexistent')
        self.assertIsNone(doc)

    # --- track_changes ---

    def test_track_changes_detects_changes(self):
        """Track changes detects field changes."""
        previous = {'hostname': 'grid-pve', 'status': 'up', 'ip_address': '10.10.30.22'}
        current = {'id': 1, 'hostname': 'grid-pve', 'status': 'down', 'ip_address': '10.10.30.22'}
        result = self.writer.track_changes('server', current, previous)
        self.assertTrue(result['created'])
        self.assertIsNotNone(result['doc_id'])
        docs = self.state.get_wiki_documents()
        doc = [d for d in docs if d['id'] == result['doc_id']][0]
        body = json.loads(doc['content'])
        # 2 changes: id (None→1) and status (up→down)
        self.assertEqual(len(body['changes']), 2)
        # Find the status change among the changes
        status_change = [c for c in body['changes'] if c['field'] == 'status'][0]
        self.assertEqual(status_change['old_value'], 'up')
        self.assertEqual(status_change['new_value'], 'down')

    def test_track_changes_no_changes(self):
        """Track changes returns no doc when nothing changed."""
        data = {'id': 1, 'hostname': 'grid-pve', 'status': 'up'}
        result = self.writer.track_changes('server', data, data)
        self.assertFalse(result['created'])
        self.assertIsNone(result['doc_id'])

    def test_track_changes_new_entity(self):
        """Track changes works for new entity (no previous data)."""
        data = {'id': 1, 'hostname': 'grid-pve', 'status': 'up'}
        result = self.writer.track_changes('server', data, None)
        self.assertFalse(result['created'])
        self.assertIsNone(result['doc_id'])

    def test_track_changes_multiple_changes(self):
        """Track changes detects multiple field changes."""
        previous = {'hostname': 'grid-pve', 'status': 'up', 'ip_address': '10.10.30.22'}
        current = {'id': 1, 'hostname': 'grid-pve-2', 'status': 'down', 'ip_address': '10.10.30.23'}
        result = self.writer.track_changes('server', current, previous)
        self.assertTrue(result['created'])
        docs = self.state.get_wiki_documents()
        doc = [d for d in docs if d['id'] == result['doc_id']][0]
        body = json.loads(doc['content'])
        # 4 changes: hostname, status, ip_address, and id
        self.assertEqual(len(body['changes']), 4)


if __name__ == '__main__':
    unittest.main()
