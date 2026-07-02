# Phase 2: Wiki Engine — Markdown Pages and Templates

**Goal**: Create standardized templates that agent workers use to generate and update wiki pages.

**Estimated Effort**: 3-4 hours

**Dependencies**: Phase 1 complete

**Acceptance Criteria**:
- Entity page template created
- Sites Overview template created
- Maintenance task template created
- Change kanban card template created
- Daily summary template created
- All templates in wiki-templates/ directory

---

## Task 2.1: Entity Page Template

**Target**: `/srv/grid-wiki/wiki-templates/service-entity.md`

**Steps**:
1. Create entity page template:
   ```markdown
   ---
   title: "{{SERVICE_NAME}}"
   type: entity
   status: <active|discovered|stale|deprecated>
   last_verified: <ISO timestamp or null>
   confidence: <verified-live|verified-source|inferred|stale|blocked>
   created: <date>
   tags: [grid, <category>, <service-type>]
   category: infrastructure
   audience: [human, agent]
   ---

   # {{SERVICE_NAME}}

   ## Overview
   {{ONE-LINE DESCRIPTION}}

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
2. Save to `/srv/grid-wiki/wiki-templates/service-entity.md`
3. Verify template exists: `ls -la /srv/grid-wiki/wiki-templates/`

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- cat /srv/grid-wiki/wiki-templates/service-entity.md"
```

**Output Files**:
- `/srv/grid-wiki/wiki-templates/service-entity.md`

---

## Task 2.2: Sites Overview Template (Multi-Site Landing Page)

**Target**: `/srv/grid-wiki/wiki-templates/sites-overview.md`

**Steps**:
1. Create sites overview template:
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
   {{ONE-LINE DESCRIPTION}}

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
2. Save to `/srv/grid-wiki/wiki-templates/sites-overview.md`
3. Verify template exists: `ls -la /srv/grid-wiki/wiki-templates/`

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- cat /srv/grid-wiki/wiki-templates/sites-overview.md"
```

**Output Files**:
- `/srv/grid-wiki/wiki-templates/sites-overview.md`

---

## Task 2.3: Maintenance Task Template

**Target**: `/srv/grid-wiki/wiki-templates/maintenance-task.md`

**Steps**:
1. Create maintenance task template:
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
2. Save to `/srv/grid-wiki/wiki-templates/maintenance-task.md`
3. Verify template exists: `ls -la /srv/grid-wiki/wiki-templates/`

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- cat /srv/grid-wiki/wiki-templates/maintenance-task.md"
```

**Output Files**:
- `/srv/grid-wiki/wiki-templates/maintenance-task.md`

---

## Task 2.4: Change Kanban Card Template

**Target**: `/srv/grid-wiki/wiki-templates/change-card.md`

**Steps**:
1. Create change kanban card template:
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
2. Save to `/srv/grid-wiki/wiki-templates/change-card.md`
3. Verify template exists: `ls -la /srv/grid-wiki/wiki-templates/`

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- cat /srv/grid-wiki/wiki-templates/change-card.md"
```

**Output Files**:
- `/srv/grid-wiki/wiki-templates/change-card.md`

---

## Task 2.5: Daily Summary Template

**Target**: `/srv/grid-wiki/wiki-templates/daily-summary.md`

**Steps**:
1. Create daily summary template:
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
2. Save to `/srv/grid-wiki/wiki-templates/daily-summary.md`
3. Verify template exists: `ls -la /srv/grid-wiki/wiki-templates/`

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- cat /srv/grid-wiki/wiki-templates/daily-summary.md"
```

**Output Files**:
- `/srv/grid-wiki/wiki-templates/daily-summary.md`

---

## Task 2.6: Wiki Index Template

**Target**: `/srv/grid-wiki/wiki-templates/wiki-index.md`

**Steps**:
1. Create wiki index template:
   ```markdown
   ---
   title: "Wiki Index"
   type: index
   last_updated: <ISO timestamp>
   ---

   # Wiki Index

   ## Pages
   | Title | Type | Status | Tags |
   | --- | --- | --- | --- |
   ```

2. Save to `/srv/grid-wiki/wiki-templates/wiki-index.md`
3. Verify template exists: `ls -la /srv/grid-wiki/wiki-templates/`

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- cat /srv/grid-wiki/wiki-templates/wiki-index.md"
```

**Output Files**:
- `/srv/grid-wiki/wiki-templates/wiki-index.md`

---

## Task 2.7: Create Wiki Templates Directory

**Target**: Create wiki-templates/ directory on CT120

**Steps**:
1. SSH to CT120: `ssh grid-pve "pct exec 120 -- bash"`
2. Create directory: `mkdir -p /srv/grid-wiki/wiki-templates`
3. Copy all templates from local workspace:
   ```bash
   rsync -avz /Users/tron/grid-network-wiki-tool/wiki-templates/ \
     grid-pve:/srv/grid-wiki/wiki-templates/
   ```
4. Verify templates exist:
   ```bash
   ls -la /srv/grid-wiki/wiki-templates/
   ```
5. Test template rendering:
   ```bash
   cat /srv/grid-wiki/wiki-templates/service-entity.md
   ```

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- ls -la /srv/grid-wiki/wiki-templates/"
```

