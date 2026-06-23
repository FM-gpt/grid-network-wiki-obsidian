---
title: "Phase 12 — UX Audit & Next-Stage Roadmap"
status: active-plan
created: 2026-06-22
last_updated: 2026-06-22
tags: [grid, project-plan, wiki, ux-audit, roadmap, phase-12]
---

# Phase 12 — UX Audit & Next-Stage Roadmap

> **Created:** 2026-06-22
> **Source:** Adversarial UX test (Dottie persona) + user walkthrough review
> **Target:** GRID Network Wiki Dashboard, all sub-pages, and associated services

---

## 1. Tool Walkthrough — User Notes (Verbatim)

> **Dashboard**
>
> - The Goal section in project brain is a mess of unformatted text
> - Above that the info tiles are good but what is the wiki service with the warning sign telling me? It would be good if I could click that to see the problem
> - Same with the other info squares
>
> **Active Dev Board**
>
> - I love this feature, this is the biggest win of this project
> - Needs a fourth column as a review gate so the orchestrator can make sure the work is delivered as per design with a full ux and code check
>
> **Boards (Change & Maintenance)**
>
> - When I click on the task tiles in the change board or maintenance board I should see the notes for the full task
> - They should be formatted in a way that is easily readable to follow what the task was and what was done for it to be completed or planned depending
> - The board keeps expanding hiding the tools at the bottom of the page as the completed list grows
> - This module on this page should be limited to the top 5 then you can open it to its own page
>
> **Dashboard Sections**
>
> - Site overview is empty
> - Recent drift reports are empty with a loading spinner
> - Service status is empty with a loading spinner
>
> **Browse Wiki**
>
> - Has each wiki page listed with a lot of formatting code in the name so they are unreadable
> - When clicked they say error loading file
>
> **Wiki Viewer**
>
> - Loaded once and looked good but didn't seem to have all the information/pages we have in the obsidian wiki
> - The second time I loaded it the loading spinner was there for a long time before loading
>
> **Change Board**
>
> - Looks good, took a long time to load
> - I should be able to click on the tile to read the full request and its updates in each queue before approving or rejecting with reason
> - If it has passed the gate and does not need user intervention/approval it should confirm auto approved
> - Where is the input for a user to enter a change request
> - What is the review gate to confirm the work was completed successfully
>
> **Maintenance Board**
>
> - I want to see the cards for the pending active and completed as I do for the other boards
> - I want them clickable for the full note/history
> - What is the review gate to confirm the work was completed successfully
> - I really like the maintenance procedures, they should also document what skill and tool is needed to complete them
> - Future opportunity to connect to an MCP server (noted below)
>
> **Dead Links**
>
> - All rules don't show anything when clicked
> - Reports don't show anything when clicked
>
> **From Dashboard Menu Level**
>
> **Monitoring**
> - When clicked takes a long time to load
> - This looks good, has more opportunity as we have a lot more services running and monitored
> - We should have the services separated into the groups by site, then server, then container, then in that container show what is running
> - When click on level I should see the useful information I would need such as how to connect to the service, how to use it, how to setup, access requirements, admin pages
> - Example: Minecraft is listed as a service — that is a LXC container on Grid Proxmox server and it is running Crafty, BlueMap, it has backups happening, it has plugins, it has DNS config, it has external access via Tailscale, it has multiple users, it needs regular updates for the server and crafty and the plugins, are there Cron Jobs set for that
> - A lot of this data is already in the wiki documents in some format but needs to be pulled together
> - The cards across the top should be clickable so I can see the full info they are relating to
>
> **Infrastructure Health**
> - Showing Prometheus connection failed
> - The Omada controller has the option for webhooks for monitoring — perhaps we can set that up instead of the current method
>
> **Drift Reports**
> - I like the design
> - The summary cards when I click them should act as a filter for the recent drift report log below
> - When I click the run detection button I get an error "the string did not match the expected pattern"
>
> **Dead Menu Links**
> - Grid Infrastructure doesn't show anything
> - Same with FMSA Office
> - Settings and API Docs don't do anything
>
> **Menu Bar Questions**
> - What is the difference between browse wiki and wiki viewer?
> - From the dashboard level the left menu bar has operations
> - When I click change board the new toolbar shows kanban board with change boards and maintenance board
> - The active development board from the dashboard should live here in its full form and also have a link from the operations level
> - When I go to the maintenance board the change board link in the menu is now in the top section instead of under kanban boards
> - That left hand menu should be reasonably static
> - We can just stick with the layout from the dashboard view
> - When you go to another level such as change board the new pages should the display as an indented sub menu under change board keeping the other items on the page
> - That allows the user to go to any other top level menu with one click
> - Unless it is relevant to do it now with these changes a future option is to collapse the menu bar
>
> **Future Spec (final phase once all other aspects are fully loaded)**
>
> - A chatbot style floating message box to side panel to chat to a chatbot that can answer basic questions on the wiki info
> - Then it can become or can be selected to connect to a profile in Hermes that is configured as the network administrator who runs the wiki and the network
> - The profile that handles all the network related tasks, the monitoring and can take action as requested from the user from the chatbox
> - It has persistent memory all the tool access, dedicated scripts pre written as tools/skills to take action with minimal token use or an MCP server connection like https://github.com/RekklesNA/ProxmoxMCP-Plus

