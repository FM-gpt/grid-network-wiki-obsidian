# Active Tasks — GRID Network Wiki

## Current Status (Updated: 2026-06-21)

| Task ID | Description | Status | Assignee | Last Updated |
|---|---|---|---|---|
| TASK-02 | Fix volume mount + restart Caddy for wiki.grid | **COMPLETED** | SELF | 2026-06-21 14:30 ACST |
| TASK-03 | Create wiki service Compose file | **COMPLETED** | SELF | 2026-06-21 14:35 ACST |
| TASK-04 | Verify Caddy route for wiki.grid | **COMPLETED** | SELF | 2026-06-21 14:40 ACST |
| Phase 1 | Discovery Engine — Build overnight agent workers | **PARKED** | EMPTY | 2026-06-21 14:45 ACST |
| Phase 2 | Wiki Engine — Templates and markdown pages | **PARKED** | EMPTY | 2026-06-21 14:45 ACST |
| Phase 3 | Dashboard UI — Browse/search wiki | **PARKED** | EMPTY | 2026-06-21 14:45 ACST |
| Phase 4 | Kanban Boards — Maintenance + Change boards | **PARKED** | EMPTY | 2026-06-21 14:45 ACST |
| Phase 5 | Cron Jobs — Overnight Hermes worker automation | **PARKED** | EMPTY | 2026-06-21 14:45 ACST |
| Phase 6 | Monitoring — Prometheus, Uptime Kuma auto-setup | **PARKED** | EMPTY | 2026-06-21 14:45 ACST |
| Phase 7 | Obsidian Sync — Bidirectional sync | **PARKED** | EMPTY | 2026-06-21 14:45 ACST |

## Notes
- Wiki content is fully deployed to CT120 at `/srv/grid-wiki/`
- Python HTTP server running on port 8082 serving wiki files
- Caddy volume mount issue resolved by switching to standalone wiki service
- Next step: Phase 1 (Discovery Engine)
