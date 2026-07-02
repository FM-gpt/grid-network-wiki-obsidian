# Phase 9: Agent Knowledge Base Enhancement

**Goal**: Make wiki an active agent knowledge base that agents can query and contribute to.

**Estimated Effort**: 2-3 hours

**Dependencies**: Phase 8 complete

**Acceptance Criteria**:
- Agent query interface functional
- Wiki serves as agent memory
- Query patterns documented
- Wiki pages structured for agent parsing
- Agent interactions recorded in wiki

---

## Task 9.1: Agent Query Interface

**Target**: Add agent query interface to wiki

**Steps**:
1. Update wiki-service.py to add agent query endpoint:
   ```python
   def query_wiki(self, query: str) -> dict:
       """Query wiki for relevant pages."""
       wiki_dir = self.root / 'wiki'
       results = []

       for page_path in wiki_dir.glob('*.md'):
           content = page_path.read_text()
           if query.lower() in content.lower():
               results.append({
                   'title': page_path.stem,
                   'path': str(page_path),
                   'content': content[:500]  # First 500 chars
               })

       return {
           'query': query,
           'results': results,
           'count': len(results)
       }
   ```
2. Add route to wiki-service.py:
   ```python
   if parsed_path.path == '/api/agent/query':
       query = parsed_path.query.get('q', '')
       result = self.server.query_wiki(query)
       self.send_response(200)
       self.send_header('Content-Type', 'application/json')
       self.end_headers()
       self.wfile.write(json.dumps(result).encode())
       return
   ```
3. Deploy to CT120 and test:
   ```bash
   curl "http://localhost:8082/api/agent/query?q=grid infrastructure"
   ```

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- curl -s 'http://localhost:8082/api/agent/query?q=grid infrastructure' | python3 -m json.tool"
```

**Output Files**:
- `/srv/grid-wiki/wiki-service.py` (updated)

---

## Task 9.2: Wiki as Agent Memory

**Target**: Wiki records agent interactions

**Steps**:
1. Create agent interaction log: `/srv/grid-wiki/wiki/AGENT-INTERACTIONS.md`
   ```markdown
   ---
   title: "Agent Interactions"
   type: log
   last_updated: "2026-06-28T00:00:00Z"
   ---

   # Agent Interactions

   ## Discovery Scans
   | Timestamp | Agent | Action | Result |
   | --- | --- | --- | --- |
   | 2026-06-28 01:00 | Hermes | Discovery scan | 10 containers scanned, 15 services discovered |
   | 2026-06-28 02:00 | Hermes | Drift detection | 2 new containers, 1 IP change |

   ## Maintenance Actions
   | Timestamp | Agent | Issue | Resolution |
   | --- | --- | --- | --- |
   | 2026-06-28 04:00 | Hermes | Prometheus target down | Restarted service, target up |

   ## Change Approvals
   | Timestamp | Agent | Change | Status |
   | --- | --- | --- | --- |
   | 2026-06-28 03:00 | Hermes | Auto-approved change | Approved |
   ```

2. Update wiki-service.py to log agent interactions:
   ```python
   def log_agent_interaction(self, agent: str, action: str, result: str):
       """Log agent interaction to wiki."""
       log_path = self.root / 'wiki' / 'AGENT-INTERACTIONS.md'
       timestamp = datetime.datetime.now().isoformat()

       with open(log_path, 'a') as f:
           f.write(f"\n| {timestamp} | {agent} | {action} | {result} |\n")

       return True
   ```
3. Deploy to CT120 and test

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- cat /srv/grid-wiki/wiki/AGENT-INTERACTIONS.md"
```

**Output Files**:
- `/srv/grid-wiki/wiki/AGENT-INTERACTIONS.md`
- `/srv/grid-wiki/wiki-service.py` (updated)

---

## Task 9.3: Query Patterns for Agents

**Target**: Document query patterns for agents

