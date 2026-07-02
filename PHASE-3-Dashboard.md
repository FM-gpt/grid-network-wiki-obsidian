# Phase 3: Dashboard — Browse, Search, and Visualize

**Goal**: Build lightweight dashboard for browsing wiki, viewing kanban boards, and monitoring wiki health.

**Estimated Effort**: 3-4 hours

**Dependencies**: Phase 2 complete

**Acceptance Criteria**:
- Dashboard index.html created
- Wiki browser functional
- Kanban boards (change/maintenance) functional
- Monitoring page shows status
- Drift report viewer functional
- All dashboard sections accessible via sidebar

---

## Task 3.1: Dashboard Structure

**Target**: Create dashboard directory structure

**Steps**:
1. Create dashboard directory on CT120:
   ```bash
   ssh grid-pve "pct exec 120 -- mkdir -p /srv/grid-wiki/dashboard/{wiki,kanban,monitoring,drift,css,js,data}"
   ```
2. Create dashboard index.html:
   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
     <meta charset="UTF-8">
     <meta name="viewport" content="width=device-width, initial-scale=1.0">
     <title>GRID Network Wiki Dashboard</title>
     <link rel="stylesheet" href="css/dashboard.css">
   </head>
   <body>
     <div class="dashboard-container">
       <!-- Sidebar -->
       <aside class="sidebar" id="sidebar">
         <div class="sidebar-header">
           <h1>GRID Wiki</h1>
           <button class="sidebar-toggle" id="sidebarToggle">☰</button>
         </div>
         <nav class="sidebar-nav">
           <a href="index.html" class="nav-link active">📊 Dashboard</a>
           <a href="monitoring.html" class="nav-link">📈 Monitoring</a>
           <a href="drift.html" class="nav-link">🔍 Drift Reports</a>
           <a href="kanban/change.html" class="nav-link">📋 Change Kanban</a>
           <a href="kanban/maintenance.html" class="nav-link">🔧 Maintenance</a>
           <a href="wiki-browser.html" class="nav-link">📖 Wiki Browser</a>
           <a href="sites.html" class="nav-link">🌐 Sites Overview</a>
           <a href="agents.html" class="nav-link">🤖 Agent Protocol</a>
           <a href="settings.html" class="nav-link">⚙️ Settings</a>
         </nav>
       </aside>

       <!-- Main Content -->
       <main class="main-content">
         <header class="top-bar">
           <h2 id="pageTitle">Dashboard</h2>
           <div class="top-bar-actions">
             <button id="refreshBtn" class="btn btn-primary">🔄 Refresh</button>
             <button id="exportBtn" class="btn btn-secondary">📥 Export Wiki</button>
           </div>
         </header>

         <div class="dashboard-content" id="dashboardContent">
           <!-- Content loaded dynamically -->
         </div>
       </main>
     </div>

     <script src="js/api.js"></script>
     <script src="js/sidebar.js"></script>
     <script src="js/dashboard.js"></script>
   </body>
   </html>
   ```
3. Save to `/srv/grid-wiki/dashboard/index.html`
4. Verify file created:
   ```bash
   ssh grid-pve "pct exec 120 -- ls -la /srv/grid-wiki/dashboard/"
   ```

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- cat /srv/grid-wiki/dashboard/index.html | head -30"
```

**Output Files**:
- `/srv/grid-wiki/dashboard/index.html`

---

## Task 3.2: Dashboard CSS

**Target**: Create dashboard.css with responsive design