---

## 2. Adversarial UX Test — Full Findings (Verbatim)

### Tester Persona
**Doris "Dottie" Kowalski, 67 — Facilities Manager**
- Manages building HVAC, electrical, plumbing, security with a three-ring binder and paper clipboards
- Computer is a laptop her grandson set up — she still doesn't trust it
- WhatsApp only for technology. "Dashboard" sounds like something you drive, not manage
- Her ONE job: "Are all my building systems running right now, or do I need to make 15 phone calls?"
- She'd rather use her clipboard if this doesn't save her time

### The Good (Grudging Admission)
- The service detail page for known services (like Caddy) is actually informative — shows ports, monitoring status, and wiki content all in one place
- The maintenance board has real procedures listed with severity levels
- The "Download Wiki" button actually works and delivers a tar.gz file
- The monitoring page shows real health data for all 12 services
- The kanban boards (change & maintenance) load with real data

### The Bad (Legitimate UX Issues)
- The top of the monitoring page says Prometheus, Uptime Kuma, and Grafana are all FAILED (red X), but the table below says all services are "healthy" — that's two contradictory messages in one view
- The dashboard shows "--" for "Last Sync" and "--" for "Maint. Backlog" — she has no idea if her data is current
- The wiki pages listed as clickable have NO VISIBLE TEXT — just blank rows that say "click me" in a language she doesn't understand
- The "GRID Infrastructure" and "FMSA Office" links in the sidebar do nothing — they just scroll to anchors on the current page
- The drift reports page shows "0 drifts" but has no way to actually see what's drifted
- The sync status page has a "Sync Now" button but no indication of whether sync ever succeeded
- The wiki.html page only shows the PROJECT-MANIFEST.md with a GitHub link — it's supposed to be a "Wiki Browser" but there's no browse-able content
- "OPEN DRIFT" shows 0 but the dashboard has no context about what "drift" means
- "MAINT. BACKLOG" shows "--" — she can't tell if there's maintenance work pending

### The Ugly (Showstoppers)
- The dashboard has a JavaScript error (`updateSitesOverview is not defined`) that silently breaks the "Sites Overview" section — she'd see a blank area and assume the whole app is broken
- The wiki search box accepts input but the results shown as clickable items have NO TEXT — she clicks on nothing and gets nothing
- The `/api/wiki-index` API endpoint returns 404 — the app's own data layer is broken
- When you look up a nonexistent service, it says "Nonexistent Service" with "N/A" everywhere — no helpful "This service isn't tracked yet" message

