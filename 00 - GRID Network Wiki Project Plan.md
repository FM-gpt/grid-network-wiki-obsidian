---
status: active-plan
created: 2026-06-21
last_updated: 2026-06-21 00:00 ACST
tags: [grid, project-plan, wiki, agent-wiki, dashboard, kanban, monitoring, automation]
---

# GRID Network Wiki — Full Project Plan

## Vision

A deployable, self-maintaining GRID Network Wiki service running on the Proxmox host that:

- Stores all data as `.md` files in a wiki directory — exportable, human-readable, Obsidian-compatible.
- Caches local copies for full offline operator access.
- Syncs bidirectionally with Obsidian vault (`/Users/tron/Documents/Obsidian Vault/GRID Network Wiki/`).
- Is maintained by Hermes agent workers using the kanban workflow, so the wiki stays current without manual intervention.
- Auto-discovers network changes (new containers, new services, config drift) via overnight agent scans.
- Provides a live dashboard for browsing, searching, and visualizing wiki state.
- Auto-generates monitoring for any new service discovered and routes errors to a maintenance kanban.
- Records agent-driven changes in a change kanban for review, keeping the wiki as the single source of truth.

---

## Architecture Overview

```
+-----------------------------------------------------------+
|                      Operator Layer                        |
|  Dashboard UI (https://wiki.grid/)   <->  Wiki on CT120     |
|        ^                                              ^    |
|        | Sites Overview (cards for each site)       |    |
|        | Drill-down into per-site details           |    |
|        | **Full Wiki Viewer** (browse/view raw MD)  |    |
|        | **Download Wiki** (export .md package)     |    |
+--------+-------------------+--------------------------+    |
                         |                                |
+------------------------+--------------------------------+
|                       Server Layer (CT120)                |
|                                                           |
|  /srv/grid-wiki/     - Wiki markdown files (SOT)          |
|  /srv/grid-wiki/sites/ - Multi-site mapping & index       |
|  /srv/grid-wiki/raw/ - Raw evidence (snapshots, logs)     |
|  /srv/grid-wiki/wiki-generated/ - Auto-syntheses          |
|  grid-wiki-service/  - Wiki API + dashboard app           |
|  grid-wiki-cron/     - Agent maintenance scripts          |
|                                                           |
+------------------------+----------------------------------+
                         |
+------------------------+----------------------------------+
|                  Agent / Cron Layer                        |
|                                                           |
|  1am-6am cron jobs (Hermes):                              |
|  - Discovery scan (Proxmox, Docker, Prometheus, Uptime)  |
|  - Drift detection vs wiki                                 |
|  - New service detection + auto-monitor setup             |
|  - Maintenance kanban worker (investigate errors)         |
|  - Wiki generation/update                                 |
|  - Multi-site inventory mapping (grid, fmsa, etc.)        |
|                                                           |
|  Dashboard kanban boards:                                 |
|  - Change Kanban (pending review)                         |
|  - Maintenance Kanban (active issues)                     |
|                                                           |
+-----------------------------------------------------------+
```

---

## Phase 0: Foundation — Wiki Service and Directory Structure (2-3 hours)

### Phase 0.0: Workspace Initialization (DO THIS FIRST)
**Goal**: Create a local-first development environment and verify it.
**Steps**:
1. Create local workspace directory: `/Users/tron/grid-network-wiki-tool/`
2. Copy all project files into it
3. `git init` and `git add .`
4. Create `scripts/deploy-to-grid.sh` (rsync + docker-compose)
5. `git commit -m "Phase 0 complete"`
6. `git push origin main`
7. Snapshot: `cp -r /Users/tron/grid-network-wiki-tool /Users/tron/grid-network-wiki-tool/Phase-0`
**Gate**: Do not start Phase 0.1 until Phase 0.0 is committed and pushed.

### Objective
Create the deployable wiki service on CT120 with its directory structure and basic web server.

### Tasks

#### 0.1 Create wiki directory structure on CT120

