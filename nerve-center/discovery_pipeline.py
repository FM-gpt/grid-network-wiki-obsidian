"""nerve-center/discovery_pipeline.py — Agent-driven discovery pipeline."""

import json
import threading
import time
from datetime import datetime
from typing import List, Dict, Optional, Callable, Any

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state import StateManager
from discoverer import ProxmoxDiscoverer
from knowledge_graph import KnowledgeGraphManager
from service_verifier import ServiceVerifier
from wiki_writer import WikiWriter


class DiscoveryPipeline:
    """Orchestrated agent-driven discovery pipeline.

    Runs a sequence of stages:
    1. discover — Proxmox API scan
    2. verify — service health checks
    3. analyze — build knowledge graph
    4. document — generate wiki docs
    5. alert — check and create alerts

    Each stage is a pluggable hook, allowing customization.
    """

    def __init__(self, state_manager: StateManager,
                 config: Optional[dict] = None) -> None:
        self.state = state_manager
        self.config = config or {}
        self.kgm = KnowledgeGraphManager(self.state)
        self.verifier = ServiceVerifier(self.state, self.kgm)
        self.writer = WikiWriter(self.state, self.kgm)
        self.discoverer: Optional[ProxmoxDiscoverer] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stage_hooks: Dict[str, List[Callable]] = {
            'pre_discover': [],
            'post_discover': [],
            'pre_verify': [],
            'post_verify': [],
            'pre_analyze': [],
            'post_analyze': [],
            'pre_document': [],
            'post_document': [],
            'pre_alert': [],
            'post_alert': [],
            'on_complete': [],
            'on_error': [],
        }
        self._init_discoverer()

    def _init_discoverer(self) -> None:
        proxmox = self.config.get('proxmox', {})
        if proxmox.get('api_url'):
            self.discoverer = ProxmoxDiscoverer(
                state_manager=self.state,
                api_url=proxmox['api_url'],
                api_user=proxmox.get('api_user', ''),
                api_token_name=proxmox.get('api_token_name', ''),
                api_token_secret=proxmox.get('api_token_secret', ''),
            )

    # --- Stage hooks ---

    def on(self, stage: str, hook: Callable) -> None:
        """Register a hook for a pipeline stage."""
        if stage in self._stage_hooks:
            self._stage_hooks[stage].append(hook)

    def _run_hooks(self, hook_name: str, **kwargs) -> None:
        for hook in self._stage_hooks.get(hook_name, []):
            try:
                hook(**kwargs)
            except Exception as e:
                print(f"Hook error on {hook_name}: {e}")

    # --- Pipeline stages ---

    def _stage_discover(self) -> dict:
        """Stage 1: Run Proxmox discovery."""
        if not self.discoverer:
            return {'error': 'Proxmox discoverer not configured'}
        result = self.discoverer.discover_all()
        # Store discovered data for downstream stages
        result['_discovered_at'] = datetime.now().isoformat()
        result['_pipeline_stage'] = 'discover'
        return result

    def _stage_verify(self, discover_result: dict) -> dict:
        """Stage 2: Verify discovered services."""
        services = discover_result.get('services', [])
        verify_results = {
            'total': len(services),
            'up': 0,
            'down': 0,
            'degraded': 0,
            'unknown': 0,
            'details': [],
        }
        for svc in services:
            result = self.verifier.verify_service(svc)
            verify_results['details'].append({
                'service_id': svc['id'],
                'name': svc['name'],
                'port': svc.get('port'),
                'url': svc.get('url'),
                **result,
            })
            status = result.get('status', 'unknown')
            if status == 'up':
                verify_results['up'] += 1
            elif status == 'degraded':
                verify_results['degraded'] += 1
            elif status == 'down':
                verify_results['down'] += 1
            else:
                verify_results['unknown'] += 1
        verify_results['_pipeline_stage'] = 'verify'
        return verify_results

    def _stage_analyze(self, discover_result: dict,
                       verify_result: dict) -> dict:
        """Stage 3: Build knowledge graph relationships."""
        relationships_created = 0
        # Link servers to their containers
        for server in discover_result.get('servers', []):
            for container in discover_result.get('containers', []):
                if container.get('server_id') == server.get('id'):
                    self.kgm.create_relationship(
                        'server', str(server['id']),
                        'container', str(container['id']),
                        'hosts',
                        {'discovered_at': discover_result.get('_discovered_at')},
                    )
                    relationships_created += 1
        # Link containers to their services
        for container in discover_result.get('containers', []):
            for svc in discover_result.get('services', []):
                if svc.get('container_id') == container.get('id'):
                    self.kgm.create_relationship(
                        'container', str(container['id']),
                        'service', str(svc['id']),
                        'runs',
                        {'discovered_at': discover_result.get('_discovered_at')},
                    )
                    relationships_created += 1
        # Link services to monitoring
        for svc in discover_result.get('services', []):
            if svc.get('prometheus_job'):
                self.kgm.create_relationship(
                    'service', str(svc['id']),
                    'service', 'prometheus',
                    'monitored_by',
                    {'job': svc['prometheus_job']},
                )
                relationships_created += 1
        return {
            'relationships_created': relationships_created,
            'graph_summary': self.kgm.get_graph_summary(),
            '_pipeline_stage': 'analyze',
        }

    def _stage_document(self, discover_result: dict,
                        verify_result: dict,
                        analyze_result: dict) -> dict:
        """Stage 4: Generate wiki documentation."""
        doc_ids = []
        # Generate docs for each discovered entity type
        for server in discover_result.get('servers', []):
            doc_ids.append(self.writer.generate_document('server', server))
        for container in discover_result.get('containers', []):
            doc_ids.append(self.writer.generate_document('container', container))
        for svc in discover_result.get('services', []):
            doc_ids.append(self.writer.generate_document('service', svc))
        # Generate summary docs
        doc_ids.append(self.writer.generate_document(
            'discovery_summary', discover_result))
        doc_ids.append(self.writer.generate_document(
            'health_report', verify_result))
        return {
            'documents_created': len(doc_ids),
            'document_ids': doc_ids,
            '_pipeline_stage': 'document',
        }

    def _stage_alert(self, discover_result: dict, verify_result: dict,
                     analyze_result: dict) -> List[dict]:
        """Stage 5: Generate alerts from verification results."""
        report = self.verifier.generate_health_report()
        # Override with our verify results
        report['services'] = {
            'total': verify_result['total'],
            'up': verify_result['up'],
            'down': verify_result['down'],
            'degraded': verify_result['degraded'],
            'unknown': verify_result['unknown'],
        }
        report['service_details'] = verify_result['details']
        alerts = self.verifier.check_alerts(report)
        # Also check for new alerts from verification
        for detail in verify_result.get('details', []):
            if detail.get('status') == 'down':
                # Find the service name from discover_result
                svc_name = 'unknown'
                for svc in discover_result.get('services', []):
                    if svc['id'] == detail.get('service_id'):
                        svc_name = svc['name']
                        break
                alerts.append({
                    'type': 'service_down',
                    'severity': 'warning',
                    'message': f"Service {svc_name} is down",
                    'timestamp': datetime.now().isoformat(),
                })
        return alerts

    # --- Pipeline execution ---

    def run(self, blocking: bool = True) -> dict:
        """Execute the full discovery pipeline."""
        result = {
            'started_at': datetime.now().isoformat(),
            'stages': {},
            'alerts': [],
            'errors': [],
        }

        try:
            # Stage 1: Discover
            self._run_hooks('pre_discover')
            discover_result = self._stage_discover()
            if 'error' in discover_result:
                result['errors'].append({
                    'stage': 'discover',
                    'error': discover_result['error'],
                })
                self._run_hooks('on_error', stage='discover', error=discover_result['error'])
                result['stages']['discover'] = discover_result
                # Continue pipeline with empty results for downstream stages
                discover_result = {'servers': [], 'containers': [], 'services': [], 'errors': []}
                self._run_hooks('post_discover', result=discover_result)
                result['stages']['discover'] = discover_result

                # Stage 2: Verify
                self._run_hooks('pre_verify')
                verify_result = self._stage_verify(discover_result)
                self._run_hooks('post_verify', result=verify_result)
                result['stages']['verify'] = verify_result

                # Stage 3: Analyze
                self._run_hooks('pre_analyze')
                analyze_result = self._stage_analyze(discover_result, verify_result)
                self._run_hooks('post_analyze', result=analyze_result)
                result['stages']['analyze'] = analyze_result

                # Stage 4: Document
                self._run_hooks('pre_document')
                doc_result = self._stage_document(
                    discover_result, verify_result, analyze_result)
                self._run_hooks('post_document', result=doc_result)
                result['stages']['document'] = doc_result

                # Stage 5: Alert
                self._run_hooks('pre_alert')
                alerts = self._stage_alert(discover_result, verify_result, analyze_result)
                self._run_hooks('post_alert', alerts=alerts)
                result['alerts'] = alerts

                self._run_hooks('on_complete', result=result)
                result['finished_at'] = datetime.now().isoformat()
                return result
            self._run_hooks('post_discover', result=discover_result)
            result['stages']['discover'] = discover_result

            # Stage 2: Verify
            self._run_hooks('pre_verify')
            verify_result = self._stage_verify(discover_result)
            self._run_hooks('post_verify', result=verify_result)
            result['stages']['verify'] = verify_result

            # Stage 3: Analyze
            self._run_hooks('pre_analyze')
            analyze_result = self._stage_analyze(discover_result, verify_result)
            self._run_hooks('post_analyze', result=analyze_result)
            result['stages']['analyze'] = analyze_result

            # Stage 4: Document
            self._run_hooks('pre_document')
            doc_result = self._stage_document(
                discover_result, verify_result, analyze_result)
            self._run_hooks('post_document', result=doc_result)
            result['stages']['document'] = doc_result

            # Stage 5: Alert
            self._run_hooks('pre_alert')
            alerts = self._stage_alert(discover_result, verify_result, analyze_result)
            self._run_hooks('post_alert', alerts=alerts)
            result['alerts'] = alerts

            # Complete
            self._run_hooks('on_complete', result=result)

        except Exception as e:
            result['errors'].append({
                'stage': 'pipeline',
                'error': str(e),
            })
            self._run_hooks('on_error', stage='pipeline', error=str(e))

        result['finished_at'] = datetime.now().isoformat()
        return result

    def run_async(self) -> threading.Thread:
        """Run the pipeline in a background thread."""
        self._running = True
        thread = threading.Thread(
            target=self._run_async_loop, daemon=True)
        thread.start()
        self._thread = thread
        return thread

    def _run_async_loop(self) -> None:
        """Background loop for periodic discovery."""
        interval = self.config.get('discovery_interval', 300)
        while self._running:
            try:
                self.run()
            except Exception as e:
                print(f"Pipeline error: {e}")
            for _ in range(interval * 10):
                if not self._running:
                    break
                threading.Event().wait(0.1)

    def stop(self) -> None:
        """Stop the background loop."""
        self._running = False

    # --- Incremental discovery ---

    def discover_incremental(self) -> dict:
        """Discover only changed entities since last run."""
        if not self.discoverer:
            return {'error': 'Proxmox discoverer not configured'}

        # Get current state
        existing_servers = {s['hostname']: s for s in self.state.list_servers()}
        existing_containers = {
            c['vmid']: c for c in self.state.list_containers()
        }

        # Run discovery
        result = self.discoverer.discover_all()

        # Track changes
        changes = {
            'servers_added': [],
            'servers_updated': [],
            'containers_added': [],
            'containers_updated': [],
            'services_added': [],
            'services_updated': [],
            'services_removed': [],
        }

        # Compare servers
        for server in result.get('servers', []):
            hostname = server['hostname']
            if hostname not in existing_servers:
                changes['servers_added'].append(server)
            else:
                old = existing_servers[hostname]
                if (old.get('status') != server.get('status') or
                        old.get('last_verified') != server.get('last_verified')):
                    changes['servers_updated'].append(server)

        # Compare containers
        for container in result.get('containers', []):
            vmid = container['vmid']
            if vmid not in existing_containers:
                changes['containers_added'].append(container)
            else:
                old = existing_containers[vmid]
                if old.get('status') != container.get('status'):
                    changes['containers_updated'].append(container)

        # Compare services
        existing_services = {
            s['name']: s for s in self.state.list_services()
        }
        discovered_services = {
            (s['name'], s.get('port')): s
            for s in result.get('services', [])
        }
        for key, svc in discovered_services.items():
            if key not in existing_services:
                changes['services_added'].append(svc)
            else:
                old = existing_services[key]
                if old.get('status') != svc.get('status'):
                    changes['services_updated'].append(svc)

        # Detect removed services
        for key, old_svc in existing_services.items():
            if key not in discovered_services:
                changes['services_removed'].append(old_svc)

        changes['_pipeline_stage'] = 'incremental_discover'
        return changes

    # --- Status ---

    def get_pipeline_status(self) -> dict:
        """Get the current status of the pipeline."""
        return {
            'running': self._running,
            'discoverer_configured': self.discoverer is not None,
            'servers_count': len(self.state.list_servers()),
            'containers_count': len(self.state.list_containers()),
            'services_count': len(self.state.list_services()),
            'graph_summary': self.kgm.get_graph_summary(),
            'wiki_docs_count': len(self.writer.get_generated_docs()),
        }
