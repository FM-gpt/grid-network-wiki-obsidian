---
title: "PROJECT MANIFEST"
current_goal: "Phase 0: Foundation — Wiki Service and Directory Structure"
last_updated: 2026-06-21
---

# GRID Network Wiki

## 1. Scope Boundaries (DO NOT VIOLATE)
- **IN SCOPE:**
  - GRID Network Wiki service on CT120
  - Auto-discovery engine (1am-6am agent workers)
  - Dashboard UI for browsing wiki and kanban boards
  - Obsidian sync to `/Users/tron/Documents/Obsidian Vault/GRID Network Wiki/`
  - Monitoring auto-setup (Prometheus, Uptime Kuma)
  - Maintenance kanban workflow
  - Change kanban workflow
  - Agent knowledge base enhancement
- **OUT OF SCOPE:**
  - Modifying core Proxmox infrastructure
  - Direct network configuration changes without kanban review
  - Building custom monitoring tools (reuse existing Prometheus/Uptime Kuma)
  - Managing non-GRID/FMSA infrastructure

## 2. Current Goal
- **Phase 0:** Foundation — Create wiki directory structure and deploy web service on CT120

## 3. Active Tasks (DO NOT PICK THESE UP)
- [ ] TASK-01: Create wiki directory structure on CT120 (`assignee: EMPTY`, `started: 2026-06-21`, `link: TASKS/INBOX/TASK-01.md`)
- [ ] TASK-02: Deploy wiki web service (Caddy container) (`assignee: EMPTY`, `started: 2026-06-21`, `link: TASKS/INBOX/TASK-02.md`)
- [ ] TASK-03: Create wiki service Compose file (`assignee: EMPTY`, `started: 2026-06-21`, `link: TASKS/INBOX/TASK-03.md`)
- [ ] TASK-04: Add Caddy route for wiki.grid (`assignee: EMPTY`, `started: 2026-06-21`, `link: TASKS/INBOX/TASK-04.md`)

## 4. Deep-Dive Index (Load only when needed)
- **Methodology & Rules:** `AGENTS.md` (Always read first)
- **Project Plan:** `00 - GRID Network Wiki Project Plan.md`
- **Wiki Directory:** `/srv/grid-wiki/` (on CT120)
- **Obsidian Sync Path:** `/Users/tron/Documents/Obsidian Vault/GRID Network Wiki/`
- **Dashboard UI:** `https://wiki.grid/` (target)
- **CT120 Host:** `10.10.30.120`

## 5. Project Meta
- **Repo Path:** /Users/tron/grid-network-wiki-tool
- **Wikki Path:** /Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki
- **Remote:** `[GitHub URL]`
- **Test Env Host:** `CT121 grid-dev-01`
- **Active URL:** `https://wiki.grid/` (target)
- **Health Endpoint:** `[http://...]`