```
/srv/grid-wiki/
├── wiki/                          # Source of truth — all .md wiki files
├── PROJECT-MANIFEST.md            # The "Brain": Current Goal, Scope, Task Index
├── ACTIVE-TASKS.md                # The "Lock": Prevents duplicate agent work
├── sites/                         # Multi-site mapping & navigation
│   ├── _index.md                  # Auto-generated sites index
│   ├── grid/                      # GRID site data
│   │   ├── site-info.md
│   │   ├── services.md
│   │   ├── monitoring-status.json
│   │   └── entities/
│   ├── fmsa/                      # FMSA site data
│   │   ├── site-info.md
│   │   ├── services.md
│   │   ├── monitoring-status.json
│   │   └── entities/
│   └── <other-site>/              # Future sites
├── maintenance/                   # Maintenance kanban state
│   ├── active/                    # Open maintenance tasks
│   ├── resolved/                  # Resolved maintenance tasks
│   └── rules/                     # Best-practice resolution rules
├── change-kanban/                 # Change kanban state
│   ├── pending/                   # Pending review changes
│   ├── approved/                  # Approved and merged
│   └── rejected/                  # Rejected changes
├── raw/                           # Raw evidence (snapshots, logs)
│   ├── live-state/                # Live Proxmox/Docker snapshots
│   ├── kanban/                    # Kanban board snapshots
│   └── session-search/            # Session search snapshots
├── wiki-generated/               # Auto-syntheses and summaries
│   ├── entities/                 # Auto-discovered entity pages
│   ├── syntheses/                # Cross-source analysis
│   └── summaries/                # Daily/weekly summaries
├── maintenance-reports/          # Health reports
│   └── <date>-health-report.md
└── sync/                         # Obsidian sync state
    ├── manifest.json             # File tracking for sync
    └── drift/                    # Drift detection results
```

#### 0.2 Deploy wiki web service (Caddy container or lightweight static server)

- Use Caddy (already running on CT120) to serve wiki files.
- Add reverse-proxy route: `wiki.grid/` -> local static file server.
- Optional: lightweight Python/Node API service for search + metadata.
- HTTPS via existing Caddy reverse-proxy infrastructure.

#### 0.3 Create wiki service Compose file

```yaml
# /srv/grid-wiki/docker-compose.yml
services:
  grid-wiki:
    image: caddy:latest
    volumes:
      - /srv/grid-wiki/wiki:/srv/http
      - /srv/grid-wiki/caddy/Caddyfile:/etc/caddy/Caddyfile
    ports:
      - "8082:80"
    restart: unless-stopped
```

#### 0.4 Add Caddy route

```
wiki.grid {
    root * /srv/http
    file_server browse
    encode gzip
}
```

---

## Phase 1: Discovery Engine — Overnight Agent Workers (4-6 hours)

### Objective
Build the agent-driven discovery system that runs 1am-6am to auto-update the wiki.

### Tasks

#### 1.1 Discovery scanner script

Create `/srv/grid-wiki/cron/discovery.sh` — a single-pass script that:

1. **Proxmox inventory scan**
   - `pct list` — all containers, status, IP, resources
   - `pvesm status` — storage pools, usage
   - `zfs list` — datasets, snapshot counts, sizes
   - `nvidia-smi` — GPU state
   - `systemctl --failed` — failed services

2. **Docker scan**
   - `docker ps --format json` — all running containers
   - `docker-compose ps` in each compose directory
   - Extract: name, image, ports, volumes, status, network

3. **Prometheus target scan**
   - `curl http://127.0.0.1:9090/api/v1/targets`
   - Compare against known wiki services

4. **Uptime Kuma monitor scan**
   - Extract monitor list from Kuma API or DB

5. **Network scan**
   - DNS resolution for `.grid` names
   - TCP port probes on known service ports
   - Tailscale tailnet state

6. **Caddy route scan**
   - Extract current Caddyfile routes
   - Compare against known services

7. **Output**
   - Write raw snapshots to `/srv/grid-wiki/raw/live-state/<timestamp>.json`
   - Write diff summary to `/srv/grid-wiki/raw/live-state/<timestamp>-diff.md`

#### 1.2 Drift detection engine

Create `/srv/grid-wiki/cron/drift-detect.sh` — compares discovery output against wiki:

