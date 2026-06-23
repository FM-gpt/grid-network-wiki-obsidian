---
title: "Sprint Plan — GRID Network Wiki"
created: 2026-06-23
last_updated: 2026-06-23
status: planning
tags: [grid, sprint, planning, roadmap, wiki]
priority: P0
---

# Sprint Plan — GRID Network Wiki

## Overview

This sprint covers all remaining work to make the GRID Network Wiki fast, agent-ready, and production-grade. It replaces the old phased roadmap with a focused, sequential plan.

## Current State (2026-06-23)

### What's Done (Phases 0-13 Complete)
- Foundation (CT131 host, Caddy routing, Python service)
- Wiki engine (132 markdown files serving from workspace)
- Dashboard UI (index, monitoring, kanban, drift, sync)
- Kanban boards (change + maintenance workflows)
- Cron jobs (overnight discovery workers)
- Monitoring (Prometheus, Uptime Kuma, service health)
- Settings UI, site drill-down pages
- Hermes profile integration (grid-admin.yaml)
- SSE bridge (port 8083) + MCP proxy (port 8084)
- Tiered Honcho search fallback
- All Phase 13 sub-tasks deployed to CT131

### What's Not Done (This Sprint)
- Search-first navigation (replacing file-browser)
- Agents page (glass-box transparency)
- Obsidian vault as canonical source of truth
- Role-based gating (Naddy vs Wiki-Interpreter)
- Frontmatter search tags
- Agent skill system for network changes
- Obsidian format example doc
- Performance optimization
- All remaining items from Phase 12 gap analysis

---

## Sprint Phases

### Phase 14: Core Architecture Shift — Vault as Source of Truth

**Goal:** Eliminate sync overhead. Obsidian vault IS the wiki. CT131 serves it directly.

**Tasks:**
1. **Wiki-config.yaml** — Config file on CT131 pointing to Obsidian vault path
2. **wiki-service.py rewrite** — Remove wiki-content directory serving; serve from vault path directly
3. **Sync script cleanup** — Remove bidirectional sync; keep one-way vault->CT131 for monitoring
4. **Caddy route update** — Ensure wiki.grid routes to CT131 correctly
5. **Verification** — All wiki pages accessible from CT131 via vault path
6. **Backup plan** — Snapshot current CT131 state before shift

**Why first:** Everything else depends on this. If the vault IS the source, we can stop worrying about sync drift and double-sourcing.

**Deliverables:**
- Config file with vault path
- Updated wiki-service.py
- Cleaned sync script
- Updated Caddy config
- Verification report

---

### Phase 15: Performance Fix — Search-First Navigation

**Goal:** Fix the slow wiki-view and wiki-browser pages. Instant load, instant search.

**Tasks:**
1. **Remove file-browser pattern** — Delete code that loads all 132+ files into JS
2. **Build search index** — Generate `wiki-index.json` from vault (tags, titles, paths, categories)
3. **Search-first UI** — Single search bar + categorized quick links (no file list)
4. **Lazy load** — Only fetch requested files, not all files at once
5. **Agent JSON index** — Same index in YAML/JSON format for agent consumption
6. **Agent-friendly headings** — Consistent H1/H2/H3 structure with search tags

**Why second:** This is the bottleneck. The entire wiki experience is blocked by this.

**Deliverables:**
- `wiki-index.json` (search index)
- `wiki-index.yaml` (agent-readable index)
- New search-first wiki.html
- New search-first wiki-browser.html
- All existing pages working with new navigation

---

### Phase 16: Agent Interface — AGENTS.md Page

**Goal:** Create the "Agents" page that serves as a transparency window for what agents see.

**Tasks:**
1. **AGENTS.md content** — Write the agent-facing page content:
   - Raw agent instructions (what agents read)
   - Wiki search index (structured data)
   - Action rules (how to navigate, search, submit changes)
   - Skills to use (Proxmox login, SSH, etc.)
   - Role definitions and restrictions
2. **Top nav bar** — Add "Agents" button to top navbar
3. **Sidebar preservation** — Keep sidebar for user navigation only
4. **Agents page HTML** — Simple page that loads and displays the raw AGENTS.md content
5. **Glass-box rendering** — Show raw markdown + structured JSON side-by-side
6. **Testing** — Verify agents can parse the page, users can read it

**Why third:** Depends on Phase 15 (search index) and Phase 14 (vault source).

**Deliverables:**
- AGENTS.md (agent-facing page content)
- Top nav bar with "Agents" link
- Agents page HTML (glass-box view)
- Agent testing report

---

| **Phase 17:** Obsidian Format Standardization — COMPLETE (example doc created, template written, format documented for review) |

**Goal:** Create an Obsidian example showing the ideal format for wiki pages.

**Tasks:**
1. **Example doc** — Create one sample page in Obsidian with:
   - YAML frontmatter (tags, title, category, audience)
   - Consistent heading structure (H1/H2/H3)
   - Agent-relevant sections (search tags, metadata)
   - Human-friendly formatting (spacing, clear headings)
   - Same format for both audiences
