---
title: "Sprint 14 — Polish & Completion"
sprint_number: 14
start_date: 2026-06-24
status: Active
supersedes: "13 - Sprint Plan — UX Polish & API Hardening"
---

# Sprint 14: Polish & Completion

## Goal
Fix all remaining dead links, broken pages, and critical UX issues. Deliver a polished, fully functional product that meets the usability standards for the "retirement home director, 68" persona.

## Scope Boundaries
- **IN SCOPE:** Dead link fixes, settings page repair, site drill-down, drift report details, chatbot improvement, favicon/metadata, error handling completeness, mobile basics, service entity pages.
- **OUT OF SCOPE:** New features, production deployment to CT130, Proxmox infrastructure changes, LLM backend integration.

## Active Tasks

| Task ID | Description | Priority | Status |
|---------|-------------|----------|--------|
| T14-01 | Fix dead links: GRID Infrastructure, FMSA Office, Settings, API Docs | RED | |
| T14-02 | Fix settings.html to work with /api/settings endpoint | RED | |
| T14-03 | Create site drill-down pages (site-grid.html, site-fmsa.html) | RED | |
| T14-04 | Fix drift reports to show detail views (not just count) | RED | |
| T14-05 | Improve chatbot with real API responses (sources, suggestions) | RED | |
| T14-06 | Add favicon to all pages, improve metadata | YELLOW | |
| T14-07 | Fix "New Project" button to actually work | YELLOW | |
| T14-08 | Add error boundary to site-grid.html and site-fmsa.html | YELLOW | |
| T14-09 | Fix sidebar nav consistency — verify ALL links resolve | GREEN | |
| T14-10 | Run adversarial UX test to verify all fixes | GREEN | |
| T14-11 | Run gap analysis planned vs delivered | GREEN | |
| T14-12 | Create next sprint plan if needed | GREEN | |

## Implementation Plan

### Phase 1: Dead Links & Critical Fixes (RED — T14-01, T14-02, T14-03, T14-04)
1. **T14-01**: Make GRID Infrastructure → site-grid.html, FMSA Office → site-fmsa.html, Settings → settings.html (working), API Docs → settings.html#api
2. **T14-02**: Fix settings.html to read/write from /api/settings
3. **T14-03**: Create site-grid.html and site-fmsa.html with real data from /api/sites-index
4. **T14-04**: Add drift report detail views — expandable rows showing vault vs overlay diffs

### Phase 2: Chatbot & Service Pages (RED — T14-05)
5. **T14-05**: Improve chatbot to use real API data from /api/chat/query, handle all quick actions with real data

### Phase 3: Polish (YELLOW — T14-06, T14-07, T14-08, T14-09)
6. **T14-06**: Add favicon (SVG) to all pages
7. **T14-07**: Make "New Project" button functional (create project flow)
8. **T14-08**: Add error boundaries to remaining pages
9. **T14-09**: Verify all sidebar nav links resolve

### Phase 4: Verification (GREEN — T14-10, T14-11, T14-12)
10. **T14-10**: Run adversarial UX test
11. **T14-11**: Run gap analysis
12. **T14-12**: Create next sprint plan if needed, update manifest

## Verification Checklist
- [ ] All sidebar links resolve to working pages
- [ ] Settings page loads and saves data
- [ ] Site drill-down pages show real data
- [ ] Drift reports show detail views
- [ ] Chatbot returns useful real responses
- [ ] No dead links anywhere
- [ ] All pages have favicon
- [ ] Zero JS errors across all pages
- [ ] Adversarial UX test passes with < 3 RED items
- [ ] Gap analysis shows < 5 remaining RED items

## Notes
- All fixes in local workspace first (`/Users/tron/grid-network-wiki-tool/`)
- Verify via browser QA after each fix
- Run adversarial UX test after all fixes complete
- Prioritize UX-critical items over polish