1. **Container drift**
   - New containers? -> Generate entity page + monitoring setup
   - Stopped containers? -> Note in drift report
   - IP changes? -> Flag for review
   - Port changes? -> Flag for review

2. **Service catalog drift**
   - Services in discovery but not in wiki? -> New entity + pending change card
   - Services in wiki but not discovered? -> Stale flag
   - Port/URL changes? -> Drift entry

3. **Monitoring drift**
   - Prometheus targets that are down or missing
   - Uptime Kuma monitors missing or misconfigured
   - Blackbox exporter targets not in config

4. **Output**
   - `/srv/grid-wiki/sync/drift/<timestamp>.json`
   - `/srv/grid-wiki/sync/drift/<timestamp>.md` (human-readable summary)
   - New pending change cards in `/srv/grid-wiki/change-kanban/pending/`
   - New entity pages in `/srv/grid-wiki/entities/` (if auto-approved)

#### 1.3 New service auto-discovery and monitoring setup

When a new service is discovered:

1. **Auto-create entity page**
   - Template: `/srv/grid-wiki/wiki-templates/service-entity.md`
   - Fields: name, site, VMID, IP, ports, compose file, health endpoint, notes
   - Add to service catalog with status "auto-discovered"

2. **Auto-generate monitoring**
   - Prometheus file_sd JSON entry
   - Uptime Kuma monitor entry (HTTP/TCP based on port type)
   - Blackbox exporter probe if HTTP service

3. **If monitoring already exists**
   - Update existing targets
   - No new card needed

4. **If monitoring is missing and auto-setup succeeds**
   - Log the action in change kanban as "auto-approved"
   - Wiki page generated automatically

5. **If monitoring setup fails**
   - Create maintenance card: "Auto-monitoring setup failed for <service>"
   - Include error details and manual instructions

#### 1.4 Hermes cron job definitions

Create Hermes cron jobs for the overnight workflow:

```
Job 1: grid-wiki-discovery
  Schedule: 1:00am daily
  Script: /srv/grid-wiki/cron/discovery.sh
  Output: raw snapshots + diff summary
  Context: grid-wiki-drift-detect (previous drift)

Job 2: grid-wiki-drift-detect
  Schedule: 2:00am daily
  Script: /srv/grid-wiki/cron/drift-detect.sh
  Output: drift report + pending change cards
  Context: grid-wiki-discovery

Job 3: grid-wiki-agent-review
  Schedule: 3:00am daily
  Prompt: Review pending change cards, auto-approve safe changes,
          flag risky ones for human review. Generate new wiki entity
          pages for auto-discovered services. Update service catalog.
          Route maintenance items to maintenance kanban.

Job 4: grid-wiki-maintenance-worker
  Schedule: 4:00am daily
  Prompt: Review maintenance kanban. For each open issue:
          - Check current service state via live commands
          - Apply best-practice resolution per rules in maintenance/rules/
          - Update status (resolved / escalated / acknowledged)
          - Generate resolution notes
          - Escalate unresolved items to Hermes dashboard

Job 5: grid-wiki-wiki-update
  Schedule: 5:00am daily
  Prompt: Apply approved changes to wiki markdown files.
          Update INDEX.md. Generate daily summary.
          Sync to Obsidian vault.

Job 6: grid-wiki-obsidian-sync
  Schedule: 6:00am daily
  Script: /srv/grid-wiki/cron/sync-obsidian.sh
  Output: Bidirectional sync results
```

---

## Phase 2: Wiki Engine — Markdown Pages and Templates (3-4 hours)

### Objective
Create standardized templates that agent workers use to generate and update wiki pages.

### Tasks

#### 2.1 Entity page template

