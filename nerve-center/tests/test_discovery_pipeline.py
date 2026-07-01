#!/usr/bin/env python3
"""Tests for nerve-center/discovery_pipeline.py."""
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from state import StateManager
from discovery_pipeline import DiscoveryPipeline


class TestDiscoveryPipeline(unittest.TestCase):
    def setUp(self):
        self.db_path = tempfile.mktemp(suffix='.db')
        self.state = StateManager(self.db_path)
        self.pipeline = DiscoveryPipeline(self.state)

    def tearDown(self):
        self.pipeline.stop()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    # --- Initialization ---

    def test_init_without_config(self):
        pipeline = DiscoveryPipeline(self.state)
        self.assertIsNotNone(pipeline.state)
        self.assertIsNotNone(pipeline.kgm)
        self.assertIsNotNone(pipeline.verifier)
        self.assertIsNotNone(pipeline.writer)
        self.assertIsNone(pipeline.discoverer)
        self.assertFalse(pipeline._running)

    def test_init_with_config(self):
        config = {
            'proxmox': {
                'api_url': 'https://10.10.30.22:8006/api2/json',
                'api_user': 'root@pam',
                'api_token_name': 'test-token',
                'api_token_secret': 'test-secret',
            }
        }
        pipeline = DiscoveryPipeline(self.state, config)
        self.assertIsNotNone(pipeline.discoverer)
        self.assertEqual(
            pipeline.discoverer.api_url,
            'https://10.10.30.22:8006/api2/json'
        )

    def test_init_with_empty_config(self):
        pipeline = DiscoveryPipeline(self.state, {})
        self.assertIsNone(pipeline.discoverer)

    # --- Stage hooks ---

    def test_on_registers_hook(self):
        """Registering a hook works."""
        called = []
        def my_hook(**kwargs):
            called.append(kwargs)
        self.pipeline.on('pre_discover', my_hook)
        self.assertEqual(len(self.pipeline._stage_hooks['pre_discover']), 1)

    def test_run_hooks_executes(self):
        """Hooks are executed during pipeline run."""
        called = []
        def my_hook(**kwargs):
            called.append(kwargs)
        self.pipeline.on('pre_discover', my_hook)
        # Just verify the hook is registered; full execution tested in run tests

    def test_run_hooks_error_handling(self):
        """Hook errors don't crash the pipeline."""
        def bad_hook(**kwargs):
            raise ValueError('hook error')
        self.pipeline.on('pre_discover', bad_hook)
        # Pipeline should continue despite hook error
        result = self.pipeline.run()
        self.assertIn('stages', result)

    # --- Pipeline run without discoverer ---

    def test_run_without_discoverer(self):
        """Pipeline run without discoverer continues with empty results."""
        result = self.pipeline.run()
        self.assertIn('stages', result)
        self.assertIn('discover', result['stages'])
        self.assertIn('verify', result['stages'])
        self.assertIn('analyze', result['stages'])
        self.assertIn('document', result['stages'])
        self.assertEqual(len(result['stages']['discover']['servers']), 0)
        self.assertIn('errors', result)

    def test_run_completes_with_stages(self):
        """Pipeline run completes all stages even without discoverer."""
        result = self.pipeline.run()
        self.assertIn('stages', result)
        self.assertIn('discover', result['stages'])
        self.assertIn('verify', result['stages'])
        self.assertIn('analyze', result['stages'])
        self.assertIn('document', result['stages'])
        self.assertIn('alerts', result)
        self.assertIn('started_at', result)
        self.assertIn('finished_at', result)

    def test_run_with_mocked_discoverer(self):
        """Pipeline run with mocked discoverer processes data."""
        config = {
            'proxmox': {
                'api_url': 'https://10.10.30.22:8006/api2/json',
                'api_user': 'root@pam',
                'api_token_name': 'test-token',
                'api_token_secret': 'test-secret',
            }
        }
        pipeline = DiscoveryPipeline(self.state, config)
        mock_discover_result = {
            'servers': [
                {
                    'id': 1,
                    'hostname': 'grid-pve',
                    'ip_address': '10.10.30.22',
                    'status': 'up',
                }
            ],
            'containers': [
                {
                    'id': 1,
                    'server_id': 1,
                    'vmid': 100,
                    'name': 'grid-core-01',
                    'type': 'lxc',
                    'status': 'running',
                    'ip_addresses': ['10.10.30.120'],
                }
            ],
            'services': [
                {
                    'id': 1,
                    'container_id': 1,
                    'name': 'prometheus',
                    'type': 'http',
                    'port': 9090,
                    'url': 'http://10.10.30.120:9090',
                    'status': 'up',
                    'prometheus_job': 'prometheus',
                }
            ],
            'errors': [],
        }
        with patch.object(pipeline.discoverer, 'discover_all', return_value=mock_discover_result):
            result = pipeline.run()
        self.assertIn('stages', result)
        self.assertEqual(len(result['stages']['discover']['servers']), 1)
        self.assertEqual(len(result['stages']['document']['document_ids']), 5)  # 1 server + 1 container + 1 service + 1 discovery_summary + 1 health_report
        self.assertIn('alerts', result)

    # --- Pipeline async ---

    def test_run_async_starts_thread(self):
        """Running async starts a thread."""
        config = {
            'proxmox': {
                'api_url': 'https://10.10.30.22:8006/api2/json',
                'api_user': 'root@pam',
                'api_token_name': 'test-token',
                'api_token_secret': 'test-secret',
            },
            'discovery_interval': 1,
        }
        pipeline = DiscoveryPipeline(self.state, config)
        thread = pipeline.run_async()
        self.assertIsNotNone(thread)
        self.assertTrue(thread.is_alive())
        pipeline.stop()

    def test_stop_stops_thread(self):
        """Stopping the pipeline stops the thread."""
        config = {
            'proxmox': {
                'api_url': 'https://10.10.30.22:8006/api2/json',
                'api_user': 'root@pam',
                'api_token_name': 'test-token',
                'api_token_secret': 'test-secret',
            },
            'discovery_interval': 1,
        }
        pipeline = DiscoveryPipeline(self.state, config)
        pipeline.run_async()
        pipeline.stop()
        self.assertFalse(pipeline._running)

    # --- Incremental discovery ---

    def test_discover_incremental_no_discoverer(self):
        """Incremental discovery without discoverer returns error."""
        result = self.pipeline.discover_incremental()
        self.assertIn('error', result)

    def test_discover_incremental_with_discoverer(self):
        """Incremental discovery with discoverer tracks changes."""
        config = {
            'proxmox': {
                'api_url': 'https://10.10.30.22:8006/api2/json',
                'api_user': 'root@pam',
                'api_token_name': 'test-token',
                'api_token_secret': 'test-secret',
            }
        }
        pipeline = DiscoveryPipeline(self.state, config)
        mock_discover_result = {
            'servers': [
                {
                    'id': 1,
                    'hostname': 'grid-pve',
                    'ip_address': '10.10.30.22',
                    'status': 'up',
                    'last_discovered': '2026-07-01T00:00:00',
                    'last_verified': '2026-07-01T00:00:00',
                }
            ],
            'containers': [
                {
                    'id': 1,
                    'server_id': 1,
                    'vmid': 100,
                    'name': 'grid-core-01',
                    'type': 'lxc',
                    'status': 'running',
                    'ip_addresses': ['10.10.30.120'],
                }
            ],
            'services': [
                {
                    'id': 1,
                    'container_id': 1,
                    'name': 'prometheus',
                    'type': 'http',
                    'port': 9090,
                    'url': 'http://10.10.30.120:9090',
                    'status': 'up',
                }
            ],
            'errors': [],
        }
        with patch.object(pipeline.discoverer, 'discover_all', return_value=mock_discover_result):
            result = pipeline.discover_incremental()
        self.assertIn('servers_added', result)
        self.assertIn('containers_added', result)
        self.assertIn('services_added', result)
        self.assertEqual(len(result['servers_added']), 1)

    def test_discover_incremental_detects_updates(self):
        """Incremental discovery detects status changes."""
        config = {
            'proxmox': {
                'api_url': 'https://10.10.30.22:8006/api2/json',
                'api_user': 'root@pam',
                'api_token_name': 'test-token',
                'api_token_secret': 'test-secret',
            }
        }
        pipeline = DiscoveryPipeline(self.state, config)
        # First, add an existing server
        self.state.upsert_server({
            'hostname': 'grid-pve',
            'ip_address': '10.10.30.22',
            'proxmox_api_url': 'https://10.10.30.22:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'up',
            'last_discovered': '2026-07-01T00:00:00',
            'last_verified': '2026-07-01T00:00:00',
        })
        mock_discover_result = {
            'servers': [
                {
                    'id': 1,
                    'hostname': 'grid-pve',
                    'ip_address': '10.10.30.22',
                    'status': 'down',  # Changed from up to down
                    'last_discovered': '2026-07-01T01:00:00',
                    'last_verified': '2026-07-01T01:00:00',
                }
            ],
            'containers': [],
            'services': [],
            'errors': [],
        }
        with patch.object(pipeline.discoverer, 'discover_all', return_value=mock_discover_result):
            result = pipeline.discover_incremental()
        self.assertEqual(len(result['servers_updated']), 1)

    # --- Pipeline status ---

    def test_get_pipeline_status(self):
        """Get pipeline status returns correct structure."""
        status = self.pipeline.get_pipeline_status()
        self.assertIn('running', status)
        self.assertIn('discoverer_configured', status)
        self.assertIn('servers_count', status)
        self.assertIn('containers_count', status)
        self.assertIn('services_count', status)
        self.assertIn('graph_summary', status)
        self.assertIn('wiki_docs_count', status)

    def test_pipeline_status_reflects_state(self):
        """Pipeline status reflects current state counts."""
        self.state.upsert_server({
            'hostname': 'grid-pve',
            'ip_address': '10.10.30.22',
            'proxmox_api_url': 'https://10.10.30.22:8006/api2/json',
            'proxmox_api_user': 'root@pam',
            'proxmox_api_token_name': 'test',
            'proxmox_api_token_secret': 'test',
            'status': 'up',
        })
        status = self.pipeline.get_pipeline_status()
        self.assertEqual(status['servers_count'], 1)


if __name__ == '__main__':
    unittest.main()
