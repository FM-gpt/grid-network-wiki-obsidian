# Phase 4: Methodology Integration & Project OS

**Goal**: Integrate "Project Manifest + State Machine" model into GRID Wiki. Turns wiki into a Project Operating System that manages the management of the GRID Wiki itself.

**Estimated Effort**: 2-3 hours

**Dependencies**: Phase 3 complete

**Acceptance Criteria**:
- PROJECT-MANIFEST.md rendered as "Project Status" widget on dashboard
- ACTIVE-TASKS.md rendered as "Development Board" on dashboard
- AGENTS.md acts as rulebook for agents
- Multi-site alignment working (GRID + FMSA as separate projects)
- Dashboard shows goal progress tracker

---

## Task 4.1: Manifest as "Project Brain"

**Target**: Render PROJECT-MANIFEST.md as Project Status widget

**Steps**:
1. Update dashboard.js to render PROJECT-MANIFEST.md:
   ```javascript
   async renderProjectStatus() {
     try {
       const response = await fetch('/api/manifest');
       const manifest = await response.json();

       this.content.innerHTML = `
         <div class="card">
           <h3>Project Status</h3>
           <div class="project-status">
             <div class="status-item">
               <strong>Current Goal:</strong>
               <p>${manifest.current_goal}</p>
             </div>
             <div class="status-item">
               <strong>Scope Boundaries:</strong>
               <p>${manifest.scope_boundaries.join(', ')}</p>
             </div>
             <div class="status-item">
               <strong>Active Tasks:</strong>
               <p>${manifest.active_tasks.length} tasks</p>
             </div>
             <div class="status-item">
               <strong>Completed Phases:</strong>
               <p>${manifest.completed_phases.length} phases</p>
             </div>
           </div>
         </div>
       `;
     } catch (error) {
       console.error('Error loading project status:', error);
     }
   }
   ```
2. Add API endpoint to wiki-service.py:
   ```python
   def get_manifest(self):
       """Get PROJECT-MANIFEST.md content."""
       manifest_path = self.root / 'PROJECT-MANIFEST.md'
       if manifest_path.exists():
           return manifest_path.read_text()
       return "No manifest found."
   ```
3. Add route to wiki-service.py:
   ```python
   def do_GET(self):
       parsed_path = urlparse(self.path)
       if parsed_path.path == '/api/manifest':
           self.send_response(200)
           self.send_header('Content-Type', 'text/plain')
           self.end_headers()
           self.wfile.write(self.server.get_manifest().encode())
           return
       # ... existing routes
   ```
4. Deploy to CT120 and test:
   ```bash
   curl http://localhost:8082/api/manifest
   ```

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- curl -s http://localhost:8082/api/manifest"
```

**Output Files**:
- `/srv/grid-wiki/dashboard/js/dashboard.js` (updated)
- `/srv/grid-wiki/wiki-service.py` (updated)

---

## Task 4.2: Active Tasks as "The Lock"

**Target**: Render ACTIVE-TASKS.md as Development Board on dashboard

**Steps**:
1. Update dashboard.js to render ACTIVE-TASKS.md:
   ```javascript
   async renderActiveTasks() {
     try {
       const response = await fetch('/api/active-tasks');
       const tasks = await response.json();

       this.content.innerHTML = `
         <div class="card">
           <h3>Active Tasks</h3>
           <div class="kanban-board">
             <div class="kanban-column">
               <h4>Parked</h4>
               <div class="kanban-cards">
                 ${tasks.filter(t => t.status === 'Parked').map(task => `
                   <div class="kanban-card">
                     <strong>${task.id}</strong>
                     <p>${task.description}</p>
                   </div>
                 `).join('')}
               </div>
             </div>
             <div class="kanban-column">
               <h4>In Progress</h4>
               <div class="kanban-cards">
                 ${tasks.filter(t => t.status === 'In Progress').map(task => `
                   <div class="kanban-card">
                     <strong>${task.id}</strong>
                     <p>${task.description}</p>
                   </div>
                 `).join('')}
               </div>
             </div>
             <div class="kanban-column">
               <h4>Completed</h4>
               <div class="kanban-cards">
                 ${tasks.filter(t => t.status === 'Completed').map(task => `
                   <div class="kanban-card">
                     <strong>${task.id}</strong>
                     <p>${task.description}</p>
                   </div>
                 `).join('')}
               </div>
             </div>
           </div>
         </div>
       `;
     } catch (error) {
       console.error('Error loading active tasks:', error);
     }
   }
   ```
2. Update dashboard.js to call renderActiveTasks() in renderDashboardIndex()
3. Deploy to CT120 and test:
   ```bash
   curl -s http://localhost:8082/api/active-tasks
   ```

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- curl -s http://localhost:8082/api/active-tasks"
```

