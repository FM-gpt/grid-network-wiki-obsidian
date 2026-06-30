"""nerve-center/service_verifier.py — Service health checking & SSL monitoring."""

import json
import socket
import ssl
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class ServiceVerifier:
    def __init__(self, state_manager, knowledge_graph=None) -> None:
        self.state = state_manager
        self.kgm = knowledge_graph
        self._default_timeout: int = 5
        self._default_port_timeout: int = 2

    # --- HTTP checks ---

    def check_http_service(self, url: str,
                           timeout: int = None) -> dict:
        """Perform HTTP/HTTPS health check."""
        import urllib.request
        import urllib.error
        timeout = timeout or self._default_timeout
        start = time.time()
        try:
            req = urllib.request.Request(url)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
                elapsed = (time.time() - start) * 1000
                status_code = resp.status
                headers = dict(resp.headers)
                body_len = len(resp.read())
                return {
                    'status': 'up' if 200 <= status_code < 400 else 'degraded',
                    'status_code': status_code,
                    'response_time_ms': round(elapsed, 1),
                    'headers': headers,
                    'body_length': body_len,
                    'last_checked': datetime.now().isoformat(),
                }
        except urllib.error.HTTPError as e:
            elapsed = (time.time() - start) * 1000
            return {
                'status': 'down',
                'status_code': e.code,
                'response_time_ms': None,
                'error': str(e),
                'last_checked': datetime.now().isoformat(),
            }
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return {
                'status': 'down',
                'status_code': None,
                'response_time_ms': None,
                'error': str(e),
                'last_checked': datetime.now().isoformat(),
            }

    # --- TCP checks ---

    def check_tcp_port(self, host: str, port: int,
                       timeout: int = None) -> dict:
        """Check if a TCP port is open."""
        timeout = timeout or self._default_port_timeout
        start = time.time()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            elapsed = (time.time() - start) * 1000
            if result == 0:
                return {
                    'status': 'up',
                    'port': port,
                    'response_time_ms': round(elapsed, 1),
                    'last_checked': datetime.now().isoformat(),
                }
            return {
                'status': 'down',
                'port': port,
                'response_time_ms': None,
                'error': f'Port {port} closed on {host}',
                'last_checked': datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                'status': 'unknown',
                'port': port,
                'response_time_ms': None,
                'error': str(e),
                'last_checked': datetime.now().isoformat(),
            }

    # --- SSL certificate checks ---

    def check_ssl_certificate(self, host: str, port: int = 443,
                              days_warning: int = 30) -> dict:
        """Check SSL certificate expiry for a host."""
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with ctx.wrap_socket(socket.socket(), server_hostname=host) as sock:
                sock.settimeout(self._default_port_timeout)
                sock.connect((host, port))
                cert = sock.getpeercert()
                sock.close()
                if not cert:
                    return {
                        'status': 'no_cert',
                        'host': host,
                        'port': port,
                        'error': 'No certificate presented',
                        'last_checked': datetime.now().isoformat(),
                    }
                expiry_str = cert.get('notAfter', '')
                # Parse: 'Dec 31 23:59:59 2025 GMT'
                expiry = datetime.strptime(expiry_str, '%b %d %H:%M:%S %Y %Z')
                days_left = (expiry - datetime.utcnow()).days
                status = 'valid'
                if days_left <= 0:
                    status = 'expired'
                elif days_left <= days_warning:
                    status = 'expiring_soon'
                return {
                    'status': status,
                    'host': host,
                    'port': port,
                    'expiry_date': expiry.isoformat(),
                    'days_remaining': days_left,
                    'issuer': cert.get('issuer', []),
                    'subject': cert.get('subject', []),
                    'last_checked': datetime.now().isoformat(),
                }
        except Exception as e:
            return {
                'status': 'error',
                'host': host,
                'port': port,
                'error': str(e),
                'last_checked': datetime.now().isoformat(),
            }

    # --- Service-level verification ---

    def verify_service(self, service: dict) -> dict:
        """Verify a single service and update its status in state."""
        if service.get('url'):
            result = self.check_http_service(service['url'])
        elif service.get('port'):
            result = self.check_tcp_port(
                service.get('host', ''),
                service['port'],
            )
        else:
            result = {'status': 'unknown', 'last_checked': datetime.now().isoformat()}

        # Update state
        self.state.update_service_status(service['id'], result['status'])
        return result

    def verify_all_services(self) -> dict:
        """Verify all services in state and return results."""
        services = self.state.list_services()
        results = {
            'total': len(services),
            'up': 0,
            'down': 0,
            'degraded': 0,
            'unknown': 0,
            'details': [],
        }
        for svc in services:
            result = self.verify_service(svc)
            results['details'].append({
                'service_id': svc['id'],
                'name': svc['name'],
                'port': svc.get('port'),
                'url': svc.get('url'),
                **result,
            })
            status = result.get('status', 'unknown')
            if status == 'up':
                results['up'] += 1
            elif status == 'degraded':
                results['degraded'] += 1
            elif status == 'down':
                results['down'] += 1
            else:
                results['unknown'] += 1
        return results

    def verify_service_by_id(self, service_id: int) -> dict:
        """Verify a single service by ID."""
        svc = self.state.get_service(service_id)
        if not svc:
            return {'status': 'not_found', 'error': f'Service {service_id} not found'}
        return self.verify_service(svc)

    # --- SSL monitoring ---

    def monitor_ssl_certificates(self, services: List[dict] = None) -> List[dict]:
        """Check SSL certificates for all HTTPS services."""
        if services is None:
            services = [s for s in self.state.list_services() if s.get('type') == 'https']
        results = []
        for svc in services:
            if svc.get('url'):
                host = svc['url'].replace('https://', '').split(':')[0]
                result = self.check_ssl_certificate(host, 443)
                result['service_id'] = svc['id']
                result['service_name'] = svc['name']
                if result['status'] in ('expired', 'expiring_soon'):
                    # Alert
                    self.state.create_agent_action({
                        'agent_id': 'ssl-monitor',
                        'action_type': 'alert',
                        'target_type': 'service',
                        'target_id': svc['id'],
                        'details': {
                            'message': f"SSL cert for {svc['name']} is {result['status']}",
                            'days_remaining': result.get('days_remaining'),
                        },
                    })
                results.append(result)
        return results

    # --- Health report ---

    def generate_health_report(self) -> dict:
        """Generate a comprehensive health report."""
        verify_results = self.verify_all_services()
        ssl_results = self.monitor_ssl_certificates()
        servers = self.state.list_servers()
        containers = self.state.list_containers()
        services = self.state.list_services()
        components = self.state.get_connected_components() if self.kgm else []

        report = {
            'generated_at': datetime.now().isoformat(),
            'servers': {
                'total': len(servers),
                'up': sum(1 for s in servers if s.get('status') == 'up'),
                'down': sum(1 for s in servers if s.get('status') == 'down'),
            },
            'containers': {
                'total': len(containers),
                'running': sum(1 for c in containers if c.get('status') == 'running'),
                'stopped': sum(1 for c in containers if c.get('status') == 'stopped'),
            },
            'services': {
                'total': verify_results['total'],
                'up': verify_results['up'],
                'down': verify_results['down'],
                'degraded': verify_results['degraded'],
                'unknown': verify_results['unknown'],
            },
            'ssl_certificates': ssl_results,
            'service_details': verify_results['details'],
            'connected_components': len(components),
        }
        return report

    # --- Alerting ---

    def check_alerts(self, report: dict = None) -> List[dict]:
        """Check for conditions that should trigger alerts."""
        if report is None:
            report = self.generate_health_report()
        alerts = []

        # Check for down servers
        if report['servers']['down'] > 0:
            alerts.append({
                'type': 'server_down',
                'severity': 'critical',
                'message': f"{report['servers']['down']} server(s) are down",
                'timestamp': datetime.now().isoformat(),
            })

        # Check for down services
        if report['services']['down'] > 0:
            alerts.append({
                'type': 'service_down',
                'severity': 'warning',
                'message': f"{report['services']['down']} service(s) are down",
                'timestamp': datetime.now().isoformat(),
            })

        # Check for expired SSL certs
        for cert in report.get('ssl_certificates', []):
            if cert.get('status') == 'expired':
                alerts.append({
                    'type': 'ssl_expired',
                    'severity': 'critical',
                    'message': f"SSL certificate expired for {cert.get('host')}:{cert.get('port')}",
                    'timestamp': datetime.now().isoformat(),
                })
            elif cert.get('status') == 'expiring_soon':
                alerts.append({
                    'type': 'ssl_expiring',
                    'severity': 'warning',
                    'message': f"SSL certificate expiring in {cert.get('days_remaining')} days for {cert.get('host')}:{cert.get('port')}",
                    'timestamp': datetime.now().isoformat(),
                })

        return alerts
