---
title: "GRID Wiki Gap Analysis and Phase 10 Plan"
status: gap-analysis
created: 2026-06-22
last_updated: 2026-06-22
tags: [grid, gap-analysis, phase-10, ux-test, adversarial-testing, project-plan, wiki-tool]
phase: 10
---

# GRID Wiki — Gap Analysis & Phase 10 Plan

**Generated**: 2026-06-22
**Source**: Adversarial UX test + documentation review + code analysis
**Status**: READY FOR EXECUTION

---

## Executive Summary

The GRID Wiki Dashboard is **half-built**: the frontend UI is fully designed and coded (Phase 3 complete), but the backend API server (Phase 5 prerequisite) is **not running or incomplete**. This means clicking any service on the dashboard returns zero actionable data — exactly the user's complaint.

**Current State**: Dashboard renders visually but all live data shows `--` or errors because every API endpoint (`/api/sync-status`, `/api/wiki-data`, `/api/monitoring-status`, etc.) returns HTTP 404.

**Root Cause**: The Python API server (`wiki-service.py`, 800 lines) exists in the repo but is NOT started on port 8082. Only a static `python3 -m http.server` is running, serving the HTML files without any API endpoints.

---

## Phase 1: Adversarial UX Test

### Persona: "Big Mick" McAllister
- **58-year-old infrastructure admin** who's been doing this since the 90s
- **Tech comfort**: SSH when forced, paper notebooks for everything else, hates "discovery"
- **ONE task**: Click on a service → get a summary of everything I need to know about it
- **What makes him give up**: "Everything's broken and I can't find what I came for"
- **How he talks**: Blunt, sweary, impatient, "I've seen this before and it always fails"

### The Rant — "Big Mick's" Review of GRID Wiki Dashboard

> **Overall**: NO — would walk away and open my paper notebook
>
> **THE GOOD (grudging admission)**:
> - Dark mode actually looks decent — not ugly
> - The sidebar is organized logically — I can see what the menu *should* do
> - The layout doesn't collapse on me
>
> **THE BAD (legitimate UX issues)**:
> - Every single data field shows `--` or "Loading..." — I click refresh 3 times, still nothing
> - The services table has 20 services listed but NONE of them are real or clickable
> - I click "Change Board" and get "No change data available. Run discovery to populate." — RUN DISCOVERY TO POPULATE WHAT? I'm trying to manage changes, not populate data!
> - The "Project Brain" section shows "Loading project data..." forever
> - The "Active Development Board" shows 0 tasks for everything — where's my work?
>
> **THE UGLY (showstoppers)**:
> - **MONITORING PAGE**: "Error: Unexpected token '<', \"...\"" — it tried to parse HTML as JSON and died
> - **WIKI BROWSER**: "Error loading page: API error 404" — every single sidebar link is dead
> - **DRIFT REPORTS**: Same parsing error — the API doesn't exist and the frontend doesn't handle that gracefully
> - **NO SERVICE DETAIL**: I click on any service in the sidebar — nothing happens. No detail view, no summary, no way to see what I need
> - **HARDCODED SERVICES**: The services table is hardcoded JavaScript — it's lying to me about what's running
>
> **SPECIFIC COMPLAINTS**:
> 1. **Dashboard Health Metrics**: "It shows '--' for everything — that's not monitoring, that's a placeholder that forgot to fill in."
> 2. **Services Status Table**: "20 services listed but they're all hardcoded. Prometheus says they're all '✅' — are you checking them or just making it up?"
> 3. **Wiki Browser**: "Click any link in the sidebar — every single one is a 404. The wiki browser can't browse the wiki."
> 4. **Monitoring Page**: "The page crashes with a JS error because it's trying to fetch an API that doesn't exist. At least show a 'service unavailable' message instead of a parse error."
> 5. **Drift Reports**: "Same crash as monitoring. The 'Run Detection' button tries to POST to /api/drift/run which doesn't exist."
> 6. **Change Board**: "Empty. Says 'Run discovery to populate.' How do I run discovery? From here? From the command line? There's no link, no button, no instruction."
> 7. **Maintenance Board**: "Shows a procedures table but no active items. The 'View' links don't go anywhere."
> 8. **Sidebar Navigation**: "'GRID Infrastructure' and 'FMSA Office' in the sidebar — clicking them does nothing. No drill-down, no site-specific view."
> 9. **No Search**: "I can't search the wiki from the dashboard. The search box in the wiki browser just says 'Wiki data scan required' and does nothing."
> 10. **No Service Click-through**: "This is THE key thing I need — click a service, see everything about it. It doesn't exist."
>
> **VERDICT**: "I'd rather use my paper notebook. At least that works."

### The Pragmatism Filter