**Output Files**:
- `/srv/grid-wiki/wiki-templates/` (directory on CT120)
- 6 template files

---

## Task 2.8: Create Wiki Content from Templates

**Target**: Generate initial wiki pages from templates

**Steps**:
1. Create initial wiki pages:
   ```bash
   # Create INDEX.md
   cat > /srv/grid-wiki/wiki/INDEX.md << 'EOF'
   ---
   title: "Wiki Index"
   type: index
   last_updated: "2026-06-28T00:00:00Z"
   ---

   # Wiki Index

   ## Pages
   | Title | Type | Status | Tags |
   | --- | --- | --- | --- |
   | [[GRID Infrastructure Overview]] | entity | active | [grid, infrastructure] |
   | [[Sites Overview]] | sites-overview | active | [grid, sites] |
   | [[Active Tasks]] | tasks | active | [grid, tasks] |
   ```

   # Create GRID Infrastructure Overview
   cat > /srv/grid-wiki/wiki/GRID-Infrastructure-Overview.md << 'EOF'
   ---
   title: "GRID Infrastructure Overview"
   type: entity
   status: active
   last_verified: "2026-06-28T00:00:00Z"
   confidence: verified-live
   created: "2026-06-23"
   tags: [grid, infrastructure]
   category: infrastructure
   audience: [human, agent]
   ---

   # GRID Infrastructure Overview

   ## Overview
   GRID Infrastructure is the core network for all GRID services. It runs on Proxmox VE (10.10.30.22) with two production containers (CT120, CT131) and one development container (CT121).

   ## Infrastructure
   | Field | Value |
   | --- | --- |
   | Type | Proxmox VE |
   | IP Address | 10.10.30.22 |
   | Hostname | grid-pve |
   | OS | Proxmox VE 8.x |
   | SSH Port | 22 |
   | API Port | 8006 |
   | Status | Active |

   ## Containers
   | Container | Name | Purpose | IP | Status |
   |-----------|------|---------|----|--------|
   | CT120 | grid-core-01 | Production Caddy, Prometheus, Grafana, Uptime Kuma | 10.10.30.120 | Active |
   | CT131 | grid-network-wiki-01 | GRID Network Wiki (wiki-service.py, SSE bridge, MCP proxy) | 10.10.30.131 | Active |
   | CT121 | grid-dev-01 | Development server | 10.10.30.121 | Active |

   ## Services
   ### Proxmox VE
   - **API:** http://10.10.30.22:8006
   - **SSH:** ssh root@10.10.30.22
   - **Management:** Web UI at port 8006
   - **Status:** Active

   ### GRID Network Wiki (CT131)
   - **Wiki Service:** http://10.10.30.131:8082
   - **SSE Bridge:** http://10.10.30.131:8083
   - **MCP Proxy:** http://10.10.30.131:8084
   - **Dashboard:** http://wiki.grid:8082/index.html
   - **Status:** Active

   ## Monitoring Status
   - **Prometheus:** configured
   - **Uptime Kuma:** configured
   - **Blackbox:** configured
   ```

   # Create Sites Overview
   cat > /srv/grid-wiki/wiki/Sites-Overview.md << 'EOF'
   ---
   title: "Sites Overview"
   type: sites-overview
   last_updated: "2026-06-28T00:00:00Z"
   ---

   # Sites Overview

   ## Sites

   | Site | Status | Services | Monitoring | Actions |
   | --- | --- | --- | --- | --- |
   | [[GRID Infrastructure Overview]] | active | 3 | configured | [[GRID Infrastructure Overview]] |
   | [[FMSA Site Integration]] | active | 5 | configured | [[FMSA Site Integration]] |
   ```

   # Create Active Tasks
   cat > /srv/grid-wiki/wiki/Active-Tasks.md << 'EOF'
   ---
   title: "Active Tasks"
   type: tasks
   last_updated: "2026-06-28T00:00:00Z"
   ---

   # Active Tasks

   | Task ID | Description | Status | Assignee |
   |---------|-------------|--------|----------|
   | TASK-01 | Sidebar navigation on ALL pages | Parked | |
   | TASK-02 | Fix 5 missing API endpoints | Parked | |
   ```

2. Verify files created:
   ```bash
   ls -la /srv/grid-wiki/wiki/
   ```
3. Test wiki access:
   ```bash
   curl -s http://localhost:8082/wiki/INDEX.md | head -20
   ```

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- ls -la /srv/grid-wiki/wiki/"
ssh grid-pve "pct exec 120 -- curl -s http://localhost:8082/wiki/INDEX.md"
```

**Output Files**:
- `/srv/grid-wiki/wiki/INDEX.md`
- `/srv/grid-wiki/wiki/GRID-Infrastructure-Overview.md`
- `/srv/grid-wiki/wiki/Sites-Overview.md`
- `/srv/grid-wiki/wiki/Active-Tasks.md`

---

## Task 2.9: Update Wiki Index

**Target**: Update INDEX.md with all wiki pages

