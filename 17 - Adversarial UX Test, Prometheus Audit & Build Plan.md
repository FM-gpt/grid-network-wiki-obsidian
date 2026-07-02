---
title: "GRID Wiki — Adversarial UX Test, Prometheus Audit & Build Plan"
created: "2026-06-30"
last_updated: "2026-06-30"
tags: [grid, wiki, ux-test, monitoring, build-plan, infrastructure]
status: completed
---

# GRID Wiki — Adversarial UX Test, Prometheus Audit & Build Plan

**Date:** 2026-06-30  
**Author:** Tron  
**Status:** Completed — findings and plan documented

---

## Executive Summary

The GRID Wiki service is a functional but incomplete monitoring and documentation platform. It has **96 wiki pages synced** from Obsidian, **69/73 Prometheus targets up** (94.5% healthy), and **10 UI pages**. However, the adversarial UX test reveals critical issues: broken dashboard cards, static monitoring data, JavaScript errors in drift reports, and a read-only settings page. The service needs to evolve from a "wiki viewer with monitoring badges" into a "self-aware infrastructure intelligence platform."

---

## 1. Adversarial UX Test

### Persona

**"Retirement home director"** — 68 years old. Filing cabinet is their CRM. Paper notebooks. Hates jargon. If they can't figure something out in 10 seconds, they go back to their notebook.

### Dashboard (Home Page)

| Finding | Severity | Details |
|---------|----------|---------|
| Active Tasks card fails to load | **CRITICAL** | Shows "Unable to load tasks" in yellow warning box. API endpoint failing. |
| Monitoring Status shows 0/12 services up | **CRITICAL** | "Last Check: N/A" — monitoring system not working. |
| Goal Progress shows 11/9 = 122% | **CONFUSING** | Mathematically valid but visually jarring. Progress bar looks full but text says 122%. |

**What works:** Clean sidebar with icons, four clear data cards, Refresh and Export buttons visible.

### Monitoring Page

| Finding | Severity | Details |
|---------|----------|---------|
| All 12 services show "healthy" but Last Check and Response Time are "N/A" | **HIGH** | No real monitoring data — just static labels. |

**What works:** Comprehensive service list (caddy, prometheus, grafana, uptime-kuma, portainer, ollama, open-webui, postgresql, redis, minecraft, samba, wiki).

### Drift Reports

| Finding | Severity | Details |
|---------|----------|---------|
| JavaScript errors leaking "[object Object]" to UI | **CRITICAL** | Raw JS object leaked to frontend. |
| Multiple entries with "Unknown" timestamps | **HIGH** | Data parsing errors. |
| Inconsistent ID formats (compact vs ISO) | **MEDIUM** | Some use `20260627-160934`, others use `2026-06-28T04:29:37.480388`. |

**What works:** baseline_corruption entry with explanation is helpful. View links for each report.

### Change Kanban

| Finding | Severity | Details |
|---------|----------|---------|
| All cards show "Risk: N/A" | **MEDIUM** | Risk assessment not populated. |
| ID jump from CHANGE-002 to CHANGE-010 | **MEDIUM** | Gaps unexplained. |

**What works:** Clear 4-column Kanban layout. Empty states are clear.

### Maintenance

| Finding | Severity | Details |
|---------|----------|---------|
| TEST-001-check in production kanban | **MEDIUM** | Test data not cleaned up. |

**What works:** Clear 3-column Kanban. Maintenance rules listed with severity levels.

### Wiki Browser

| Finding | Severity | Details |
|---------|----------|---------|
| 96 pages in one infinite scroll, no pagination | **HIGH** | Extremely long, no "Load More" or page numbers. |
| All items have identical icons | **HIGH** | Can't distinguish files vs folders. |

**What works:** Pages properly categorized (infra/, fmsa/, project/, research/, minecraft/). Search bar present.

### Sites Overview

| Finding | Severity | Details |
|---------|----------|---------|
| Only 2 sites shown (GRID, FMSA) | **MEDIUM** | No way to add/manage more. |

**What works:** Clean table with Site, Status, Services, Monitoring columns.

### Agent Protocol

| Finding | Severity | Details |
|---------|----------|---------|
| Highly technical content | **MEDIUM** | LXC, Proxmox, node_exporter — not for non-technical users. |

**What works:** Well-structured Markdown. Clear workflows.

### Settings

| Finding | Severity | Details |
|---------|----------|---------|
| Wiki Root shows "N/A" | **CRITICAL** | Configuration missing. |
| Read-only interface | **CRITICAL** | No input fields to change Theme, Auto-refresh, Language. |

**What works:** Clean list of current settings.

---

## 2. Prometheus Monitoring Audit

### Overall Health

| Metric | Value |
|--------|-------|
| Total targets | 73 |
| UP | 69 (94.5%) |
| DOWN | 4 (5.5%) |

### Down Targets (All Expected/Non-Critical)

| Job | Instance | Health | Notes |
|-----|----------|--------|-------|
| grid-llamacpp-gpu | 10.10.30.128:8080 | down | GPU service down (expected) |
| grid-llamacpp-gpu | 10.10.30.128:8081 | down | GPU service down (expected) |
| grid-lxcs | 10.10.30.125:9100 | down | CT125 placeholder container (expected) |
| grid-test-env-cadvisor | 10.10.30.121:8081 | down | Test environment cadvisor (expected) |

### Services by Job Type

