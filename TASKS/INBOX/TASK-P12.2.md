# TASK: Phase 12.2 — Dashboard UX Overhaul (P1)

## Context
Phase 12 — UX Audit & Next-Stage Roadmap. All work in `/Users/tron/grid-network-wiki-tool/`

## Tasks

### 12.2.1 - Format project brain Goal section
Problem: Renders as unformatted text
Fix: Parse markdown headings, bold, lists. Use markdown-to-HTML renderer.

### 12.2.2 - Make info tiles clickable
Fix: Each health metric tile should be clickable to show details or navigate.

### 12.2.3 - Add Review Gate column to Active Dev Board
Fix: Fourth column (Parked → In Progress → Review Gate → Completed).
Orchestrator moves tasks for UX/code verification.

### 12.2.4 - Limit Active Dev Board display
Fix: Show top 5 tasks only. Add "Expand to full board" link.
Prevent board from hiding bottom tools.

### 12.2.5 - Fix Sites Overview
Fix: Populate with actual site data from `wiki-content/sites/`.
Make each site card clickable for drill-down.

### 12.2.6 - Fix Service Status section
Fix: Remove loading spinner. Load from `loadServices()` or show "No services tracked" placeholder.

### 12.2.7 - Fix Recent Drift Reports section
Fix: Remove loading spinner. Show "No drift reports yet" or display actual data.

## Verification
- Project Brain renders formatted markdown
- Tiles are clickable with visual feedback
- Dev Board limited to 5 tasks with expand link
- All sections show meaningful content