**Output Files**:
- `/srv/grid-wiki/dashboard/js/dashboard.js` (updated)

---

## Task 4.3: AGENTS.md as "Protocol" Layer

**Target**: AGENTS.md acts as rulebook for agents

**Steps**:
1. Create AGENTS.md endpoint:
   ```python
   def get_agents_protocol(self):
       """Get AGENTS.md content."""
       agents_path = self.root / 'AGENTS.md'
       if agents_path.exists():
           return agents_path.read_text()
       return "No agents protocol found."
   ```
2. Add route to wiki-service.py:
   ```python
   if parsed_path.path == '/api/agents':
       self.send_response(200)
       self.send_header('Content-Type', 'text/plain')
       self.end_headers()
       self.wfile.write(self.server.get_agents_protocol().encode())
       return
   ```
3. Update dashboard.js to render AGENTS.md:
   ```javascript
   async renderAgentsProtocol() {
     try {
       const response = await fetch('/api/agents');
       const protocol = await response.text();

       this.content.innerHTML = `
         <div class="card">
           <h3>Agent Protocol</h3>
           <div class="protocol-content">
             <pre>${protocol}</pre>
           </div>
         </div>
       `;
     } catch (error) {
       console.error('Error loading agents protocol:', error);
     }
   }
   ```
4. Deploy to CT120 and test:
   ```bash
   curl -s http://localhost:8082/api/agents
   ```

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- curl -s http://localhost:8082/api/agents"
```

**Output Files**:
- `/srv/grid-wiki/wiki-service.py` (updated)
- `/srv/grid-wiki/dashboard/js/dashboard.js` (updated)

---

## Task 4.4: Goal Progress Tracker

**Target**: Add visual goal progress tracker to dashboard

**Steps**:
1. Update dashboard.js to render goal progress:
   ```javascript
   async renderGoalProgress() {
     try {
       const response = await fetch('/api/manifest');
       const manifest = await response.json();

       const totalPhases = 9; // Total phases in project plan
       const completedPhases = manifest.completed_phases.length;
       const progress = (completedPhases / totalPhases) * 100;

       this.content.innerHTML = `
         <div class="card">
           <h3>Goal Progress</h3>
           <div class="progress-container">
             <div class="progress-bar">
               <div class="progress-fill" style="width: ${progress}%"></div>
             </div>
             <p class="progress-text">${completedPhases}/${totalPhases} phases complete (${progress.toFixed(0)}%)</p>
           </div>
         </div>
       `;
     } catch (error) {
       console.error('Error loading goal progress:', error);
     }
   }
   ```
2. Call renderGoalProgress() in renderDashboardIndex()
3. Deploy to CT120 and test

**Verification**:
- Goal progress bar displays correctly
- Progress percentage matches completed phases

**Output Files**:
- `/srv/grid-wiki/dashboard/js/dashboard.js` (updated)

---

## Task 4.5: Multi-Site Alignment

**Target**: GRID and FMSA as separate projects under umbrella

**Steps**:
1. Create SITE-INFRA.md for GRID:
   ```markdown
   ---
   title: "GRID Site Infrastructure"
   type: site
   status: active
   last_updated: "2026-06-28T00:00:00Z"
   ---

   # GRID Site Infrastructure

   ## Overview
   GRID infrastructure includes CT120 (grid-core-01), CT131 (grid-network-wiki-01), and CT121 (grid-dev-01).

   ## Containers
   - CT120: grid-core-01 (Production)
   - CT131: grid-network-wiki-01 (Wiki)
   - CT121: grid-dev-01 (Development)

   ## Services
   - Caddy (reverse proxy)
   - Prometheus (monitoring)
   - Grafana (dashboards)
   - Uptime Kuma (uptime monitoring)
   - Wiki Service (wiki.grid)
   ```

2. Create SITE-INFRA.md for FMSA:
   ```markdown
   ---
   title: "FMSA Site Infrastructure"
   type: site
   status: active
   last_updated: "2026-06-28T00:00:00Z"
   ---

   # FMSA Site Infrastructure

   ## Overview
   FMSA infrastructure includes remote site with Proxmox host and containers.

   ## Containers
   - CT120: grid-core-01 (Production)
   - CT121: grid-dev-01 (Development)

   ## Services
   - Caddy (reverse proxy)
   - Prometheus (monitoring)
   - Grafana (dashboards)
   - Uptime Kuma (uptime monitoring)
   ```

3. Save to `/srv/grid-wiki/wiki/`
4. Update wiki index:
   ```bash
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
   | [[GRID Site Infrastructure]] | site | active | [grid, sites] |
   | [[FMSA Site Infrastructure]] | site | active | [fmsa, sites] |
   | [[Active Tasks]] | tasks | active | [grid, tasks] |
   ```

5. Deploy to CT120 and test

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- ls -la /srv/grid-wiki/wiki/ | grep -E 'SITE-INFRA|INDEX'"
```

