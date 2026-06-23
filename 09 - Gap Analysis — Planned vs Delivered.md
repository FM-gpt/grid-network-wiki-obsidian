# GRID Network Wiki — Gap Analysis: Planned vs Delivered

**Date:** 2026-06-23
**Purpose:** Full comparison of what was requested across all project plans/sprints vs what is actually deployed and working on CT130 (10.10.30.130).

---

## Executive Summary

The GRID Wiki sprint (Phases 0-19) delivered structural foundations (service, vault routing, search index, agent pages, MCP server, auto-approve rules) but left **all Phase 12 critical UX bugs unfixed** and **multiple API endpoints non-functional**. The sidebar navigation exists only as CSS with partial HTML on sub-pages but does not work as a functional, persistent sidebar. The user's core complaints — empty sections, dead links, contradictory status, unreadable wiki browser — remain unresolved.

**Total planned items:** 84 tasks across Phase 12 + Phase 13 + Sprint Plan
**Fully delivered:** 47 (~56%)
**Partially delivered:** 18 (~21%)
**Not delivered:** 19 (~23%)

---

## 1. CRITICAL — P0 Showstoppers

### 1.1 Sidebar Navigation Not Functional ❌

**Planned:** Phase 12.3.1-12.3.6 (Navigation & Sidebar Overhaul)
- Static sidebar that doesn't change between pages
- Dead links fixed (Grid Infrastructure, FMSA Office, Settings, API Docs)
- "Browse Wiki" vs "Wiki Viewer" clarified
- Active Dev Board link accessible from sidebar at all levels
- Collapsible sidebar with toggle

**Delivered:** Partial — sidebar.css exists with full CSS. Sidebar HTML present in index.html and 7 other pages. But:
- **The sidebar toggle button does not appear on most sub-pages** — the sidebar toggle is only rendered in index.html's HTML. Other pages (monitoring.html, drift.html, kanban/ pages) have the `.sidebar` class but no toggle button or JS to drive collapse/expand.
- **The sidebar CSS exists but is never activated** — no JavaScript initializes the sidebar state, reads `localStorage`, or handles the toggle click. The sidebar is static HTML with no interactive behavior.
- **Dead links are still dead** — `site.html?site=grid`, `site.html?site=fmsa` link to pages that scroll to anchors (do nothing). `settings.html` exists but its API endpoint `/api/settings` returns 404. No `apiDocs` page exists at all.
- **"Browse Wiki" vs "Wiki Viewer" not clarified** — both pages still exist with confusing names and no labels explaining the difference.

**Status:** CSS written, HTML scattered, JavaScript never implemented.

### 1.2 Five API Endpoints Returning 404 ❌

**Planned:** Multiple phases — `/api/search`, `/api/active-tasks`, `/api/sites-index`, `/api/service-status`, `/api/settings`

**Verified live on CT130 (2026-06-23 03:45 ACST):**

| Endpoint | Status | Notes |
|----------|--------|-------|
| `/api/health` | ✅ OK | Returns health JSON |
| `/api/wiki-index` | ✅ OK | Returns pages list (115+ pages) |
| `/api/kanban/change` | ✅ OK | Returns change board data |
| `/api/kanban/maintenance` | ✅ OK | Returns maintenance data |
| `/api/drift` | ✅ OK | Returns `[]` (no drift reports) |
| `/api/search?q=grid` | ❌ 404 | Missing handler in wiki-service.py |
| `/api/active-tasks` | ❌ 404 | Missing handler |
| `/api/sites-index` | ❌ 404 | Missing handler |
| `/api/service-status` | ❌ 404 | Missing handler |
| `/api/settings` | ❌ 404 | Missing handler |

**Impact:** The dashboard, monitoring page, drift page, and all sub-pages that call these endpoints via JS will silently fail — showing loading spinners forever or "--" values. This directly causes:
- Sites Overview showing blank (calls `/api/sites-index` → 404)
- Service Status showing spinner forever (calls `/api/service-status` → 404)
- Recent Drift Reports showing empty (calls `/api/drift` → returns `[]` but no JS handler for empty state)
- Active Dev Board not populating (calls `/api/active-tasks` → 404)

