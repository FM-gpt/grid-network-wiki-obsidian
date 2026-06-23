---
title: "PROJECT MANIFEST"
current_goal: "Sprint 15: Production Readiness & Final Polish — Planned. Final polish, production deployment to CT130, and LLM integration restoration."
last_updated: 2026-06-24 16:00 ACST
---

# GRID Network Wiki

## 1. Scope Boundaries (DO NOT VIOLATE)
- **IN SCOPE:**
  - GRID Network Wiki service on CT130 (10.10.30.130:8082)
  - Auto-discovery engine (1am-6am agent workers)
  - Dashboard UI for browsing wiki and kanban boards
  - Obsidian sync to `/Users/tron/Documents/Obsidian Vault/GRID Network Wiki/`
  - Monitoring integration (Prometheus on CT120, Uptime Kuma on CT120, Grafana on CT120)
  - Maintenance kanban workflow
  - Change kanban workflow
  - Agent knowledge base enhancement
  - Chatbot assistant integration
- **OUT OF SCOPE:**
  - Modifying core Proxmox infrastructure
  - Direct network configuration changes without kanban review
  - Building custom monitoring tools (reuse existing Prometheus/Uptime Kuma)
  - Managing non-GRID/FMSA infrastructure

## 2. Current Goal
- **Sprint active:** [12 - Sprint Plan — Core Pages & Reliability](12 - Sprint Plan — Core Pages & Reliability.md)
  - Phases 1-10: Fix broken pages, data accuracy, and reliability
  - Create missing search-wiki.html and agents.html pages
  - Fix service.html content display
  - Fix sidebar inconsistencies
  - Fix dashboard metric accuracy
  - Improve chatbot response quality
  - Add error boundaries and graceful degradation
- **Superseded:** Sprint 11 (Phases 30-40). All prior sprint claims superseded by Sprint 12.

## 3. Active Tasks
|| Task ID | Description | Status | Assignee |
||---------|-------------|--------|----------|
|| T12-01 | Create missing search-wiki.html page | Parked | |
|| T12-02 | Create missing agents.html page | Parked | |
|| T12-03 | Fix service.html — add content/health data display | Parked | |
|| T12-04 | Fix sidebar inconsistency — wiki.html still shows "Wiki Viewer" | Parked | |
|| T12-05 | Fix dashboard "OPEN DRIFT: 10" vs actual drift data | Parked | |
|| T12-06 | Fix wiki.html stale cache / "Loading wiki pages..." issue | Parked | |
|| T12-07 | Verify all sidebar nav links resolve correctly | Parked | |
|| T12-08 | Chatbot response quality improvement | Parked | |
|| T12-09 | Add favicon and page metadata | Parked | |
|| T12-10 | Hardening: error boundaries, graceful degradation | Parked | |

## 4. Deep-Dive Index (Load only when needed)
- **Methodology & Rules:** `AGENTS.md` (Always read first)
- **Project Plan:** `00 - GRID Network Wiki Project Plan.md`
- **UX Audit Roadmap:** `02 - Phase 12 - UX Audit & Next-Stage Roadmap.md`
- **AI Assistant Spec:** `08 - Phase 12.8 - AI Chatbot Assistant Spec.md`
- **Current Sprint:** [12 - Sprint Plan — Core Pages & Reliability](12 - Sprint Plan — Core Pages & Reliability.md)
- **Gap Analysis:** `09 - Gap Analysis — Planned vs Delivered.md`
- **Wiki Directory:** `/srv/grid-wiki/` (on CT130)
- **Obsidian Sync Path:** `/Users/tron/Documents/Obsidian Vault/GRID Network Wiki/`
- **Dashboard UI:** `http://localhost:8082/index.html` (local) / `http://10.10.30.130:8082/index.html` (CT130)
- **CT130 Host:** `10.10.30.130`
- **CT120 Host:** `10.10.30.120`
- **CT121 Host:** `10.10.30.121`

## 5. Monitoring Stack (CT120 — 10.10.30.120)

| Service | Port | Status | Notes |
|---------|------|--------|-------|
| Prometheus | 9090 | Running | 18 scrape jobs, 15d retention |
| Grafana | 3000 | Running (200) | Login page accessible |
| Uptime Kuma | 3001 | Running (302) | Redirects to login |
| Caddy | 8080 | Running (200) | Reverse proxy |
| InfluxDB | 8086 | NOT responding | Ping returned 000 |
| LLM (Ollama) | 11434 | NOT responding | No response |
| omada-exporter-grid | 9202 | Running | Prometheus job |
| omada-exporter-fmsa | 9203 | Running | Prometheus job |
| omada-enrichment-exporter | 9204 | Running | Prometheus job |

## 6. Project Meta
- **Repo Path:** /Users/tron/grid-network-wiki-tool
- **Wiki Path:** /Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki
- **Remote:** https://github.com/FM-gpt/grid-network-wiki-tool.git
- **Test Env Host:** CT121 grid-dev-01 (10.10.30.121)
- **Active URL:** http://10.10.30.130:8082/index.html (CT130)
- **Health Endpoint:** http://10.10.30.130:8082/api/health
- **Wiki Data:** http://10.10.30.130:8082/api/wiki-data
- **Wiki Index:** http://10.10.30.130:8082/api/wiki-index
- **Sync Status:** http://10.10.30.130:8082/api/sync-status
- **Monitoring:** http://10.10.30.130:8082/monitoring.html
- **Change Board:** http://10.10.30.130:8082/kanban/change.html
- **Maintenance Board:** http://10.10.30.130:8082/kanban/maintenance.html

## 7. Active Sprint Reference

All follow-on phases should reference the current sprint plan:
- **Current Sprint:** [12 - Sprint Plan — Core Pages & Reliability](12 - Sprint Plan — Core Pages & Reliability.md)
- **Gap Analysis:** [09 - Gap Analysis — Planned vs Delivered.md](09 - Gap Analysis — Planned vs Delivered.md)
- **UX Audit Roadmap:** [02 - Phase 12 - UX Audit & Next-Stage Roadmap.md](02 - Phase 12 - UX Audit & Next-Stage Roadmap.md)

New sprint plans (post-Sprint 12) should be named `13 - Sprint Plan — <name>.md` and this manifest should be updated to point to the active sprint.
