-- nerve-center/schema.sql
-- GRID Network Nerve Center SQLite Database Schema

-- Servers (Proxmox hosts)
CREATE TABLE IF NOT EXISTS servers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hostname TEXT NOT NULL UNIQUE,
    ip_address TEXT NOT NULL,
    proxmox_api_url TEXT NOT NULL,
    proxmox_api_user TEXT NOT NULL,
    proxmox_api_token_name TEXT NOT NULL,
    proxmox_api_token_secret TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'unknown',
    last_discovered TEXT,
    last_verified TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Containers/VMs (LXC on Proxmox)
CREATE TABLE IF NOT EXISTS containers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id INTEGER NOT NULL REFERENCES servers(id),
    vmid INTEGER NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'unknown',
    ip_addresses TEXT NOT NULL DEFAULT '[]',
    memory_mb INTEGER,
    cpu_cores INTEGER,
    disk_total_mb INTEGER,
    disk_used_mb INTEGER,
    os TEXT,
    template TEXT,
    last_discovered TEXT,
    last_verified TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(server_id, vmid)
);

-- Services (running on containers)
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    container_id INTEGER NOT NULL REFERENCES containers(id),
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    port INTEGER,
    protocol TEXT NOT NULL DEFAULT 'tcp',
    url TEXT,
    status TEXT NOT NULL DEFAULT 'unknown',
    response_time_ms INTEGER,
    last_checked TEXT,
    prometheus_job TEXT,
    prometheus_target TEXT,
    monitoring_configured INTEGER NOT NULL DEFAULT 0,
    caddy_configured INTEGER NOT NULL DEFAULT 0,
    health_check_url TEXT,
    health_check_interval INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Service Relationships
CREATE TABLE IF NOT EXISTS service_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_service_id INTEGER NOT NULL REFERENCES services(id),
    target_service_id INTEGER NOT NULL REFERENCES services(id),
    relationship_type TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(source_service_id, target_service_id, relationship_type)
);

-- Wiki Documents (byproduct of agent actions)
CREATE TABLE IF NOT EXISTS wiki_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT NOT NULL,
    related_service_id INTEGER REFERENCES services(id),
    related_container_id INTEGER REFERENCES containers(id),
    status TEXT NOT NULL DEFAULT 'active',
    properties TEXT,
    entity_type TEXT,
    entity_id TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    last_updated TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Agent Actions (audit log)
CREATE TABLE IF NOT EXISTS agent_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id INTEGER,
    status TEXT NOT NULL DEFAULT 'pending',
    details TEXT,
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- User Requests
CREATE TABLE IF NOT EXISTS user_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    request_type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    assigned_agent_id TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_containers_server ON containers(server_id);
CREATE INDEX IF NOT EXISTS idx_services_container ON services(container_id);
CREATE INDEX IF NOT EXISTS idx_services_status ON services(status);
CREATE INDEX IF NOT EXISTS idx_services_type ON services(type);
CREATE INDEX IF NOT EXISTS idx_wiki_slug ON wiki_documents(slug);
CREATE INDEX IF NOT EXISTS idx_wiki_category ON wiki_documents(category);
CREATE INDEX IF NOT EXISTS idx_agent_actions_status ON agent_actions(status);
CREATE INDEX IF NOT EXISTS idx_agent_actions_type ON agent_actions(action_type);
CREATE INDEX IF NOT EXISTS idx_user_requests_status ON user_requests(status);