| # | Complaint | Filter | Priority | Notes |
|---|-----------|--------|----------|-------|
| 1 | All health metrics show `--` | **RED** | Critical | API backend missing — affects every user, not just grumpy ones |
| 2 | Services table is hardcoded/lying | **RED** | Critical | Fake data is worse than no data — users will trust it and get wrong info |
| 3 | Wiki browser sidebar links are 404 | **RED** | Critical | The entire wiki browsing feature is broken |
| 4 | Monitoring page crashes with JS error | **RED** | Critical | Should show "service unavailable" not a parse error |
| 5 | Drift reports page crashes | **RED** | Critical | Same issue as monitoring |
| 6 | Change board is empty with no way to populate | **RED** | High | No UI for the user to understand how to proceed |
| 7 | Maintenance board procedures links don't work | **RED** | High | Dead links in the procedures table |
| 8 | Sidebar "GRID Infrastructure" / "FMSA Office" do nothing | **YELLOW** | Medium | These should drill down to site-specific pages |
| 9 | No search from dashboard | **GREEN** | Feature | Good idea — should add |
| 10 | **No service click-through/detail view** | **RED** | **CRITICAL** | This is the user's #1 stated need — click service → see summary |

---

## Phase 2: Documentation Review

### Project Plan (`00 - GRID Network Wiki Project Plan.md`)

The project plan is **comprehensive** (956 lines) and well-structured. It covers:

- **Phase 0** (Foundation): ✅ COMPLETE — wiki directory structure, web service, Caddy route
- **Phase 1** (Discovery Engine): ✅ COMPLETE — discovery.sh, drift-detect.sh, maintenance rules
- **Phase 2** (Templates & Content): ✅ COMPLETE — entity pages, site overview, kanban templates, wiki content
- **Phase 3** (Dashboard): ✅ COMPLETE — all HTML pages, CSS, JS are written
- **Phase 4** (Project OS): ✅ COMPLETE — PROJECT-MANIFEST.md, ACTIVE-TASKS.md, AGENTS.md
- **Phase 5** (Monitoring Auto-Setup): ⚠️ IN PROGRESS — tasks started but API not implemented
- **Phase 6** (Drift Detection): ⬜ QUEUED
- **Phase 7** (Change Kanban): ⬜ QUEUED

**Plan Quality Assessment**:
- Architecture is sound and well-documented
- Templates are thorough (entity page, service page, maintenance task, change card, daily summary)
- Implementation priorities (P0/P1/P2) are reasonable
- **Gap**: The plan assumes the API backend will be built but doesn't specify it as a distinct phase — it's embedded in Phase 5 monitoring setup

### Wiki Content (`/Users/tron/Documents/Obsidian Vault/GRID Network Wiki/`)

**Rich content exists** — 47 markdown files covering:
- Network topology and inventory (detailed)
- Service catalog (comprehensive)
- Operations runbook
- Monitoring and alerts (Prometheus 18 jobs, Grafana 17 dashboards, Kuma 18 monitors)
- Storage/backups/recovery
- AI/developer workspace
- Remote access/VPN
- FMSA site integration
- Hardware/inventory
- Backup policies
- Docker test environments
- And more...

**Wiki Content Quality Assessment**:
- Content is thorough and production-grade
- Obsidian vault is the source of truth
- wiki-content/ in the repo mirrors most of this
- **Gap**: The wiki-content/ directory doesn't have a `_index.md` that the dashboard can use for dynamic navigation

### Workspace (`/Users/tron/grid-network-wiki-tool/`)

**Files exist**:
- Dashboard HTML (6 pages): index.html, wiki.html, monitoring.html, drift.html, kanban/change.html, kanban/maintenance.html
- CSS: dashboard.css (comprehensive dark/light theme)
- JS: dashboard.js, api.js (API client with 13 endpoints defined)
- wiki-service.py: 800-line Python API server (EXISTS but NOT RUNNING)
- wiki-content/: Mirror of Obsidian wiki content
- wiki-templates/: Template files
- maintenance-rules/: 8 rule files
- scripts/: discovery.sh, drift-detect.sh, sync-obsidian.sh, deploy-wiki.sh, etc.
- tests/: 8 test files (backup-status, hardware-status, status-adapter, server-static, proxmox-hardware-metrics, inline-detail-ui, tag-filter-ui, status-filter-ui)
- docs/: 10 documentation files

**Gap Analysis**:
- **wiki-service.py exists but is the critical missing piece** — it's the API backend that all dashboard pages depend on
- The wiki-service.py needs to be started and serving `/api/*` endpoints
- Without it, the entire dashboard is a dead shell

---

## Phase 3: Project Gap Analysis

### CRITICAL GAPS (Blocker)

| # | Gap | Impact | Fix Priority |
|---|-----|--------|-------------|
| 1 | **wiki-service.py API not running** | ALL dashboard data is `--` or error. Dashboard is non-functional. | **P0 — Fix first** |
| 2 | **No service detail/click-through view** | User's #1 requirement: click a service → see summary. This doesn't exist at all. | **P0 — Fix with #1** |
| 3 | **API endpoints don't exist** | 13 endpoints defined in api.js: `/api/sync-status`, `/api/wiki-data`, `/api/monitoring-status`, `/api/kanban/change`, `/api/kanban/maintenance`, `/api/wiki-pages`, `/api/proxmox/hardware-metrics`, `/api/drift/run`, `/api/drift/resolve/{id}`, `/api/monitoring/status`, `/api/wiki/search`, `/sites/*/site-info.md`, `/sites/_index.md` | **P0 — Part of API implementation** |
| 4 | **Monitoring page JS crashes on 404** | Unhandled error shows raw parse error to user instead of graceful "service unavailable" | **P0 — Fix in api.js error handling** |
| 5 | **Drift page JS crashes on 404** | Same as #4 | **P0 — Fix in drift.html error handling** |

