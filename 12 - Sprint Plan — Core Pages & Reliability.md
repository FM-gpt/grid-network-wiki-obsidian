---
title: "Sprint 12 — Core Pages & Reliability"
sprint_number: 12
start_date: 2026-06-24
status: Active
supersedes: "11 - Sprint Plan — Adversarial UX Fixes"
---

# Sprint 12: Core Pages & Reliability

## Goal
Fix all remaining broken pages from the browser QA, eliminate 404 errors, stabilize the service.html content view, and harden reliability of the GRID Wiki system.

## Scope Boundaries
- **IN SCOPE:** Fix all 404 pages, service.html content, wiki.html cache issues, sidebar consistency, dashboard data accuracy, chatbot quality, and reliability hardening.
- **OUT OF SCOPE:** New feature development, mobile responsiveness, service entity pages (20 services), advanced chatbot features.

## Active Tasks

| Task ID | Description | Priority | Status |
|---------|-------------|----------|--------|
| T12-01 | Create missing search-wiki.html page | RED | Parked |
| T12-02 | Create missing agents.html page | RED | Parked |
| T12-03 | Fix service.html — add content/health data display | RED | Parked |
| T12-04 | Fix sidebar inconsistency — wiki.html still shows "Wiki Viewer" | YELLOW | Parked |
| T12-05 | Fix dashboard "OPEN DRIFT: 10" vs actual drift data | YELLOW | Parked |
| T12-06 | Fix wiki.html stale cache / "Loading wiki pages..." issue | YELLOW | Parked |
| T12-07 | Verify all sidebar nav links resolve correctly | GREEN | Parked |
| T12-08 | Chatbot response quality improvement | GREEN | Parked |
| T12-09 | Add favicon and page metadata | GREEN | Parked |
| T12-10 | Hardening: error boundaries, graceful degradation | YELLOW | Parked |

## Implementation Plan

### Phase 1: Fix Broken Pages (RED)
1. **T12-01**: Create search-wiki.html with search functionality using `/api/wiki-search` endpoint
2. **T12-02**: Create agents.html with agent interface / knowledge base display
3. **T12-03**: Fix service.html to display service health data from `/api/services` endpoint

### Phase 2: Data Accuracy (YELLOW)
4. **T12-04**: Ensure wiki.html sidebar shows "Wiki Reader" (matches sidebar.js fix)
5. **T12-05**: Fix dashboard OPEN DRIFT counter — use actual drift count from `/api/drift`
6. **T12-06**: Fix wiki.html cache mechanism to show fresh data
7. **T12-07**: Verify all sidebar nav links in every HTML file

### Phase 3: Quality & Reliability (GREEN + YELLOW)
8. **T12-08**: Improve chatbot response quality — better context from wiki content
9. **T12-09**: Add proper `<title>`, meta tags, and favicon to all pages
10. **T12-10**: Add error boundaries — graceful fallback when APIs fail

## Verification Checklist
- [ ] All pages load without 404
- [ ] All sidebar links resolve to existing pages
- [ ] Dashboard metrics match actual data
- [ ] service.html shows real service data
- [ ] search-wiki.html works with search input
- [ ] agents.html loads and displays content
- [ ] Chatbot returns useful responses
- [ ] All pages have proper metadata
- [ ] Adversarial UX test passes

## Notes
- All fixes must be made in local workspace first (`/Users/tron/grid-network-wiki-tool/`)
- Deploy to CT130 only after local verification
- Verify via browser QA after each deployment
- Run adversarial UX test after all fixes are complete