**Steps**:
1. Create dashboard.css:
   ```css
   /* GRID Network Wiki Dashboard Styles */

   :root {
     --primary-color: #2563eb;
     --secondary-color: #64748b;
     --success-color: #22c55e;
     --warning-color: #f59e0b;
     --danger-color: #ef4444;
     --bg-color: #f8fafc;
     --sidebar-bg: #1e293b;
     --sidebar-text: #f1f5f9;
     --card-bg: #ffffff;
     --text-color: #0f172a;
     --border-color: #e2e8f0;
   }

   * {
     margin: 0;
     padding: 0;
     box-sizing: border-box;
   }

   body {
     font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
     background-color: var(--bg-color);
     color: var(--text-color);
     line-height: 1.6;
   }

   .dashboard-container {
     display: flex;
     min-height: 100vh;
   }

   /* Sidebar */
   .sidebar {
     width: 250px;
     background-color: var(--sidebar-bg);
     color: var(--sidebar-text);
     padding: 1rem;
     transition: transform 0.3s ease;
     position: fixed;
     height: 100vh;
     overflow-y: auto;
   }

   .sidebar-header {
     display: flex;
     justify-content: space-between;
     align-items: center;
     margin-bottom: 1.5rem;
   }

   .sidebar-header h1 {
     font-size: 1.5rem;
     font-weight: 700;
   }

   .sidebar-toggle {
     background: none;
     border: none;
     color: var(--sidebar-text);
     font-size: 1.5rem;
     cursor: pointer;
   }

   .sidebar-nav {
     list-style: none;
   }

   .nav-link {
     display: block;
     padding: 0.75rem 1rem;
     color: var(--sidebar-text);
     text-decoration: none;
     border-radius: 0.5rem;
     margin-bottom: 0.5rem;
     transition: background-color 0.2s;
   }

   .nav-link:hover {
     background-color: rgba(255, 255, 255, 0.1);
   }

   .nav-link.active {
     background-color: var(--primary-color);
   }

   /* Main Content */
   .main-content {
     flex: 1;
     margin-left: 250px;
     padding: 2rem;
   }

   .top-bar {
     display: flex;
     justify-content: space-between;
     align-items: center;
     margin-bottom: 2rem;
   }

   .top-bar h2 {
     font-size: 2rem;
     font-weight: 700;
   }

   .top-bar-actions {
     display: flex;
     gap: 1rem;
   }

   .btn {
     padding: 0.75rem 1.5rem;
     border: none;
     border-radius: 0.5rem;
     font-weight: 600;
     cursor: pointer;
     transition: opacity 0.2s;
   }

   .btn:hover {
     opacity: 0.9;
   }

   .btn-primary {
     background-color: var(--primary-color);
     color: white;
   }

   .btn-secondary {
     background-color: var(--secondary-color);
     color: white;
   }

   .dashboard-content {
     display: grid;
     grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
     gap: 1.5rem;
   }

   .card {
     background-color: var(--card-bg);
     border-radius: 0.75rem;
     padding: 1.5rem;
     box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
   }

   .card h3 {
     font-size: 1.25rem;
     font-weight: 600;
     margin-bottom: 1rem;
   }

   /* Responsive */
   @media (max-width: 768px) {
     .sidebar {
       transform: translateX(-100%);
     }

     .sidebar.open {
       transform: translateX(0);
     }

     .main-content {
       margin-left: 0;
     }
   }
   ```