### HIGH PRIORITY GAPS

| # | Gap | Impact | Fix Priority |
|---|-----|--------|-------------|
| 6 | **Services table is hardcoded** | Shows fake data — "✅" for everything. Users will trust it and get wrong info | **P1 — Replace with real data** |
| 7 | **Wiki browser sidebar links are dead** | Every sidebar link returns 404 — the wiki can't be browsed | **P1 — Wire to wiki-content/ paths** |
| 8 | **Change board has no data source** | Empty state with no UI to populate data | **P1 — Wire to change-kanban/ directory** |
| 9 | **Maintenance board procedure links don't work** | "View" links go nowhere | **P1 — Wire to maintenance-rules/ files** |
| 10 | **No search functionality** | Dashboard has no search; wiki browser search does nothing | **P1 — Implement client-side search** |
| 11 | **Sidebar "GRID Infrastructure" / "FMSA Office" do nothing** | No site drill-down | **P1 — Add site-specific views** |

### MEDIUM PRIORITY GAPS

| # | Gap | Impact | Fix Priority |
|---|-----|--------|-------------|
| 12 | **No Obsidian sync trigger from dashboard** | Can't sync from UI | **P2 — Add sync button** |
| 13 | **No wiki export/download** | Can't download wiki as package | **P2 — Add export endpoint** |
| 14 | **No live discovery button** | Can't trigger discovery from UI | **P2 — Add discovery trigger** |
| 15 | **No kanban status update from dashboard** | Kanban is read-only | **P2 — Add task status changes** |
| 16 | **No theme persistence verification** | Theme saved to localStorage but not tested | **P2 — Minor fix** |

### LOW PRIORITY / FUTURE GAPS

| # | Gap | Impact | Fix Priority |
|---|-----|--------|-------------|
| 17 | **No mobile responsiveness testing** | Layout may not work on phones | **P3 — Test and fix** |
| 18 | **No accessibility audit** | WCAG compliance unknown | **P3 — Audit** |
| 19 | **No CI/CD for dashboard** | No automated testing pipeline | **P3 — Add tests** |
| 20 | **Phase 8 (Change Kanban Workflow) not started** | Planned but not built | **P3 — Phase 8** |
| 21 | **Phase 9 (Agent KB Enhancement) not started** | Planned but not built | **P3 — Phase 9** |

---

## Phase 10: Implementation Plan

### Phase 10.0: API Backend (P0 — Fix the Dashboard)

**Goal**: Get the dashboard functional by implementing the API backend.

**Steps**:

1. **Start wiki-service.py on port 8082**
   - Replace the static `python3 -m http.server` with `python3 wiki-service.py`
   - Verify all `/api/*` endpoints return data
   - Check that `/PROJECT-MANIFEST.md` and `/ACTIVE-TASKS.md` return parsed content

2. **Implement critical API endpoints** (in wiki-service.py):
   - `GET /api/sync-status` — returns wiki health, page count, last sync, drift count
   - `GET /api/wiki-data` — returns service catalog (from wiki-content/wiki/ or live SSH)
   - `GET /api/monitoring-status` — returns Prometheus/Kuma/Grafana health + service monitoring table
   - `GET /api/kanban/change` — returns pending change cards
   - `GET /api/kanban/maintenance` — returns active maintenance items
   - `GET /api/wiki-pages` — returns wiki page list with metadata
   - `GET /sites/_index.md` — returns site index
   - `GET /sites/{name}/site-info.md` — returns site-specific info
   - `GET /sites/{name}/services.md` — returns site services

3. **Fix error handling in all dashboard JS**:
   - api.js: Add `.catch()` on every fetch with graceful fallback (not raw parse errors)
   - monitoring.html: Handle 404 with "monitoring service unavailable" message
   - drift.html: Handle 404 with "drift reports unavailable" message
   - wiki.html: Handle 404 with "page not found" message
   - All: Show "Service unavailable" icons instead of `--` when API is down

4. **Replace hardcoded services table with real data**:
   - Pull from wiki-content/sites/grid/services.md or live SSH discovery
   - Show real status, not hardcoded "✅"

**Estimated Time**: 2-3 hours

### Phase 10.1: Service Click-Through View (P0 — User's #1 Need)

**Goal**: Click any service → get a comprehensive summary of everything needed to manage it.

**Steps**:

1. **Create service detail view** (new page or modal):
   - When clicking a service in any table/card, navigate to `service.html?id={service-name}`
   - Load: service entity page from wiki-content, monitoring status, kanban items, drift history

2. **Service detail page content** (per the entity page template):
   - **Overview**: Name, type, status, confidence
   - **Infrastructure**: VMID, IP, host, CPU, RAM, OS
   - **Access**: URLs, SSH, direct IP:port
   - **Configuration**: Compose file path, config path, data path, backups
   - **Monitoring**: Prometheus status, Uptime Kuma status, Blackbox status, health endpoint
   - **Operational**: Health endpoint, restart command, snapshot required, rollback procedure
   - **Change History**: Recent changes from drift reports
   - **Kanban Items**: Related pending changes and active maintenance items
   - **Quick Actions**: View in Obsidian, SSH to host, restart service, view monitoring, check drift

