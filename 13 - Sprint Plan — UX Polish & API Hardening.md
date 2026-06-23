---
title: "Sprint 13 — UX Polish & API Hardening"
sprint_number: 13
start_date: 2026-06-24
status: Active
supersedes: "12 - Sprint Plan — Core Pages & Reliability"
---

# Sprint 13: UX Polish & API Hardening

## Goal
Fix all remaining UX inconsistencies, complete the missing API endpoints, harden reliability, and deliver a polished product ready for the adversarial UX test.

## Scope Boundaries
- **IN SCOPE:** Dashboard sidebar consistency, missing API endpoints, chatbot backend, reliability hardening, metadata/favicon, error boundaries.
- **OUT OF SCOPE:** Mobile responsiveness, service entity pages (20 services), advanced chatbot features, Caddy proxy setup, Phase 12.5 monitoring hierarchy.

## Active Tasks

| Task ID | Description | Priority | Status |
|---------|-------------|----------|--------|
| T13-01 | Fix dashboard sidebar — "Wiki Viewer" → "Wiki Reader" | RED | |
| T13-02 | Complete ALL missing API endpoints (search, active-tasks, sites-index, service-status, settings, chat) | RED | |
| T13-03 | Fix dashboard "OPEN DRIFT: 10" — match actual drift count | RED | |
| T13-04 | Fix service.html to show real service data | RED | |
| T13-05 | Add chatbot backend integration (Honcho memory, Hermes profile) | RED | |
| T13-06 | Add proper favicon, meta tags, page titles to all pages | YELLOW | |
| T13-07 | Add error boundaries — graceful degradation on all pages | YELLOW | |
| T13-08 | Improve chatbot response quality with better wiki context | YELLOW | |
| T13-09 | Fix sidebar nav link consistency across ALL pages | YELLOW | |
| T13-10 | Verify all pages pass adversarial UX test criteria | GREEN | |

## Implementation Plan

### Phase 1: Critical API Endpoints (RED — T13-02)
1. Implement `/api/search?q=` endpoint using wiki-index data
2. Implement `/api/active-tasks` endpoint reading ACTIVE-TASKS.md
3. Implement `/api/sites-index` endpoint reading sites-index.md
4. Implement `/api/service-status` endpoint with live health checks
5. Implement `/api/settings` endpoint with localStorage sync
6. Implement `/api/chat/query` backend with Honcho memory integration

### Phase 2: Dashboard & Sidebar Fixes (RED — T13-01, T13-03)
1. Fix dashboard sidebar "Wiki Viewer" → "Wiki Reader" in index.html
2. Fix OPEN DRIFT counter — use actual drift count from `/api/drift`
3. Fix service.html to show real service data from `/api/service-status`

### Phase 3: Chatbot Backend (RED — T13-05)
1. Wire up chatbox.js to `/api/chat/query` backend
2. Add Honcho memory profile/context search
3. Add Hermes profile integration for write actions

### Phase 4: Reliability & Polish (YELLOW — T13-06, T13-07, T13-08, T13-09)
1. Add favicon, meta tags, proper titles to all pages
2. Add error boundaries — graceful fallback on API failures
3. Improve chatbot response quality with wiki context
4. Verify all sidebar nav links resolve correctly

### Phase 5: Verification (GREEN — T13-10)
1. Run adversarial UX test
2. Compare planned vs delivered gap analysis
3. Create Sprint 14 plan for remaining items
4. Update PROJECT-MANIFEST.md

## Verification Checklist
- [ ] All API endpoints return valid data (no 404s)
- [ ] Dashboard sidebar shows "Wiki Reader" consistently
- [ ] Dashboard metrics match actual data
- [ ] service.html shows real service data
- [ ] Chatbot returns useful responses with Honcho integration
- [ ] All pages have proper metadata
- [ ] All pages handle API failures gracefully
- [ ] Adversarial UX test passes with < 3 RED items
- [ ] Gap analysis shows < 10 remaining RED items

## Notes
- All fixes must be made in local workspace first (`/Users/tron/grid-network-wiki-tool/`)
- Deploy to CT130 only after local verification
- Verify via browser QA after each deployment
- Run adversarial UX test after all fixes are complete
- Prioritize API completeness over new features