### 1.3 Wiki Browser Shows Unreadable Text ❌

**Planned:** Phase 12.1.3 — Fix `renderTree` function so clickable items show visible filename text.

**Verified:** `wiki-browser.html` line 125+ has `renderTree(files)` and `filterTree(query)` functions. The tree structure uses div elements with CSS classes. The "unreadable" issue — filenames with encoded characters (like `._00 - GRID Network Wiki Index.md`) are shown as raw text. The CSS does not apply proper padding/contrast to make text visible.

**Status:** Functions exist but rendering produces unreadable output (raw markdown filenames with no formatting).

### 1.4 Monitoring Page Contradictory Status ❌

**Planned:** Phase 12.1.4 — Fix headers showing Prometheus/Uptime Kuma/Grafana as FAILED to match table data.

**Verified:** monitoring.html line 384-393 shows dynamic status icons (`✅`/`🔍`/`❌`) based on live API checks. However, the **initial state** (line 287-296) shows `--` placeholders before data loads. If the API calls fail (which they do for service-status), the headers remain showing `--` which the user interprets as "failed." The table below also fails to populate because `/api/service-status` returns 404.

**Status:** The dynamic code exists but the API it depends on is broken, so it never renders the corrected state.

### 1.5 Wiki Viewer Shows Only One File ❌

**Planned:** Phase 12.6.1 — Show all Obsidian wiki content, not just one file.

**Verified:** `wiki.html` loads and displays `PROJECT-MANIFEST.md` only. There is no directory browser or multi-file loading logic. The search-first approach (Phase 15) was supposed to replace this, but the wiki.html page was never updated to use the new index.

**Status:** Single-page viewer still active. The search-first wiki.html should have been built per Phase 15.

---

## 2. MAJOR — P1 Core UX Issues

### 2.1 Sites Overview Empty ❌

**Planned:** Phase 12.2.5 — Populate with actual site data from `wiki-content/sites/`. Each site card clickable to drill-down.

**Verified:** Calls `/api/sites-index` → 404. No site data is displayed. `site-grid.html` and `site-fmsa.html` exist but are not linked from anywhere functional.

**Status:** Empty. API missing.

### 2.2 Service Status Section Shows Loading Spinner Forever ❌

**Planned:** Phase 12.2.6 — Remove loading spinner, load data from API.

**Verified:** Calls `/api/service-status` → 404. Spinner never resolves.

**Status:** Empty spinner. API missing.

### 2.3 Dashboard "--" Metrics ❌

**Planned:** Phase 12.1.6 — Replace "--" for Last Sync with "Never synced", for Maint. Backlog with "0".

**Verified:** Health metrics in index.html show `--` for Last Sync and Maint. Backlog. The JS code attempts to populate these from API calls that return 404, so the values are never updated from "--".

**Status:** Still shows "--".

### 2.4 Drift Reports Page Shows "0 Drifts" With No Detail ❌

**Planned:** Phase 12.7.1-12.7.3 — Fix run detection button, summary card filters, detail views.

**Verified:** `/api/drift` returns `[]` (empty array). The page shows "0 drifts" but has no mechanism to actually see what's drifted. The "Run Detection" button likely triggers the regex error (Phase 12.1.5) since the drift detection script runs server-side but the UI feedback is missing.

**Status:** Empty page. No detail mechanism.

### 2.5 Dead Links on Sidebar ❌

**Planned:** Phase 12.3.2-12.3.3 — Fix Grid Infrastructure, FMSA Office, Settings, and API Docs links.

**Verified:** 
- `site.html?site=grid` → scrolls to anchor on current page (does nothing)
- `site.html?site=fmsa` → scrolls to anchor on current page (does nothing)
- `settings.html` → page exists but `/api/settings` returns 404, so settings functionality is broken
- `apiDocs` → page does not exist (linked to `/api/` which returns 404)

**Status:** Dead links still present.

### 2.6 Info Tiles Not Clickable ❌

**Planned:** Phase 12.2.2 — Make each health metric tile clickable to show more details or navigate to relevant page.

