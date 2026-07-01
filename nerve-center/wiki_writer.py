"""nerve-center/wiki_writer.py — Generate wiki docs from discovered data."""

import json
from datetime import datetime
from typing import List, Dict, Optional


class WikiWriter:
    def __init__(self, state_manager, knowledge_graph=None) -> None:
        self.state = state_manager
        self.kgm = knowledge_graph
        self._templates: Dict[str, callable] = {}
        self._register_builtins()

    def _register_builtins(self) -> None:
        """Register built-in document generators."""
        self._templates['server'] = self._generate_server_doc
        self._templates['container'] = self._generate_container_doc
        self._templates['service'] = self._generate_service_doc
        self._templates['health_report'] = self._generate_health_report_doc
        self._templates['relationship'] = self._generate_relationship_doc
        self._templates['discovery_summary'] = self._generate_discovery_summary_doc

    # --- Document generation ---

    def generate_document(self, doc_type: str, data: dict,
                          source: str = 'agent-generated') -> int:
        """Generate a wiki document from structured data."""
        if doc_type not in self._templates:
            raise ValueError(f"Unknown document type: {doc_type}")
        content = self._templates[doc_type](data)
        slug = f"generated:{doc_type}:{data.get('id', data.get('name', ''))}"
        wiki_doc = {
            'title': content.get('title', f'{doc_type} documentation'),
            'slug': slug,
            'category': doc_type,
            'content': json.dumps(content.get('body', content)),
            'source': source,
            'status': 'active',
            'version': 1,
            'entity_type': doc_type,
            'entity_id': str(data.get('id', data.get('name', ''))),
            'last_updated': datetime.now().isoformat(),
        }
        # Check if document exists
        existing = self.state.get_wiki_document_by_slug(slug)
        if existing:
            self.state.update_wiki_document(existing['id'], {
                'content': wiki_doc['content'],
                'updated_at': wiki_doc['last_updated'],
            })
            return existing['id']
        return self.state.create_wiki_document(wiki_doc)

    def generate_bulk(self, doc_type: str, items: List[dict],
                      source: str = 'agent-generated') -> List[int]:
        """Generate multiple wiki documents."""
        ids = []
        for item in items:
            try:
                doc_id = self.generate_document(doc_type, item, source)
                ids.append(doc_id)
            except Exception as e:
                print(f"Failed to generate {doc_type} doc for {item.get('name', item.get('id'))}: {e}")
        return ids

    # --- Built-in generators ---

    def _generate_server_doc(self, data: dict) -> dict:
        """Generate server documentation."""
        return {
            'title': f"Server: {data.get('hostname', 'Unknown')}",
            'body': {
                'hostname': data.get('hostname', ''),
                'ip_address': data.get('ip_address', ''),
                'proxmox_api_url': data.get('proxmox_api_url', ''),
                'status': data.get('status', 'unknown'),
                'last_discovered': data.get('last_discovered', ''),
                'last_verified': data.get('last_verified', ''),
                'containers': [],
                'services': [],
            },
        }

    def _generate_container_doc(self, data: dict) -> dict:
        """Generate container documentation."""
        return {
            'title': f"Container: {data.get('name', 'Unknown')} (VMID: {data.get('vmid', 'N/A')})",
            'body': {
                'name': data.get('name', ''),
                'vmid': data.get('vmid', 0),
                'type': data.get('type', 'lxc'),
                'status': data.get('status', 'unknown'),
                'ip_addresses': data.get('ip_addresses', []),
                'memory_mb': data.get('memory_mb', 0),
                'cpu_cores': data.get('cpu_cores', 0),
                'disk_total_mb': data.get('disk_total_mb', 0),
                'disk_used_mb': data.get('disk_used_mb', 0),
                'os': data.get('os', 'unknown'),
                'server_id': data.get('server_id', 0),
            },
        }

    def _generate_service_doc(self, data: dict) -> dict:
        """Generate service documentation."""
        return {
            'title': f"Service: {data.get('name', 'Unknown')} ({data.get('type', '')}:{data.get('port', '')})",
            'body': {
                'name': data.get('name', ''),
                'type': data.get('type', ''),
                'port': data.get('port', 0),
                'protocol': data.get('protocol', 'tcp'),
                'url': data.get('url', ''),
                'status': data.get('status', 'unknown'),
                'response_time_ms': data.get('response_time_ms'),
                'container_id': data.get('container_id', 0),
                'prometheus_job': data.get('prometheus_job'),
                'prometheus_target': data.get('prometheus_target'),
                'monitoring_configured': data.get('monitoring_configured', 0),
                'caddy_configured': data.get('caddy_configured', 0),
                'health_check_url': data.get('health_check_url'),
                'health_check_interval': data.get('health_check_interval'),
                'last_checked': data.get('last_checked', ''),
            },
        }

    def _generate_health_report_doc(self, data: dict) -> dict:
        """Generate a health report wiki document."""
        services = data.get('services', {})
        servers = data.get('servers', {})
        containers = data.get('containers', {})
        return {
            'title': f"Health Report: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            'body': {
                'generated_at': data.get('generated_at', datetime.now().isoformat()),
                'summary': {
                    'servers_up': servers.get('up', 0),
                    'servers_down': servers.get('down', 0),
                    'servers_total': servers.get('total', 0),
                    'containers_running': containers.get('running', 0),
                    'containers_stopped': containers.get('stopped', 0),
                    'containers_total': containers.get('total', 0),
                    'services_up': services.get('up', 0),
                    'services_down': services.get('down', 0),
                    'services_degraded': services.get('degraded', 0),
                    'services_unknown': services.get('unknown', 0),
                    'services_total': services.get('total', 0),
                },
                'service_details': data.get('service_details', []),
                'ssl_certificates': data.get('ssl_certificates', []),
                'connected_components': data.get('connected_components', 0),
            },
        }

    def _generate_relationship_doc(self, data: dict) -> dict:
        """Generate relationship documentation."""
        return {
            'title': f"Relationship: {data.get('source_id', '')} --{data.get('relationship_type', '')}--> {data.get('target_id', '')}",
            'body': {
                'source_type': data.get('source_type', ''),
                'source_id': data.get('source_id', ''),
                'target_type': data.get('target_type', ''),
                'target_id': data.get('target_id', ''),
                'relationship_type': data.get('relationship_type', ''),
                'properties': data.get('properties', {}),
                'created_at': data.get('created_at', ''),
            },
        }

    def _generate_discovery_summary_doc(self, data: dict) -> dict:
        """Generate a discovery summary wiki document."""
        servers = data.get('servers', [])
        containers = data.get('containers', [])
        services = data.get('services', [])
        return {
            'title': f"Discovery Summary: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            'body': {
                'generated_at': datetime.now().isoformat(),
                'summary': {
                    'servers_discovered': len(servers),
                    'containers_discovered': len(containers),
                    'services_discovered': len(services),
                },
                'servers': [{'hostname': s.get('hostname'), 'status': s.get('status')} for s in servers],
                'containers': [{'name': c.get('name'), 'status': c.get('status'), 'vmid': c.get('vmid')} for c in containers],
                'services': [{'name': s.get('name'), 'port': s.get('port'), 'status': s.get('status')} for s in services],
                'errors': data.get('errors', []),
            },
        }

    # --- Template management ---

    def register_template(self, doc_type: str,
                          generator: callable) -> None:
        """Register a custom document generator."""
        self._templates[doc_type] = generator

    def list_templates(self) -> List[str]:
        """List all available document types."""
        return list(self._templates.keys())

    # --- Document retrieval ---

    def get_generated_docs(self, doc_type: str = None) -> List[dict]:
        """Get all generated wiki documents, optionally filtered by type."""
        docs = self.state.get_wiki_documents()
        if doc_type:
            docs = [d for d in docs if d.get('category') == doc_type or d.get('entity_type') == doc_type]
        return docs

    def get_document_by_slug(self, slug: str) -> Optional[dict]:
        """Get a wiki document by slug."""
        return self.state.get_wiki_document_by_slug(slug)

    # --- Change tracking ---

    def track_changes(self, doc_type: str, data: dict,
                      previous_data: Optional[dict] = None) -> dict:
        """Track changes in discovered data and generate a diff doc."""
        changes = []
        if previous_data:
            for key in set(list(data.keys()) + list(previous_data.keys())):
                old_val = previous_data.get(key)
                new_val = data.get(key)
                if old_val != new_val:
                    changes.append({
                        'field': key,
                        'old_value': old_val,
                        'new_value': new_val,
                    })
        if changes:
            change_doc = {
                'title': f"Change Log: {doc_type} {data.get('name', data.get('hostname', ''))}",
                'slug': f"changes:{doc_type}:{data.get('name', data.get('hostname', ''))}",
                'category': 'change_log',
                'content': json.dumps({
                    'doc_type': doc_type,
                    'entity_id': data.get('id', data.get('name', '')),
                    'changes': changes,
                    'timestamp': datetime.now().isoformat(),
                }),
                'source': 'wiki-writer',
                'status': 'active',
                'version': 1,
                'entity_type': 'change_log',
                'entity_id': f"{doc_type}:{data.get('name', data.get('hostname', ''))}",
                'last_updated': datetime.now().isoformat(),
            }
            existing = self.state.get_wiki_document_by_slug(change_doc['slug'])
            if existing:
                self.state.update_wiki_document(existing['id'], {
                    'content': change_doc['content'],
                    'updated_at': change_doc['last_updated'],
                })
                return {'created': False, 'doc_id': existing['id']}
            doc_id = self.state.create_wiki_document(change_doc)
            return {'created': True, 'doc_id': doc_id}
        return {'created': False, 'doc_id': None}
