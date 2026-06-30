#!/usr/bin/env python3
"""Tests for nerve-center/service_verifier.py."""
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from state import StateManager
from service_verifier import ServiceVerifier


class TestServiceVerifier(unittest.TestCase):
    def setUp(self):
        self.db_path = tempfile.mktemp(suffix='.db')
        self.state = StateManager(self.db_path)
        self.verifier = ServiceVerifier(state_manager=self.state)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    # --- check_http_service ---

    def test_check_http_service_up(self):
        """When HTTP service responds 200, returns up."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_resp.read.return_value = b'{"ok": true}'
            mock_resp.headers = {}
            mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_resp)
            mock_urlopen.return_value.__exit__ = MagicMock(return_value=None)
            result = self.verifier.check_http_service('http://127.0.0.1:8082/api/health')
            self.assertEqual(result['status'], 'up')
            self.assertEqual(result['status_code'], 200)
            self.assertIsNotNone(result['response_time_ms'])

    def test_check_http_service_down(self):
        """When HTTP service fails, returns down."""
        with patch('urllib.request.urlopen', side_effect=Exception('connection refused')):
            result = self.verifier.check_http_service('http://127.0.0.1:19999/nonexistent')
            self.assertEqual(result['status'], 'down')
            self.assertIsNotNone(result.get('error'))

    def test_check_http_service_http_error(self):
        """When HTTP service returns 500, returns down."""
        import urllib.error
        http_err = urllib.error.HTTPError('http://test', 500, 'Internal Server Error', {}, None)
        with patch('urllib.request.urlopen', side_effect=http_err):
            result = self.verifier.check_http_service('http://127.0.0.1:8082/api/health')
            self.assertEqual(result['status'], 'down')
            self.assertEqual(result['status_code'], 500)

    # --- check_tcp_port ---

    def test_check_tcp_port_open(self):
        """When TCP port is open, returns up."""
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_sock.connect_ex.return_value = 0
            mock_socket.return_value = mock_sock
            result = self.verifier.check_tcp_port('127.0.0.1', 8080)
            self.assertEqual(result['status'], 'up')
            self.assertEqual(result['port'], 8080)
            self.assertIsNotNone(result['response_time_ms'])

    def test_check_tcp_port_closed(self):
        """When TCP port is closed, returns down."""
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_sock.connect_ex.return_value = 111
            mock_socket.return_value = mock_sock
            result = self.verifier.check_tcp_port('127.0.0.1', 8080)
            self.assertEqual(result['status'], 'down')

    def test_check_tcp_port_error(self):
        """When TCP check raises, returns unknown."""
        with patch('socket.socket', side_effect=Exception('network error')):
            result = self.verifier.check_tcp_port('127.0.0.1', 8080)
            self.assertEqual(result['status'], 'unknown')

    # --- check_ssl_certificate ---

    def test_check_ssl_certificate_valid(self):
        """When cert is valid, returns valid status."""
        mock_cert = {
            'notAfter': 'Dec 31 23:59:59 2027 GMT',
            'issuer': [['CN', 'Test CA']],
            'subject': [['CN', 'test.example.com']],
        }
        mock_sock = MagicMock()
        mock_sock.getpeercert.return_value = mock_cert
        mock_sock.connect.return_value = None
        mock_sock.close.return_value = None
        with patch('ssl.create_default_context') as mock_ctx:
            mock_ctx.return_value.wrap_socket.return_value.__enter__ = MagicMock(return_value=mock_sock)
            mock_ctx.return_value.wrap_socket.return_value.__exit__ = MagicMock(return_value=None)
            result = self.verifier.check_ssl_certificate('test.example.com', 443)
            self.assertEqual(result['status'], 'valid')
            self.assertIsNotNone(result['days_remaining'])
            self.assertGreater(result['days_remaining'], 30)

    def test_check_ssl_certificate_expiring_soon(self):
        """When cert expires soon, returns expiring_soon."""
        # Use a date 15 days from now
        from datetime import datetime, timedelta, timedelta
        future = datetime.utcnow() + timedelta(days=15)
        expiry_str = future.strftime('%b %d %H:%M:%S %Y GMT')
        mock_cert = {
            'notAfter': expiry_str,
            'issuer': [],
            'subject': [],
        }
        mock_sock = MagicMock()
        mock_sock.getpeercert.return_value = mock_cert
        mock_sock.connect.return_value = None
        mock_sock.close.return_value = None
        with patch('ssl.create_default_context') as mock_ctx:
            mock_ctx.return_value.wrap_socket.return_value.__enter__ = MagicMock(return_value=mock_sock)
            mock_ctx.return_value.wrap_socket.return_value.__exit__ = MagicMock(return_value=None)
            result = self.verifier.check_ssl_certificate('test.example.com', 443)
            self.assertEqual(result['status'], 'expiring_soon')
            self.assertLessEqual(result['days_remaining'], 30)

    def test_check_ssl_certificate_expired(self):
        """When cert is expired, returns expired."""
        from datetime import datetime, timedelta
        past = datetime.utcnow() - timedelta(days=10)
        expiry_str = past.strftime('%b %d %H:%M:%S %Y GMT')
        mock_cert = {
            'notAfter': expiry_str,
            'issuer': [],
            'subject': [],
        }
        mock_sock = MagicMock()
        mock_sock.getpeercert.return_value = mock_cert
        mock_sock.connect.return_value = None
        mock_sock.close.return_value = None
        with patch('ssl.create_default_context') as mock_ctx:
            mock_ctx.return_value.wrap_socket.return_value.__enter__ = MagicMock(return_value=mock_sock)
            mock_ctx.return_value.wrap_socket.return_value.__exit__ = MagicMock(return_value=None)
            result = self.verifier.check_ssl_certificate('test.example.com', 443)
            self.assertEqual(result['status'], 'expired')
            self.assertLess(result['days_remaining'], 0)

    def test_check_ssl_certificate_error(self):
        """When SSL check fails, returns error status."""
        with patch('ssl.create_default_context', side_effect=Exception('ssl error')):
            result = self.verifier.check_ssl_certificate('test.example.com', 443)
            self.assertEqual(result['status'], 'error')

    # --- verify_service ---

    def test_verify_service_http(self):
        """Verifying an HTTP service updates its status."""
        sid = self.state.upsert_service({
            'container_id': 1,
            'name': 'test-service',
            'type': 'http',
            'port': 8080,
            'url': 'http://127.0.0.1:19999/fake',
        })
        with patch('urllib.request.urlopen', side_effect=Exception('fail')):
            result = self.verifier.verify_service({'id': sid, 'url': 'http://127.0.0.1:19999/fake'})
            self.assertEqual(result['status'], 'down')
            # Verify state was updated
            updated = self.state.get_service(sid)
            self.assertIsNotNone(updated)
            self.assertEqual(updated['status'], 'down')

    def test_verify_service_no_url_no_port(self):
        """Service with no URL or port returns unknown."""
        svc = {'id': 1, 'name': 'empty-service'}
        result = self.verifier.verify_service(svc)
        self.assertEqual(result['status'], 'unknown')

    # --- verify_all_services ---

    def test_verify_all_services_empty(self):
        """With no services, returns empty report."""
        result = self.verifier.verify_all_services()
        self.assertEqual(result['total'], 0)
        self.assertEqual(result['up'], 0)
        self.assertEqual(result['down'], 0)

    def test_verify_all_services_with_services(self):
        """With services, returns counts and details."""
        # Add a service
        self.state.upsert_service({
            'container_id': 1,
            'name': 'test-svc',
            'type': 'http',
            'port': 8080,
            'url': 'http://127.0.0.1:19999/fake',
        })
        with patch('urllib.request.urlopen', side_effect=Exception('fail')):
            result = self.verifier.verify_all_services()
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['down'], 1)
        self.assertEqual(len(result['details']), 1)

    def test_verify_service_by_id(self):
        """verify_service_by_id works for existing service."""
        sid = self.state.upsert_service({
            'container_id': 1,
            'name': 'test-svc',
            'type': 'http',
            'port': 8080,
            'url': 'http://127.0.0.1:19999/fake',
        })
        with patch('urllib.request.urlopen', side_effect=Exception('fail')):
            result = self.verifier.verify_service_by_id(sid)
            self.assertEqual(result['status'], 'down')

    def test_verify_service_by_id_not_found(self):
        """verify_service_by_id returns not_found for missing service."""
        result = self.verifier.verify_service_by_id(9999)
        self.assertEqual(result['status'], 'not_found')

    # --- monitor_ssl_certificates ---

    def test_monitor_ssl_certificates_empty(self):
        """With no HTTPS services, returns empty list."""
        result = self.verifier.monitor_ssl_certificates()
        self.assertEqual(len(result), 0)

    def test_monitor_ssl_certificates_finds_https(self):
        """Finds HTTPS services and checks their certs."""
        self.state.upsert_service({
            'container_id': 1,
            'name': 'https-svc',
            'type': 'https',
            'port': 443,
            'url': 'https://test.example.com',
        })
        mock_cert = {
            'notAfter': 'Dec 31 23:59:59 2027 GMT',
            'issuer': [],
            'subject': [],
        }
        mock_sock = MagicMock()
        mock_sock.getpeercert.return_value = mock_cert
        mock_sock.connect.return_value = None
        mock_sock.close.return_value = None
        with patch('ssl.create_default_context') as mock_ctx:
            mock_ctx.return_value.wrap_socket.return_value.__enter__ = MagicMock(return_value=mock_sock)
            mock_ctx.return_value.wrap_socket.return_value.__exit__ = MagicMock(return_value=None)
            result = self.verifier.monitor_ssl_certificates()
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['service_name'], 'https-svc')

    # --- generate_health_report ---

    def test_generate_health_report(self):
        """Health report includes all sections."""
        report = self.verifier.generate_health_report()
        self.assertIn('generated_at', report)
        self.assertIn('servers', report)
        self.assertIn('containers', report)
        self.assertIn('services', report)
        self.assertIn('ssl_certificates', report)
        self.assertIn('service_details', report)

    # --- check_alerts ---

    def test_check_alerts_no_alerts(self):
        """With all healthy, returns no alerts."""
        report = self.verifier.generate_health_report()
        alerts = self.verifier.check_alerts(report)
        self.assertEqual(len(alerts), 0)

    def test_check_alerts_server_down(self):
        """Down servers trigger critical alerts."""
        report = {'servers': {'down': 2}, 'services': {'down': 0}}
        alerts = self.verifier.check_alerts(report)
        server_alerts = [a for a in alerts if a['type'] == 'server_down']
        self.assertEqual(len(server_alerts), 1)
        self.assertEqual(server_alerts[0]['severity'], 'critical')

    def test_check_alerts_service_down(self):
        """Down services trigger warning alerts."""
        report = {'servers': {'down': 0}, 'services': {'down': 1}}
        alerts = self.verifier.check_alerts(report)
        svc_alerts = [a for a in alerts if a['type'] == 'service_down']
        self.assertEqual(len(svc_alerts), 1)
        self.assertEqual(svc_alerts[0]['severity'], 'warning')

    def test_check_alerts_ssl_expired(self):
        """Expired SSL certs trigger critical alerts."""
        report = {
            'servers': {'down': 0},
            'services': {'down': 0},
            'ssl_certificates': [
                {'status': 'expired', 'host': 'test.com', 'port': 443},
            ],
        }
        alerts = self.verifier.check_alerts(report)
        ssl_alerts = [a for a in alerts if a['type'] == 'ssl_expired']
        self.assertEqual(len(ssl_alerts), 1)
        self.assertEqual(ssl_alerts[0]['severity'], 'critical')

    def test_check_alerts_ssl_expiring(self):
        """Expiring SSL certs trigger warning alerts."""
        report = {
            'servers': {'down': 0},
            'services': {'down': 0},
            'ssl_certificates': [
                {'status': 'expiring_soon', 'host': 'test.com', 'port': 443, 'days_remaining': 10},
            ],
        }
        alerts = self.verifier.check_alerts(report)
        ssl_alerts = [a for a in alerts if a['type'] == 'ssl_expiring']
        self.assertEqual(len(ssl_alerts), 1)
        self.assertEqual(ssl_alerts[0]['severity'], 'warning')


if __name__ == '__main__':
    unittest.main()