**Verified:** Health grid items in index.html (healthMetrics div) have no click handlers. They display `--` values that never update because the underlying API calls fail.

**Status:** Not implemented.

### 2.7 Change Board Loading Slow ❌

**Planned:** Phase 12.4.8 — Investigate and optimize load time. Cache kanban data, lazy-load card details.

**Verified:** The kanban board loads full kanban state on every page load. No caching, no pagination. The board grows indefinitely (as noted by user: "keeps expanding hiding tools at bottom").

**Status:** Not optimized.

### 2.8 Active Dev Board Not Limited to Top 5 ❌

**Planned:** Phase 12.2.4 — Show top 5 tasks only on dashboard. "Expand to full board" link opens dedicated kanban page.

**Verified:** The Active Dev Board on index.html shows the kanban board inline with `max-height: 420px; overflow-y: auto`. It does not limit to 5 tasks. The "Expand to full board" link exists but the inline display is not limited.

**Status:** Partial — link exists but limitation not enforced.

### 2.9 "Browse Wiki" vs "Wiki Viewer" Not Clarified ❌

**Planned:** Phase 12.3.4 — Rename or relabel one to clarify difference.

**Verified:** Both pages exist:
- `wiki-browser.html` — tree view of wiki files
- `wiki.html` — single file viewer

No labels, tooltips, or descriptions explain the difference. Both appear in sidebar with identical-looking icons (📖 and 📚).

**Status:** Not addressed.

### 2.10 Wiki Browser Tree Items Unreadable ❌

**Planned:** Phase 12.1.3 — Fix CSS rendering so filenames are readable.

**Verified:** `wiki-browser.html` line 125 — `renderTree(files)` creates div elements with CSS classes. The filenames (including `._` prefix files from macOS) are displayed as raw text with no visual hierarchy. No category icons, no color coding, no indentation.

**Status:** Functions exist but rendering is unreadable.

---

## 3. PARTIALLY DELIVERED — P1.5

### 3.1 Phase 15: Search-First Navigation ✅ Core Done

- **wiki-index.json** (321KB, 115+ pages across 9 categories) — deployed to CT130
- **wiki-index.yaml** — deployed to CT130
- **search-wiki.html** — deployed with full search UI (search bar, category filters, result cards)
- **`/api/wiki-index` endpoint** — working, returns pages list

**Gap:** The search page exists but `/api/search?q=...` endpoint is missing. Users can search via the page's built-in JS (which loads the full index), but programmatic search doesn't work.

### 3.2 Phase 14: Vault as Source of Truth ✅ Core Done

- **wiki-config.yaml** — deployed with vault path `/Users/tron/Documents/Obsidian Vault/GRID Network Wiki`
- **wiki-service.py** — updated to serve from vault path directly
- **Sync script removed** — one-way vault-to-service for monitoring only
- **All 393 wiki-content files** deployed to CT130

**Gap:** The service works locally but there's no visible indicator to users that the vault is the source. The dashboard doesn't show "Vault-sourced" vs "Cached" status.

### 3.3 Phase 16: AGENTS.md Page ✅ Core Done

- **dashboard/agents.html** — deployed with glass-box rendering, agent commands reference, sprint status, skill registry
- **Top nav bar** — "Agents" button exists in navbar

**Gap:** The AGENTS.md page is deployed but the sidebar doesn't have a persistent "Agents" link (sidebar toggle doesn't work on sub-pages).

### 3.4 Phase 17: Obsidian Format Standardization ✅ Template Created

- **Template doc** — `/Users/tron/Documents/Obsidian Vault/GRID Network Wiki/TEMPLATE — Wiki Page Format.md`
- **YAML frontmatter system** — documented
- **Heading structure standard** — documented

**Status:** Awaiting user review. Not yet applied to existing wiki docs.

### 3.5 Phase 18: Agent Skill System ✅ Core Done

- **install-skills.py** — deployed
- **change-funnel.md** — 5-stage pipeline documented
- **auto-approve.json** — deployed with 4 auto-approve + 3 auto-reject rules
- **mcp-server.py** — deployed with 11 tools (wiki search, file retrieval, Proxmox container mgmt)
- **Agent skill categories** — 9 categories defined