### Dottie's Specific Complaints
1. **Dashboard (main):** "Why does it say my monitoring tools are DOWN when the table right below says they're all working? I'm more confused than when I started."
2. **Dashboard (health metrics):** "It says '131 wiki pages' but shows '--' for last sync. How do I know if this is current?"
3. **Monitoring page:** "First it tells me everything's broken with red X marks, then the table below says everything's fine. Is the monitoring broken or is monitoring telling on itself?"
4. **Wiki Browser:** "I click 'Browse Wiki' and get a list of files I can't read. They're all blank. I click one and it shows me a text file. This is what you call a BROWSER?"
5. **wiki.html:** "This page is supposed to be a 'Wiki Browser' but it just shows one document. Where's the rest?"
6. **Drift Reports:** "What's 'drift'? I clicked the button that says 'Run Detection' and nothing happened. Is it running? Did it finish? Did it find anything?"
7. **Sidebar links (GRID Infrastructure / FMSA Office):** "I click these hoping to see my building's info and... nothing. The page doesn't change. I must have clicked wrong."
8. **Service detail (nonexistent):** "I clicked a service name in the table and it says 'Nonexistent Service' with 'N/A' for everything. Just tell me 'This service isn't tracked yet' — don't make me guess."
9. **Sync Status:** "There's a button that says 'Sync Now' but no way to know if it ever worked. I'd click it a hundred times and never know."

### Verdict
> "I've used clipboards for 45 years and I know exactly what I have on mine right now. This thing shows me red X marks that aren't red X marks, blank lists of files, and numbers with no explanation. My clipboard works. I don't need a dashboard that lies to me."

### Pragmatism Filter Summary
| # | Complaint | Rating |
|---|-----------|--------|
| 1 | Monitoring contradictory status | RED |
| 2 | "--" for sync and backlog | RED |
| 3 | Wiki files have no visible text | RED |
| 4 | Sidebar links do nothing | RED |
| 5 | Drift Reports page empty | YELLOW |
| 6 | Sync status page empty | YELLOW |
| 7 | wiki.html shows only 1 file | RED |
| 8 | `/api/wiki-index` returns 404 | RED |
| 9 | Nonexistent service page | RED |
| 10 | `updateSitesOverview` JS error | RED |
| 11 | "Drift" terminology | WHITE |
| 12 | "I'd rather use clipboard" | WHITE |

---

## 3. Phase 12 — Full Roadmap

### Phase 12.1 — Critical Bug Fixes (Highest Priority)
| Task | Priority | Details |
|------|----------|---------|
| 12.1.1 | P0 | **Fix `updateSitesOverview` JS error** — Add missing function to `dashboard.js` that renders the Sites Overview grid. If no sites data available, render "No sites tracked yet" placeholder. |
| 12.1.2 | P0 | **Fix `/api/wiki-index` 404** — Path should be `wiki-content/wiki/INDEX.md` not `wiki/INDEX.md`. Update `wiki-service.py` line 140. |
| 12.1.3 | P0 | **Fix wiki-browser.html tree items** — The `renderTree` function renders clickable items but the filename text is not visible. Fix CSS rendering and ensure `filterTree` properly displays filtered results with text. |
| 12.1.4 | P0 | **Fix monitoring page contradictory status** — Headers showing Prometheus/Uptime Kuma/Grafana as FAILED contradict the table below showing all services healthy. Either sync headers to table data or label them "Live checks:" vs "Cached data:". |
| 12.1.5 | P0 | **Fix drift detection "string did not match expected pattern" error** — Debug the regex or pattern matching in the run detection function on drift.html. |
| 12.1.6 | P0 | **Fix dashboard "--" metrics** — Replace "--" for Last Sync with "Never synced", for Maint. Backlog with "0". Critical operational indicators must always show values. |

### Phase 12.2 — Dashboard UX Overhaul
| Task | Priority | Details |
|------|----------|---------|
| 12.2.1 | P1 | **Format project brain Goal section** — Currently renders as unformatted text. Parse markdown headings, bold, lists. Use a proper markdown-to-HTML renderer. |
| 12.2.2 | P1 | **Make info tiles clickable** — Each health metric tile (wiki service with warning sign, page count, sync time, etc.) should be clickable to show more details or navigate to the relevant page. |
| 12.2.3 | P1 | **Add Review Gate column to Active Dev Board** — Fourth column (Parked → In Progress → Review Gate → Completed). Orchestrator moves tasks here for UX/code verification before completion. |
| 12.2.4 | P1 | **Limit Active Dev Board display** — Show top 5 tasks only on dashboard. Provide "Expand to full board" link that opens dedicated kanban page. Prevent board from growing and hiding bottom tools. |
| 12.2.5 | P1 | **Fix Sites Overview** — Populate with actual site data from `wiki-content/sites/`. Each site card clickable to drill-down page. |
| 12.2.6 | P1 | **Fix Service Status section** — Remove loading spinner. Either load data from `loadServices()` or show "No services tracked" placeholder. |
| 12.2.7 | P1 | **Fix Recent Drift Reports section** — Remove loading spinner. Show "No drift reports yet" or display actual data. |