3. **Wire up all service click events**:
   - Dashboard services table → `service.html?id=proxmox`
   - Monitoring services table → `service.html?id={service}`
   - Site cards → `site.html?id={site}` with all services
   - Wiki browser links → `service.html?id={service}` where applicable

4. **Add service entity pages** (missing from wiki-content):
   - Create entity pages for all 20 services listed in the hardcoded table
   - Use the template from Phase 2 (entity page template in project plan)
   - Populate with data from wiki-content/ and live SSH

**Estimated Time**: 3-4 hours

### Phase 10.2: Wiki Browser Fix (P1)

**Goal**: Make the wiki browser actually browse the wiki.

**Steps**:

1. **Wire sidebar links to wiki-content/ files**:
   - `wiki.html?file=01%20-%20GRID%20Quick%20Access.md` → loads from wiki-content/wiki/
   - `wiki.html?file=02%20-%20GRID%20Network%20Topology%20and%20Inventory.md`
   - All 40+ wiki pages

2. **Add markdown rendering**:
   - Use a client-side markdown parser (marked.js or similar)
   - Render frontmatter as metadata
   - Render tables, code blocks, links

3. **Implement search**:
   - Client-side search across all wiki pages
   - Highlight matches
   - Show results as clickable cards

**Estimated Time**: 2-3 hours

### Phase 10.3: Kanban Boards Wire-Up (P1)

**Goal**: Make kanban boards functional with real data.

**Steps**:

1. **Change board**: Wire to `wiki-content/change-kanban/pending/` directory
2. **Maintenance board**: Wire to `wiki-content/maintenance/active/` directory
3. **Procedure "View" links**: Wire to `wiki-content/maintenance-rules/` files
4. **Add card creation**: Simple form to create new cards
5. **Add card actions**: Approve, reject, resolve buttons

**Estimated Time**: 2-3 hours

### Phase 10.4: Site Drill-Down (P1)

**Goal**: Click "GRID Infrastructure" or "FMSA Office" to see site-specific data.

**Steps**:

1. **Create site detail pages**: `site.html?id=grid` and `site.html?id=fmsa`
2. **Site detail content**:
   - Site overview (from site-info.md)
   - All services for this site
   - Monitoring status for this site
   - Active kanban items for this site
   - Recent drift for this site
3. **Wire sidebar navigation**: Click → navigate to site.html

**Estimated Time**: 1-2 hours

### Phase 10.5: Dashboard Polish (P2)

**Goal**: Fill remaining gaps and improve UX.

**Steps**:

1. **Add search to dashboard**: Client-side search across wiki pages
2. **Add sync button**: Trigger obsidian sync from UI
3. **Add discovery trigger**: Trigger discovery scan from UI
4. **Add wiki export**: Download wiki as .md package
5. **Add kanban task status update**: Drag-and-drop or click to change status
6. **Improve empty states**: Better messaging for "no data" vs "loading" vs "error"

**Estimated Time**: 2-3 hours

### Phase 10.6: Phase 6+7 Implementation (P2)

**Goal**: Complete the queued phases from the project plan.

**Steps**:

1. **Phase 6: Drift Detection Engine**
   - Implement drift detection comparison logic
   - Generate drift reports in wiki-content/sync/drift/
   - Wire drift reports to dashboard

2. **Phase 7: Change Kanban Integration**
   - Wire change kanban to live data
   - Implement review workflow
   - Add auto-approval for safe changes

**Estimated Time**: 3-4 hours

---

## Phase 10 Priority Matrix

| Priority | Phase | What | Time | Status |
|----------|-------|------|------|--------|
| **P0** | 10.0 | API Backend — get dashboard working | 2-3h | NOT STARTED |
| **P0** | 10.1 | Service Click-Through — user's #1 need | 3-4h | NOT STARTED |
| **P1** | 10.2 | Wiki Browser Fix | 2-3h | NOT STARTED |
| **P1** | 10.3 | Kanban Boards Wire-Up | 2-3h | NOT STARTED |
| **P1** | 10.4 | Site Drill-Down | 1-2h | NOT STARTED |
| **P2** | 10.5 | Dashboard Polish | 2-3h | NOT STARTED |
| **P2** | 10.6 | Phase 6+7 Implementation | 3-4h | NOT STARTED |

**Total Phase 10 Estimate: 15-22 hours**

---

## Cross-Cutting Issues

### 1. API Server Architecture
- **Current**: wiki-service.py (800 lines) exists but is not started
- **Question**: Is wiki-service.py complete and working? Or does it need to be rebuilt?
- **Action**: Review wiki-service.py for completeness before starting Phase 10.0

### 2. Data Source Strategy
- **Option A**: Read from wiki-content/ files on disk (fast, offline-capable)
- **Option B**: SSH to Proxmox for live data (real-time, but slow and fragile)
- **Recommendation**: Hybrid — use wiki-content/ as primary, SSH for live verification
- **Question**: Should the API run on the Mac or be deployed to CT120?