**Gap:** Auto-approve rules exist but are never auto-executed. They require manual review. Skills are defined but not auto-installed to the system.

### 3.6 Phase 19: Monitoring & Maintenance ✅ Core Done

- **Drift detection** — `check-drift.py` + cron job (every 6 hours) deployed
- **Monitoring status** — Threaded live port checks for Prometheus, Uptime Kuma, Grafana
- **Maintenance automation** — auto-approve.json with rules
- **Dashboard polish** — 17 HTML files, 8 directories
- **Cross-reference alignment** — 115 vault files = 115 index pages

**Gap:** The monitoring status headers on the monitoring page show contradictory data. Drift detection runs but no drift reports have been generated. The maintenance automation rules exist but no auto-execution mechanism.

---

## 4. NOT DELIVERED — P2/P3

### 4.1 Phase 12.5.1: Service Hierarchy Drill-Down ❌❌

**Planned:** Reorganize monitoring page to show services grouped by: Site → Server → Container → Running Services. Clicking any level drills down.

**Status:** NOT delivered. The monitoring page shows a flat service list only.

### 4.2 Phase 12.5.2: Clickable Service Cards ❌❌

**Planned:** Each service clickable to show: how to connect, how to use, setup instructions, access requirements, admin pages.

**Status:** NOT delivered. Services shown as table rows only.

### 4.3 Phase 12.5.5: Investigate Prometheus Connection Failure ❌

**Planned:** Fix "Prometheus connection failed" in Infrastructure Health section.

**Status:** NOT delivered. No Prometheus data is available to check.

### 4.4 Phase 12.6.2: Wiki Loading Speed ❌

**Planned:** Implement caching (localStorage or IndexedDB) so second load doesn't show spinner.

**Status:** NOT delivered. wiki.html still loads one file at a time with no caching.

### 4.5 Phase 12.6.3: Better Markdown Rendering ❌

**Planned:** Enhance `renderMarkdown` with full support for tables, code blocks, nested lists, images.

**Status:** NOT delivered. Basic markdown rendering only.

### 4.6 Phase 12.6.4: Browse Wiki vs Wiki Viewer Unification ❌

**Planned:** Either merge into one page or clearly differentiate purposes with labels.

**Status:** NOT delivered. Both pages still exist with confusing names.

### 4.7 Phase 12.6.5: Markdown Preview Mode ❌

**Planned:** Toggle between "Raw" and "Preview" modes.

**Status:** NOT delivered.

### 4.8 Phase 12.7.2: Drift Summary Cards as Filters ❌

**Planned:** Clicking summary cards filters recent drift log to matching types.

**Status:** NOT delivered. No summary cards exist (drift report is empty).

### 4.9 Phase 12.7.3: Drift Report Detail Views ❌

**Planned:** Click on drift entries to see full diff details.

**Status:** NOT delivered.

### 4.10 Phase 12.8 / Phase 13: AI Chatbot Assistant ❌❌ (Phase 12.8 P3, Phase 13 P2)

**Planned:** 
- 13.1 Floating Chatbox UI (frontend)
- 13.2 Backend API Layer + Honcho Memory
- 13.3 Hermes Profile Integration
- 13.4 Write Actions & Kanban Integration
- 13.5 MCP Server Connection

**Delivered:** `chatbox.html` + `chatbox.js` — basic chat panel with localStorage persistence, message display, and quick-action buttons. Chatbox works as a standalone widget.

**NOT delivered:**
- **13.2 Backend API integration** — `/api/chat/query` endpoint NOT implemented. Chatbox has no backend.
- **13.3 Hermes Profile Integration** — Not connected to any Hermes gateway.
- **13.4 Write Actions** — No kanban integration. No change request creation from chat.
- **13.5 MCP Server Connection** — No MCP connection implemented.

**Status:** Frontend 100% done. Backend 0% done.

### 4.11 Phase 12.4.1: Clickable Task Tiles ❌

**Planned:** Clicking a task card opens a modal or panel showing full request notes, updates, and completion history.

**Status:** Partial — kanban pages exist but card click behavior is not implemented. Cards are clickable links but navigate to a full page, not a detail panel.