2. **Template doc** — Create a reusable template
3. **Frontmatter tag system** — Standardized tags for search indexing
4. **User review** — You (Tron) check the example in Obsidian
5. **Docs** — Update wiki-content docs to match template

**Why fourth:** This standardizes what we serve. Before we build the search index, we need a consistent format.

**Deliverables:**
- Obsidian example doc (user to review)
- Wiki page template
- Frontmatter tag system docs
- Updated wiki docs matching template

---

### Phase 18: Agent Skill System

**Goal:** Agents can use skills to perform network changes safely.

**Tasks:**
1. **Skill definitions** — Define skills for:
   - Proxmox login
   - SSH to containers
   - Caddy config changes
   - Docker service management
   - Change request submission
   - Kanban workflow
2. **Skill installation** — Agents install skills on first use
3. **Skill execution** — Agents use skills to perform tasks
4. **Change funnel** — Agents submit change requests to kanban before acting
5. **Audit trail** — All agent actions logged
6. **Testing** — Agent skill workflow end-to-end

**Why fifth:** Skills depend on Phase 16 (AGENTS.md page) and Phase 15 (search index).

**Deliverables:**
- Skill definitions
- Skill installation flow
- Change funnel integration
- Audit logging
- Testing report

---

### Phase 19: Remaining Items from Phase 12 Gap Analysis

**Goal:** Complete all undelivered items from earlier phases.

**Tasks:**
1. **Proxmox MCP integration** — Full MCP actions for container management
2. **Full monitoring status** — Live service health checks
3. **Drift detection automation** — Cron-based drift detection
4. **Maintenance automation** — Auto-approve/reject rules
5. **Dashboard polish** — All tiles working, all links fixed
6. **Cross-reference cleanup** — Ensure all wiki pages link correctly
7. **Final verification** — All Phase 0-13 items verified
8. **Documentation** — Update all docs to reflect current state

**Why last:** This is cleanup and completion of everything we started.

**Deliverables:**
- All Phase 12 items complete
- Proxmox MCP fully working
- Drift detection automated
- Dashboard fully polished
- Updated documentation

---

## Sprint Timeline

| Phase | Description | Duration | Dependencies |
|-------|-------------|----------|-------------|
| 14 | Vault as Source of Truth | 2-3 days | None |
| 15 | Search-First Navigation | 3-4 days | Phase 14 |
| 16 | AGENTS.md Page | 2-3 days | Phase 15 |
| 17 | Obsidian Format Standardization | 2-3 days | Phase 15 |
| 18 | Agent Skill System | 3-4 days | Phase 16 |
| 19 | Remaining Items & Cleanup | 2-3 days | All previous |

**Total estimated duration:** 14-20 days

---

## Key Decisions

1. **Vault is canonical** — Obsidian vault IS the source. No sync overhead.
2. **Search-first, not file-list** — Instant load, instant search. No loading 132 files in JS.
3. **Same format for humans and agents** — One Obsidian markdown format. Frontmatter tags for search.
4. **Glass-box transparency** — AGENTS.md shows raw agent context. You see what AI sees.
5. **Role-based gating** — Naddy vs Wiki-Interpreter separated by role tags.
6. **Agent skills** — Safe network change workflow through kanban funnel.
7. **Performance priority** — Every phase optimizes for speed.

---

## What This Sprint Delivers

- ✅ Fast wiki (instant search, no file loading)
- ✅ Agent-ready (structured index, skills, change funnel)
- ✅ Vault as source (no sync overhead, single truth)
- ✅ Glass-box transparency (AGENTS.md page)
- ✅ Role safety (Naddy can't confuse with agent instructions)
- ✅ Complete Phase 0-13 integration
- ✅ Production-ready GRID Network Wiki

---

## Next Steps

1. **Create Obsidian example doc** (Phase 17) — ✅ DONE — Example doc at `/Users/tron/Documents/Obsidian Vault/GRID Network Wiki/TEMPLATE — Wiki Page Format.md` — user to review
2. **Start Phase 14** — Vault as source of truth
3. **Execute Phase 15** — Search-first navigation (performance fix)
4. **Continue through phases** — Each builds on previous

---

## Risks & Mitigations

- **Risk:** Vault path changes break CT131 serving
  - **Mitigation:** Config file with easy update, backup snapshot
- **Risk:** Agent skills introduce security risks
  - **Mitigation:** Kanban funnel for all changes, audit logging
- **Risk:** Format standardization slows adoption
  - **Mitigation:** Template, gradual migration, user review
- **Risk:** Performance issues persist after Phase 15
  - **Mitigation:** Benchmarks after each phase, rollback if needed

---

## Completion Criteria

- All wiki pages accessible from CT131
- Search loads in < 1 second
- AGENTS.md page functional and tested
- Agent skills installed and working
- All Phase 12-13 items verified
- Dashboard fully polished
- Documentation complete

---

END OF SPRINT PLAN
