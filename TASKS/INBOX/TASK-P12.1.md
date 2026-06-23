# TASK: Phase 12.1 — Critical Bug Fixes (P0)

## Context
Phase 12 — UX Audit & Next-Stage Roadmap. All work in `/Users/tron/grid-network-wiki-tool/`

## Tasks

### 12.1.1 - Fix updateSitesOverview JS error
File: `dashboard/js/dashboard.js`
The function exists at line 388 but may fail if `API.sitesIndex()` throws. Ensure it handles missing data gracefully. Add try/catch in `loadAll()` for `updateSitesOverview()` call.

### 12.1.2 - Fix /api/wiki-index 404
Files: `dashboard/js/api.js` (line 24 calls `/wiki/INDEX.md`), `wiki-service.py` (line 141 serves `wiki-content/wiki/INDEX.md`)
Problem: `api.js` calls `this.get('/wiki/INDEX.md')` but server expects `/api/wiki-index`. Also, server serves as `text/markdown` but frontend expects JSON.
Fix: Change `api.js` to call `/api/wiki-index`, update server to return JSON array of pages, or add dual routing.

### 12.1.3 - Fix wiki-browser.html tree items
Files: `dashboard/wiki-browser.html` (lines 125-143 `renderTree`), `dashboard/css/dashboard.css`
Problem: Tree items show as blank/no visible text. The `renderTree` function receives `allFiles` which may contain objects (from `/api/wiki-index`) or strings (from fallback). Need to handle both formats. Also need to ensure CSS `--text-primary` variable is set correctly.

### 12.1.4 - Fix monitoring page contradictory status
File: `dashboard/monitoring.html`
Problem: Health grid shows ✅/❌ based on `svc.prometheus?.status` but table shows different data. Need to ensure the status values are consistent between health grid and table.

### 12.1.5 - Fix drift detection error
Files: `dashboard/drift.html` (line 114 calls `/api/drift/run` POST), `wiki-service.py` (do_POST only handles `/api/sync/run`)
Problem: `wiki-service.py` do_POST only handles `/api/sync/run`. POST to `/api/drift/run` returns 405.
Fix: Add `/api/drift/run` POST handler to `do_POST` method.

### 12.1.6 - Fix dashboard "--" metrics
File: `dashboard/js/dashboard.js`
Problem: `healthDrift` and `healthMaint` start as "--". `loadAll()` calls `updateRecentDrift` and `updateKanbanMetrics` but they may fail silently. Ensure initial values are set, and functions handle empty data.

## Verification
- No JS errors in browser console
- All data sections show values
- All API endpoints return valid data
- Browser QA: open http://localhost:8082/index.html and verify

## Rules
- Read AGENTS.md first
- All changes in local workspace only
- Update ACTIVE-TASKS.md on completion
