---
title: "Sprint 15 — Production Readiness & Final Polish"
sprint_number: 15
start_date: 2026-06-24
status: Planned
supersedes: "14 - Sprint Plan — Polish & Completion"
---

# Sprint 15: Production Readiness & Final Polish

## Goal
Final production polish, deployment readiness, and LLM integration restoration.

## Scope Boundaries
- **IN SCOPE:** Favicon, mobile basics, production deployment, LLM reconnection, final QA pass
- **OUT OF SCOPE:** New feature development, Proxmox infrastructure changes

## Active Tasks

| Task ID | Description | Priority | Status |
|---------|-------------|----------|--------|
| T15-01 | Add favicon SVG to all pages | GREEN | |
| T15-02 | Fix mobile responsiveness for core pages | GREEN | |
| T15-03 | Deploy to CT130 (10.10.30.130:8082) | RED | |
| T15-04 | Verify production deployment | RED | |
| T15-05 | Re-enable LLM backend when Ollama is online | YELLOW | |
| T15-06 | Final adversarial UX test | GREEN | |
| T15-07 | Update PROJECT-MANIFEST.md | GREEN | |
| T15-08 | Final gap analysis | GREEN | |

## Implementation Plan

### Phase 1: Production Deployment (RED — T15-03, T15-04)
1. **T15-03**: Deploy wiki-service.py to CT130
2. **T15-04**: Verify all routes work on production

### Phase 2: Final Polish (GREEN — T15-01, T15-02, T15-06)
3. **T15-01**: Add favicon to all pages
4. **T15-02**: Basic mobile responsiveness
5. **T15-06**: Final adversarial UX test

### Phase 3: LLM Restoration (YELLOW — T15-05)
6. **T15-05**: Re-enable chatbot LLM integration when Ollama is back online

### Phase 4: Completion (GREEN — T15-07, T15-08)
7. **T15-07**: Update PROJECT-MANIFEST.md
8. **T15-08**: Final gap analysis

## Verification Checklist
- [ ] All routes working on production
- [ ] Favicon visible in browser tabs
- [ ] Pages usable on mobile viewport (320px+)
- [ ] Final UX test passes with 0 RED items
- [ ] Manifest points to Sprint 15
- [ ] LLM integration ready for re-enablement
