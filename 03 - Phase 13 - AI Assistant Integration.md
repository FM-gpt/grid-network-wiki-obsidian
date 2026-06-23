---
title: "Phase 13 — AI Assistant Integration"
status: complete
created: 2026-06-22
last_updated: 2026-06-23
tags: [grid, phase-13, ai-assistant, chatbot, hermes-integration, complete]
priority: P2
---

# Phase 13 — AI Assistant Integration

> **Source:** Phase 12.8 spec (`08 - Phase 12.8 - AI Chatbot Assistant Spec.md`)
> **Priority:** P2 (High — builds on all Phase 12 foundation)
> **Target:** GRID Network Wiki Dashboard

---

## Objective

Implement the AI chatbot assistant for the GRID Network Wiki dashboard, enabling conversational queries against wiki content, infrastructure monitoring, and network administration tasks — powered by Hermes agent integration.

---

## Implementation Strategy

Phase 13 breaks into 5 sub-phases, implemented in priority order. Each sub-phase is independently functional before the next begins.

### Phase 13.1 — Floating Chatbox UI (Frontend Foundation)
**Priority:** P1
**Goal:** Standalone chat panel widget with message history, input, and localStorage persistence.

#### Tasks

| Task | Details |
|------|---------|
| 13.1.1 | Create `dashboard/chatbox.html` — floating chat panel overlay |
| 13.1.2 | Build message display component (user/assistant bubbles, markdown support) |
| 13.1.3 | Add chat trigger button (bottom-right corner of all pages) |
| 13.1.4 | Implement localStorage persistence for conversation history (30-day TTL) |
| 13.1.5 | Add quick-action buttons for common queries: "Wiki Status", "Service Health", "Active Tasks", "Drift Report", "Sites Overview" |
| 13.1.6 | Style: dark theme matching dashboard, smooth open/close animation |

**Verification:**
- Chat button appears on all dashboard pages
- Panel expands/collapses smoothly
- Message history persists across page reloads
- Quick actions return valid results (even if mock data)
- No JS errors in console

---

### Phase 13.2 — Backend API Layer + Honcho Memory Integration
**Priority:** P1
**Goal:** Server-side endpoints for chat queries, integrated with Honcho memory layer.

#### Tasks

| Task | Details |
|------|---------|
| 13.2.1 | Add `/api/chat/query` POST endpoint to `wiki-service.py` |
| 13.2.2 | Add `/api/chat/honcho/search` endpoint — proxy semantic search over stored context |
| 13.2.3 | Add `/api/chat/honcho/profile` endpoint — read peer cards |
| 13.2.4 | Add `/api/chat/honcho/context` endpoint — full session context snapshot |
| 13.2.5 | Add `/api/chat/honcho/reasoning` endpoint — dialectic synthesis for complex questions |
| 13.2.6 | Add `/api/chat/honcho/conclude` endpoint — write persistent facts |
| 13.2.7 | Implement `query_wiki_content` — search wiki-content for relevant markdown files |
| 13.2.8 | Implement `get_monitoring_status` — return live service health data |
| 13.2.9 | Implement `get_active_tasks` — return current kanban board state |
| 13.2.10 | Implement `get_site_info` — return site infrastructure details |
| 13.2.11 | Implement `check_drift_report` — return latest drift detection results |
| 13.2.12 | Add rate limiting (10 requests/minute per session) |

**Verification:**
- All endpoints return valid JSON
- Honcho search returns relevant excerpts from past conversations
- Honcho profile returns user/AI peer facts
- Honcho reasoning returns synthesized answers
- Wiki content queries return relevant results
- Monitoring status reflects live data
- Rate limiting works correctly

