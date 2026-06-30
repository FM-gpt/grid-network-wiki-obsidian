"""nerve-center/discoverer.py — Proxmox API scanner → service map."""

import json
import socket
import ssl
import time
import urllib.request
import urllib.error
from datetime import datetime
from typing import List, Dict, Optional


class ProxmoxDiscoverer:
    def __init__(self, state_manager, api_url: str, api_user: str,
                 api_token_name: str, api_token_secret: str) -> None:
        self.state = state_manager
        self.api_url = api_url.rstrip('/')
        self.api_user = api_user
        self.api_token_name = api_token_name
        self.api_token_secret = api_token_secret
        self._verify_ssl = False

    # --- HTTP helpers ---

    def _api_get(self, path: str) -> dict:
        """Make authenticated GET request to Proxmox API."""
        url = f"{self.api_url}/api2/json/{path}"
        req = urllib.request.Request(url)
        req.add_header(
            'Authorization',
            f'PVEAPIToken={self.api_token_name}!{self.api_token_secret}',
        )
        req.add_header('Content-Type', 'application/json')
        ctx = ssl.create_default_context()
        if not self._verify_ssl:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            raise Exception(f"Proxmox API error: {e.code} {e.reason}")
        except socket.timeout:
            raise Exception("Proxmox API timeout")

    # --- Discovery ---

    def discover_servers(self) -> List[dict]:
        """Discover all Proxmox hosts."""
        servers: List[dict] = []
        try:
            data = self._api_get('nodes')
            for node in data.get('data', []):
                hostname = node.get('node', '')
                ip = node.get('ip', '')
                status = 'up' if node.get('online') else 'down'
                server = {
                    'hostname': hostname,
                    'ip_address': ip,
                    'proxmox_api_url': f"https://{ip}:8006/api2/json",
                    'proxmox_api_user': self.api_user,
                    'proxmox_api_token_name': self.api_token_name,
                    'proxmox_api_token_secret': self.api_token_secret,
                    'status': status,
                    'last_discovered': datetime.now().isoformat(),
                    'last_verified': datetime.now().isoformat(),
                }
                sid = self.state.upsert_server(server)
                servers.append({**server, 'id': sid})
        except Exception as e:
            print(f"Error discovering servers: {e}")
        return servers

    def discover_containers(self, server_hostname: str) -> List[dict]:
        """Discover all containers/VMs on a Proxmox host."""
        containers: List[dict] = []
        try:
            lxc_data = self._api_get(f"nodes/{server_hostname}/lxc")
            for lxc in lxc_data.get('data', []):
                vmid = lxc.get('vmid', 0)
                name = lxc.get('name', f'vm-{vmid}')
                status = 'running' if lxc.get('status') == 'running' else 'stopped'
                ip_addrs: List[str] = []
                try:
                    net_data = self._api_get(f"nodes/{server_hostname}/lxc/{vmid}/config")
                    net_conf = net_data.get('data', {}).get('net', '')
                    if net_conf:
                        for iface in net_conf.split(','):
                            if 'ip=' in iface:
                                ip = iface.split('=')[1].split('/')[0]
                                ip_addrs.append(ip)
                except Exception:
                    pass
                res_data = self._api_get(f"nodes/{server_hostname}/lxc/{vmid}/status/current")
                res = res_data.get('data', {})
                server = self.state.get_server(server_hostname)
                server_id = server['id'] if server else None
                container = {
                    'server_id': server_id,
                    'vmid': vmid,
                    'name': name,
                    'type': 'lxc',
                    'status': status,
                    'ip_addresses': ip_addrs,
                    'memory_mb': res.get('maxmem', 0),
                    'cpu_cores': res.get('maxcpu', 0),
                    'disk_total_mb': res.get('maxdisk', 0) // (1024 * 1024),
                    'disk_used_mb': res.get('disk', 0) // (1024 * 1024),
                    'os': None,
                    'template': None,
                    'last_discovered': datetime.now().isoformat(),
                    'last_verified': datetime.now().isoformat(),
                }
                cid = self.state.upsert_container(container)
                containers.append({**container, 'id': cid})
        except Exception as e:
            print(f"Error discovering containers on {server_hostname}: {e}")
        return containers

    def discover_services(self, container: dict) -> List[dict]:
        """Discover services running on a container via TCP port probes."""
        services: List[dict] = []
        service_map = [
            ('http', 80, 'HTTP'),
            ('https', 443, 'HTTPS'),
            ('ssh', 22, 'SSH'),
            ('postgresql', 5432, 'PostgreSQL'),
            ('mysql', 3306, 'MySQL'),
            ('redis', 6379, 'Redis'),
            ('prometheus', 9090, 'Prometheus'),
            ('grafana', 3000, 'Grafana'),
            ('caddy', 8080, 'Caddy'),
            ('portainer', 9443, 'Portainer'),
            ('minecraft', 19132, 'Minecraft'),
            ('samba', 445, 'Samba'),
            ('ollama', 11434, 'Ollama'),
            ('open-webui', 3002, 'Open WebUI'),
            ('omada', 8043, 'Omada Controller'),
            ('proxmox', 8006, 'Proxmox API'),
        ]
        for proto, port, name in service_map:
            is_open = self._check_port_open(container['ip_addresses'], port)
            if is_open:
                url = (
                    f"http://{container['ip_addresses'][0]}:{port}"
                    if proto in ('http', 'https')
                    else None
                )
                service = {
                    'container_id': container['id'],
                    'name': name,
                    'type': proto,
                    'port': port,
                    'protocol': 'tcp',
                    'url': url,
                    'status': 'up',
                    'response_time_ms': 0,
                    'last_checked': datetime.now().isoformat(),
                    'prometheus_job': None,
                    'prometheus_target': None,
                    'monitoring_configured': 0,
                    'caddy_configured': 0,
                    'health_check_url': None,
                    'health_check_interval': None,
                }
                sid = self.state.upsert_service(service)
                services.append({**service, 'id': sid})
        return services

    def _check_port_open(self, ip_addresses: List[str], port: int,
                         timeout: int = 3) -> bool:
        """Check if a TCP port is open on any of the given IPs."""
        for ip in ip_addresses:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((ip, port))
                sock.close()
                if result == 0:
                    return True
            except Exception:
                pass
        return False

    # --- Verification ---

    def verify_server(self, server: dict) -> str:
        """Verify server is reachable."""
        try:
            self._api_get('version')
            return 'up'
        except Exception:
            return 'down'

    def verify_container(self, container: dict) -> str:
        """Verify container is running."""
        try:
            data = self._api_get(
                f"nodes/{container['server_hostname']}/lxc/{container['vmid']}/status/current"
            )
            return (
                'running'
                if data.get('data', {}).get('status') == 'running'
                else 'stopped'
            )
        except Exception:
            return 'unknown'

    def verify_service(self, service: dict) -> dict:
        """Verify service health via HTTP GET."""
        if not service.get('url'):
            return {'status': 'unknown', 'response_time_ms': None}
        start = time.time()
        try:
            req = urllib.request.Request(service['url'])
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
                elapsed = (time.time() - start) * 1000
                return {'status': 'up', 'response_time_ms': round(elapsed, 1)}
        except Exception:
            elapsed = (time.time() - start) * 1000
            return {'status': 'down', 'response_time_ms': None}

    def discover_all(self) -> dict:
        """Full discovery: servers → containers → services."""
        result: Dict[str, list] = {
            'servers': [],
            'containers': [],
            'services': [],
            'errors': [],
        }
        servers = self.discover_servers()
        result['servers'] = servers
        for server in servers:
            if server['status'] != 'up':
                continue
            containers = self.discover_containers(server['hostname'])
            result['containers'].extend(containers)
            for container in containers:
                if container['status'] != 'running':
                    continue
                services = self.discover_services(container)
                result['services'].extend(services)
        return result