### Phase 12.3 — Navigation & Sidebar Overhaul
| Task | Priority | Details |
|------|----------|---------|
| 12.3.1 | P1 | **Static sidebar layout** — Sidebar should not change between pages. Keep dashboard layout as the canonical sidebar. When on a sub-page (e.g., Change Board), show it as an indented submenu under the parent item, not as a top-level replacement. |
| 12.3.2 | P1 | **Fix dead sidebar links** — Either build the Grid Infrastructure / FMSA Office drill-down pages, or hide/remove these links until ready. Showing dead links erodes trust. |
| 12.3.3 | P1 | **Fix Settings and API Docs links** — Same as above. Build placeholder pages or hide until ready. |
| 12.3.4 | P1 | **Clarify "Browse Wiki" vs "Wiki Viewer"** — Rename or relabel one of them. Browse Wiki = wiki-browser.html (tree view). Wiki Viewer = wiki.html (single page viewer). Add tooltip or subtitle explaining the difference. |
| 12.3.5 | P1 | **Add Active Dev Board link to sidebar** — The development board should be accessible from the sidebar menu at all levels, not just the dashboard. |
| 12.3.6 | P2 | **Collapsible sidebar (future)** — Add a toggle to collapse/expand the sidebar. Not urgent but useful for dashboard-focused users. |

### Phase 12.4 — Change Board & Maintenance Board Enhancements
| Task | Priority | Details |
|------|----------|---------|
| 12.4.1 | P1 | **Clickable task tiles on all boards** — Clicking a task card should open a modal or slide-out panel showing the full request notes, updates, and completion history. Format for easy readability. |
| 12.4.2 | P1 | **Change request input form** — Add a "New Change Request" button/form that lets users submit change requests directly from the Change Board page. |
| 12.4.3 | P1 | **Approve/Reject with reason** — Each task card should have Approve/Reject buttons with a reason input field. Track approval history on the card. |
| 12.4.4 | P1 | **Auto-approve logic** — If a task does not require user intervention/approval, auto-approve and show a confirmation banner. |
| 12.4.5 | P1 | **Review gate confirmation** — Add a formal review gate step on both boards to confirm work was completed successfully before marking complete. |
| 12.4.6 | P1 | **Maintenance board card grouping** — Show cards for Pending, Active, and Completed as separate sections (like other boards), not just a summary. Each clickable for full note/history. |
| 12.4.7 | P1 | **Maintenance procedures — document skills/tools** — Each procedure should list required skills, tools, and MCP server connections needed to complete it. |
| 12.4.8 | P2 | **Change board loading performance** — Investigate and optimize the long load time for change board. Cache kanban data, lazy-load card details. |

### Phase 12.5 — Monitoring Enhancements
| Task | Priority | Details |
|------|----------|---------|
| 12.5.1 | P1 | **Service hierarchy drill-down** — Reorganize monitoring page to show services grouped by: Site → Server → Container → Running Services. Clicking any level drills down to show the next level. |
| 12.5.2 | P1 | **Clickable service cards** — Each service should be clickable to show useful information: how to connect, how to use, setup instructions, access requirements, admin pages. |
| 12.5.3 | P1 | **Service detail enrichment** — Pull together wiki data for each service: LXC info, backups, plugins, DNS config, Tailscale access, users, updates, cron jobs. Already exists in wiki docs but needs to be surfaced. |
| 12.5.4 | P1 | **Make top cards clickable** — The summary cards across the top (Prometheus, Uptime Kuma, Grafana, etc.) should be clickable to see full info they relate to. |
| 12.5.5 | P1 | **Investigate Prometheus connection failure** — Fix "Prometheus connection failed" in Infrastructure Health section. Check if Prometheus is actually running and accessible. |
| 12.5.6 | P2 | **Omada controller webhook monitoring** — Set up Omada Controller webhooks for monitoring as an alternative to the current polling method. |
| 12.5.7 | P2 | **Monitoring page load performance** — Optimize the long load time. Cache data, use pagination, or lazy-load sections. |

