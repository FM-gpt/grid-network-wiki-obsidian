# Task S16-C: Code Fixes — Routing, Path Resolution, and Missing Features

**Status:** PARKED
**Assignee:** EMPTY
**Sprint:** Sprint 16
**Created:** 2026-06-24

## Description
Fix all code issues identified in the CT131 migration review.

## Issues to Fix

### C-01: Missing /api/status route
- Dashboard JS calls `/api/status` but no route exists
- Fix: Add route alias to `/api/health` (same handler)

### C-02: Missing /api/services route
- Dashboard JS calls `/api/services` but no route exists
- Fix: Add route alias to `/api/service-status` or implement new handler

### C-03: Missing /api/dashboard route
- Dashboard JS calls `/api/dashboard` but no route exists
- Fix: Add handler returning dashboard stats JSON (page count, service count, drift count, sync status, etc.)

### C-04: _resolve_wiki_file vault path mismatch
- Code references `/Users/tron/Documents/Obsidian Vault/GRID Network Wiki` but runs in CT131
- Fix: `_get_vault_path()` should check if path is accessible; if not (container mode), return `ROOT / 'wiki-content'` as effective root
- This allows the entire wiki-content directory to serve as the wiki content root

### C-05: Missing maintenance-rules/ directory
- `/Users/tron/grid-network-wiki-tool/maintenance-rules/` does not exist
- Fix: Create directory and populate from CT131 existing files (8 files at `/srv/grid-wiki/wiki-content/maintenance-rules/`)

### C-06: wiki-config.yaml vault.path
- Update to point to vault for local dev, handle container mode in code

### C-07: /api/monitoring-status route
- Implement Prometheus query integration for monitoring status

### C-08: /api/proxmox/hardware-metrics route
- Implement Proxmox API query for hardware metrics

### C-09: Verify all dashboard HTML pages
- Test all pages load correctly

### C-10: Verify kanban pages
- Test `/kanban/change.html` and `/kanban/maintenance.html`

## Verification
- All /api/* routes return 200 (no 404s)
- Dashboard renders and loads data
- Wiki browser loads pages from wiki-content
- Kanban boards show real data