**Honcho Integration Notes:**
- Honcho is self-hosted at `http://10.10.30.130:8000` (or `http://localhost:8000` locally)
- API key from macOS keychain: `security find-generic-password -s honcho-database -w`
- Honcho provides 5 tools the chatbot can leverage:
  - `honcho_profile` — peer cards (user/AI identity, facts, preferences)
  - `honcho_search` — semantic search over stored context
  - `honcho_context` — full session context snapshot
  - `honcho_reasoning` — dialectic synthesis (LLM call on Honcho's backend)
  - `honcho_conclude` — write/delete persistent facts
- The chatbot backend should use the Honcho Python client or REST API to call these
- When a user asks about infrastructure, past decisions, or user preferences, the chatbot first queries Honcho memory before searching wiki content
- Honcho is the chatbot's "identity" layer — the GRID Network Admin profile stores infrastructure knowledge, user preferences, and operational history

---

### Phase 13.3 — Hermes Profile Integration
**Priority:** P2
**Goal:** Connect chatbot to Hermes agent for live infrastructure actions.

#### Tasks

| Task | Details |
|------|---------|
| 13.3.1 | Create Hermes profile config for "GRID Network Admin" |
| 13.3.2 | Implement WebSocket/SSE bridge from chatbot to Hermes gateway |
| 13.3.3 | Define action schema: `query`, `monitor`, `create_change`, `trigger_drift`, `maintenance_check` |
| 13.3.4 | Implement action routing — map user queries to Hermes tasks |
| 13.3.5 | Add authentication via existing OAuth tokens |
| 13.3.6 | Implement conversation context passing (session_id, user preferences) |

**Verification:**
- Chatbot can query wiki content via Hermes
- Monitoring queries return live data from Hermes
- Action requests route correctly to Hermes
- Authentication works with existing OAuth

---

### Phase 13.4 — Write Actions & Kanban Integration
**Priority:** P2
**Goal:** Enable chatbot to create change requests and trigger maintenance.

#### Tasks

| Task | Details |
|------|---------|
| 13.4.1 | Add `/api/chat/action` POST endpoint for write operations |
| 13.4.2 | Implement `create_change_request` — generates pending change card in kanban |
| 13.4.3 | Implement `trigger_drift_detection` — starts drift scan, reports back |
| 13.4.4 | Implement `maintenance_check` — runs maintenance procedure lookup |
| 13.4.5 | Add confirmation dialog for destructive actions |
| 13.4.6 | All actions logged to change board for audit trail |
| 13.4.7 | Add action history display in chat panel |

**Verification:**
- Change request creation works via chat
- Drift detection triggers and reports correctly
- Action history displays in chat
- All actions logged to kanban board
- Confirmation dialogs work for destructive actions

---

### Phase 13.5 — MCP Server Connection
**Priority:** P3
**Goal:** Connect chatbot to MCP servers for infrastructure actions.

#### Tasks

| Task | Details |
|------|---------|
| 13.5.1 | Research ProxmoxMCP-Plus API and integration requirements |
| 13.5.2 | Add MCP server connection configuration |
| 13.5.3 | Implement MCP action routing (start/stop containers, check health, view logs) |
| 13.5.4 | Add safety gate — all MCP actions require explicit user confirmation |
| 13.5.5 | Implement resource utilization queries |
| 13.5.6 | Add MCP error handling and fallback messages |

**Verification:**
- MCP connections establish successfully
- Container start/stop works with confirmation
- Health checks return accurate data
- Logs display correctly in chat
- Safety gates prevent unauthorized actions
- Error handling provides clear messages

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Dashboard Pages (index.html, monitoring.html, etc.)        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Chatbox Widget (floating overlay)                  │    │
│  │  - Message display (markdown)                       │    │
│  │  - Input field + send button                        │    │
│  │  - Quick action buttons                             │    │
│  │  - localStorage persistence                         │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                    │
│                    ┌────▼────┐                               │
│                    │  API    │                               │
│                    │  Layer  │                               │
│                    │         │                               │
│                    │ /api/   │                               │
│                    │ chat/   │                               │
│                    │ query   │                               │
│                    │ /action │                               │
│                    └────┬────┘                               │
│                         │                                    │
├─────────────────────────┼───────────────────────────────────┤
│                         │                                    │
│                    ┌────▼────────┐                          │
│                    │ wiki-service │                          │
│                    │ .py (Python) │                          │
│                    │              │                          │
│                    │ - query_wiki │                          │
│                    │ - get_status │                          │
│                    │ - create_req │                          │
│                    │ - trigger_drift│                        │
│                    └────┬─────────┘                          │
│                         │                                    │
│                    ┌────▼─────────┐                          │
│                    │  Hermes      │                          │
│                    │  Gateway     │                          │
│                    │  (SSE/WS)    │                          │
│                    └────┬─────────┘                          │
│                         │                                    │
│                    ┌────▼─────────┐                          │
│                    │  MCP Servers │                          │
│                    │  (Proxmox    │                          │
│                    │   + others)  │                          │
│                    └──────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Order & Dependencies

1. **Phase 13.1** — No dependencies. Frontend foundation.
2. **Phase 13.2** — Depends on 13.1. Backend API layer.
3. **Phase 13.3** — Depends on 13.2. Hermes integration.
4. **Phase 13.4** — Depends on 13.2. Write actions & kanban.
5. **Phase 13.5** — Depends on 13.3. MCP server connections.

**Parallel opportunities:**
- 13.1 and 13.2 can start in parallel (frontend/backend split)
- 13.4 can begin while 13.3 is in progress (different concerns)

---

## Security Considerations

1. **All write actions require confirmation** — no silent changes from chatbot
2. **MCP infrastructure actions require explicit approval** — safety gate before container start/stop/network changes
3. **Rate limiting** — prevent flooding via chat interface
4. **Audit trail** — all actions logged to kanban change board
5. **No raw config data** — chatbot returns sanitized summaries only
6. **Authentication via existing OAuth** — no new auth mechanism

---

## Verification Criteria

**ALL COMPLETE (2026-06-23):**

- [x] Chat panel opens/collapses smoothly on all pages
- [x] Messages display correctly (user and assistant)
- [x] Markdown rendering works in chat messages
- [x] Wiki content queries return accurate results (173+ files indexed)
- [x] Infrastructure status queries return live data
- [x] Change request creation flows through kanban board
- [x] Hermes profile integration authenticated and working (grid-admin.yaml)
- [x] MCP infrastructure actions require approval gate
- [x] All write actions logged to change board
- [x] Rate limiting works correctly
- [x] No JavaScript errors in console
- [x] Mobile-responsive layout tested (all new pages)
- [x] Message history persists across page reloads (localStorage)
- [x] Error states show helpful messages
- [x] CT131 grid-network-wiki-01 deployed and running
- [x] Caddy proxy routes wiki.grid → CT131:8082
- [x] Tiered Honcho search implemented (bypasses 8192 token limit)
- [x] SSE bridge (port 8083) connects chatbot to Hermes gateway
- [x] MCP proxy (port 8084) routes Proxmox actions
- [x] Settings page (theme, sync, wiki management, debug)
- [x] GRID Infrastructure site drill-down (site-grid.html)
- [x] FMSA Office site drill-down (site-fmsa.html)
- [x] Wiki content index (_index.md) with all sections
- [x] All docs synced to Obsidian vault

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Hermes gateway connection unstable | Implement retry logic + fallback to local wiki queries |
| MCP server API changes | Pin API version, add compatibility layer |
| Chatbot returning incorrect info | Add confidence scoring + source links to responses |
| Rate limiting too aggressive/relaxed | Make limits configurable via admin panel |
| Large responses overwhelm chat | Implement streaming/pagination for large results |

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `dashboard/chatbox.html` | Create | Chat panel overlay |
| `dashboard/js/chatbox.js` | Create | Chatbox logic + UI |
| `wiki-service.py` | Modify | Add `/api/chat/*` endpoints |
| `dashboard/js/dashboard.js` | Modify | Add chatbox trigger to all pages |
| `dashboard/css/dashboard.css` | Modify | Add chatbox styles |
| `hermes/profiles/grid-admin.yaml` | Create | Hermes profile config |
| `mcp/proxmox-config.yaml` | Create | MCP server configuration |
| `scripts/mcp-bridge.py` | Create | MCP action router |

---

*Phase 13 Plan created: 2026-06-22*
*Based on: 02 - Phase 12 - UX Audit & Next-Stage Roadmap.md (Phase 12.8 spec)*
*Next step: Begin Phase 13.1 implementation*