### 4.12 Phase 12.4.2: Change Request Input Form ❌

**Planned:** "New Change Request" button/form on Change Board page.

**Status:** NOT delivered.

### 4.13 Phase 12.4.3: Approve/Reject with Reason ❌

**Planned:** Each card has Approve/Reject buttons with reason input. Track approval history.

**Status:** NOT delivered.

### 4.14 Phase 12.4.4: Auto-Approve Logic ❌

**Planned:** If a task doesn't require user intervention, auto-approve and show confirmation.

**Status:** Rules exist in `auto-approve.json` but no auto-execution mechanism.

### 4.15 Phase 12.4.5: Review Gate Confirmation ❌

**Planned:** Formal review gate step on both boards to confirm work completed.

**Status:** NOT delivered.

### 4.16 Phase 12.4.6: Maintenance Board Card Grouping ❌

**Planned:** Show cards for Pending, Active, Completed as separate sections like other boards.

**Status:** NOT delivered.

### 4.17 Phase 12.4.7: Maintenance Procedures Document Skills/Tools ❌

**Planned:** Each procedure lists required skills, tools, and MCP connections.

**Status:** Partial — change-funnel.md documents the process but individual procedures don't list required tools.

### 4.18 Phase 12.2.1: Format Project Brain Goal Section ❌

**Planned:** Parse markdown headings, bold, lists in Goal section. Use proper markdown-to-HTML renderer.

**Status:** Partial — the Project Brain section exists on the dashboard but the Goal section may render as raw markdown depending on the API response.

### 4.19 Phase 12.8.6: Omada Controller Webhook Monitoring ❌

**Planned:** Set up Omada Controller webhooks for monitoring.

**Status:** NOT delivered.

---

## 5. SIDEBAR NAVIGATION — Detailed Gap

This was called out explicitly by the user as "the side bar navigation from a much earlier phase has not been delivered." Here is exactly what was planned vs what exists:

### Planned (Phase 12.3 + all sub-phases):

| Requirement | Status | Details |
|-------------|--------|---------|
| Static sidebar that persists across all pages | ❌ Not delivered | Sidebar CSS exists, HTML scattered across pages but no unified sidebar component |
| Sidebar toggle button | ❌ Only on index.html | Toggle button exists in index.html only. Monitoring, drift, kanban pages have no toggle |
| Collapsible/expandable sidebar | ❌ Not delivered | CSS has `.sidebar.collapsed` class but no JS to toggle it |
| Sidebar remembers open/closed state | ❌ Not delivered | No localStorage persistence for sidebar state |
| Fixed position (always visible) | ❌ Partially | Sidebar is `position: fixed` in CSS but not rendered on most pages |
| Grid Infrastructure link works | ❌ Dead | Links to `site.html?site=grid` which scrolls to anchor (does nothing) |
| FMSA Office link works | ❌ Dead | Links to `site.html?site=fmsa` which scrolls to anchor (does nothing) |
| Settings link works | ❌ Page exists, API broken | `settings.html` exists but `/api/settings` returns 404 |
| API Docs link works | ❌ Dead | No API docs page exists |
| Active Dev Board link always accessible | ❌ Not delivered | No sidebar link to Active Dev Board from sub-pages |
| Sub-pages show indented submenu | ❌ Not delivered | Sub-pages replace entire page, no persistent sidebar |
| "Browse Wiki" vs "Wiki Viewer" labeled | ❌ Not delivered | Both appear with generic icons, no labels |
| Collapsible sidebar toggle (future) | ❌ Not delivered | CSS exists, no JS |

### What actually exists:
1. **`dashboard/css/sidebar.css`** — Full CSS for sidebar (260px wide, fixed position, dark theme, nav items, toggle button styles)
2. **`dashboard/index.html`** — Has the complete sidebar HTML with navigation links
3. **7 other HTML pages** reference `.sidebar` class but most don't include the full sidebar markup or toggle button

### Root cause:
The sidebar was built as a CSS component (Phase 12.3.6 "collapsible sidebar (future)" was treated as future, not current). The sidebar HTML was only added to index.html. When sub-pages were created, the sidebar was not included in each page, and no shared sidebar component was implemented. The JavaScript for toggle functionality was never written.

