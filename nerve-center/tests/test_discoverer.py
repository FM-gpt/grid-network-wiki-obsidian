#!/usr/bin/env python3
"""Tests for nerve-center/discoverer.py."""
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from state import StateManager
from discoverer import ProxmoxDiscoverer


class TestProxmoxDiscoverer(unittest.TestCase):
    def setUp(self):
        self.db_path = tempfile.mktemp(suffix='.db')
        self.state = StateManager(self.db_path)
        self.discoverer = ProxmoxDiscoverer(
            state_manager=self.state,
            api_url='https://10.10.30.22:8006/api2/json',
            api_user='root@pam',
            api_token_name='test-token',
            api_token_secret='test-secret',
        )

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    # --- _check_port_open ---

    def test_check_port_open_connected(self):
        """When port is open, returns True."""
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_sock.connect_ex.return_value = 0
            mock_socket.return_value = mock_sock
            result = self.discoverer._check_port_open(['127.0.0.1'], 80)
            self.assertTrue(result)
            mock_sock.close.assert_called_once()

    def test_check_port_open_closed(self):
        """When port is closed, returns False."""
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_sock.connect_ex.return_value = 111
            mock_socket.return_value = mock_sock
            result = self.discoverer._check_port_open(['127.0.0.1'], 8080)
            self.assertFalse(result)
            mock_sock.close.assert_called_once()

    def test_check_port_open_multiple_ips_first_matches(self):
        """When first IP matches, returns True without trying others."""
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_sock.connect_ex.return_value = 0
            mock_socket.return_value = mock_sock
            result = self.discoverer._check_port_open(['127.0.0.1', '10.0.0.1'], 80)
            self.assertTrue(result)
            mock_sock.close.assert_called_once()

    def test_check_port_open_fallback_to_second_ip(self):
        """When first IP fails, tries second IP."""
        with patch('socket.socket') as mock_socket:
            mock_sock1 = MagicMock()
            mock_sock1.connect_ex.return_value = 111
            mock_sock2 = MagicMock()
            mock_sock2.connect_ex.return_value = 0
            mock_socket.side_effect = [mock_sock1, mock_sock2]
            result = self.discoverer._check_port_open(['127.0.0.1', '10.0.0.2'], 80)
            self.assertTrue(result)
            self.assertEqual(mock_socket.call_count, 2)

    def test_check_port_open_all_fail(self):
        """When all IPs fail, returns False."""
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_sock.connect_ex.return_value = 111
            mock_socket.return_value = mock_sock
            result = self.discoverer._check_port_open(['127.0.0.1', '10.0.0.1', '10.0.0.2'], 80)
            self.assertFalse(result)
            self.assertEqual(mock_socket.call_count, 3)

    # --- discover_servers ---

    def test_discover_servers_success(self):
        """When Proxmox API returns nodes, creates server records."""
        mock_response = {
            'data': [
                {'node': 'grid-pve', 'ip': '10.10.30.22', 'online': True},
                {'node': 'grid-pve-2', 'ip': '10.10.30.23', 'online': True},
            ]
        }
        with patch.object(self.discoverer, '_api_get', return_value=mock_response):
            servers = self.discoverer.discover_servers()
        self.assertEqual(len(servers), 2)
        self.assertEqual(servers[0]['hostname'], 'grid-pve')
        self.assertEqual(servers[0]['status'], 'up')
        self.assertEqual(servers[0]['ip_address'], '10.10.30.22')
        self.assertIsNotNone(servers[0]['id'])
        state_servers = self.state.list_servers()
        self.assertEqual(len(state_servers), 2)

    def test_discover_servers_down(self):
        """When node is offline, status is 'down'."""
        mock_response = {
            'data': [
                {'node': 'offline-node', 'ip': '10.10.30.99', 'online': False},
            ]
        }
        with patch.object(self.discoverer, '_api_get', return_value=mock_response):
            servers = self.discoverer.discover_servers()
        self.assertEqual(len(servers), 1)
        self.assertEqual(servers[0]['status'], 'down')

    def test_discover_servers_api_error(self):
        """When API call fails, returns empty list."""
        with patch.object(self.discoverer, '_api_get', side_effect=Exception('API error')):
            servers = self.discoverer.discover_servers()
        self.assertEqual(len(servers), 0)

    # --- discover_containers ---

    def test_discover_containers_success(self):
        """When Proxmox API returns LXCs, creates container records."""
        lxc_list = {
            'data': [
                {'vmid': 100, 'name': 'grid-core-01', 'status': 'running'},
                {'vmid': 101, 'name': 'grid-dev-01', 'status': 'running'},
            ]
        }
        net_data = {
            'data': {
                'net': 'name=eth0,ip=10.10.30.120/24,gw=10.10.30.1'
            }
        }
        res_data = {
            'data': {
                'maxmem': 8589934592,
                'maxcpu': 4,
                'maxdisk': 107374182400,
                'disk': 21474836480,
            }
        }
        call_count = [0]
        def mock_api_get(path):
            call_count[0] += 1
            if 'config' in path:
                return net_data
            elif 'status' in path:
                return res_data
            return lxc_list
        with patch.object(self.discoverer, '_api_get', side_effect=mock_api_get):
            server = {
                'hostname': 'grid-pve',
                'ip_address': '10.10.30.22',
                'proxmox_api_url': 'https://10.10.30.22:8006/api2/json',
                'proxmox_api_user': 'root@pam',
                'proxmox_api_token_name': 'test',
                'proxmox_api_token_secret': 'test',
                'status': 'up',
            }
            sid = self.state.upsert_server(server)
            containers = self.discoverer.discover_containers('grid-pve')
        self.assertEqual(len(containers), 2)
        self.assertEqual(containers[0]['vmid'], 100)
        self.assertEqual(containers[0]['name'], 'grid-core-01')
        self.assertEqual(containers[0]['status'], 'running')
        self.assertEqual(containers[0]['ip_addresses'], ['10.10.30.120'])
        self.assertEqual(containers[0]['memory_mb'], 8589934592)
        self.assertEqual(containers[0]['cpu_cores'], 4)
        self.assertEqual(containers[0]['disk_total_mb'], 102400)
        self.assertEqual(containers[0]['disk_used_mb'], 20480)
        self.assertIsNotNone(containers[0]['id'])
        state_containers = self.state.list_containers()
        self.assertEqual(len(state_containers), 2)

    def test_discover_containers_stopped(self):
        """When container is stopped, status is 'stopped'."""
        lxc_list = {
            'data': [
                {'vmid': 200, 'name': 'stopped-lxc', 'status': 'stopped'},
            ]
        }
        net_data = {'data': {'net': 'name=eth0,ip=10.10.30.100/24'}}
        res_data = {'data': {'maxmem': 0, 'maxcpu': 0, 'maxdisk': 0, 'disk': 0}}
        def mock_api_get(path):
            if 'config' in path:
                return net_data
            if 'status' in path:
                return res_data
            return lxc_list
        with patch.object(self.discoverer, '_api_get', side_effect=mock_api_get):
            server = {
                'hostname': 'grid-pve',
                'ip_address': '10.10.30.22',
                'proxmox_api_url': 'https://10.10.30.22:8006/api2/json',
                'proxmox_api_user': 'root@pam',
                'proxmox_api_token_name': 'test',
                'proxmox_api_token_secret': 'test',
                'status': 'up',
            }
            self.state.upsert_server(server)
            containers = self.discoverer.discover_containers('grid-pve')
        self.assertEqual(len(containers), 1)
        self.assertEqual(containers[0]['status'], 'stopped')

    def test_discover_containers_no_ip_config(self):
        """When LXC has no IP config, ip_addresses is empty list."""
        lxc_list = {'data': [{'vmid': 300, 'name': 'no-ip-lxc', 'status': 'running'}]}
        net_data = {'data': {'net': ''}}
        res_data = {'data': {'maxmem': 0, 'maxcpu': 0, 'maxdisk': 0, 'disk': 0}}
        def mock_api_get(path):
            if 'config' in path:
                return net_data
            if 'status' in path:
                return res_data
            return lxc_list
        with patch.object(self.discoverer, '_api_get', side_effect=mock_api_get):
            server = {
                'hostname': 'grid-pve',
                'ip_address': '10.10.30.22',
                'proxmox_api_url': 'https://10.10.30.22:8006/api2/json',
                'proxmox_api_user': 'root@pam',
                'proxmox_api_token_name': 'test',
                'proxmox_api_token_secret': 'test',
                'status': 'up',
            }
            self.state.upsert_server(server)
            containers = self.discoverer.discover_containers('grid-pve')
        self.assertEqual(len(containers), 1)
        self.assertEqual(containers[0]['ip_addresses'], [])

    # --- discover_services ---

    def test_discover_services_port_probe(self):
        """discover_services only creates services for open ports."""
        container = {
            'id': 1,
            'ip_addresses': ['10.10.30.22'],
        }
        def mock_connect_ex(args):
            # args is (ip, port) tuple
            port = args[1]
            return 0 if port == 22 else 111
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_sock.connect_ex.side_effect = mock_connect_ex
            mock_socket.return_value = mock_sock
            services = self.discoverer.discover_services(container)
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0]['name'], 'SSH')
        self.assertEqual(services[0]['port'], 22)
        self.assertEqual(services[0]['url'], None)

    def test_discover_services_http_url(self):
        """HTTP/HTTPS services get URL set."""
        container = {
            'id': 1,
            'ip_addresses': ['10.10.30.22'],
        }
        def mock_connect_ex(args):
            return 0  # all ports open
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_sock.connect_ex.side_effect = mock_connect_ex
            mock_socket.return_value = mock_sock
            services = self.discoverer.discover_services(container)
        http_svc = [s for s in services if s['name'] == 'HTTP']
        https_svc = [s for s in services if s['name'] == 'HTTPS']
        self.assertEqual(len(http_svc), 1)
        self.assertEqual(http_svc[0]['url'], 'http://10.10.30.22:80')
        self.assertEqual(len(https_svc), 1)
        self.assertEqual(https_svc[0]['url'], 'http://10.10.30.22:443')

    # --- verify methods ---

    def test_verify_server_up(self):
        """When API version endpoint is reachable, returns 'up'."""
        with patch.object(self.discoverer, '_api_get', return_value={'version': '8.0'}):
            server = {'hostname': 'grid-pve'}
            result = self.discoverer.verify_server(server)
            self.assertEqual(result, 'up')

    def test_verify_server_down(self):
        """When API version endpoint fails, returns 'down'."""
        with patch.object(self.discoverer, '_api_get', side_effect=Exception('fail')):
            server = {'hostname': 'grid-pve'}
            result = self.discoverer.verify_server(server)
            self.assertEqual(result, 'down')

    def test_verify_container_running(self):
        """When container status is 'running', returns 'running'."""
        with patch.object(self.discoverer, '_api_get', return_value={'data': {'status': 'running'}}):
            container = {'server_hostname': 'grid-pve', 'vmid': 100}
            result = self.discoverer.verify_container(container)
            self.assertEqual(result, 'running')

    def test_verify_container_stopped(self):
        """When container status is 'stopped', returns 'stopped'."""
        with patch.object(self.discoverer, '_api_get', return_value={'data': {'status': 'stopped'}}):
            container = {'server_hostname': 'grid-pve', 'vmid': 100}
            result = self.discoverer.verify_container(container)
            self.assertEqual(result, 'stopped')

    def test_verify_container_unknown(self):
        """When container status API fails, returns 'unknown'."""
        with patch.object(self.discoverer, '_api_get', side_effect=Exception('fail')):
            container = {'server_hostname': 'grid-pve', 'vmid': 100}
            result = self.discoverer.verify_container(container)
            self.assertEqual(result, 'unknown')

    def test_verify_service_up(self):
        """When HTTP service responds, returns up with response time."""
        service = {'url': 'http://127.0.0.1:8082/api/health'}
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = b'{"status": "healthy"}'
            # Use a context manager that properly returns mock_resp
            mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_resp)
            mock_urlopen.return_value.__exit__ = MagicMock(return_value=None)
            result = self.discoverer.verify_service(service)
            self.assertEqual(result['status'], 'up')
            self.assertIsNotNone(result['response_time_ms'])

    def test_verify_service_down(self):
        """When HTTP service fails, returns down."""
        service = {'url': 'http://127.0.0.1:19999/nonexistent'}
        with patch('urllib.request.urlopen', side_effect=Exception('connection refused')):
            result = self.discoverer.verify_service(service)
            self.assertEqual(result['status'], 'down')
            self.assertIsNone(result['response_time_ms'])

    def test_verify_service_no_url(self):
        """When service has no URL, returns unknown."""
        service = {'url': None}
        result = self.discoverer.verify_service(service)
        self.assertEqual(result['status'], 'unknown')
        self.assertIsNone(result['response_time_ms'])

    # --- discover_all ---

    def test_discover_all_flow(self):
        """Full discovery flow works end-to-end."""
        server_data = {'data': [{'node': 'grid-pve', 'ip': '10.10.30.22', 'online': True}]}
        lxc_list = {'data': [{'vmid': 100, 'name': 'test-lxc', 'status': 'running'}]}
        net_data = {'data': {'net': 'name=eth0,ip=10.10.30.100/24'}}
        res_data = {'data': {'maxmem': 4294967296, 'maxcpu': 2, 'maxdisk': 53687091200, 'disk': 10737418240}}

        def mock_api_get(path):
            if path == 'nodes':
                return server_data
            if 'config' in path:
                return net_data
            if 'status' in path:
                return res_data
            return lxc_list

        with patch.object(self.discoverer, '_api_get', side_effect=mock_api_get):
            with patch('socket.socket') as mock_socket:
                mock_sock = MagicMock()
                def mock_connect_ex(args):
                    port = args[1]
                    return 0 if port == 80 else 111
                mock_sock.connect_ex.side_effect = mock_connect_ex
                mock_socket.return_value = mock_sock
                result = self.discoverer.discover_all()
        self.assertEqual(len(result['servers']), 1)
        self.assertEqual(len(result['containers']), 1)
        self.assertEqual(len(result['services']), 1)
        self.assertEqual(result['servers'][0]['hostname'], 'grid-pve')
        self.assertEqual(result['containers'][0]['name'], 'test-lxc')
        self.assertEqual(result['containers'][0]['status'], 'running')
        self.assertEqual(result['services'][0]['name'], 'HTTP')
        self.assertEqual(result['services'][0]['port'], 80)

    def test_discover_all_skips_down_servers(self):
        """Down servers are skipped in discovery."""
        server_data = {'data': [{'node': 'offline', 'ip': '10.10.30.99', 'online': False}]}
        with patch.object(self.discoverer, '_api_get', return_value=server_data):
            result = self.discoverer.discover_all()
        self.assertEqual(len(result['servers']), 1)
        self.assertEqual(len(result['containers']), 0)
        self.assertEqual(len(result['services']), 0)

    def test_discover_all_skips_stopped_containers(self):
        """Stopped containers are skipped in service discovery."""
        server_data = {'data': [{'node': 'grid-pve', 'ip': '10.10.30.22', 'online': True}]}
        lxc_list = {'data': [{'vmid': 100, 'name': 'stopped-lxc', 'status': 'stopped'}]}
        net_data = {'data': {'net': 'name=eth0,ip=10.10.30.100/24'}}
        res_data = {'data': {'maxmem': 0, 'maxcpu': 0, 'maxdisk': 0, 'disk': 0}}
        def mock_api_get(path):
            if path == 'nodes':
                return server_data
            if 'config' in path:
                return net_data
            if 'status' in path:
                return res_data
            return lxc_list
        with patch.object(self.discoverer, '_api_get', side_effect=mock_api_get):
            result = self.discoverer.discover_all()
        self.assertEqual(len(result['servers']), 1)
        self.assertEqual(len(result['containers']), 1)
        self.assertEqual(len(result['services']), 0)


if __name__ == '__main__':
    unittest.main()