```markdown
---
title: "<Service Name>"
type: entity
status: <active|discovered|stale|deprecated>
last_verified: <ISO timestamp or null>
confidence: <verified-live|verified-source|inferred|stale|blocked>
created: <date>
tags: [grid, <category>, <service-type>]
---

# <Service Name>

## Overview
<One-line description>

## Infrastructure
| Field | Value |
| --- | --- |
| Type | <LXC / Docker / VM / Physical> |
| VMID | <number or N/A> |
| IP | <IP address> |
| Host | <hostname> |
| CPU | <cores> |
| RAM | <MB> |

## Access
| Method | Address | Notes |
| --- | --- | --- |
| URL | <URL> | <notes> |
| SSH | <host:port> | <notes> |
| Direct | <IP:port> | <notes> |

## Configuration
- **Compose file**: `<path>`
- **Config path**: `<path>`
- **Data path**: `<path>`
- **Backups**: <policy>

## Monitoring
| Tool | Status | Endpoint |
| --- | --- | --- |
| Prometheus | <up/down/missing> | <job name> |
| Uptime Kuma | <configured/not set> | <monitor name> |
| Blackbox | <configured/not set> | <probe config> |

## Operational Notes
- **Health endpoint**: `<path>`
- **Restart command**: `<command>`
- **Snapshot required**: <yes/no>
- **Rollback procedure**: <brief>

## Change History
| Date | Change | By | Notes |
| --- | --- | --- | --- |
```

#### 2.2 Sites Overview template (multi-site landing page)

