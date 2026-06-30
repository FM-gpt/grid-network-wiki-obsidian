"""nerve-center/state.py — SQLite state manager for GRID Network Nerve Center."""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any


class StateManager:
    def __init__(self, db_path: Optional[str] = None) -> None:
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'nerve-center.db')
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database from schema.sql."""
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path) as f:
            schema = f.read()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript(schema)
            conn.commit()

    # --- Servers ---

    def get_server(self, hostname: str) -> Optional[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute("SELECT * FROM servers WHERE hostname = ?", (hostname,))
            row = cur.fetchone()
            return dict(row) if row else None

    def upsert_server(self, server: dict) -> int:
        """Insert or update server. Returns server_id."""
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute("""
                INSERT OR REPLACE INTO servers
                    (hostname, ip_address, proxmox_api_url,
                     proxmox_api_user, proxmox_api_token_name, proxmox_api_token_secret,
                     status, last_discovered, last_verified, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                RETURNING id
            """, (
                server['hostname'],
                server['ip_address'],
                server.get('proxmox_api_url', ''),
                server.get('proxmox_api_user', ''),
                server.get('proxmox_api_token_name', ''),
                server.get('proxmox_api_token_secret', ''),
                server.get('status', 'unknown'),
                server.get('last_discovered'),
                server.get('last_verified'),
                datetime.now().isoformat(),
            ))
            result = cur.fetchone()[0]
            conn.commit()
            return result
        finally:
            conn.close()

    def list_servers(self) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute("SELECT * FROM servers ORDER BY hostname")
            return [dict(r) for r in cur.fetchall()]

    # --- Containers ---

    def get_container(self, vmid: int) -> Optional[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute("SELECT * FROM containers WHERE vmid = ?", (vmid,))
            row = cur.fetchone()
            return dict(row) if row else None

    def upsert_container(self, container: dict) -> int:
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute("""
                INSERT OR REPLACE INTO containers
                    (server_id, vmid, name, type, status,
                     ip_addresses, memory_mb, cpu_cores,
                     disk_total_mb, disk_used_mb,
                     os, template,
                     last_discovered, last_verified, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                RETURNING id
            """, (
                container['server_id'],
                container['vmid'],
                container['name'],
                container['type'],
                container.get('status', 'unknown'),
                json.dumps(container.get('ip_addresses', [])),
                container.get('memory_mb'),
                container.get('cpu_cores'),
                container.get('disk_total_mb'),
                container.get('disk_used_mb'),
                container.get('os'),
                container.get('template'),
                container.get('last_discovered'),
                container.get('last_verified'),
                datetime.now().isoformat(),
            ))
            result = cur.fetchone()[0]
            conn.commit()
            return result
        finally:
            conn.close()

    def list_containers(self, server_id: int = None) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if server_id:
                cur = conn.execute(
                    "SELECT * FROM containers WHERE server_id = ? ORDER BY vmid",
                    (server_id,),
                )
            else:
                cur = conn.execute("SELECT * FROM containers ORDER BY server_id, vmid")
            return [dict(r) for r in cur.fetchall()]

    def get_server_containers(self, server_id: int) -> List[dict]:
        return self.list_containers(server_id)

    # --- Services ---

    def get_service(self, service_id: int) -> Optional[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute("SELECT * FROM services WHERE id = ?", (service_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def upsert_service(self, service: dict) -> int:
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute("""
                INSERT OR REPLACE INTO services
                    (container_id, name, type, port, protocol,
                     url, status, response_time_ms, last_checked,
                     prometheus_job, prometheus_target,
                     monitoring_configured, caddy_configured,
                     health_check_url, health_check_interval, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                RETURNING id
            """, (
                service['container_id'],
                service['name'],
                service['type'],
                service.get('port'),
                service.get('protocol', 'tcp'),
                service.get('url'),
                service.get('status', 'unknown'),
                service.get('response_time_ms'),
                service.get('last_checked'),
                service.get('prometheus_job'),
                service.get('prometheus_target'),
                service.get('monitoring_configured', 0),
                service.get('caddy_configured', 0),
                service.get('health_check_url'),
                service.get('health_check_interval'),
                datetime.now().isoformat(),
            ))
            result = cur.fetchone()[0]
            conn.commit()
            return result
        finally:
            conn.close()

    def list_services(self, container_id: int = None, type: str = None, status: str = None) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT * FROM services WHERE 1=1"
            params = []
            if container_id is not None:
                query += " AND container_id = ?"
                params.append(container_id)
            if type is not None:
                query += " AND type = ?"
                params.append(type)
            if status is not None:
                query += " AND status = ?"
                params.append(status)
            query += " ORDER BY name"
            cur = conn.execute(query, params)
            return [dict(r) for r in cur.fetchall()]

    def update_service_status(self, service_id: int, status: str, response_time_ms: int = None) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE services SET status = ?, response_time_ms = ?, last_checked = ?, updated_at = ? WHERE id = ?",
                (status, response_time_ms, datetime.now().isoformat(), datetime.now().isoformat(), service_id),
            )
            conn.commit()
            return True

    def get_container_services(self, container_id: int) -> List[dict]:
        return self.list_services(container_id=container_id)

    def get_service_relationships(self, service_id: int) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                "SELECT sr.*, s.name as target_name, s.type as target_type "
                "FROM service_relationships sr "
                "JOIN services s ON sr.target_service_id = s.id "
                "WHERE sr.source_service_id = ? "
                "UNION ALL "
                "SELECT sr.*, s.name as target_name, s.type as target_type "
                "FROM service_relationships sr "
                "JOIN services s ON sr.source_service_id = s.id "
                "WHERE sr.target_service_id = ?",
                (service_id, service_id),
            )
            return [dict(r) for r in cur.fetchall()]

    def create_relationship(self, source_id: int, target_id: int, relationship_type: str) -> int:
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute(
                "INSERT OR IGNORE INTO service_relationships "
                "(source_service_id, target_service_id, relationship_type) "
                "VALUES (?, ?, ?) RETURNING id",
                (source_id, target_id, relationship_type),
            )
            row = cur.fetchone()
            conn.commit()
            return row[0] if row else None
        finally:
            conn.close()

    def delete_relationship(self, source_id: int, target_id: int, relationship_type: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM service_relationships "
                "WHERE source_service_id = ? AND target_service_id = ? AND relationship_type = ?",
                (source_id, target_id, relationship_type),
            )
            conn.commit()
            return True

    # --- Wiki Documents ---

    def create_wiki_document(self, doc: dict) -> int:
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute(
                "INSERT INTO wiki_documents "
                "(title, slug, category, content, source, "
                "related_service_id, related_container_id, last_updated) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?) RETURNING id",
                (
                    doc['title'],
                    doc['slug'],
                    doc['category'],
                    doc['content'],
                    doc.get('source', 'agent-generated'),
                    doc.get('related_service_id'),
                    doc.get('related_container_id'),
                    doc.get('last_updated', datetime.now().isoformat()),
                ),
            )
            result = cur.fetchone()[0]
            conn.commit()
            return result
        finally:
            conn.close()

    def get_wiki_documents(self, category: str = None, related_service_id: int = None) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT id, title, slug, category, source, related_service_id, last_updated FROM wiki_documents WHERE 1=1"
            params = []
            if category is not None:
                query += " AND category = ?"
                params.append(category)
            if related_service_id is not None:
                query += " AND related_service_id = ?"
                params.append(related_service_id)
            query += " ORDER BY last_updated DESC"
            cur = conn.execute(query, params)
            return [dict(r) for r in cur.fetchall()]

    def get_wiki_document_by_slug(self, slug: str) -> Optional[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute("SELECT * FROM wiki_documents WHERE slug = ?", (slug,))
            row = cur.fetchone()
            return dict(row) if row else None

    # --- Agent Actions ---

    def create_agent_action(self, action: dict) -> int:
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute(
                "INSERT INTO agent_actions "
                "(agent_id, action_type, target_type, target_id, status, details, started_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING id",
                (
                    action['agent_id'],
                    action['action_type'],
                    action['target_type'],
                    action.get('target_id'),
                    action.get('status', 'pending'),
                    json.dumps(action.get('details', {})),
                    action.get('started_at', datetime.now().isoformat()),
                ),
            )
            result = cur.fetchone()[0]
            conn.commit()
            return result
        finally:
            conn.close()

    def get_agent_actions(self, status: str = None, type: str = None) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT * FROM agent_actions WHERE 1=1"
            params = []
            if status is not None:
                query += " AND status = ?"
                params.append(status)
            if type is not None:
                query += " AND action_type = ?"
                params.append(type)
            query += " ORDER BY created_at DESC LIMIT 100"
            cur = conn.execute(query, params)
            return [dict(r) for r in cur.fetchall()]

    # --- User Requests ---

    def create_user_request(self, request: dict) -> int:
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute(
                "INSERT INTO user_requests "
                "(user_id, request_type, title, description, status) "
                "VALUES (?, ?, ?, ?, ?) RETURNING id",
                (
                    request['user_id'],
                    request['request_type'],
                    request['title'],
                    request.get('description', ''),
                    'pending',
                ),
            )
            result = cur.fetchone()[0]
            conn.commit()
            return result
        finally:
            conn.close()

    def get_user_requests(self, status: str = None) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT * FROM user_requests WHERE 1=1"
            params = []
            if status is not None:
                query += " AND status = ?"
                params.append(status)
            query += " ORDER BY created_at DESC"
            cur = conn.execute(query, params)
            return [dict(r) for r in cur.fetchall()]

    def update_user_request(self, request_id: int, status: str, details: dict = None) -> bool:
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                "UPDATE user_requests SET status = ?, updated_at = ? WHERE id = ?",
                (status, datetime.now().isoformat(), request_id),
            )
            if details is not None:
                conn.execute(
                    "UPDATE user_requests SET description = ? WHERE id = ?",
                    (json.dumps(details), request_id),
                )
            conn.commit()
            return True
        finally:
            conn.close()