**Steps**:
1. Create agent query patterns: `/srv/grid-wiki/wiki/AGENT-QUERY-PATTERNS.md`
   ```markdown
   ---
   title: "Agent Query Patterns"
   type: documentation
   last_updated: "2026-06-28T00:00:00Z"
   ---

   # Agent Query Patterns

   ## Wiki Query Patterns

   ### What services are running?
   **Query**: `grid infrastructure overview`
   **Expected Result**: Returns GRID Infrastructure Overview page with container list

   ### Is <service> monitored?
   **Query**: `prometheus monitoring <service>`
   **Expected Result**: Returns service entity page with monitoring status

   ### What changed recently?
   **Query**: `drift report recent`
   **Expected Result**: Returns latest drift report with changes found

   ### How do I manage <service>?
   **Query**: `<service> operations`
   **Expected Result**: Returns service entity page with operational notes

   ### Is <service> healthy?
   **Query**: `<service> health`
   **Expected Result**: Returns monitoring status page with service health

   ## Agent Interaction Patterns

   ### Discovery Scan
   1. Read `PROJECT-MANIFEST.md` for current goal
   2. Run discovery scan script
   3. Generate snapshots in `/srv/grid-wiki/raw/live-state/`
   4. Run drift detection
   5. Log interaction in `AGENT-INTERACTIONS.md`

   ### Maintenance Worker
   1. Read open maintenance cards
   2. Match issue to rule in `maintenance/rules/`
   3. Apply auto-fix if available
   4. Move card to resolved if fixed
   5. Log interaction in `AGENT-INTERACTIONS.md`

   ### Change Review
   1. Read pending change cards
   2. Review evidence and impact
   3. Approve or reject change
   4. Move card to approved/rejected
   5. Log interaction in `AGENT-INTERACTIONS.md`
   ```

2. Deploy to CT120 and test

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- cat /srv/grid-wiki/wiki/AGENT-QUERY-PATTERNS.md"
```

**Output Files**:
- `/srv/grid-wiki/wiki/AGENT-QUERY-PATTERNS.md`

---

## Task 9.4: Wiki Pages Structured for Agent Parsing

**Target**: Ensure wiki pages have structured data for agents

**Steps**:
1. Update entity page template to include structured data:
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

   ## Agent Instructions
   ### How to Use This Page
   Agents should read this page to understand the service. Key data for agent tasks:
   - **Proxmox API**: Use MCP actions via port 8084
   - **Wiki**: Access via /api/wiki-index for structured data
   - **Monitoring**: Check /api/monitoring-status for live status
   - **Change Management**: Submit changes through Kanban before acting

   ### Data Access
   | Resource | Endpoint | Purpose |
   |----------|----------|---------|
   | Wiki Index | /api/wiki-index | Structured wiki content list |
   | Wiki Pages | /wiki-content/{path} | Raw markdown files |
   | Monitoring | /api/monitoring-status | Service health data |
   | Proxmox MCP | /api/proxmox/{action} | Container management |

   ## Change History
   | Date | Change | By | Notes |
   | --- | --- | --- | --- |
   ```