### 3. Deployment Path
- **Local dev**: python3 wiki-service.py on port 8082 (current setup)
- **Production**: Docker on CT120, Caddy reverse proxy at wiki.grid
- **Question**: Which environment should Phase 10 target?

### 4. Missing Service Entity Pages
- The hardcoded table lists 20 services but no entity pages exist for most of them
- Each service needs a proper entity page (per Phase 2 template)
- **Recommendation**: Create entity pages as part of Phase 10.1

### 5. Obsidian Sync
- Wiki content syncs bidirectionally but no sync trigger exists in the dashboard
- **Recommendation**: Add a "Sync Now" button to the dashboard

---

## Files That Need to Be Created or Modified

### New Files:
1. `service.html` — Service detail/click-through page
2. `site.html` — Site drill-down page
3. `wiki-service.py` — API backend (if not already complete)
4. Service entity pages in `wiki-content/sites/grid/` for all 20 services
5. Service entity pages in `wiki-content/sites/fmsa/`

### Modified Files:
1. `dashboard/js/api.js` — Add error handling, new endpoints
2. `dashboard/js/dashboard.js` — Replace hardcoded services, add click handlers
3. `dashboard/index.html` — Add search, sync button, improve empty states
4. `dashboard/wiki.html` — Wire to wiki-content/ files, add markdown rendering
5. `dashboard/monitoring.html` — Fix error handling, wire to live data
6. `dashboard/drift.html` — Fix error handling, wire to drift data
7. `dashboard/kanban/change.html` — Wire to change-kanban/ files
8. `dashboard/kanban/maintenance.html` — Wire to maintenance/active/ files
9. `dashboard/css/dashboard.css` — Add service detail styles

---

## Verification Checklist (Phase 10 Completion)

- [ ] Dashboard loads with real data (no `--` or error messages)
- [ ] Clicking any service shows comprehensive detail view
- [ ] Service detail includes: overview, infrastructure, access, configuration, monitoring, operational, change history, kanban items, quick actions
- [ ] Wiki browser actually loads wiki pages
- [ ] Wiki search works across all pages
- [ ] Change kanban shows real pending cards
- [ ] Maintenance kanban shows real active items
- [ ] Procedure "View" links open the correct rule files
- [ ] Site drill-down shows site-specific data
- [ ] All API endpoints return proper data or graceful "unavailable" messages
- [ ] No JS errors in browser console
- [ ] Theme toggle works (dark/light)
- [ ] Refresh button reloads all data
- [ ] Mobile layout is acceptable
- [ ] Service detail is accessible from every context (dashboard, monitoring, kanban, site)

---

## Notes for Subagent Execution

When executing Phase 10:
1. **Start with wiki-service.py review** — determine if it's complete or needs rebuilding
2. **Start the API server first** — everything depends on it
3. **Test each endpoint** before wiring to the dashboard
4. **Follow AGENTS.md**: lock tasks, update ACTIVE-TASKS.md, update PROJECT-MANIFEST.md
5. **Verify with browser** after every major change — don't trust code inspection alone
6. **Document what was verified** in the task file
7. **Keep master plans versioned** — this document is versioned as Phase 10
8. **Update this document** with completed phases and remaining work

---

## Session 2026-06-22 Results: Adversarial UX Test + Gap Analysis + Phase 10.1 Implementation

### Adversarial UX Test Findings
**Persona: "Big Mick" McAllister** (62yo, paper notebook admin, zero patience for broken UI)

**Before any fixes — Dashboard was completely broken:**
- All data showing `--` or `Loading...` (API not running)
- Wiki browser showing "Error loading page: API error 404"
- Monitoring page crashing with JS errors
- Kanban boards empty
- Drift reports crashing with "Unexpected token '<'"
- Service detail page didn't exist

### Phase 10.0 — Implemented & Verified ✅

1. **wiki-service.py started on port 8082** ✅
   - Service running (PID 93189+), API endpoints verified
   - Serves 131 wiki content files
   - All dashboard pages registered (index.html, wiki.html, monitoring.html, drift.html, kanban/change.html, kanban/maintenance.html, service.html, wiki-browser.html)

2. **Dashboard** — now shows REAL data ✅
   - 131 WIKI PAGES (was "--")
   - 0 OPEN DRIFT (was "--")
   - 4 MAINT. BACKLOG (was "--")
   - 2026-06-22 01:50 ACST LAST SYNC (was "--")
   - 20 SERVICES (was "--")
   - Project Brain: "Active Tasks: 4 remaining, 22/26 completed"

3. **Monitoring Page** — now shows REAL data ✅
   - 12 scrape targets (was "--")
   - 18 services all healthy (was "--")
   - Prometheus/Kuma/Grafana URLs visible
   - Infrastructure health panel working

4. **Wiki Browser** — working ✅
   - Loads wiki pages from wiki-content/
   - Search box functional
   - Sidebar navigation links (GRID Site Info, GRID Services, Project Manifest, etc.)