### Phase 12.6 — Wiki Viewer Improvements
| Task | Priority | Details |
|------|----------|---------|
| 12.6.1 | P1 | **Show all Obsidian wiki content** — Currently wiki.html only shows one file. Load all wiki pages with a directory browser. |
| 12.6.2 | P1 | **Loading speed improvements** — Implement caching (localStorage or IndexedDB) so second load doesn't show a long spinner. |
| 12.6.3 | P1 | **Better markdown rendering** — Enhance the `renderMarkdown` function with full support for tables, code blocks, nested lists, images, and nested formatting. |
| 12.6.4 | P1 | **"Browse Wiki" and "Wiki Viewer" unification** — Either merge the two into one page or clearly differentiate their purposes with labels and descriptions. |
| 12.6.5 | P2 | **Markdown-to-HTML preview mode** — Add a toggle between "Raw" and "Preview" modes in wiki-browser.html for easier reading. |

### Phase 12.7 — Drift Reports Enhancement
| Task | Priority | Details |
|------|----------|---------|
| 12.7.1 | P1 | **Fix run detection button error** — Debug "the string did not match the expected pattern" error. Likely a regex or validation issue in the client-side JS or server-side handler. |
| 12.7.2 | P1 | **Summary cards as filters** — When clicking summary cards (Total Drifts, Critical, Warning, Info), filter the recent drift report log below to show only matching types. |
| 12.7.3 | P2 | **Drift report detail views** — Allow clicking on drift report entries to see full diff details. |

### Phase 12.8 — Future Spec: AI Chatbot Assistant (Final Phase)
| Task | Priority | Details |
|------|----------|---------|
| 12.8.1 | P3 | **Floating chatbox side panel** — Add a chatbot-style floating message box to the side panel. Answer basic questions from wiki info. |
| 12.8.2 | P3 | **Hermes profile integration** — Allow the chatbot to connect to a Hermes profile configured as the network administrator who runs the wiki and the network. This profile handles network tasks, monitoring, and can take action from the chatbox. |
| 12.8.3 | P3 | **Persistent memory** — Chatbot maintains persistent memory of all tool access, context, and conversation history. |
| 12.8.4 | P3 | **Dedicated scripts/tools** — Pre-write tools/skills for the chatbot to take action with minimal token use. |
| 12.8.5 | P3 | **MCP server connection** — Connect to MCP servers like ProxmoxMCP-Plus for infrastructure actions (https://github.com/RekklesNA/ProxmoxMCP-Plus). |

---

## 4. Priority Summary

### P0 — Must Fix Now (Blocking)
- `updateSitesOverview` JS error
- `/api/wiki-index` 404
- wiki-browser.html unreadable tree items
- Monitoring page contradictory status
- Drift detection error
- Dashboard "--" metrics

### P1 — Fix in Phase 12.1-12.7 (Core UX)
- Goal section formatting
- Info tile clickability
- Review gate column
- Active Dev Board limitation
- Sidebar navigation overhaul
- Board tile clickability and detail views
- Change request input
- Monitoring hierarchy drill-down
- Wiki viewer content loading
- All dead links

### P2 — Nice-to-Have (Phase 12.8 or Later)
- Collapsible sidebar
- Auto-approve logic
- Monitoring load performance
- Omada webhook monitoring
- Markdown preview mode
- Drift report detail views
- Maintenance board loading performance

### P3 — Future Spec (Post-Phase 12)
- AI Chatbot Assistant
- Hermes profile integration
- Persistent memory
- Dedicated scripts/tools
- MCP server connections

---

## 5. Verification Criteria

For each phase completion, verify:
- [ ] No JavaScript errors in browser console
- [ ] All sidebar links are functional or hidden
- [ ] All info tiles show meaningful values (no "--")
- [ ] All data sections load within 2 seconds
- [ ] All clickable elements have clear visual feedback
- [ ] Error states show helpful messages (not "N/A" or "Unknown")
- [ ] Mobile-responsive layout tested

---

*Phase 12 Roadmap created: 2026-06-22*
*Supersedes: Phase 11 operational maintenance mode*
*Next phase: 13 - AI Assistant Integration (post-Phase 12)*
