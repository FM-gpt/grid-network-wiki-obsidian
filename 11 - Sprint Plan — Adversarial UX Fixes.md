---
title: "SPRINT 11 — ADVERSARIAL UX FIXES"
sprint: 11
date: 2026-06-23
priority: P0 — Product Usability
source: Adversarial UX Test (Retirement Home Director persona) + Gap Analysis
supersedes: Sprint 10 (Phases 20-29)
status: active
---

# Sprint 11: Adversarial UX Fixes

> **Purpose:** Fix all critical UX issues identified by the adversarial UX test and gap analysis. This sprint makes the GRID Wiki usable for real humans — not just agents.
>
> **Active Sprint:** Supersedes Sprint 10. All prior "complete" labels for Phase 12+ are marked UNDELIVERED.
>
> **Goal:** Go from "unusable" to "first-time user can accomplish their core task."

---

## Executive Summary

The GRID Wiki has 84+ planned items but the **user cannot use it** because:
- Sidebar navigation is non-functional (CSS only, no JS)
- 5/10 API endpoints return 404 (dashboard sections empty)
- Wiki browser shows unreadable raw text
- Monitoring page shows contradictory status
- Wiki viewer only shows one file
- No onboarding for first-time users
- No export capability
- No breadcrumb/home navigation inside project views

**This sprint fixes all of that.**

---

## Sprint Scope

### In Scope (P0 — Must Fix)

| # | ID | Issue | Category | Estimated Effort |
|---|----|-------|----------|-----------------|
| 1 | T11-01 | Sidebar navigation fully functional across ALL pages | Navigation | 2h |
| 2 | T11-02 | Fix 5 missing API endpoints (/api/search, /api/active-tasks, /api/sites-index, /api/service-status, /api/settings) | API | 3h |
| 3 | T11-03 | Fix Active Tasks widget — match Kanban board data | Data | 1h |
| 4 | T11-04 | Fix Wiki browser — readable text with hierarchy | UI | 1.5h |
| 5 | T11-05 | Fix Monitoring page — consistent status indicators | Data | 1.5h |
| 6 | T11-06 | Fix Wiki viewer — show directory browser, not single file | Feature | 2h |
| 7 | T11-07 | Add onboarding/empty-state flow for first-time users | UX | 1h |
| 8 | T11-08 | Add export functionality (PDF/CSV) for project data | Feature | 1.5h |
| 9 | T11-09 | Add breadcrumb + home navigation in project detail views | Navigation | 0.5h |
| 10 | T11-10 | Add "Add Project" visual feedback (loading + confirmation) | UX | 0.5h |

### In Scope (P1 — Should Fix)

| # | ID | Issue | Category | Estimated Effort |
|---|----|-------|----------|-----------------|
| 11 | T11-11 | Fix "Browse Wiki" vs "Wiki Viewer" naming confusion | UX | 0.5h |
| 12 | T11-12 | Fix Settings page — make /api/settings return real data | API | 0.5h |
| 13 | T11-13 | Fix dead links (site.html, apiDocs) | Navigation | 1h |
| 14 | T11-14 | Chatbot backend — wire up /api/chat/query and /api/chat/action | Feature | 2h |

### Out of Scope (defer to Sprint 12)

- Phase 12.5 Service Hierarchy Drill-Down
- Phase 12.5.2 Clickable Service Cards
- Phase 12.6.2 Wiki Loading Speed (caching)
- Phase 12.6.3 Better Markdown Rendering
- Phase 12.7.2 Drift Summary Cards as Filters
- Phase 12.7.3 Drift Report Detail Views
- Phase 12.8 Omada Webhook Monitoring
- Phase 12.4.5 Review Gate Confirmation
- Phase 12.4.6 Maintenance Board Card Grouping
- Phase 12.4.7 Maintenance Procedures Document Skills/Tools

---

## Phase Plan (Sequential)

### Phase 30: Sidebar Navigation (P0)

**Goal:** Sidebar is a persistent, functional navigation component on ALL pages.