**Steps**:
1. Generate wiki index:
   ```bash
   # Create script to generate wiki index
   cat > /srv/grid-wiki/scripts/generate-wiki-index.sh << 'EOF'
   #!/bin/bash
   # Generate wiki index from wiki directory

   WIKI_DIR="/srv/grid-wiki/wiki"
   INDEX_FILE="/srv/grid-wiki/wiki/INDEX.md"

   echo "---" > "$INDEX_FILE"
   echo "title: \"Wiki Index\"" >> "$INDEX_FILE"
   echo "type: index" >> "$INDEX_FILE"
   echo "last_updated: \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"" >> "$INDEX_FILE"
   echo "---" >> "$INDEX_FILE"
   echo "" >> "$INDEX_FILE"
   echo "# Wiki Index" >> "$INDEX_FILE"
   echo "" >> "$INDEX_FILE"
   echo "## Pages" >> "$INDEX_FILE"
   echo "" >> "$INDEX_FILE"
   echo "| Title | Type | Status | Tags |" >> "$INDEX_FILE"
   echo "| --- | --- | --- | --- |" >> "$INDEX_FILE"

   for file in "$WIKI_DIR"/*.md; do
     if [ -f "$file" ]; then
       title=$(grep "^title:" "$file" | sed 's/title: "\(.*\)"/\1/')
       type=$(grep "^type:" "$file" | sed 's/type: "\(.*\)"/\1/')
       status=$(grep "^status:" "$file" | sed 's/status: "\(.*\)"/\1/')
       tags=$(grep "^tags:" "$file" | sed 's/tags: \(.*\)/\1/')
       echo "| $title | $type | $status | $tags |" >> "$INDEX_FILE"
     fi
   done

   echo "Wiki index generated."
   EOF

   chmod +x /srv/grid-wiki/scripts/generate-wiki-index.sh
   ```
2. Run script:
   ```bash
   ssh grid-pve "pct exec 120 -- bash -c 'cd /srv/grid-wiki && ./scripts/generate-wiki-index.sh'"
   ```
3. Verify index:
   ```bash
   cat /srv/grid-wiki/wiki/INDEX.md
   ```

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- cat /srv/grid-wiki/wiki/INDEX.md"
```

**Output Files**:
- `/srv/grid-wiki/scripts/generate-wiki-index.sh`
- `/srv/grid-wiki/wiki/INDEX.md` (updated)

---

## Task 2.10: Deploy to CT120 and Verify

**Target**: Deploy all Phase 2 components to CT120

**Steps**:
1. Sync files to CT120:
   ```bash
   rsync -avz --delete \
     /Users/tron/grid-network-wiki-tool/ \
     grid-pve:/srv/grid-wiki/
   ```
2. Verify templates:
   ```bash
   ssh grid-pve "pct exec 120 -- ls -la /srv/grid-wiki/wiki-templates/"
   ```
3. Verify wiki pages:
   ```bash
   ssh grid-pve "pct exec 120 -- ls -la /srv/grid-wiki/wiki/"
   ```
4. Test wiki access:
   ```bash
   curl -s http://localhost:8082/wiki/INDEX.md
   curl -s http://localhost:8082/wiki/GRID-Infrastructure-Overview.md
   ```

**Verification**:
- All templates exist
- Wiki pages accessible via HTTP
- INDEX.md lists all pages

**Output Files**:
- `/srv/grid-wiki/wiki-templates/` (deployed to CT120)
- `/srv/grid-wiki/wiki/` (deployed to CT120)

---

## Task 2.11: Update Project Manifest

**Target**: Mark Phase 2 complete in PROJECT-MANIFEST.md

**Steps**:
1. Read current `PROJECT-MANIFEST.md`
2. Update `current_goal` to "Phase 3: Dashboard — Browse, Search, and Visualize"
3. Add Phase 2 to `completed_phases` list
4. Commit changes: `git add . && git commit -m "Phase 2 complete"`

**Verification**:
```bash
cat /Users/tron/grid-network-wiki-tool/PROJECT-MANIFEST.md | grep -A 2 "current_goal"
```

**Output Files**:
- `/Users/tron/grid-network-wiki-tool/PROJECT-MANIFEST.md` (updated)

---

## Task 2.12: Document Phase 2 Completion

**Target**: Create Phase 2 completion report

**Steps**:
1. Create `/srv/grid-wiki/raw/live-state/phase-2-completion.md`
2. Document:
   - Entity page template created
   - Sites Overview template created
   - Maintenance task template created
   - Change kanban card template created
   - Daily summary template created
   - Wiki index generated
   - Initial wiki pages created
3. Commit to git: `git add . && git commit -m "Phase 2 completion report"`

**Verification**:
```bash
cat /srv/grid-wiki/raw/live-state/phase-2-completion.md
```

**Output Files**:
- `/srv/grid-wiki/raw/live-state/phase-2-completion.md`

---

## Summary

**Total Tasks**: 12
**Estimated Time**: 3-4 hours
**Files Created**: 7
**Directories Created**: 1
**Templates Created**: 6

**Next Phase**: Phase 3 — Dashboard — Browse, Search, and Visualize