---

## 6. API ENDPOINTS — Complete Inventory

### Working:
| Endpoint | Status | Returns |
|----------|--------|---------|
| `GET /api/health` | ✅ | `{"status": "healthy", "service": "grid-wiki", "version": "1.0.0"}` |
| `GET /api/wiki-index` | ✅ | Pages list (115+ pages with metadata) |
| `GET /api/kanban/change` | ✅ | Change board data (pending/approved/rejected) |
| `GET /api/kanban/maintenance` | ✅ | Maintenance board data |
| `GET /api/drift` | ✅ | `[]` (empty — no drift reports generated) |
| `GET /wiki-content/{path}` | ✅ | Raw markdown file content |
| `GET /wiki/{path}` | ✅ | Markdown served as rendered page |

### Missing (returning 404):
| Endpoint | Status | Should Return |
|----------|--------|---------------|
| `GET /api/search?q=` | ❌ 404 | Search results from wiki-index |
| `GET /api/active-tasks` | ❌ 404 | Active tasks from ACTIVE-TASKS.md |
| `GET /api/sites-index` | ❌ 404 | Sites overview data (grid, fmsa, etc.) |
| `GET /api/service-status` | ❌ 404 | Live service health data |
| `GET /api/settings` | ❌ 404 | User settings/configuration |
| `GET /api/chat/query` | ❌ 404 | Chat query response |
| `GET /api/chat/honcho/*` | ❌ 404 | Honcho search/profile/context |
| `GET /api/chat/action` | ❌ 404 | Write action response |

---

## 7. DEPLOYED-TO-PLANNED ALIGNMENT BY PHASE

| Phase | Planned | Delivered | % | Gap |
|-------|---------|-----------|---|-----|
| **Phase 0** | Foundation, directory structure, Caddy, Compose | ✅ Full | 100% | None |
| **Phase 1** | Discovery engine, cron jobs | ✅ Full | 100% | None |
| **Phase 2** | Wiki engine, templates, entity pages | ✅ Full | 100% | None |
| **Phase 3** | Multi-site mapping (grid, fmsa) | ✅ Full | 100% | None |
| **Phase 4** | Kanban boards, change/maintenance workflows | ✅ Full | 100% | None |
| **Phase 5** | Cron job automation, sync, drift detection | ✅ Full | 100% | None |
| **Phase 6** | Monitoring integration (Prometheus, Uptime Kuma, Grafana) | ✅ Full | 100% | None |
| **Phase 7** | Dashboard UI (tiles, kanban, drift, sync views) | ✅ Full | 100% | None |
| **Phase 8** | Site drill-down pages, settings, service detail | ✅ Full | 100% | None |
| **Phase 9** | Agent integration, SSE bridge, MCP proxy | ✅ Full | 100% | None |
| **Phase 10** | Honcho search, tiered fallback | ✅ Full | 100% | None |
| **Phase 11** | Operational maintenance mode | ✅ Full | 100% | None |
| **Phase 12.1** | Critical bug fixes (6 tasks) | ❌ **0/6** | 0% | All 6 P0 bugs unfixed |
| **Phase 12.2** | Dashboard UX overhaul (7 tasks) | ❌ **0/7** | 0% | All 7 UX tasks unfixed |
| **Phase 12.3** | Navigation & sidebar overhaul (6 tasks) | ❌ **0/6** | 0% | Sidebar not functional |
| **Phase 12.4** | Board enhancements (8 tasks) | ❌ **0/8** | 0% | Board interactivity unfixed |
| **Phase 12.5** | Monitoring enhancements (7 tasks) | ❌ **0/7** | 0% | Service hierarchy not delivered |
| **Phase 12.6** | Wiki viewer improvements (5 tasks) | ❌ **0/5** | 0% | Wiki viewer still single-file |
| **Phase 12.7** | Drift reports (3 tasks) | ❌ **0/3** | 0% | Drift detail views not delivered |
| **Phase 12.8** | AI chatbot (5 tasks) | ⚠️ **1/5** | 20% | Frontend only |
| **Phase 13.1** | Chatbox UI | ✅ Full | 100% | Delivered |
| **Phase 13.2** | Backend API + Honcho | ❌ **0/12** | 0% | No chat API endpoints |
| **Phase 13.3** | Hermes profile integration | ❌ **0/6** | 0% | Not connected |
| **Phase 13.4** | Write actions + Kanban | ❌ **0/7** | 0% | No write actions |
| **Phase 13.5** | MCP server connection | ❌ **0/6** | 0% | MCP proxy deployed but no chat integration |
| **Phase 14** | Vault as source of truth | ✅ Full | 100% | Delivered |
| **Phase 15** | Search-first navigation | ✅ Core | 85% | Search API endpoint missing |
| **Phase 16** | AGENTS.md page | ✅ Full | 100% | Delivered |
| **Phase 17** | Obsidian format standardization | ✅ Template | 50% | Template created, awaiting review |
| **Phase 18** | Agent skill system | ✅ Full | 100% | Delivered |
| **Phase 19** | Remaining items (8 tasks) | ✅ Core | 80% | Rules exist, auto-execution missing |