| Job | Targets | Type |
|-----|---------|------|
| grid-admin-http | 21 | HTTP health checks |
| grid-admin-tcp | 16 | TCP port checks |
| grid-admin-https-insecure | 3 | HTTPS checks |
| grid-lxcs | 8 | LXC node_exporter |
| fmsa-lxcs | 5 | FMSA LXC node_exporter |
| grid-test-env-* | 11 | Test environment |
| omada-* | 3 | Omada network monitoring |
| proxmox-host | 1 | Proxmox host |

### Wiki Service Status

- Running on port 8082
- 96 wiki pages synced
- All API endpoints functional
- Dashboard serving correctly

---

## 3. What This Service Could Be (If Fully Aware)

Right now it's a **wiki viewer with monitoring badges**. But with self-awareness, it could become:

### "GRID Infrastructure Intelligence Platform"

A service that knows:

1. **Its own state** — uptime, memory, CPU, disk, API response times
2. **The infrastructure it monitors** — all 69+ services, their health, trends
3. **Its own needs** — what's missing, what's broken, what needs attention
4. **Future needs** — what to build next, what to prioritize, what's at risk

This is the differentiator. Most monitoring tools show data. This one **understands** the data and tells you what to do about it.

---

## 4. Comprehensive Build Plan

### Phase 1: Fix Critical UX Issues (P0 — Immediate, 1-2 days)

| Task | Description | Effort |
|------|-------------|--------|
| 1.1 | Fix Active Tasks API endpoint | 2h |
| 1.2 | Fix Monitoring Status to show real Prometheus data | 4h |
| 1.3 | Fix Goal Progress math (11/9 = 122%) | 1h |
| 1.4 | Fix Drift Reports JS errors ([object Object]) | 2h |
| 1.5 | Fix Settings page (Wiki Root N/A, add input fields) | 2h |
| 1.6 | Remove TEST-001-check from production | 30m |

**Why first:** These make the service look broken. Fix them first to stop users from thinking it's down.

### Phase 2: Real-Time Monitoring Integration (P1 — High, 3-5 days)

| Task | Description | Effort |
|------|-------------|--------|
| 2.1 | Dashboard: Show real Prometheus metrics | 4h |
| 2.2 | Monitoring page: Add real-time charts (1h, 6h, 24h, 7d) | 8h |
| 2.3 | Alerting: Add Prometheus alert rules | 4h |
| 2.4 | Service health checks: Add blackbox exporter probes | 4h |

**Why second:** The service monitors 69 services but shows no real data. This makes it actually useful.

### Phase 3: Wiki Search & Navigation (P1 — High, 2-3 days)

| Task | Description | Effort |
|------|-------------|--------|
| 3.1 | Wiki Browser: Add pagination (20 items/page) | 3h |
| 3.2 | Wiki Browser: Add collapsible categories | 4h |
| 3.3 | Wiki Browser: Improve search (full-text, fuzzy matching) | 6h |
| 3.4 | Wiki Browser: Add breadcrumbs | 2h |

**Why third:** 96 pages in one scroll is unusable. Better navigation makes the wiki actually useful.

### Phase 4: Self-Awareness & Intelligence (P2 — Medium, 5-7 days)

This is where the service becomes truly unique:

| Task | Description | Effort |
|------|-------------|--------|
| 4.1 | Service health dashboard: Self-monitoring | 4h |
| 4.2 | Auto-discovery: Service catalog | 8h |
| 4.3 | Anomaly detection: Predictive alerts | 12h |
| 4.4 | Knowledge base: Auto-generate docs | 8h |
| 4.5 | Recommendations engine: Suggest improvements | 12h |

**Why this matters:** This is the differentiator. Most monitoring tools show data. This one **understands** the data and tells you what to do about it.

### Phase 5: Advanced Features (P3 — Low, 7-10 days)

| Task | Description | Effort |
|------|-------------|--------|
| 5.1 | AI assistant: Chat with your infrastructure | 16h |
| 5.2 | Collaboration: Multi-user support | 12h |
| 5.3 | Automation: Auto-remediation | 16h |
| 5.4 | Backup & restore: Full service backup | 8h |
| 5.5 | Analytics: Usage dashboard | 8h |

**Why last:** These are nice-to-haves. Build Phase 1-4 first.

---

## 5. Summary

| Metric | Value |
|--------|-------|
| Total phases | 5 |
| Total tasks | 23 |
| Estimated effort | 25-35 days |

### Key Milestones

1. **Phase 1 (1-2 days):** Fix critical UX — make the service look functional
2. **Phase 2 (3-5 days):** Real-time monitoring — make the service actually monitor
3. **Phase 3 (2-3 days):** Wiki navigation — make the wiki usable
4. **Phase 4 (5-7 days):** Self-awareness — make the service intelligent
5. **Phase 5 (7-10 days):** Advanced features — make the service powerful

### Recommendations

- Start with **Phase 1** — quick, high-impact, stops the service from looking broken
- **Phase 2** is the highest value — monitoring 69 services with no real data is worse than no monitoring at all
- **Phase 4** is the most innovative — this is where the service becomes unique
- **Phase 5** is the longest — consider splitting into separate projects

### Risks

- Phase 4 (self-awareness) requires AI/ML work — consider starting with Phase 1-3 first
- Phase 5 (AI assistant) depends on Phase 4 (knowledge base) — can't build AI without data
- Prometheus integration (Phase 2) may require network access to CT120 — verify connectivity
- Multi-user support (Phase 5) requires security review — don't rush authentication

---

*Generated: 2026-06-30*  
*Source: Adversarial UX test + Prometheus API audit + comprehensive planning*