2. Save to `/srv/grid-wiki/dashboard/css/dashboard.css`
3. Verify file created:
   ```bash
   ssh grid-pve "pct exec 120 -- ls -la /srv/grid-wiki/dashboard/css/"
   ```

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- cat /srv/grid-wiki/dashboard/css/dashboard.css | head -50"
```

**Output Files**:
- `/srv/grid-wiki/dashboard/css/dashboard.css`

---

## Task 3.3: API Client (api.js)

**Target**: Create API client for dashboard

**Steps**:
1. Create api.js:
   ```javascript
   // GRID Network Wiki API Client

   class WikiAPI {
     static async getWikiIndex() {
       const response = await fetch('/api/wiki-index');
       return await response.json();
     }

     static async getWikiPage(slug) {
       const response = await fetch(`/api/wiki/${slug}`);
       return await response.text();
     }

     static async searchWiki(query, limit = 10) {
       const response = await fetch(`/api/wiki/search?query=${encodeURIComponent(query)}&limit=${limit}`);
       return await response.json();
     }

     static async getActiveTasks() {
       const response = await fetch('/api/active-tasks');
       return await response.json();
     }

     static async getMonitoringStatus() {
       const response = await fetch('/api/monitoring-status');
       return await response.json();
     }

     static async getDriftReport(date) {
       const response = await fetch(`/api/drift/${date}`);
       return await response.json();
     }

     static async getDriftLatest() {
       const response = await fetch('/api/drift/latest');
       return await response.json();
     }

     static async getKanbanChanges() {
       const response = await fetch('/api/kanban/changes');
       return await response.json();
     }

     static async getKanbanMaintenance() {
       const response = await fetch('/api/kanban/maintenance');
       return await response.json();
     }

     static async approveChange(cardId) {
       const response = await fetch(`/api/kanban/changes/${cardId}/approve`, {
         method: 'POST'
       });
       return await response.json();
     }

     static async rejectChange(cardId) {
       const response = await fetch(`/api/kanban/changes/${cardId}/reject`, {
         method: 'POST'
       });
       return await response.json();
     }

     static async resolveMaintenance(cardId) {
       const response = await fetch(`/api/kanban/maintenance/${cardId}/resolve`, {
         method: 'POST'
       });
       return await response.json();
     }

     static async chatQuery(message) {
       const response = await fetch('/api/chat/query', {
         method: 'POST',
         headers: {
           'Content-Type': 'application/json'
         },
         body: JSON.stringify({ message })
       });
       return await response.json();
     }

     static async chatAction(message) {
       const response = await fetch('/api/chat/action', {
         method: 'POST',
         headers: {
           'Content-Type': 'application/json'
         },
         body: JSON.stringify({ message })
       });
       return await response.json();
     }

     static async syncVaultToOverlay() {
       const response = await fetch('/api/sync/run', {
         method: 'POST'
       });
       return await response.json();
     }

     static async getSettings() {
       const response = await fetch('/api/settings');
       return await response.json();
     }

     static async exportWiki() {
       const response = await fetch('/api/wiki-export');
       return await response.blob();
     }
   }

   // Export for use in other modules
   window.WikiAPI = WikiAPI;
   ```
2. Save to `/srv/grid-wiki/dashboard/js/api.js`
3. Verify file created:
   ```bash
   ssh grid-pve "pct exec 120 -- ls -la /srv/grid-wiki/dashboard/js/"
   ```

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- cat /srv/grid-wiki/dashboard/js/api.js | head -50"
```

**Output Files**:
- `/srv/grid-wiki/dashboard/js/api.js`

---

## Task 3.4: Sidebar Navigation (sidebar.js)

**Target**: Create sidebar navigation component

**Steps**:
1. Create sidebar.js:
   ```javascript
   // Sidebar Navigation

   class Sidebar {
     constructor() {
       this.sidebar = document.getElementById('sidebar');
       this.toggleBtn = document.getElementById('sidebarToggle');
       this.navLinks = document.querySelectorAll('.nav-link');
       this.isOpen = false;
     }

     init() {
       this.setupEventListeners();
       this.loadState();
     }

     setupEventListeners() {
       this.toggleBtn.addEventListener('click', () => this.toggle());
       this.navLinks.forEach(link => {
         link.addEventListener('click', (e) => {
           e.preventDefault();
           this.navigateTo(link);
         });
       });
     }

     toggle() {
       this.isOpen = !this.isOpen;
       this.sidebar.classList.toggle('open', this.isOpen);
       this.saveState();
     }

     navigateTo(link) {
       // Update active state
       this.navLinks.forEach(l => l.classList.remove('active'));
       link.classList.add('active');

       // Navigate to page
       const href = link.getAttribute('href');
       if (href) {
         window.location.href = href;
       }
     }

     loadState() {
       const savedState = localStorage.getItem('grid-wiki-sidebar-open');
       this.isOpen = savedState === 'true';
       this.sidebar.classList.toggle('open', this.isOpen);
     }

     saveState() {
       localStorage.setItem('grid-wiki-sidebar-open', this.isOpen);
     }
   }

   // Initialize sidebar
   document.addEventListener('DOMContentLoaded', () => {
     const sidebar = new Sidebar();
     sidebar.init();
   });
   ```