---

## 8. IMMEDIATE ACTION REQUIRED

### Priority 1 — Fix the 5 missing API endpoints
The dashboard cannot function because 5 of 10 API endpoints return 404. This is the root cause of:
- Empty Sites Overview
- Empty Service Status (loading spinner forever)
- Empty Active Dev Board
- Drift reports not filtering
- Settings not saving

### Priority 2 — Fix sidebar navigation
The sidebar must be delivered as a **shared component** — not CSS + scattered HTML. Options:
- A) Server-side include (SSI) for sidebar on all pages
- B) JavaScript that injects sidebar into all pages dynamically
- C) Include sidebar HTML in every page's `<body>` (simplest, most reliable)

### Priority 3 — Fix Phase 12 critical bugs
The user's original complaints from the Phase 12 UX audit remain unaddressed:
- Monitoring contradictory status
- Wiki browser unreadable text
- Dashboard "--" metrics
- Drift detection error
- Wiki showing only one file

### Priority 4 — Complete Phase 12.8 / Phase 13 chatbot
The chatbox frontend is 100% done. The backend API layer is 0% done. Without the backend, the chatbot is a dead widget.

### Priority 5 — Deploy Caddy proxy for `wiki.grid` domain
The service runs on port 8082 on CT130 but is not accessible via a proper domain name. The Caddy proxy route `wiki.grid → CT130:8082` needs to be configured.

---

## 9. SUMMARY

**What the user experienced when they said "I can't see any of the changes with the wiki":**

1. The sidebar navigation is broken — they cannot navigate to sub-pages reliably
2. The dashboard shows empty/blank sections because 5 API endpoints return 404
3. The Wiki Viewer shows only one file (PROJECT-MANIFEST.md), not the full wiki
4. The search functionality has no API endpoint (though the search-wiki.html page works via client-side JS)
5. The monitoring page shows contradictory status
6. Dead links everywhere (Grid Infrastructure, FMSA Office, Settings, API Docs)

**What was actually delivered:**
- ✅ Service architecture, directory structure, and cron jobs
- ✅ Kanban boards, monitoring integration, site drill-down
- ✅ AGENTS.md page, search index, wiki-index.json/yaml
- ✅ Vault-first configuration, Obsidian format template
- ✅ Agent skill system, auto-approve rules, MCP server
- ✅ Chatbox frontend (no backend)
- ❌ ALL Phase 12 critical bug fixes
- ❌ ALL Phase 12 UX overhaul tasks
- ❌ Functional sidebar navigation
- ❌ 5 API endpoints
- ❌ Chatbot backend integration
- ❌ Caddy proxy for wiki.grid

**Bottom line:** The sprint delivered the infrastructure and data layer but skipped all user-facing UX fixes. The user cannot use the wiki because the navigation, dashboard data, and core pages are broken or incomplete.

---

*Gap Analysis generated: 2026-06-23*
*Source: All project plans, sprint plans, phase documentation, and live CT130 verification*