**Output Files**:
- `/srv/grid-wiki/wiki/GRID-Site-Infrastructure.md`
- `/srv/grid-wiki/wiki/FMSA-Site-Infrastructure.md`
- `/srv/grid-wiki/wiki/INDEX.md` (updated)

---

## Task 4.6: Dashboard Integration

**Target**: Integrate Project Status, Active Tasks, and Goal Progress into dashboard

**Steps**:
1. Update dashboard.js renderDashboardIndex():
   ```javascript
   async renderDashboardIndex() {
     this.pageTitle.textContent = 'Dashboard';
     this.content.innerHTML = `
       <div class="dashboard-content">
         <div class="card">
           <h3>Project Status</h3>
           <p>Current Goal: <strong>${manifest.current_goal}</strong></p>
           <p>Active Tasks: <strong>${manifest.active_tasks.length}</strong></p>
           <p>Completed Phases: <strong>${manifest.completed_phases.length}</strong></p>
         </div>
         <div class="card">
           <h3>Goal Progress</h3>
           <div class="progress-bar">
             <div class="progress-fill" style="width: ${progress}%"></div>
           </div>
           <p>${completedPhases}/${totalPhases} phases complete</p>
         </div>
         <div class="card">
           <h3>Active Tasks</h3>
           <p>Loading active tasks...</p>
         </div>
         <div class="card">
           <h3>Monitoring Status</h3>
           <p>Loading monitoring status...</p>
         </div>
       </div>
     `;

     await this.loadDashboardData();
   }
   ```
2. Deploy to CT120 and test

**Verification**:
- Dashboard shows project status
- Goal progress tracker displays
- Active tasks count matches

**Output Files**:
- `/srv/grid-wiki/dashboard/js/dashboard.js` (updated)

---

## Task 4.7: Update Project Manifest

**Target**: Mark Phase 4 complete in PROJECT-MANIFEST.md

**Steps**:
1. Read current `PROJECT-MANIFEST.md`
2. Update `current_goal` to "Phase 5: Monitoring Auto-Setup"
3. Add Phase 4 to `completed_phases` list
4. Commit changes: `git add . && git commit -m "Phase 4 complete"`

**Verification**:
```bash
cat /Users/tron/grid-network-wiki-tool/PROJECT-MANIFEST.md | grep -A 2 "current_goal"
```

**Output Files**:
- `/Users/tron/grid-network-wiki-tool/PROJECT-MANIFEST.md` (updated)

---

## Task 4.8: Document Phase 4 Completion

**Target**: Create Phase 4 completion report

**Steps**:
1. Create `/srv/grid-wiki/raw/live-state/phase-4-completion.md`
2. Document:
   - PROJECT-MANIFEST.md rendered as Project Status widget
   - ACTIVE-TASKS.md rendered as Development Board
   - AGENTS.md acts as rulebook
   - Goal progress tracker added
   - Multi-site alignment working
3. Commit to git: `git add . && git commit -m "Phase 4 completion report"`

**Verification**:
```bash
cat /srv/grid-wiki/raw/live-state/phase-4-completion.md
```

**Output Files**:
- `/srv/grid-wiki/raw/live-state/phase-4-completion.md`

---

## Summary

**Total Tasks**: 8
**Estimated Time**: 2-3 hours
**Files Created**: 3
**Directories Created**: 0
**Dashboard Widgets**: 3

**Next Phase**: Phase 5 — Monitoring Auto-Setup