2. Update existing entity pages to include agent instructions
3. Deploy to CT120 and test

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- cat /srv/grid-wiki/wiki/GRID-Infrastructure-Overview.md | grep -A 20 'Agent Instructions'"
```

**Output Files**:
- `/srv/grid-wiki/wiki-templates/service-entity.md` (updated)
- `/srv/grid-wiki/wiki/*.md` (updated)

---

## Task 9.5: Agent Interactions Recorded in Wiki

**Target**: Agent interactions logged in wiki

**Steps**:
1. Update wiki-service.py to log all agent interactions:
   ```python
   def log_agent_interaction(self, agent: str, action: str, result: str):
       """Log agent interaction to wiki."""
       log_path = self.root / 'wiki' / 'AGENT-INTERACTIONS.md'
       timestamp = datetime.datetime.now().isoformat()

       with open(log_path, 'a') as f:
           f.write(f"\n| {timestamp} | {agent} | {action} | {result} |\n")

       return True
   ```
2. Update cron jobs to log interactions:
   - Update `grid-wiki-discovery` to log interaction
   - Update `grid-wiki-maintenance-worker` to log interaction
   - Update `grid-wiki-agent-review` to log interaction
3. Deploy to CT120 and test

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- cat /srv/grid-wiki/wiki/AGENT-INTERACTIONS.md"
```

**Output Files**:
- `/srv/grid-wiki/wiki/AGENT-INTERACTIONS.md` (updated)
- `/srv/grid-wiki/cron/cron-jobs.yaml` (updated)

---

## Task 9.6: Update Project Manifest

**Target**: Mark Phase 9 complete in PROJECT-MANIFEST.md

**Steps**:
1. Read current `PROJECT-MANIFEST.md`
2. Update `current_goal` to "PROJECT COMPLETE"
3. Add Phase 9 to `completed_phases` list
4. Commit changes: `git add . && git commit -m "Phase 9 complete"`

**Verification**:
```bash
cat /Users/tron/grid-network-wiki-tool/PROJECT-MANIFEST.md | grep -A 2 "current_goal"
```

**Output Files**:
- `/Users/tron/grid-network-wiki-tool/PROJECT-MANIFEST.md` (updated)

---

## Task 9.7: Document Phase 9 Completion

**Target**: Create Phase 9 completion report

**Steps**:
1. Create `/srv/grid-wiki/raw/live-state/phase-9-completion.md`
2. Document:
   - Agent query interface functional
   - Wiki serves as agent memory
   - Query patterns documented
   - Wiki pages structured for agent parsing
   - Agent interactions recorded in wiki
3. Commit to git: `git add . && git commit -m "Phase 9 completion report"`

**Verification**:
```bash
cat /srv/grid-wiki/raw/live-state/phase-9-completion.md
```

**Output Files**:
- `/srv/grid-wiki/raw/live-state/phase-9-completion.md`

---

## Summary

**Total Tasks**: 7
**Estimated Time**: 2-3 hours
**Files Created**: 2
**Directories Created**: 0
**Agent Features**: 5

**PROJECT COMPLETE**

---

## Final Deliverables

### Part 1: Global Architecture Specification

**File**: `/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki tool/ARCHITECTURE_SPECIFICATION.md`

Contains:
- Target Tech Stack
- Directory Structure
- Data Models / Schema
- System Boundaries & Contracts
- System Architecture Diagram
- Key Design Principles
- Security Considerations
- Performance Considerations
- Deployment Strategy
- Maintenance & Operations
- Success Metrics
- Future Enhancements

### Part 2: Atomic Task & Document Chunks

**Files Created**:

1. `/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki tool/PHASE-0-Foundation.md`
   - 9 tasks, 2-3 hours
   - Wiki service and directory structure

2. `/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki tool/PHASE-1-Discovery-Engine.md`
   - 8 tasks, 4-6 hours
   - Discovery scanner, drift detection, auto-discovery, cron jobs

3. `/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki tool/PHASE-2-Wiki-Engine.md`
   - 12 tasks, 3-4 hours
   - Wiki templates, entity pages, sites overview

4. `/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki tool/PHASE-3-Dashboard.md`
   - 8 tasks, 3-4 hours
   - Dashboard UI, API client, sidebar, main logic

5. `/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki tool/PHASE-4-Methodology-Integration.md`
   - 8 tasks, 2-3 hours
   - Project Manifest, Active Tasks, AGENTS.md, goal progress tracker

6. `/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki tool/PHASE-5-Monitoring-Auto-Setup.md`
   - 7 tasks, 2-3 hours
   - Prometheus, Uptime Kuma, Blackbox, Grafana auto-configuration

7. `/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki tool/PHASE-6-Wiki-Export-Accessibility.md`
   - 6 tasks, 1-2 hours
   - Wiki viewer, export feature, direct file access

8. `/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki tool/PHASE-7-Maintenance-Auto-Resolution.md`
   - 5 tasks, 3-4 hours
   - 8 best-practice rules, maintenance worker logic

9. `/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki tool/PHASE-8-Change-Kanban-Workflow.md`
   - 6 tasks, 2-3 hours
   - Change submission, kanban boards, user flagging

10. `/Users/tron/Documents/Obsidian Vault/Projects/GRID Network Wiki tool/PHASE-9-Agent-Knowledge-Base-Enhancement.md`
    - 7 tasks, 2-3 hours
    - Agent query interface, wiki as agent memory, query patterns

**Total**:
- 9 phases
- 67 tasks
- 25-35 hours estimated
- 10+ files created
- 2+ directories created
- 8 monitoring rules
- 6 cron jobs
- 8 dashboard sections
- 6 kanban boards

**Next Steps**:
1. Review all phase documents
2. Prioritize phases based on project needs
3. Execute phases sequentially
4. Deploy to CT120 after each phase
5. Verify with browser QA
6. Update PROJECT-MANIFEST.md after each phase
7. Create completion reports for each phase