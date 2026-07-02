#!/usr/bin/env python3
"""GRID Wiki HTTP Server with agent query interface and interaction logging."""
import http.server
import os
import json
import glob
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Configuration
PORT = 8082
WIKI_DIR = Path(os.environ.get('WIKI_DIR', '/srv/grid-wiki'))
WIKI_CONTENT_DIR = Path(os.environ.get('WIKI_CONTENT_DIR', '/srv/grid-wiki-tool/wiki-content'))
DASHBOARD_DIR = Path(os.environ.get('DASHBOARD_DIR', '/srv/grid-wiki-tool/dashboard'))
WIKI_INDEX_PATH = DASHBOARD_DIR / 'wiki-index.json'

class WikiServer:
    """GRID Wiki server with agent query and interaction logging."""
    
    def __init__(self, wiki_dir=None, wiki_content_dir=None):
        self.wiki_dir = Path(wiki_dir) if wiki_dir else WIKI_DIR
        self.wiki_content_dir = Path(wiki_content_dir) if wiki_content_dir else WIKI_CONTENT_DIR
        self.dashboard_dir = Path(os.environ.get('DASHBOARD_DIR', '/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki/tool/dashboard'))
        self.wiki_index_path = self.dashboard_dir / 'wiki-index.json'
        
    def query_wiki(self, query: str) -> dict:
        """Query wiki for relevant pages."""
        results = []
        query_lower = query.lower()
        
        # Search in wiki-content
        for page_path in self.wiki_content_dir.rglob('*.md'):
            content = page_path.read_text()
            if query_lower in content.lower():
                results.append({
                    'title': page_path.stem,
                    'path': str(page_path.relative_to(self.wiki_content_dir.parent)),
                    'content': content[:500],
                    'score': self._calculate_relevance(content, query_lower)
                })
        
        # Search in wiki directory
        if self.wiki_dir.exists():
            for page_path in self.wiki_dir.rglob('*.md'):
                content = page_path.read_text()
                if query_lower in content.lower():
                    results.append({
                        'title': page_path.stem,
                        'path': str(page_path.relative_to(self.wiki_dir.parent)),
                        'content': content[:500],
                        'score': self._calculate_relevance(content, query_lower)
                    })
        
        # Sort by relevance score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'query': query,
            'results': results,
            'count': len(results)
        }
    
    def _calculate_relevance(self, content: str, query: str) -> int:
        """Calculate relevance score for a page."""
        score = 0
        # Title match (highest priority)
        title = Path(content.split('\n')[0] if content.startswith('#') else content.split('#')[1].split('\n')[0] if '#' in content else '').strip()
        if query in title.lower():
            score += 100
        # Content match
        score += content.lower().count(query) * 10
        # Frontmatter match
        if '---' in content:
            frontmatter = content.split('---')[1]
            if query in frontmatter.lower():
                score += 50
        return score
    
    def log_agent_interaction(self, agent: str, action: str, result: str) -> bool:
        """Log agent interaction to wiki."""
        log_path = self.wiki_content_dir / 'wiki' / 'AGENT-INTERACTIONS.md'
        timestamp = datetime.now().isoformat()
        
        # Ensure directory exists
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create log file if it doesn't exist
        if not log_path.exists():
            log_path.write_text(f"""---
title: "Agent Interactions"
type: log
last_updated: "{timestamp}"
---

# Agent Interactions

## Discovery Scans
| Timestamp | Agent | Action | Result |
| --- | --- | --- | --- |
""")
        
        with open(log_path, 'a') as f:
            f.write(f"| {timestamp} | {agent} | {action} | {result} |\n")
        
        return True
    
    def get_wiki_index(self) -> dict:
        """Get wiki page index."""
        if self.wiki_index_path.exists():
            return json.loads(self.wiki_index_path.read_text())
        
        # Generate index
        pages = []
        for page_path in self.wiki_content_dir.rglob('*.md'):
            content = page_path.read_text()
            frontmatter = {}
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    for line in parts[1].strip().split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            frontmatter[key.strip()] = value.strip().strip('"').strip("'")
            
            pages.append({
                'slug': page_path.stem,
                'title': frontmatter.get('title', page_path.stem),
                'path': str(page_path.relative_to(self.wiki_content_dir.parent)),
                'category': frontmatter.get('category', 'uncategorized'),
                'tags': frontmatter.get('tags', '[]'),
                'status': frontmatter.get('status', 'active'),
                'last_updated': frontmatter.get('last_updated', datetime.now().strftime('%Y-%m-%d')),
                'size_bytes': page_path.stat().st_size
            })
        
        return {
            'pages': pages,
            'generated_at': datetime.now().isoformat() + 'Z'
        }
    
    def get_monitoring_status(self) -> dict:
        """Get monitoring status."""
        grid_status_path = self.wiki_content_dir / 'sites' / 'grid' / 'monitoring-status.json'
        if grid_status_path.exists():
            return json.loads(grid_status_path.read_text())
        return {'error': 'Monitoring status not found'}
    
    def get_drift_reports(self) -> list:
        """Get drift reports."""
        drift_dir = self.wiki_content_dir / 'sync' / 'drift'
        if not drift_dir.exists():
            return []
        
        reports = []
        for report_path in sorted(drift_dir.glob('*.json'), reverse=True):
            reports.append(json.loads(report_path.read_text()))
        return reports
    
    def get_kanban_cards(self, column: str = 'all') -> dict:
        """Get kanban cards."""
        kanban_dir = self.wiki_content_dir / 'change-kanban'
        if not kanban_dir.exists():
            return {}
        
        cards = {}
        if column == 'all':
            for col in ['pending', 'approved', 'merged']:
                col_dir = kanban_dir / col
                if col_dir.exists():
                    cards[col] = []
                    for card_path in col_dir.glob('*.md'):
                        content = card_path.read_text()
                        frontmatter = {}
                        if content.startswith('---'):
                            parts = content.split('---', 2)
                            if len(parts) >= 3:
                                for line in parts[1].strip().split('\n'):
                                    if ':' in line:
                                        key, value = line.split(':', 1)
                                        frontmatter[key.strip()] = value.strip().strip('"').strip("'")
                        cards[col].append({
                            'id': frontmatter.get('title', card_path.stem).split(':')[0],
                            'description': frontmatter.get('description', ''),
                            'risk': frontmatter.get('risk', 'medium'),
                            'status': frontmatter.get('status', 'pending')
                        })
        else:
            col_dir = kanban_dir / column
            if col_dir.exists():
                cards[column] = []
                for card_path in col_dir.glob('*.md'):
                    content = card_path.read_text()
                    frontmatter = {}
                    if content.startswith('---'):
                        parts = content.split('---', 2)
                        if len(parts) >= 3:
                            for line in parts[1].strip().split('\n'):
                                if ':' in line:
                                    key, value = line.split(':', 1)
                                    frontmatter[key.strip()] = value.strip().strip('"').strip("'")
                    cards[column].append({
                        'id': frontmatter.get('title', card_path.stem).split(':')[0],
                        'description': frontmatter.get('description', ''),
                        'risk': frontmatter.get('risk', 'medium'),
                        'status': frontmatter.get('status', 'pending')
                    })
        
        return cards
    
    def get_active_tasks(self) -> list:
        """Get active tasks."""
        active_tasks_path = self.wiki_content_dir.parent / 'ACTIVE-TASKS.md'
        if not active_tasks_path.exists():
            return []
        
        content = active_tasks_path.read_text()
        tasks = []
        in_table = False
        for line in content.split('\n'):
            if line.startswith('|'):
                in_table = True
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                if len(cells) >= 5 and cells[0] != '':
                    tasks.append({
                        'id': cells[1] if len(cells) > 1 else '',
                        'description': cells[2] if len(cells) > 2 else '',
                        'status': cells[3] if len(cells) > 3 else '',
                        'assignee': cells[4] if len(cells) > 4 else '',
                        'last_updated': cells[5] if len(cells) > 5 else ''
                    })
        return tasks
    
    def get_project_manifest(self) -> dict:
        """Get project manifest."""
        manifest_path = self.wiki_content_dir.parent / 'PROJECT-MANIFEST.md'
        if not manifest_path.exists():
            return {'error': 'Project manifest not found'}
        
        content = manifest_path.read_text()
        manifest = {}
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                for line in parts[1].strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        manifest[key.strip()] = value.strip()
        
        return {
            'title': manifest.get('title', 'PROJECT MANIFEST'),
            'current_goal': manifest.get('current_goal', 'Active'),
            'completed_phases': manifest.get('completed_phases', '[]'),
            'last_updated': manifest.get('last_updated', '')
        }
    
    def get_sites(self) -> list:
        """Get sites overview."""
        sites_dir = self.wiki_content_dir / 'sites'
        if not sites_dir.exists():
            return []
        
        sites = []
        for site_dir in sites_dir.iterdir():
            if site_dir.is_dir():
                monitoring_path = site_dir / 'monitoring-status.json'
                if monitoring_path.exists():
                    monitoring = json.loads(monitoring_path.read_text())
                    sites.append({
                        'name': site_dir.name.upper(),
                        'path': f"sites/{site_dir.name}",
                        'status': 'active',
                        'service_count': len(monitoring.get('services', [])),
                        'monitoring_status': 'configured' if monitoring.get('services') else 'not configured'
                    })
        return sites
    
    def get_dashboard_status(self) -> dict:
        """Get dashboard status."""
        active_tasks = self.get_active_tasks()
        monitoring = self.get_monitoring_status()
        wiki_index = self.get_wiki_index()
        
        return {
            'activeTasks': len(active_tasks),
            'goalProgress': 85,
            'monitoringUp': monitoring.get('prometheus', {}).get('up', 0),
            'monitoringTotal': monitoring.get('prometheus', {}).get('total_targets', 0),
            'wikiPages': len(wiki_index.get('pages', [])),
            'tasks': active_tasks,
            'recentActivity': [
                {
                    'timestamp': datetime.now().isoformat(),
                    'event': 'Dashboard initialized',
                    'details': 'GRID Wiki dashboard ready'
                }
            ]
        }
    
    def export_data(self) -> dict:
        """Export all wiki data."""
        return {
            'wiki_index': self.get_wiki_index(),
            'monitoring_status': self.get_monitoring_status(),
            'drift_reports': self.get_drift_reports(),
            'kanban_cards': self.get_kanban_cards(),
            'sites': self.get_sites(),
            'exported_at': datetime.now().isoformat()
        }


class WikiHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for GRID Wiki."""
    
    server_instance: WikiServer | None = None  # type: ignore[assignment]
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        # API routes
        if path == '/api/dashboard/status':
            result = self.server_instance.get_dashboard_status()
            self._send_json(result)
        elif path == '/api/monitoring-status':
            result = self.server_instance.get_monitoring_status()
            self._send_json(result)
        elif path == '/api/wiki-index':
            result = self.server_instance.get_wiki_index()
            self._send_json(result)
        elif path.startswith('/api/wiki/'):
            slug = path.split('/api/wiki/')[1]
            result = self._get_wiki_page(slug)
            self._send_json(result)
        elif path == '/api/drift-reports':
            result = self.server_instance.get_drift_reports()
            self._send_json(result)
        elif path.startswith('/api/kanban/'):
            column = path.split('/api/kanban/')[1]
            result = self.server_instance.get_kanban_cards(column)
            self._send_json(result)
        elif path == '/api/active-tasks':
            result = self.server_instance.get_active_tasks()
            self._send_json(result)
        elif path == '/api/project-manifest':
            result = self.server_instance.get_project_manifest()
            self._send_json(result)
        elif path == '/api/sites':
            result = self.server_instance.get_sites()
            self._send_json(result)
        elif path == '/api/export':
            result = self.server_instance.export_data()
            self._send_json(result)
        elif path == '/api/agent/query':
            query = query_params.get('q', [''])[0]
            if not query:
                self._send_error(400, 'Missing query parameter "q"')
                return
            result = self.server_instance.query_wiki(query)
            self._send_json(result)
            self.server_instance.log_agent_interaction('dashboard', f'query: {query}', f'Found {result["count"]} results')
        elif path == '/api/settings':
            self._send_json({
                'wikiRoot': str(self.server_instance.wiki_content_dir),
                'theme': 'light',
                'autoRefresh': 30,
                'language': 'en'
            })
        else:
            # Serve static files from dashboard directory
            if path == '/':
                path = '/index.html'
            
            file_path = self.server_instance.dashboard_dir / path.lstrip('/')
            if file_path.exists() and file_path.is_file():
                content_type = self._get_content_type(file_path.suffix)
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, f"File not found: {path}")
    
    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/settings':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            settings = json.loads(body)
            self._send_json({'status': 'saved', 'settings': settings})
        elif path == '/api/drift/check':
            self.server_instance.log_agent_interaction('dashboard', 'drift-check', 'Drift check initiated')
            self._send_json({'status': 'started', 'message': 'Drift check initiated'})
        elif path == '/api/discovery/start':
            self.server_instance.log_agent_interaction('dashboard', 'discovery', 'Discovery started')
            self._send_json({'status': 'started', 'message': 'Discovery started'})
        else:
            self.send_error(404, f"Endpoint not found: {path}")
    
    def _get_wiki_page(self, slug: str) -> dict:
        """Get a wiki page by slug."""
        # Search in wiki-content
        for page_path in self.server_instance.wiki_content_dir.rglob('*.md'):
            if page_path.stem.lower() == slug.lower():
                content = page_path.read_text()
                return {
                    'slug': slug,
                    'title': page_path.stem,
                    'content': content,
                    'path': str(page_path)
                }
        
        # Search in wiki directory
        if self.server_instance.wiki_dir.exists():
            for page_path in self.server_instance.wiki_dir.rglob('*.md'):
                if page_path.stem.lower() == slug.lower():
                    content = page_path.read_text()
                    return {
                        'slug': slug,
                        'title': page_path.stem,
                        'content': content,
                        'path': str(page_path)
                    }
        
        return {'error': f'Page not found: {slug}'}
    
    def _send_json(self, data: dict):
        """Send JSON response."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def _send_error(self, code: int, message: str):
        """Send error response."""
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode())
    
    def _get_content_type(self, extension: str) -> str:
        """Get content type for file extension."""
        content_types = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.svg': 'image/svg+xml',
        }
        return content_types.get(extension, 'application/octet-stream')
    
    def log_message(self, format, *args):
        """Suppress request logs."""
        pass


def main():
    """Start the wiki server."""
    server_instance = WikiServer()
    WikiHandler.server_instance = server_instance
    
    server = http.server.HTTPServer(('0.0.0.0', PORT), WikiHandler)
    print(f"GRID Wiki server running on http://0.0.0.0:{PORT}")
    print(f"Dashboard: http://localhost:{PORT}/")
    print(f"API: http://localhost:{PORT}/api/dashboard/status")
    print(f"Wiki Index: http://localhost:{PORT}/api/wiki-index")
    print(f"Monitoring: http://localhost:{PORT}/api/monitoring-status")
    print(f"Agent Query: http://localhost:{PORT}/api/agent/query?q=grid")
    server.serve_forever()


if __name__ == '__main__':
    main()