Steps:
1. Create a shared sidebar HTML template (`dashboard/inc/sidebar.html`)
2. Update all dashboard HTML pages to include the sidebar
3. Implement sidebar toggle with localStorage persistence
4. Ensure sidebar collapses/exapnds correctly
5. Fix all dead links in the sidebar
6. Test on every page: index.html, monitoring.html, drift.html, kanban/*.html, site.html, settings.html

**Acceptance Criteria:**
- Sidebar appears on every page (verified by browser)
- Sidebar toggle button works on every page
- Sidebar remembers open/closed state (localStorage)
- All links navigate to correct destinations
- Active page is highlighted in sidebar

---

### Phase 31: API Endpoints (P0)

**Goal:** All dashboard sections load data correctly.

Steps:
1. Add `/api/search` handler to wiki-service.py (unified search across wiki-content)
2. Add `/api/active-tasks` handler (parse ACTIVE-TASKS.md)
3. Add `/api/sites-index` handler (list wiki-content/sites/ directories)
4. Add `/api/service-status` handler (query Prometheus or return cached status)
5. Add `/api/settings` handler (return service configuration)
6. Add `/api/chat/query` handler (bridge to Honcho)
7. Add `/api/chat/action` handler (create kanban items from chat)
8. Deploy to CT130
9. Verify all endpoints return 200 with valid JSON

**Acceptance Criteria:**
- All 7 new endpoints return 200 with valid JSON
- Dashboard sections populate correctly (Sites, Service Status, Active Tasks)
- No console errors when loading dashboard

---

### Phase 32: Active Tasks Widget (P0)

**Goal:** Active Tasks count matches Kanban board data exactly.

Steps:
1. Audit `/api/active-tasks` response data
2. Update dashboard.js to correctly read and display active task counts
3. Ensure "Active Tasks" on dashboard shows same count as kanban board
4. Fix any data source mismatch (kanban files vs ACTIVE-TASKS.md)
5. Test: navigate to kanban board, note counts, return to dashboard, verify match

**Acceptance Criteria:**
- Dashboard "Active Tasks" count matches kanban board count
- "Active Development Board" shows top 5 tasks only
- "Expand to full board" link works correctly

---

### Phase 33: Wiki Browser Fix (P0)

**Goal:** Wiki browser shows readable, hierarchical file tree with category icons.

Steps:
1. Fix `renderTree()` in wiki-browser.html to apply proper CSS classes
2. Add category-based icons (📋 for plans, 🔧 for ops, 📊 for monitoring, etc.)
3. Add indentation for directory hierarchy
4. Improve filterTree() for search within tree
5. Fix CSS: ensure text has proper contrast, padding, and font size
6. Test: open wiki-browser.html, verify all files readable and clickable

**Acceptance Criteria:**
- All files in tree are readable (proper contrast, font size, padding)
- Directory hierarchy is visually clear (indentation, expand/collapse)
- Category icons are displayed correctly
- File search filters the tree correctly
- Clicking a file opens it in a new view

---

### Phase 34: Monitoring Page Fix (P0)

**Goal:** Monitoring page shows consistent, accurate status data.

Steps:
1. Audit monitoring.html status display logic
2. Fix status icons to correctly reflect API data (no contradictory state)
3. Handle "unreachable" state gracefully (show "⚠️" not "❌")
4. Ensure service cards show correct Prometheus source
5. Test: load monitoring.html, verify all status icons match API data

**Acceptance Criteria:**
- All status icons accurately reflect current state
- No contradictory headers vs table data
- Unreachable services show "⚠️" not "❌"
- Clicking a service card shows connection details

---

### Phase 35: Wiki Viewer Fix (P0)

**Goal:** Wiki viewer shows a directory browser, not a single file.

Steps:
1. Replace wiki.html single-file viewer with directory browser
2. Use `/api/wiki-index` to populate the file list
3. Add category filters (Plans, Operations, Monitoring, Sites, etc.)
4. Add search within the directory
5. Clicking a file renders it with markdown formatting
6. Test: open wiki.html, verify directory browser loads, click files to view

**Acceptance Criteria:**
- Wiki viewer loads as a directory browser (not single file)
- Files grouped by category with icons
- Search filters the directory correctly
- Clicking a file renders markdown content
- "Back to directory" button works

---

### Phase 36: Onboarding & Empty States (P0)

**Goal:** First-time users know what to do immediately.

Steps:
1. Add "getting started" section to dashboard when no projects exist
2. Add prominent "Add First Project" CTA button
3. Add tooltip/walkthrough overlay on first visit
4. Add empty-state messages for all dashboard sections
5. Store "has onboarding" flag in localStorage
6. Test: clear localStorage, load dashboard, verify onboarding appears

**Acceptance Criteria:**
- Dashboard shows "getting started" CTA for new users
- Onboarding does not reappear for returning users
- All empty dashboard sections show helpful messages (not "--" or blank)
- First user can find how to add a project within 3 clicks

---

### Phase 37: Export Functionality (P1)

**Goal:** Users can export project data for sharing.

Steps:
1. Add `/api/wiki-export` handler (or verify existing one works)
2. Add "Export" buttons to dashboard cards
3. Implement PDF export (using browser's print-to-PDF)
4. Implement CSV export for kanban data
5. Test: click export on dashboard, verify download starts

**Acceptance Criteria:**
- Dashboard has "Export" button (PDF)
- Kanban board has "Export" button (CSV)
- PDF export produces readable document
- CSV export contains all kanban data

---

### Phase 38: Breadcrumb Navigation (P0)

**Goal:** Users always know where they are and how to navigate back.

Steps:
1. Add breadcrumb component to all sub-pages (wiki.html, monitoring.html, kanban/*.html, site.html, settings.html)
2. Add "Home" button to every page
3. Add "Current Page" highlight in sidebar
4. Test: navigate to each page, verify breadcrumb shows correct path

**Acceptance Criteria:**
- Every sub-page has a visible breadcrumb
- Every page has a "Home" button
- Breadcrumb links navigate correctly
- Current page is highlighted in sidebar

---

### Phase 39: Add Project Feedback (P0)

**Goal:** Users get visual confirmation when adding projects/tasks.

Steps:
1. Add loading spinner to "Add" buttons
2. Add success toast notification after action completes
3. Disable button during loading to prevent double-click
4. Test: click "Add Project," verify loading state, verify success message

**Acceptance Criteria:**
- Loading spinner appears when "Add" is clicked
- Success toast appears after action completes
- Button is disabled during loading
- No double-submission possible

---

### Phase 40: Remaining P1 Items

Steps:
1. Fix "Browse Wiki" vs "Wiki Viewer" naming — relabel with tooltips
2. Fix Settings page — make `/api/settings` return real data
3. Fix dead links (site.html, apiDocs) — update to functional destinations
4. Wire up chatbot backend — connect chatbox to `/api/chat/query` and `/api/chat/action`
5. Test all fixes in browser

---

## Verification Checklist

Before marking this sprint complete:

- [ ] Sidebar works on ALL pages (index, monitoring, drift, kanban/change, kanban/maintenance, site, settings)
- [ ] All 7 new API endpoints return 200
- [ ] Dashboard loads with no console errors
- [ ] Active Tasks count matches kanban board
- [ ] Wiki browser shows readable files with icons
- [ ] Monitoring page status is consistent
- [ ] Wiki viewer is a directory browser
- [ ] Onboarding CTA appears for new users
- [ ] Export buttons work
- [ ] Breadcrumbs and home navigation present on all sub-pages
- [ ] Add Project has visual feedback
- [ ] All links navigate correctly
- [ ] Chatbot sends messages to backend
- [ ] Deployed to CT130
- [ ] Browser QA completed

---

## Deployment Plan

1. Update all files in `/Users/tron/grid-network-wiki-tool/` (local workspace)
2. Run `npm test` (if applicable)
3. Run `npm run build` (if applicable)
4. Deploy to CT130: `./deploy.sh` or `scp` to CT130:8082
5. Restart wiki-service.py on CT130
6. Browser QA — click through every page
7. Adversarial UX test — re-test as persona
8. Report verification results

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Deploying to CT130 breaks production | HIGH | Deploy to CT121 first, verify, then CT130 |
| API endpoint conflicts with existing routes | MEDIUM | Check wiki-service.py route table before adding |
| Sidebar changes break sub-pages | MEDIUM | Test each page individually after change |
| Onboarding localStorage conflicts | LOW | Use unique key prefix: `grid-wiki-onboarding-` |
| PDF export doesn't work in all browsers | LOW | Use browser-native print, not JS PDF library |

---

## Success Criteria

**This sprint is complete when:**
1. A first-time user can add a project, view the wiki, check monitoring, and navigate between pages without confusion
2. All dashboard sections show real data (no "--", no spinners forever)
3. All links work
4. Sidebar is functional on every page
5. Adversarial UX test (rerun) shows improvement in ALL previously failed categories
6. Zero RED items remain from the gap analysis
