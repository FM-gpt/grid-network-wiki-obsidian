---
title: "Phase 12.8 — AI Chatbot Assistant Spec"
status: spec
created: 2026-06-22
last_updated: 2026-06-22
tags: [grid, phase-12, spec, chatbot, ai-assistant, p3]
priority: P3
---

# Phase 12.8 — AI Chatbot Assistant (Future Spec)

> **Status:** Specification only — not implemented
> **Priority:** P3 (Future)
> **Target:** GRID Network Wiki Dashboard

---

## Overview

This phase defines the design for an AI chatbot assistant integrated into the GRID Network Wiki dashboard. The chatbot serves as a conversational interface for wiki content queries, infrastructure status checks, and network administration tasks.

---

## Tasks

| Task | Priority | Details |
|------|----------|---------|
| 12.8.1 | P3 | **Floating chatbox side panel** — Add a chatbot-style floating message box to the side panel. Answer basic questions from wiki info. |
| 12.8.2 | P3 | **Hermes profile integration** — Allow the chatbot to connect to a Hermes profile configured as the network administrator who runs the wiki and the network. This profile handles network tasks, monitoring, and can take action from the chatbox. |
| 12.8.3 | P3 | **Persistent memory** — Chatbot maintains persistent memory of all tool access, context, and conversation history. |
| 12.8.4 | P3 | **Dedicated scripts/tools** — Pre-write tools/skills for the chatbot to take action with minimal token use. |
| 12.8.5 | P3 | **MCP server connection** — Connect to MCP servers like ProxmoxMCP-Plus for infrastructure actions (https://github.com/RekklesNA/ProxmoxMCP-Plus). |

---

## Design Considerations

### 12.8.1 — Floating Chatbox Side Panel

- **Location:** Right side of dashboard, collapsible
- **Trigger:** Clickable icon in bottom-right corner
- **Behavior:** Expands to reveal a message interface with:
  - Message history (scrollable)
  - Input field with send button
  - Quick action buttons for common queries
- **Tech:** Pure HTML/CSS/JS — no framework dependency
- **Storage:** localStorage for message history persistence

### 12.8.2 — Hermes Profile Integration

- **Connection:** WebSocket or SSE to Hermes agent gateway
- **Profile:** Configured network administrator profile
- **Capabilities:**
  - Query wiki content
  - Check monitoring status
  - Create change requests
  - Trigger maintenance procedures
  - Run drift detection
- **Security:** Authenticated via existing OAuth tokens

### 12.8.3 — Persistent Memory

- **Scope:** Per-user conversation history
- **Storage:** localStorage (client) + Redis/SQLite (server)
- **Retention:** 30-day rolling window
- **Privacy:** No PII stored, no raw config data cached

### 12.8.4 — Dedicated Scripts/Tools

Pre-built tools for the chatbot:
- `check_wiki_status` — Returns wiki service health
- `get_monitoring_data` — Returns live service status
- `create_change_request` — Creates pending change card
- `run_drift_detection` — Triggers drift scan
- `get_active_tasks` — Returns current task board state
- `query_wiki_content` — Searches wiki markdown files
- `get_site_info` — Returns site infrastructure details
- `maintenance_checklist` — Returns maintenance procedures

### 12.8.5 — MCP Server Connection

- **Target:** ProxmoxMCP-Plus (https://github.com/RekklesNA/ProxmoxMCP-Plus)
- **Purpose:** Infrastructure actions from chatbot
- **Actions:**
  - Start/stop containers
  - Check container health
  - View logs
  - Resource utilization
- **Safety:** All infrastructure actions require approval via change board

---

## Verification Criteria

- [ ] Chat panel opens/collapses smoothly
- [ ] Messages display correctly (user and assistant)
- [ ] Wiki content queries return accurate results
- [ ] Infrastructure status queries work
- [ ] Change request creation flows through kanban board
- [ ] Hermes profile integration authenticated
- [ ] Memory persists across page reloads
- [ ] MCP infrastructure actions require approval gate
- [ ] No JavaScript errors in console
- [ ] Mobile-responsive layout

---

## Implementation Notes

- Start with read-only queries (wiki content, monitoring status)
- Add write actions (change requests, drift detection) only after validation
- Infrastructure actions (containers, networking) require explicit user confirmation
- All actions logged to change board for audit trail
- Rate limit API calls to prevent flooding

---

*Phase 12.8 Spec created: 2026-06-22*
*Status: Awaiting implementation in Phase 13*