```markdown
---
title: "GRID Sites Overview"
type: sites-overview
last_updated: <ISO timestamp>
---

# GRID Sites Overview

## Sites

| Site | Status | Services | Monitoring | Actions |
| --- | --- | --- | --- | --- |
| [[01 - GRID Network Wiki Index]] | <active|degraded|down> | <count> | <status> | [[01 - GRID Network Wiki Index]] |
| [[16 - FMSA Site Integration]] | <active|degraded|down> | <count> | <status> | [[16 - FMSA Site Integration]] |
| <future-site> | <status> | <count> | <status> | <link> |

## Site Details — <Site Name>

### Overview
<One-line description>

### Infrastructure
- **Proxmox host**: `<hostname>` (`<IP>`)
- **Containers**: `<count> (active / total>`
- **Docker services**: `<count>`
- **Storage**: `<pool>` (`<total>` / `<used>`)
- **Network**: `<VLANs>`

### Service Summary
| Service | Type | IP | Ports | Status |
| --- | --- | --- | --- | --- |

### Monitoring Status
- **Prometheus**: <configured / not configured>
- **Uptime Kuma**: <configured / not configured>
- **Blackbox**: <configured / not configured>

### Key Personnel
- **Admin**: <name/contact>
- **Support**: <name/contact>

### Notes
- <Any additional site-specific info>
```

#### 2.3 Maintenance task template

```markdown
---
title: "<Issue Summary>"
type: maintenance
status: <open|investigating|resolved|escalated>
severity: <low|medium|high|critical>
discovered: <ISO timestamp>
resolved: <ISO timestamp or null>
---

# <Issue Summary>

## Description
<Brief description of the issue>

## Evidence
<Commands, logs, or screenshots showing the problem>

## Investigation
<Steps taken to investigate>

## Resolution
<Actions taken to resolve>

## Best Practice Reference
<link to relevant wiki page or rule>

## Follow-up
<Any remaining items>
```

#### 2.4 Change kanban card template

```markdown
---
title: "<Change Summary>"
type: change
status: <pending|approved|rejected|merged>
submitted: <ISO timestamp>
reviewed: <ISO timestamp or null>
risk: <low|medium|high>
---

# <Change Summary>

## Proposed Change
<What will change>

## Rationale
<Why this change is needed>

## Evidence
<Discovery output, logs, or context>

## Impact Assessment
- **Services affected**: <list>
- **Downtime required**: <yes/no>
- **Rollback procedure**: <brief>

## Review Notes
<Reviewer comments>

## Approval
<Approved by: Tron / Auto-approved>
```

#### 2.5 Daily summary template

```markdown
---
title: "GRID Network Wiki Daily Summary — <date>"
type: summary
date: <date>
---

# GRID Network Wiki Daily Summary — <date>

## Discovery Results
- Containers scanned: <N>
- Services discovered: <N>
- New services: <list>
- Stale services: <list>

## Drift Detected
<Summary of changes found>

## Changes Processed
<Auto-approved, pending, rejected counts>

## Maintenance Issues
<Open issues and their status>

## Wiki Updates
<Pages added, modified, or removed>

## Monitoring Actions
<Auto-configured, failed, manual required>

## Notes
<Any operator notes>
```

---

## Phase 3: Dashboard — Browse, Search, and Visualize (3-4 hours)

### Objective
Build a lightweight dashboard for browsing the wiki, viewing kanban boards, and monitoring wiki health.

### Tasks

#### 3.1 Dashboard structure

```
/srv/grid-wiki/dashboard/
├── index.html              # Main dashboard
├── wiki/                   # Wiki browser
│   └── index.html
├── kanban/                 # Kanban boards
│   ├── change.html
│   └── maintenance.html
├── monitoring/             # Monitoring status
│   └── index.html
├── drift/                  # Drift report viewer
│   └── index.html
├── css/
│   └── dashboard.css
├── js/
│   ├── dashboard.js        # Main app logic
│   ├── wiki.js             # Wiki browser
│   ├── kanban.js           # Kanban board
│   └── api.js              # API client for wiki service
└── data/
    ├── wiki-index.json     # Auto-generated wiki index
    ├── kanban-changes.json # Pending changes
    ├── kanban-maintenance.json # Open maintenance tasks
    └── monitoring-status.json # Auto-generated
```

#### 3.2 Dashboard features

1. **Project Brain (Manifest View)**
   - Render `PROJECT-MANIFEST.md` as the **"Project Status"** widget
   - Shows: Current Goal, Scope Boundaries, Active Tasks, Deep-Doc Index
   - Visual "Goal Progress" tracker based on active task completion
   - Tron can update the Manifest directly from the dashboard (authenticated write)
   - This is the "Project OS" layer — the brain of the GRID Wiki project

2. **Development Board (Active Tasks)**
   - Render `ACTIVE-TASKS.md` as a **Kanban-style board** on the dashboard
   - Columns: Parked | In Progress | Completed
   - Cards show: Task ID, Title, Status, Assignee, Started Date
   - Clicking a card opens the full task file
   - Tron can drag-and-drop cards to change status (authenticated)
   - Prevents duplicate work across all agents

3. **Sites Overview (landing page)**
   - Cards for each site (GRID, FMSA, future sites)
   - Each card shows: site name, status (active/degraded/down), service count, monitoring status
   - Clicking a card drills down into the site-specific wiki pages and dashboard
   - Auto-generated from `/srv/grid-wiki/sites/_index.md`

4. **Wiki browser**
   - Tree view of all wiki pages
   - Search across all pages (client-side grep)
   - Page preview without leaving dashboard
   - Click to open Obsidian via `obsidian://open` URLs

5. **Change Kanban board**
   - Cards for pending changes
   - Columns: Pending -> Approved -> Merged
   - Cards show: title, risk level, submitter, status
   - Click card for full details
   - Approve/reject buttons (authenticated)

6. **Maintenance Kanban board**
   - Cards for open maintenance issues
   - Columns: Open -> Investigating -> Resolved -> Escalated
   - Severity color coding
   - Click card for investigation steps
   - "Apply resolution" button for auto-fixed issues

7. **Monitoring status**
   - All services and their monitoring state
   - Prometheus targets (up/down/missing)
   - Uptime Kuma monitors (configured/missing)
   - New service alerts

8. **Wiki health**
   - Last sync timestamp
   - Drift count (pending changes)
   - Maintenance backlog
   - Wiki file count

9. **Full Wiki Viewer**
   - Tree view of the entire `/srv/grid-wiki/wiki/` directory
   - Click any file to view its raw markdown content
   - Search across all wiki pages (client-side grep)
   - Each card/section in the dashboard links directly to its corresponding wiki page
   - "Open in Obsidian" link for each page (works if user has Obsidian installed locally)

10. **Wiki Export**
    - "Download Wiki" button to generate a `tar.gz` of `/srv/grid-wiki/wiki/`
    - Exports full markdown package including INDEX.md and all entity pages
    - Users can download the entire wiki as a portable markdown package at any time

#### 3.3 API endpoints (Python or Node microservice)

```
GET  /api/wiki-index        - Wiki page list + metadata
GET  /api/wiki/<slug>       - Wiki page content
POST /api/wiki/search       - Search wiki pages
GET  /api/kanban/changes    - Pending change cards
POST /api/kanban/changes/<id>/approve  - Approve change
POST /api/kanban/changes/<id>/reject   - Reject change
GET  /api/kanban/maintenance  - Open maintenance cards
POST /api/kanban/maintenance/<id>/resolve  - Resolve maintenance
GET  /api/monitoring-status   - Monitoring overview
GET  /api/drift/<date>       - Drift report
GET  /api/sync-status        - Last sync info
```

---

## Phase 4: Methodology Integration & Project OS (2-3 hours)

### Objective
Integrate the "Project Manifest + State Machine" model from the Development Project Wiki into the GRID Wiki tool. This turns the GRID Wiki from a static wiki into a **Project Operating System** that manages the management of the GRID Wiki itself.

### Tasks

#### 4.1 Manifest as "Project Brain"

The `PROJECT-MANIFEST.md` (created in Phase 0) becomes the living "RAM" of the GRID Wiki project:

1. **`PROJECT-MANIFEST.md`** contains:
   - `current_goal`: What the team is focused on (e.g., "Phase 0 Foundation")
   - `scope_boundaries`: Hard limits to prevent scope creep
   - `active_tasks`: List of in-progress work (with assignee locks)
   - `deep_doc_index`: Links to heavy documentation (agents only load when needed)

2. **Dashboard Integration**:
   - Read `PROJECT-MANIFEST.md` to render the **"Project Status"** widget on the dashboard
   - Show current goal, scope boundaries, and active tasks at a glance
   - Allow Tron to update the Manifest directly from the dashboard (authenticated write)
   - Show a visual "Goal Progress" tracker based on active task completion

3. **Agent Integration**:
   - Auto-discovery agents (1am-6am) read the Manifest to understand the "Current Goal"
   - Agents only discover things relevant to the current goal (e.g., if "Phase 0" is the goal, agents focus on foundation infrastructure)
   - Agents update the Manifest when a goal is achieved (e.g., "Phase 0 complete. New Goal: Phase 1")

#### 4.2 Active Tasks as "The Lock"

The `ACTIVE-TASKS.md` becomes the source of truth for a new **"Development Board"** on the dashboard:

1. **`ACTIVE-TASKS.md`** is a simple table:
   ```
   | Task ID | Status | Assignee | Started | Link |
   |---|---|---|---|---|
   | TASK-01 | Parked | EMPTY | - | `TASKS/INBOX/TASK-01.md` |
   | TASK-02 | In Progress | TRON | 2026-06-20 | `TASKS/INBOX/TASK-02.md` |
   ```

2. **Dashboard Integration**:
   - Render `ACTIVE-TASKS.md` as a **Kanban-style board** on the dashboard
   - Columns: Parked | In Progress | Completed
   - Cards show: Task ID, Title, Status, Assignee, Started Date
   - Clicking a card opens the full task file
   - Tron can drag-and-drop cards to change status (authenticated)

3. **Agent Integration**:
   - **State Machine Enforcement**: Agents follow the "State Machine" workflow:
     - Scan Manifest -> Check Lock -> Read Task -> Execute -> Update State
   - **Duplicate Work Prevention**: If a task is `In Progress` and assigned to `TRON`, no other agent picks it up
   - **Completion Protocol**: When a task is done, the agent moves it to `TASKS/COMPLETED/` and updates the Manifest

#### 4.3 AGENTS.md as "Protocol" Layer

The `AGENTS.md` file acts as the **Rulebook** for the GRID Wiki tool:

1. **Unified Language**: Both auto-discovery agents and project agents follow the same "State Machine" rules
2. **Scope Control**: If the GRID Wiki project starts to drift, the Manifest's `SCOPE BOUNDARIES` acts as a hard wall
3. **Context Hygiene**: Agents are instructed to **NEVER** read the entire project directory — only load specific files when linked in the Manifest

#### 4.4 Multi-Site Alignment

The methodology allows the GRID Wiki to manage **GRID** and **FMSA** as separate "projects" under one umbrella:

1. **`PROJECT-MANIFEST.md`**: For the overall GRID Wiki Project (managing the tool itself)
2. **`SITE-INFRA.md`**: For the GRID Network (managing the servers)
3. **`SITE-INFRA.md`**: For the FMSA Network (managing the remote site)

All of these files live in the GRID Wiki server, but they are distinct "Entities" that the agents manage.

---

## Phase 5: Monitoring Auto-Setup (2-3 hours)

### Objective
Build the automated monitoring setup that runs when new services are discovered.

### Tasks

#### 5.1 Prometheus auto-configuration

Script: `/srv/grid-wiki/cron/auto-monitor-prometheus.sh`

- For each discovered service:
  - Determine scrape type (HTTP, TCP, node_exporter, cAdvisor)
  - Generate file_sd JSON entry
  - Add to appropriate job file
  - Validate with `docker exec prometheus promtool check config`
  - Reload Prometheus: `docker exec prometheus kill -HUP 1`
  - Log result to `/srv/grid-wiki/monitoring/prometheus/auto-<date>.log`

#### 5.2 Uptime Kuma auto-configuration

Script: `/srv/grid-wiki/cron/auto-monitor-uptime-kuma.sh`

- For each discovered service:
  - Create monitor entry in Kuma DB or via API
  - Use appropriate monitor type (HTTP, TCP, Ping, etc.)
  - Name: `<service-name> - uptime`
  - Log result to `/srv/grid-wiki/monitoring/uptime-kuma/auto-<date>.log`

#### 5.3 Blackbox exporter auto-configuration

- For HTTP services: add HTTPS probe to Blackbox config

#### 5.4 Grafana dashboard auto-panel

- When new Prometheus targets appear:
  - Check if a Grafana dashboard exists for the service type
  - If yes: add new target panel
  - If no: create a simple "service health" panel
  - Log: `/srv/grid-wiki/monitoring/grafana/auto-<date>.log`

---

## Phase 6: Wiki Export & Accessibility (1-2 hours)

### Objective
Ensure the wiki is fully accessible via the web dashboard and easily exportable as a package of `.md` files. No complex bidirectional sync.

### Tasks

#### 6.1 Full Wiki Viewer in Dashboard

- Add a "Browse Wiki" section to the dashboard
- Tree view of the `/srv/grid-wiki/wiki/` directory
- Click any file to view its raw markdown content
- Each card/section in the dashboard links to its corresponding wiki page
- "Open in Obsidian" link for each page (works if user has Obsidian installed locally)

#### 6.2 Wiki Export Feature

- Add a "Download Wiki" button to the dashboard
- Users can download the full wiki as a portable markdown package at any time

#### 6.3 Direct File Access

- `/srv/grid-wiki/wiki/` remains a standard directory on the server
- Accessible via SCP/SFTP for advanced users
- No database layer — just markdown files on disk
- After sync: update manifest

---

## Phase 7: Maintenance Auto-Resolution (3-4 hours)

### Objective
Build the rules-based maintenance system that auto-fixes common issues.

### Tasks

#### 7.1 Best-practice rules

Create `/srv/grid-wiki/maintenance/rules/`:

```
rules/
├── prometheus-target-down.md      # How to handle down targets
├── container-not-starting.md      # Container startup failures
├── disk-space-low.md              # Disk usage thresholds and actions
├── service-health-check-failed.md  # Health endpoint failures
├── monitoring-missing.md          # Service without monitoring
├── zfs-snapshot-stale.md          # Stale snapshot timers
├── dns-resolution-failed.md       # DNS name resolution issues
└── caddy-route-missing.md         # Missing or broken reverse-proxy routes
```

Each rule file format:

```markdown
---
rule: <rule-name>
trigger: <condition>
auto_fix: <true/false>
requires_approval: <true/false>
---

# <Rule Name>

## Trigger
<When this rule fires>

## Investigation Steps
1. <step 1>
2. <step 2>
3. <step 3>

## Auto-Fix (if auto_fix: true)
<What the agent does automatically>

## Manual Fix (if requires_approval: true)
<What the agent needs Tron to do>

## Escalation Criteria
<When to escalate to Tron>
```

#### 7.2 Maintenance worker logic

The agent worker for maintenance kanban:

1. Read all open maintenance cards
2. For each card:
   - Run investigation commands (live state)
   - Match issue to a rule in `maintenance/rules/`
   - If auto-fix available and safe: apply fix
   - If manual fix needed: create review card
   - If escalation criteria met: flag for human review
3. Update card status
4. Log resolution details

---

## Phase 8: Change Kanban Workflow (2-3 hours)

### Objective
Build the change management workflow where agents submit changes and Tron reviews them.

### Tasks

#### 8.1 Change submission

When any agent makes a network change:

1. Agent creates a card in `/srv/grid-wiki/change-kanban/pending/`
2. Card includes: what changed, why, evidence, rollback plan
3. Card is auto-notified to Hermes dashboard kanban
4. Tron reviews and approves/rejects
5. Approved changes are merged into wiki markdown files
6. Wiki is synced to Obsidian

#### 8.2 Dashboard integration

- Hermes kanban board `grid-wiki-change` for pending changes
- Hermes kanban board `grid-wiki-maintenance` for open issues
- Both boards visible in the wiki dashboard
- User flags on cards feed into the appropriate kanban

#### 8.3 User flagging

- Users can flag changes at the card level
- Flags feed into the change kanban as "user-reported"
- Flags can also be kept as user notes (non-blocking)

---

## Phase 9: Agent Knowledge Base Enhancement (2-3 hours)

### Objective
Make the wiki an active agent knowledge base that agents can query and contribute to.

### Tasks

#### 9.1 Agent query interface

- Wiki pages contain structured data agents can parse
- `INDEX.md` serves as a catalog for agents to discover relevant pages
- Entity pages include standardized sections agents can query
- `CHANGELOG.md` tracks all changes for agent reference

#### 9.2 Wiki as agent memory

- Agent interactions with the network are recorded in wiki
- Changes made by agents are logged in the change kanban
- Maintenance actions are documented in the maintenance kanban
- This creates a complete audit trail

#### 9.3 Query patterns for agents

Agents can query the wiki for:

- "What services are running?" -> Read `02 - GRID Service Catalog` + live discovery
- "Is <service> monitored?" -> Check monitoring status API + service catalog
- "What changed recently?" -> Read `CHANGELOG.md` + recent drift reports
- "How do I manage <service>?" -> Read entity page + Operations Runbook
- "Is <service> healthy?" -> Check monitoring status API + maintenance kanban

---

## Implementation Priority

| Priority | Phase | Title | Estimate |
|----------|-------|-------|----------|
| P0 | 4 | Methodology Integration (Project Manifest + Lock) | 2-3h |
| P0 | 0 | Foundation — Wiki service + directory | 2-3h |
| P0 | 1 | Discovery engine — overnight workers | 4-6h |
| P0 | 2 | Wiki engine — templates | 3-4h |
| P0 | 3 | Dashboard — browse + kanban UI | 3-4h |
| P0 | 6 | Obsidian sync | 2-3h |
| P1 | 5 | Monitoring auto-setup | 2-3h |
| P2 | 9 | Agent KB enhancement | 2-3h |

**Total estimate: 25-35 hours**

---

## Integration with Existing Hermes Infrastructure

### Existing components reused:
- **Hermes kanban boards**: `doc-grid-network-wiki` board for maintenance; new boards for changes
- **Cron jobs**: Existing maintenance cron jobs extend into wiki maintenance
- **Prometheus**: Auto-generated file_sd targets join existing jobs
- **Uptime Kuma**: Auto-generated monitors join existing monitors
- **Caddy**: Wiki gets a new Caddy route via existing reverse-proxy
- **AGENTS.md**: Protocol file for all GRID Wiki agents (embedded methodology)
- **Ollama/Open WebUI**: Wiki can serve as a knowledge base for AI agents
- **Honcho**: Wiki state and sync status tracked in Honcho memory
- **Aider/Devstral**: Wiki content can be reviewed and improved by coding agents
- **grid-aider wrapper**: Agents use standard Aider workflow on wiki content