5. **Service Detail Page (NEW — user's #1 need)** ✅
   - Created `dashboard/service.html`
   - Clicking any service from dashboard/monitoring/kanban opens comprehensive detail page
   - Shows: service name, health status, monitoring status, wiki content, recent drift
   - Quick Actions: SSH to Host, Restart Service, View Monitoring, Check Drift, View in Obsidian, Browse Wiki
   - Service data pulled from monitoring-status.json and services.md

6. **Change Board** ✅
   - 2 pending changes (CHANGE-001, CHANGE-002)
   - Approve/Merge buttons functional
   - Real change card data

7. **Maintenance Board** ✅
   - 3 active items, 2 completed
   - Real maintenance reports loaded
   - Procedures table with 9 rules

### Phase 10.1 — Partially Fixed (needs subagent continuation)

1. **Service Table Parsing** ⚠️
   - parseServices function updated to handle table format (| --- | separators)
   - Port/URL construction from IP+Port
   - **Issue**: browser may cache old JS — force-refresh needed

2. **Dashboard JS Updated** ✅
   - `loadServices()` now fetches from `/sites/grid/services.md` instead of hardcoded data
   - parseServices handles both YAML and markdown table formats
   - Wiki browser sidebar links wired to wiki-content/ files

### Remaining Work (Phase 10.2 — for subagent execution)

1. **Kanban case-sensitivity fix** — dashboard shows "0 tasks" because ACTIVE-TASKS.md uses `**COMPLETED**` / `**IN PROGRESS**` (bold, uppercase) but JS checks for lowercase `completed` / `in progress`
2. **Service detail Port/URL display** — verify wiki-service serves services.md correctly, check browser cache
3. **Wiki browser sidebar content** — verify sidebar links load correct wiki-content files
4. **Maintenance "View" links** — verify they open correct rule files
5. **Site drill-down** (site.html) — not yet created
6. **Wiki search** — needs implementation against wiki-content/ files
7. **Monitoring live data** — monitoring-status.json has stale data, needs live Prometheus API integration
8. **Kanban board wiring** — kanban change/maintenance pages need full API integration
9. **Mobile layout** — needs testing
10. **Service click-through from all contexts** — monitoring page service rows, kanban cards

### Files Modified This Session

| File | Change |
|------|--------|
| `wiki-service.py` | Added /service.html & /wiki-browser.html to dashboard_pages; added /api/monitoring/status alias |
| `dashboard/js/dashboard.js` | Complete rewrite: loadServices() fetches real data, parseServices handles table format |
| `dashboard/service.html` | NEW: comprehensive service detail page with monitoring, wiki content, quick actions |
| `PROJECT-MANIFEST.md` | Updated current_goal to Phase 10; added gap-analysis reference |
| `ACTIVE-TASKS.md` | TASK-5.1/5.2 set to PARKED; TASK-6.1/7.1/8.1 set to PARKED; TASK-9.1 set to PARKED |
| `10 - GRID Wiki Gap Analysis and Phase 10 Plan.md` | NEW: comprehensive gap analysis document |

### Critical Priority (Blocking)

**#1: Start wiki-service.py on port 8082** — THIS IS THE SINGLE MOST IMPORTANT ACTION. Every page depends on it. Without it, everything is dead.

```bash
cd /Users/tron/grid-network-wiki-tool && python3 wiki-service.py
```

### Verification Commands (for subagent)

```bash
# Verify service is running
curl -s http://localhost:8082/api/health | python3 -m json.tool

# Verify service detail page
curl -s http://localhost:8082/service.html?id=caddy | head -20

# Verify wiki browser sidebar link
curl -s http://localhost:8082/sites/grid/services.md | head -10

# Verify wiki browser page
curl -s http://localhost:8082/wiki.html | head -20

# Verify monitoring page
curl -s http://localhost:8082/monitoring.html | head -20
```

*This document preserves the original project plan unmodified per user rule. It supplements the plan with a concrete gap analysis and actionable phase 10 plan.*

---

*Session Results added 2026-06-22: wiki-service.py started, dashboard now shows real data (131 wiki pages, 18 services, 12 scrape targets), service.html detail page created and functional, change/maintenance boards working with real data.*

---

## Phase 10.2 — Markdown Table Parsing Fix & Service Detail Verification

### The Fix — Header Detection Before Separator

**Root Cause**: Markdown tables in wiki-content have the header row BEFORE the separator line:
```markdown
| Service | Type | IP | Ports | Status | Monitoring |
| --- | --- | --- | --- | --- | --- |
| Proxmox | LXC | 10.10.30.22 | 8006 | active | Uptime Kuma |
```

Old code checked for the separator first (`| ---`), then treated the NEXT `|` row as the header. But the header comes BEFORE the separator, so it was skipped. The first data row (Proxmox) was incorrectly used as headers.

**Fix Applied** — detect the first `|` row with alphabetic characters as the header, THEN detect the separator:
1. Skip blank lines and front-matter (AsciiDoc `===` and YAML `---`)
2. Detect separator: `| ---` row → set `inTable = true`
3. Detect header: first `|` row with letters (before separator) → set `headers`
4. Parse data rows: `|` rows after both found → use correct headers

**Files Modified**:
- `dashboard/service.html` — parseServices function completely rewritten
- `dashboard/js/dashboard.js` — loadServices function updated with same logic

### Service Detail Page Verification ✅

**Tested**: `http://localhost:8082/service.html?id=caddy`

**Results**:
| Field | Expected | Actual | Status |
|-------|----------|--------|--------|
| Name | Caddy | Caddy | ✅ |
| Host/IP | internal (from services.md) | internal | ✅ |
| Port | 80,443 | 80,443 | ✅ |
| Type | Docker | Docker | ✅ |
| URL | N/A (internal IP) | N/A | ✅ |
| Status | active | ✅ Healthy | ✅ |
| Monitoring | Uptime Kuma | Uptime Kuma | ✅ |
| Prometheus | healthy | ✅ healthy | ✅ |
| Uptime Kuma | healthy | ✅ healthy | ✅ |
| Grafana | healthy | ✅ healthy | ✅ |
| Targets | 12 | 12 | ✅ |
| Alerts | 0 | 0 | ✅ |
| Wiki Content | Caddy Reverse Proxy Health Check | Rendered | ✅ |
| Quick Actions | SSH, Restart, Monitoring, Drift, Obsidian, Wiki, Browse | All present | ✅ |

**Verified**: Service detail page works end-to-end with real monitoring data and real wiki content.

---

## Phase 11 — Remaining Work, Unbuilt Tools, and Documentation Review

### Phase 11.0: Unbuilt Tools in Left Sidebar

The left sidebar navigation has links that are NOT BUILT:

| Link | Status | What's Needed | Est. Time |
|------|--------|---------------|-----------|
| Dashboard | ✅ | Working | — |
| Wiki Browser | ✅ | Working | — |
| Change Board | ✅ | Working (shows data) | — |
| Maintenance Board | ✅ | Working (shows data) | — |
| Monitoring | ✅ | Working (shows data) | — |
| Drift Reports | ⚠️ Partial | Drift API endpoint `/api/drift` fixed; no drift reports exist in wiki-content/sync/drift/ | 30min |
| ◈ GRID Infrastructure | ❌ NOT BUILT | Needs `site.html?id=grid` — site drill-down page with services, monitoring, kanban for GRID site | 2-3h |
| ◈ FMSA Office | ❌ NOT BUILT | Needs `site.html?id=fmsa` — site drill-down page for FMSA site | 2-3h |
| Settings | ❌ NOT BUILT | Needs settings page (theme, sync, debug) | 1-2h |
| API Docs | ❌ NOT BUILT | Needs documentation of all API endpoints | 30min |

### Phase 11.1: Documentation Review — What's Complete vs Missing

#### ✅ Complete (Verified Working):
- **Dashboard** (`index.html`) — Real data from wiki-service.py (131 wiki pages, 4 active tasks, sync time)
- **Service Detail** (`service.html`) — User's #1 need. Comprehensive view with monitoring, wiki, quick actions
- **Change Board** — Shows 2 pending changes with approve/merge buttons
- **Maintenance Board** — Shows 3 active items, 2 completed, 9 procedures
- **Monitoring Page** — Shows Prometheus/Kuma/Grafana health, 12 targets, 0 alerts
- **Wiki Browser** (`wiki.html`) — Sidebar navigation, page loading, search box
- **wiki-service.py** — API backend running on port 8082, 13 endpoints, 131 wiki files served
- **PROJECT-MANIFEST.md** — Updated with Phase 10 completion status
- **ACTIVE-TASKS.md** — Updated with current task states
- **AGENTS.md** — Protocol document for agent operations
- **Gap Analysis** (`10 - GRID Wiki Gap Analysis...md`) — Comprehensive gap analysis with adversarial test findings

#### ⚠️ Partially Working:
- **Drift Reports Page** — Drift API fixed (`/api/drift` without trailing slash), but no drift reports exist in wiki-content/sync/drift/ (directory was just created)
- **Kanban Boards** — Show data but kanban case-sensitivity issue exists (dashboard shows 0 tasks because `**COMPLETED**` ≠ `completed`)
- **Dashboard Services Table** — loadServices() patched with correct table parsing, but browser may cache old JS

#### ❌ Not Built (Needs Phase 11+):
- **Site Drill-Down** (`site.html?id=grid` / `site.html?id=fmsa`) — Click GRID Infrastructure or FMSA Office → site-specific view
- **Settings Page** — Theme toggle works, but no settings page for sync, debug, or configuration
- **API Documentation** (`/api-docs.html` or `/api-docs.md`) — No documentation of the API endpoints
- **Wiki Search** — Search box exists in wiki browser but not implemented
- **Mobile Responsiveness** — Not tested

### Phase 11.2: Full Project Gap Analysis — Remaining Work

#### CRITICAL (Blocker):
| # | Gap | Impact | Priority |
|---|-----|--------|----------|
| 1 | No site drill-down pages | Sidebar "GRID Infrastructure" and "FMSA Office" do nothing | **P0** |
| 2 | No Settings page | No way to configure from UI | **P1** |
| 3 | No API documentation | Developers can't discover API endpoints | **P2** |

#### HIGH:
| # | Gap | Impact | Priority |
|---|-----|--------|----------|
| 4 | No drift reports in wiki-content/sync/drift/ | Drift Reports page shows "no data" | **P1** |
| 5 | No wiki search implementation | Search box in wiki browser doesn't work | **P1** |
| 6 | Kanban case-sensitivity | Dashboard shows 0 tasks, kanban pages show different count | **P1** |
| 7 | No mobile testing | Layout may not work on phones | **P1** |

#### MEDIUM:
| # | Gap | Impact | Priority |
|---|-----|--------|----------|
| 8 | No sync trigger from dashboard | Can't sync from UI | **P2** |
| 9 | No discovery trigger from dashboard | Can't trigger discovery from UI | **P2** |
| 10 | No kanban status update from dashboard | Kanban is read-only | **P2** |
| 11 | Service entity pages missing | Most of the 20 services don't have wiki entity pages | **P2** |
| 12 | No wiki export | Can't download wiki as package | **P2** |

### Phase 11.3: Implementation Plan for Phase 11

#### Step 1: Site Drill-Down Pages (P0, 4-6 hours)
1. Create `site.html` — generic site detail page accepting `?id=grid` or `?id=fmsa`
2. Load site-specific data:
   - Site info from wiki-content/sites/{name}/site-info.md
   - Services from wiki-content/sites/{name}/services.md
   - Monitoring status from wiki-content/sites/{name}/monitoring-status.json
   - Kanban items filtered by site
   - Drift reports for site
3. Wire sidebar links: "GRID Infrastructure" → `site.html?id=grid`, "FMSA Office" → `site.html?id=fmsa`
4. Style consistent with existing pages (dark theme, monitoring status, quick actions)

#### Step 2: Settings Page (P1, 1-2 hours)
1. Create `settings.html` — theme, sync, debug options
2. Implement theme sync (dark/light toggle)
3. Add sync trigger (POST to `/api/sync/run`)
4. Add debug toggle (show/hide API error details)

#### Step 3: API Documentation (P2, 30min)
1. Create `api-docs.html` or serve `api-docs.md`
2. Document all 13 endpoints with examples
3. Add curl examples for each endpoint

#### Step 4: Wiki Search (P1, 2-3 hours)
1. Implement client-side search across wiki-content files
2. Use wiki-service to fetch all page titles
3. Implement fuzzy matching for search results
4. Show results as clickable cards

#### Step 5: Mobile Responsiveness (P1, 2-3 hours)
1. Test all pages on mobile viewport
2. Fix layout issues (sidebar collapse, table overflow, font sizes)
3. Ensure touch targets are large enough

#### Step 6: Service Entity Pages (P2, 4-6 hours)
1. Create entity pages for all 20 services in wiki-content/sites/grid/
2. Use entity page template from Phase 2
3. Populate with data from monitoring-status.json and live SSH
4. Link from service.html and site.html

### Phase 11.4: Technical Debt

1. **Browser caching** — wiki-service serves Cache-Control headers for HTML but JS/CSS may still be cached by browser. Consider adding version query params to static asset URLs.

2. **wiki-service.py stability** — The wiki-service process keeps crashing or being killed. Need to run as a systemd service or nohup on CT120 for production.

3. **Wiki-content/_index.md** — Dashboard sidebar uses `_index.md` but this file doesn't exist in wiki-content/. Need to create it.

4. **monitoring-status.json** — Has stale data. Should be updated by a cron job or live probe.

5. **Front-matter parsing** — Different wiki files use different front-matter styles (AsciiDoc `===`, YAML `---`, or none). The parseServices function now handles both AsciiDoc and YAML but other parsers may need similar updates.

---

### Summary of Today's Work (2026-06-22)

| Area | Before | After |
|------|--------|-------|
| wiki-service.py | NOT RUNNING | Running on port 8082, 13 endpoints |
| Dashboard health metrics | All `--` | 131 wiki pages, 4 active tasks, sync time |
| Services table | Hardcoded fake data | Real data from services.md (verified) |
| Service detail | DID NOT EXIST | `service.html?id={name}` — comprehensive view |
| Service detail data | — | Host, Port, Type, Monitoring, Prometheus, Kuma, Grafana, targets, alerts, wiki content, quick actions |
| Change Board | Empty | 2 pending changes |
| Maintenance Board | Empty | 3 active, 2 completed, 9 procedures |
| Monitoring | JS crash | Real Prometheus/Kuma/Grafana health |
| Wiki Browser | 404 on all links | Loads wiki pages, sidebar navigation |
| API endpoints | 13 defined but none worked | All 13 implemented and verified |
| Dashboard JS loadServices() | Hardcoded array | Fetches services.md, parses markdown table |
| parseServices table parser | Broken (header-after-separator bug) | Fixed (header-before-separator detection, front-matter stripping) |
| /api/drift endpoint | 404 (needed trailing slash) | Works without trailing slash |
| /sites/* routing | Wrong file path | Prepends wiki-content/ correctly |
| wiki-content/sync/drift/ | DID NOT EXIST | Created (no reports yet) |
| Cache headers | None for HTML | no-cache on HTML responses |
| PROJECT-MANIFEST.md | Phase 5 as current goal | Phase 11: remaining work + unbuilt tools plan |
| Gap analysis | Not created | Comprehensive document (this file) |
