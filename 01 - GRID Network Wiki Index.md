# GRID Network Wiki — Project Index

## Project Overview
A deployable, self-maintaining GRID Network Wiki service running on CT120 (Proxmox VM 120, grid-core-01).

## Status
- **Overall**: Phase 0 in progress
- **Phase 0**: Foundation — Wiki Service and Directory Structure
- **Last Updated**: 2026-06-21

## Directory Structure (on CT120)
```
/srv/grid-wiki/
├── wiki/                    — Source of truth (markdown pages)
├── sites/                   — Multi-site mapping (grid/, fmsa/)
├── maintenance/             — Maintenance kanban (active/, resolved/, rules/)
├── change-kanban/           — Change kanban (pending/, approved/, rejected/)
├── raw/                     — Raw evidence (live-state/, kanban/, session-search/)
├── wiki-generated/          — Auto-syntheses (entities/, syntheses/, summaries/)
├── maintenance-reports/     — Health reports
├── sync/                    — Obsidian sync (manifest, drift/)
├── cron/                    — Agent maintenance scripts
└── PROJECT-MANIFEST.md      — Project RAM
```

## Active Tasks
| Task | Status | Assignee | Summary |
|------|--------|----------|---------|
| TASK-01 | **Completed** | TRON | Created wiki directory structure on CT120 (26 dirs) |
| TASK-02 | **In Progress** | TRON | Deploy wiki web service — BLOCKED: Caddy volume mount |
| TASK-03 | Parked | EMPTY | Create wiki service Compose file |
| TASK-04 | Parked | EMPTY | Add/verify Caddy route for wiki.grid |

## Key Infrastructure
- **CT120** (grid-core-01): 10.10.30.120 — accessed via `pct exec 120` on grid-pve
- **grid-pve** (Proxmox host): 10.10.30.22 — SSH key: `~/.ssh/proxmox_grid_ed25519`
- **Existing Caddy**: `/srv/grid-core/reverse-proxy/` — serves 30+ `.grid` routes
- **Compose binary**: `docker-compose` (v1.29.2)
- **Obsidian Vault**: `/Users/tron/Documents/Obsidian Vault/GRID Network Wiki/`
- **Target URL**: `https://wiki.grid/`

## Phase Progress
- Phase 0 (Foundation): In progress — TASK-01 done, TASK-02 blocked
- Phase 1 (Discovery Engine): Not started
- Phase 2 (Wiki Engine + Templates): Not started
- Phase 3 (Dashboard UI): Not started
- Phase 4 (Monitoring Auto-Setup): Not started
- Phase 5 (Obsidian Sync): Not started
- Phase 6 (Maintenance Auto-Resolution): Not started
- Phase 7 (Change Kanban Workflow): Not started
- Phase 8 (Agent KB Enhancement): Not started