2. Save to `/srv/grid-wiki/dashboard/js/sidebar.js`
3. Verify file created:
   ```bash
   ssh grid-pve "pct exec 120 -- ls -la /srv/grid-wiki/dashboard/js/"
   ```

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- cat /srv/grid-wiki/dashboard/js/sidebar.js | head -50"
```

**Output Files**:
- `/srv/grid-wiki/dashboard/js/sidebar.js`

---

## Task 3.5: Dashboard Main Logic (dashboard.js)

**Target**: Create dashboard main application logic

**Steps**:
1. Create dashboard.js:
   ```javascript
   // Dashboard Main Application

   class Dashboard {
     constructor() {
       this.state = {
         currentView: 'index',
         sidebarOpen: true,
         onboardingComplete: false
       };
       this.content = document.getElementById('dashboardContent');
       this.pageTitle = document.getElementById('pageTitle');
     }

     init() {
       this.loadState();
       this.renderSidebar();
       this.renderCurrentView();
       this.setupEventListeners();
     }

     loadState() {
       const savedState = localStorage.getItem('grid-wiki-dashboard-state');
       if (savedState) {
         this.state = JSON.parse(savedState);
       }
     }

     saveState() {
       localStorage.setItem('grid-wiki-dashboard-state', JSON.stringify(this.state));
     }

     renderSidebar() {
       // Sidebar is rendered in sidebar.js
     }

     renderCurrentView() {
       switch (this.state.currentView) {
         case 'index':
           this.renderDashboardIndex();
           break;
         case 'monitoring':
           this.renderMonitoring();
           break;
         case 'drift':
           this.renderDrift();
           break;
         case 'kanban':
           this.renderKanban();
           break;
         case 'wiki':
           this.renderWikiBrowser();
           break;
         case 'sites':
           this.renderSites();
           break;
         case 'agents':
           this.renderAgents();
           break;
         case 'settings':
           this.renderSettings();
           break;
         default:
           this.renderDashboardIndex();
       }
     }

     renderDashboardIndex() {
       this.pageTitle.textContent = 'Dashboard';
       this.content.innerHTML = `
         <div class="dashboard-content">
           <div class="card">
             <h3>Active Tasks</h3>
             <p id="activeTasksCount">Loading...</p>
           </div>
           <div class="card">
             <h3>Monitoring Status</h3>
             <p id="monitoringStatus">Loading...</p>
           </div>
           <div class="card">
             <h3>Drift Reports</h3>
             <p id="driftReports">Loading...</p>
           </div>
           <div class="card">
             <h3>Wiki Pages</h3>
             <p id="wikiPages">Loading...</p>
           </div>
         </div>
       `;

       // Load data
       this.loadDashboardData();
     }

     async loadDashboardData() {
       try {
         const [tasks, monitoring, drift, wiki] = await Promise.all([
           WikiAPI.getActiveTasks(),
           WikiAPI.getMonitoringStatus(),
           WikiAPI.getDriftLatest(),
           WikiAPI.getWikiIndex()
         ]);

         document.getElementById('activeTasksCount').textContent = `${tasks.length} active tasks`;
         document.getElementById('monitoringStatus').textContent = 'Prometheus: Up, Uptime Kuma: Configured';
         document.getElementById('driftReports').textContent = `${drift.pending_changes} pending changes`;
         document.getElementById('wikiPages').textContent = `${wiki.pages.length} wiki pages`;
       } catch (error) {
         console.error('Error loading dashboard data:', error);
       }
     }

     renderMonitoring() {
       this.pageTitle.textContent = 'Monitoring';
       this.content.innerHTML = `
         <div class="card">
           <h3>Service Status</h3>
           <p>Monitoring status will be loaded here...</p>
         </div>
       `;
     }

     renderDrift() {
       this.pageTitle.textContent = 'Drift Reports';
       this.content.innerHTML = `
         <div class="card">
           <h3>Drift Reports</h3>
           <p>Drift reports will be loaded here...</p>
         </div>
       `;
     }

     renderKanban() {
       this.pageTitle.textContent = 'Kanban Boards';
       this.content.innerHTML = `
         <div class="card">
           <h3>Change Kanban</h3>
           <p>Change cards will be loaded here...</p>
         </div>
         <div class="card">
           <h3>Maintenance Kanban</h3>
           <p>Maintenance cards will be loaded here...</p>
         </div>
       `;
     }

     renderWikiBrowser() {
       this.pageTitle.textContent = 'Wiki Browser';
       this.content.innerHTML = `
         <div class="card">
           <h3>Wiki Browser</h3>
           <p>Wiki browser will be loaded here...</p>
         </div>
       `;
     }

     renderSites() {
       this.pageTitle.textContent = 'Sites Overview';
       this.content.innerHTML = `
         <div class="card">
           <h3>Sites Overview</h3>
           <p>Sites overview will be loaded here...</p>
         </div>
       `;
     }

     renderAgents() {
       this.pageTitle.textContent = 'Agent Protocol';
       this.content.innerHTML = `
         <div class="card">
           <h3>Agent Protocol</h3>
           <p>Agent protocol documentation will be loaded here...</p>
         </div>
       `;
     }

     renderSettings() {
       this.pageTitle.textContent = 'Settings';
       this.content.innerHTML = `
         <div class="card">
           <h3>Settings</h3>
           <p>Settings will be loaded here...</p>
         </div>
       `;
     }

     setupEventListeners() {
       document.getElementById('refreshBtn').addEventListener('click', () => {
         this.loadDashboardData();
       });

       document.getElementById('exportBtn').addEventListener('click', () => {
         WikiAPI.exportWiki().then(blob => {
           const url = URL.createObjectURL(blob);
           const a = document.createElement('a');
           a.href = url;
           a.download = 'grid-wiki-export.tar.gz';
           a.click();
           URL.revokeObjectURL(url);
         });
       });
     }

     navigateTo(view) {
       this.state.currentView = view;
       this.saveState();
       this.renderCurrentView();
     }
   }

   // Initialize dashboard
   document.addEventListener('DOMContentLoaded', () => {
     const dashboard = new Dashboard();
     dashboard.init();
   });
   ```
2. Save to `/srv/grid-wiki/dashboard/js/dashboard.js`
3. Verify file created:
   ```bash
   ssh grid-pve "pct exec 120 -- ls -la /srv/grid-wiki/dashboard/js/"
   ```

**Verification**:
```bash
ssh grid-pve "pct exec 120 -- cat /srv/grid-wiki/dashboard/js/dashboard.js | head -50"
```

**Output Files**:
- `/srv/grid-wiki/dashboard/js/dashboard.js`

---

## Task 3.6: Deploy Dashboard to CT120

**Target**: Deploy all dashboard files to CT120

**Steps**:
1. Sync dashboard files to CT120:
   ```bash
   rsync -avz --delete \
     /Users/tron/grid-network-wiki-tool/dashboard/ \
     grid-pve:/srv/grid-wiki/dashboard/
   ```
2. Verify files deployed:
   ```bash
   ssh grid-pve "pct exec 120 -- ls -la /srv/grid-wiki/dashboard/"
   ```
3. Test dashboard access:
   ```bash
   curl -s http://localhost:8082/index.html | head -30
   ```
4. Verify Caddy route:
   ```bash
   curl -I https://wiki.grid
   ```

**Verification**:
- Dashboard loads in browser
- All CSS and JS files accessible
- No 404 errors

**Output Files**:
- `/srv/grid-wiki/dashboard/` (deployed to CT120)

---

## Task 3.7: Update Project Manifest

**Target**: Mark Phase 3 complete in PROJECT-MANIFEST.md

**Steps**:
1. Read current `PROJECT-MANIFEST.md`
2. Update `current_goal` to "Phase 4: Methodology Integration & Project OS"
3. Add Phase 3 to `completed_phases` list
4. Commit changes: `git add . && git commit -m "Phase 3 complete"`

**Verification**:
```bash
cat /Users/tron/grid-network-wiki-tool/PROJECT-MANIFEST.md | grep -A 2 "current_goal"
```

**Output Files**:
- `/Users/tron/grid-network-wiki-tool/PROJECT-MANIFEST.md` (updated)

---

## Task 3.8: Document Phase 3 Completion

**Target**: Create Phase 3 completion report

**Steps**:
1. Create `/srv/grid-wiki/raw/live-state/phase-3-completion.md`
2. Document:
   - Dashboard index.html created
   - CSS styles created
   - API client created
   - Sidebar navigation created
   - Dashboard main logic created
   - All dashboard sections accessible
3. Commit to git: `git add . && git commit -m "Phase 3 completion report"`

**Verification**:
```bash
cat /srv/grid-wiki/raw/live-state/phase-3-completion.md
```

**Output Files**:
- `/srv/grid-wiki/raw/live-state/phase-3-completion.md`

---

## Summary

**Total Tasks**: 8
**Estimated Time**: 3-4 hours
**Files Created**: 5
**Directories Created**: 1
**Dashboard Sections**: 8

**Next Phase**: Phase 4 — Methodology Integration & Project OS