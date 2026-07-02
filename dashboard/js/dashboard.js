// Main Dashboard Application Logic
class DashboardApp {
    constructor() {
        this.api = new API();
        this.currentView = 'dashboard';
        this.settings = {
            theme: 'light',
            autoRefresh: 30,
            language: 'en'
        };
        this.refreshInterval = null;
        this.sseConnection = null;
    }

    async init() {
        await this.loadSettings();
        this.applyTheme();
        this.setupNavigation();
        await this.renderCurrentView();
        this.startAutoRefresh();
        this.checkOnboarding();
        
        // Handle hash changes
        window.addEventListener('hashchange', () => this.handleRoute());
        
        console.log('Dashboard initialized');
    }

    async loadSettings() {
        try {
            const settings = await this.api.getSettings();
            this.settings = { ...this.settings, ...settings };
        } catch (error) {
            console.warn('Failed to load settings, using defaults:', error);
        }
    }

    applyTheme() {
        if (this.settings.theme === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }

    setupNavigation() {
        // Update active nav item based on current hash
        const hash = window.location.hash.slice(1) || 'dashboard';
        document.querySelectorAll('.sidebar-link').forEach(link => {
            const linkHash = link.getAttribute('href').slice(1);
            link.classList.toggle('active', linkHash === hash);
        });
    }

    async handleRoute() {
        const hash = window.location.hash.slice(1) || 'dashboard';
        this.currentView = hash;
        this.setupNavigation();
        await this.renderCurrentView();
    }

    async renderCurrentView() {
        const mainContent = document.getElementById('main-content');
        if (!mainContent) return;

        try {
            switch (this.currentView) {
                case 'dashboard':
                    await this.renderDashboard(mainContent);
                    break;
                case 'monitoring':
                    await this.renderMonitoring(mainContent);
                    break;
                case 'drift':
                    await this.renderDrift(mainContent);
                    break;
                case 'kanban':
                    await this.renderKanban(mainContent);
                    break;
                case 'wiki-browser':
                    await this.renderWikiBrowser(mainContent);
                    break;
                case 'sites':
                    await this.renderSites(mainContent);
                    break;
                case 'agents':
                    await this.renderAgents(mainContent);
                    break;
                case 'settings':
                    await this.renderSettings(mainContent);
                    break;
                default:
                    await this.renderDashboard(mainContent);
            }
        } catch (error) {
            this.showError(mainContent, `Failed to render view: ${error.message}`);
        }
    }

    async renderDashboard(container) {
        const status = await this.api.getDashboardStatus();
        
        container.innerHTML = `
            <div class="flex justify-between items-center mb-4">
                <h1 class="text-2xl font-bold">GRID Network Wiki</h1>
                <div class="flex gap-2">
                    <button class="btn btn-primary" onclick="dashboardApp.startDiscovery()">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.66 0 3-4.03 3-9s-1.34-9-3-9m0 18c-1.66 0-3-4.03-3-9s1.34-9 3-9m-9 9a9 9 0 019-9"/>
                        </svg>
                        Run Discovery
                    </button>
                    <button class="btn btn-secondary" onclick="dashboardApp.exportData()">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/>
                        </svg>
                        Export
                    </button>
                </div>
            </div>

            <div class="card-grid">
                <div class="stat-card">
                    <div class="stat-label">Active Tasks</div>
                    <div class="stat-value">${status.activeTasks || 0}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Goal Progress</div>
                    <div class="stat-value">${Math.min(status.goalProgress || 0, 100)}%</div>
                    <div class="progress mt-4">
                        <div class="progress-bar ${status.goalProgress >= 100 ? 'success' : ''}" 
                             style="width: ${Math.min(status.goalProgress || 0, 100)}%"></div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Monitoring Status</div>
                    <div class="stat-value success">${status.monitoringUp || 0}/${status.monitoringTotal || 0} services up</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Wiki Pages</div>
                    <div class="stat-value">${status.wikiPages || 0}</div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Active Tasks</h2>
                    <button class="btn btn-secondary btn-sm" onclick="dashboardApp.refreshTasks()">Refresh</button>
                </div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Task ID</th>
                                <th>Description</th>
                                <th>Status</th>
                                <th>Assignee</th>
                                <th>Last Updated</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${status.tasks ? status.tasks.map(task => `
                                <tr>
                                    <td><code>${task.id}</code></td>
                                    <td>${task.description}</td>
                                    <td><span class="badge badge-${this.getStatusColor(task.status)}">${task.status}</span></td>
                                    <td>${task.assignee || 'Unassigned'}</td>
                                    <td>${this.formatDate(task.lastUpdated)}</td>
                                </tr>
                            `).join('') : '<tr><td colspan="5" class="text-center text-muted">No active tasks</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Recent Activity</h2>
                </div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Event</th>
                                <th>Details</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${status.recentActivity ? status.recentActivity.map(activity => `
                                <tr>
                                    <td>${this.formatDate(activity.timestamp)}</td>
                                    <td>${activity.event}</td>
                                    <td class="text-muted">${activity.details}</td>
                                </tr>
                            `).join('') : '<tr><td colspan="3" class="text-center text-muted">No recent activity</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    async renderMonitoring(container) {
        const monitoring = await this.api.getMonitoringStatus();
        
        container.innerHTML = `
            <div class="flex justify-between items-center mb-4">
                <h1 class="text-2xl font-bold">Monitoring Status</h1>
                <div class="flex gap-2 items-center">
                    <select class="btn btn-secondary" onchange="dashboardApp.changeTimeRange(this.value)">
                        <option value="1h">1 Hour</option>
                        <option value="6h">6 Hours</option>
                        <option value="24h" selected>24 Hours</option>
                        <option value="7d">7 Days</option>
                    </select>
                    <button class="btn btn-primary" onclick="dashboardApp.refreshMonitoring()">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                        </svg>
                        Live Refresh
                    </button>
                </div>
            </div>

            <div class="card-grid">
                <div class="stat-card">
                    <div class="stat-label">Prometheus</div>
                    <div class="stat-value">${monitoring.prometheus?.up || 0}/${monitoring.prometheus?.total_targets || 0} targets</div>
                    <div class="text-sm text-muted mt-4">
                        <span class="badge badge-${monitoring.prometheus?.down > 0 ? 'warning' : 'success'}">
                            ${monitoring.prometheus?.down || 0} down
                        </span>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Uptime Kuma</div>
                    <div class="stat-value">${monitoring.uptime_kuma?.configured || 0} configured</div>
                    <div class="text-sm text-muted mt-4">
                        <span class="badge badge-${monitoring.uptime_kuma?.down > 0 ? 'danger' : 'success'}">
                            ${monitoring.uptime_kuma?.down || 0} down
                        </span>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Service Status</h2>
                </div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Type</th>
                                <th>Status</th>
                                <th>Response Time</th>
                                <th>Last Check</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${monitoring.services ? monitoring.services.map(service => `
                                <tr>
                                    <td><strong>${service.name}</strong></td>
                                    <td><span class="badge badge-info">${service.type}</span></td>
                                    <td><span class="badge badge-${service.status === 'up' ? 'success' : 'danger'}">${service.status}</span></td>
                                    <td>${service.response_time_ms ? service.response_time_ms + 'ms' : 'N/A'}</td>
                                    <td>${this.formatDate(service.last_check)}</td>
                                    <td>
                                        <button class="btn btn-secondary btn-sm" onclick="dashboardApp.viewService('${service.name}')">
                                            View
                                        </button>
                                    </td>
                                </tr>
                            `).join('') : '<tr><td colspan="6" class="text-center text-muted">No services configured</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    async renderDrift(container) {
        const driftReports = await this.api.getDriftReports();
        
        container.innerHTML = `
            <div class="flex justify-between items-center mb-4">
                <h1 class="text-2xl font-bold">Drift Reports</h1>
                <button class="btn btn-primary" onclick="dashboardApp.runDriftCheck()">
                    Run Drift Check
                </button>
            </div>

            ${driftReports.length === 0 ? `
                <div class="alert alert-info">
                    No drift reports available. Run a drift check to compare vault and overlay.
                </div>
            ` : `
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Recent Drift Reports</h2>
                    </div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Timestamp</th>
                                    <th>Vault Files</th>
                                    <th>Overlay Files</th>
                                    <th>Drift Detected</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${driftReports.map(report => `
                                    <tr>
                                        <td>${this.formatDate(report.timestamp)}</td>
                                        <td>${report.vault_files || 0}</td>
                                        <td>${report.overlay_files || 0}</td>
                                        <td>
                                            <span class="badge badge-${report.drift_detected ? 'danger' : 'success'}">
                                                ${report.drift_detected ? 'Yes' : 'No'}
                                            </span>
                                        </td>
                                        <td>
                                            <button class="btn btn-secondary btn-sm" onclick="dashboardApp.viewDriftReport('${report.id}')">
                                                View
                                            </button>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `}
        `;
    }

    async renderKanban(container) {
        const kanbanCards = await this.api.getKanbanCards();
        
        container.innerHTML = `
            <div class="flex justify-between items-center mb-4">
                <h1 class="text-2xl font-bold">Change Kanban</h1>
                <button class="btn btn-primary" onclick="dashboardApp.createChangeRequest()">
                    Create Change Request
                </button>
            </div>

            <div class="card-grid" style="grid-template-columns: repeat(3, 1fr);">
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Pending</h2>
                        <span class="badge badge-gray">${kanbanCards.pending?.length || 0}</span>
                    </div>
                    ${kanbanCards.pending ? kanbanCards.pending.map(card => `
                        <div class="card mb-4" style="border-left: 3px solid var(--warning);">
                            <div class="flex justify-between items-center mb-2">
                                <strong>${card.id}</strong>
                                <span class="badge badge-warning">${card.risk || 'N/A'}</span>
                            </div>
                            <p class="text-sm text-muted mb-3">${card.description}</p>
                            <div class="flex gap-2">
                                <button class="btn btn-secondary btn-sm" onclick="dashboardApp.approveChange('${card.id}')">Approve</button>
                                <button class="btn btn-secondary btn-sm" onclick="dashboardApp.rejectChange('${card.id}')">Reject</button>
                            </div>
                        </div>
                    `).join('') : '<p class="text-muted text-center">No pending changes</p>'}
                </div>

                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Approved</h2>
                        <span class="badge badge-gray">${kanbanCards.approved?.length || 0}</span>
                    </div>
                    ${kanbanCards.approved ? kanbanCards.approved.map(card => `
                        <div class="card mb-4" style="border-left: 3px solid var(--success);">
                            <div class="flex justify-between items-center mb-2">
                                <strong>${card.id}</strong>
                                <span class="badge badge-success">Approved</span>
                            </div>
                            <p class="text-sm text-muted mb-3">${card.description}</p>
                            <button class="btn btn-secondary btn-sm" onclick="dashboardApp.mergeChange('${card.id}')">Merge</button>
                        </div>
                    `).join('') : '<p class="text-muted text-center">No approved changes</p>'}
                </div>

                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">Merged</h2>
                        <span class="badge badge-gray">${kanbanCards.merged?.length || 0}</span>
                    </div>
                    ${kanbanCards.merged ? kanbanCards.merged.map(card => `
                        <div class="card mb-4" style="border-left: 3px solid var(--info);">
                            <div class="flex justify-between items-center mb-2">
                                <strong>${card.id}</strong>
                                <span class="badge badge-info">Merged</span>
                            </div>
                            <p class="text-sm text-muted">${card.description}</p>
                        </div>
                    `).join('') : '<p class="text-muted text-center">No merged changes</p>'}
                </div>
            </div>
        `;
    }

    async renderWikiBrowser(container) {
        const wikiIndex = await this.api.getWikiIndex();
        
        container.innerHTML = `
            <div class="flex justify-between items-center mb-4">
                <h1 class="text-2xl font-bold">Wiki Browser</h1>
                <div class="flex gap-2">
                    <input type="text" id="wiki-search" class="btn btn-secondary" placeholder="Search wiki..." 
                           oninput="dashboardApp.searchWiki(this.value)">
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Wiki Pages (${wikiIndex.pages?.length || 0})</h2>
                    <div class="flex gap-2">
                        <select class="btn btn-secondary" onchange="dashboardApp.filterByCategory(this.value)">
                            <option value="all">All Categories</option>
                            <option value="infrastructure">Infrastructure</option>
                            <option value="monitoring">Monitoring</option>
                            <option value="maintenance">Maintenance</option>
                            <option value="security">Security</option>
                            <option value="networking">Networking</option>
                            <option value="services">Services</option>
                        </select>
                        <select class="btn btn-secondary" onchange="dashboardApp.setPagination(this.value)">
                            <option value="20">20 per page</option>
                            <option value="50">50 per page</option>
                            <option value="100">100 per page</option>
                        </select>
                    </div>
                </div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Icon</th>
                                <th>Title</th>
                                <th>Category</th>
                                <th>Tags</th>
                                <th>Status</th>
                                <th>Last Updated</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${wikiIndex.pages ? wikiIndex.pages.map(page => `
                                <tr>
                                    <td><span class="badge badge-info">${this.getCategoryIcon(page.category)}</span></td>
                                    <td><a href="#wiki/${page.slug}" class="text-primary hover:underline">${page.title}</a></td>
                                    <td><span class="badge badge-gray">${page.category}</span></td>
                                    <td>${page.tags ? page.tags.map(tag => `<span class="badge badge-gray mr-1">#${tag}</span>`).join('') : ''}</td>
                                    <td><span class="badge badge-${page.status === 'active' ? 'success' : 'gray'}">${page.status}</span></td>
                                    <td>${this.formatDate(page.last_updated)}</td>
                                    <td>
                                        <button class="btn btn-secondary btn-sm" onclick="dashboardApp.viewWikiPage('${page.slug}')">View</button>
                                    </td>
                                </tr>
                            `).join('') : '<tr><td colspan="7" class="text-center text-muted">No wiki pages found</td></tr>'}
                        </tbody>
                    </table>
                </div>
                <div class="flex justify-between items-center mt-4">
                    <div class="text-sm text-muted">
                        Showing ${wikiIndex.pages?.length || 0} of ${wikiIndex.total || 0} pages
                    </div>
                    <div class="flex gap-2">
                        <button class="btn btn-secondary btn-sm" onclick="dashboardApp.previousPage()">Previous</button>
                        <button class="btn btn-secondary btn-sm" onclick="dashboardApp.nextPage()">Next</button>
                    </div>
                </div>
            </div>
        `;
    }

    async renderSites(container) {
        const sites = await this.api.getSites();
        
        container.innerHTML = `
            <div class="flex justify-between items-center mb-4">
                <h1 class="text-2xl font-bold">Sites Overview</h1>
            </div>

            <div class="card-grid">
                ${sites ? sites.map(site => `
                    <div class="card">
                        <div class="card-header">
                            <h2 class="card-title">${site.name}</h2>
                            <span class="badge badge-${site.status === 'active' ? 'success' : 'gray'}">${site.status}</span>
                        </div>
                        <div class="stat-card mb-4">
                            <div class="stat-label">Services</div>
                            <div class="stat-value">${site.service_count || 0}</div>
                        </div>
                        <div class="stat-card mb-4">
                            <div class="stat-label">Monitoring Status</div>
                            <div class="stat-value">${site.monitoring_status || 'N/A'}</div>
                        </div>
                        <button class="btn btn-primary" onclick="dashboardApp.viewSite('${site.name}')">
                            View Details
                        </button>
                    </div>
                `).join('') : '<div class="alert alert-info">No sites configured</div>'}
            </div>
        `;
    }

    async renderAgents(container) {
        const agents = await this.api.get('/api/agents');
        
        container.innerHTML = `
            <div class="flex justify-between items-center mb-4">
                <h1 class="text-2xl font-bold">Agent Protocol</h1>
            </div>

            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">AGENTS.md</h2>
                    <button class="btn btn-secondary btn-sm" onclick="dashboardApp.refreshAgents()">Refresh</button>
                </div>
                <div class="table-container">
                    <pre class="p-4" style="background: var(--gray-50); border-radius: var(--radius); font-size: 13px; line-height: 1.6; overflow-x: auto;">${agents.content || 'No agent protocol content available'}</pre>
                </div>
            </div>
        `;
    }

    async renderSettings(container) {
        const settings = await this.api.getSettings();
        
        container.innerHTML = `
            <div class="flex justify-between items-center mb-4">
                <h1 class="text-2xl font-bold">Settings</h1>
            </div>

            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Dashboard Settings</h2>
                </div>
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Wiki Root</label>
                        <input type="text" id="wiki-root" class="btn btn-secondary w-full" value="${settings.wikiRoot || 'N/A'}" readonly>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Theme</label>
                        <select id="theme" class="btn btn-secondary w-full">
                            <option value="light" ${settings.theme === 'light' ? 'selected' : ''}>Light</option>
                            <option value="dark" ${settings.theme === 'dark' ? 'selected' : ''}>Dark</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Auto-refresh (seconds)</label>
                        <input type="number" id="auto-refresh" class="btn btn-secondary w-full" value="${settings.autoRefresh || 30}" min="10" max="300">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Language</label>
                        <select id="language" class="btn btn-secondary w-full">
                            <option value="en" ${settings.language === 'en' ? 'selected' : ''}>English</option>
                            <option value="es" ${settings.language === 'es' ? 'selected' : ''}>Spanish</option>
                            <option value="fr" ${settings.language === 'fr' ? 'selected' : ''}>French</option>
                        </select>
                    </div>
                    <button class="btn btn-primary" onclick="dashboardApp.saveSettings()">Save Settings</button>
                </div>
            </div>
        `;
    }

    // Utility methods
    getStatusColor(status) {
        const colors = {
            'completed': 'success',
            'in_progress': 'warning',
            'pending': 'info',
            'failed': 'danger',
            'cancelled': 'gray'
        };
        return colors[status] || 'gray';
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        try {
            const date = new Date(dateString);
            return date.toLocaleString();
        } catch (e) {
            return dateString;
        }
    }

    getCategoryIcon(category) {
        const icons = {
            'infrastructure': '🏗️',
            'monitoring': '📊',
            'maintenance': '🔧',
            'security': '🔒',
            'networking': '🌐',
            'services': '⚙️',
            'backup': '💾',
            'tasks': '📋',
            'planning': '📝',
            'template': '📄'
        };
        return icons[category] || '📄';
    }

    showError(container, message) {
        container.innerHTML = `
            <div class="error-boundary">
                <h3>Error</h3>
                <p>${message}</p>
                <button class="btn btn-secondary" onclick="dashboardApp.retry()">Retry</button>
            </div>
        `;
    }

    // Action methods
    async startDiscovery() {
        try {
            await this.api.startDiscovery();
            alert('Discovery started successfully');
        } catch (error) {
            alert(`Failed to start discovery: ${error.message}`);
        }
    }

    async exportData() {
        try {
            const response = await fetch('/api/export');
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'grid-wiki-export.json';
            a.click();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            alert(`Export failed: ${error.message}`);
        }
    }

    async refreshTasks() {
        await this.renderCurrentView();
    }

    async refreshMonitoring() {
        await this.renderCurrentView();
    }

    async viewService(name) {
        window.location.hash = `service/${name}`;
    }

    async runDriftCheck() {
        try {
            await this.api.post('/api/drift/check', {});
            alert('Drift check started');
        } catch (error) {
            alert(`Drift check failed: ${error.message}`);
        }
    }

    async viewDriftReport(id) {
        window.location.hash = `drift/${id}`;
    }

    async createChangeRequest() {
        window.location.hash = 'kanban/create';
    }

    async approveChange(id) {
        try {
            await this.api.put(`/api/kanban/${id}/approve`, {});
            alert(`Change ${id} approved`);
            await this.renderCurrentView();
        } catch (error) {
            alert(`Failed to approve change: ${error.message}`);
        }
    }

    async rejectChange(id) {
        try {
            await this.api.put(`/api/kanban/${id}/reject`, {});
            alert(`Change ${id} rejected`);
            await this.renderCurrentView();
        } catch (error) {
            alert(`Failed to reject change: ${error.message}`);
        }
    }

    async mergeChange(id) {
        try {
            await this.api.put(`/api/kanban/${id}/merge`, {});
            alert(`Change ${id} merged`);
            await this.renderCurrentView();
        } catch (error) {
            alert(`Failed to merge change: ${error.message}`);
        }
    }

    async searchWiki(query) {
        if (query.length < 2) return;
        try {
            const results = await this.api.searchWiki(query);
            console.log('Search results:', results);
        } catch (error) {
            console.error('Search failed:', error);
        }
    }

    async filterByCategory(category) {
        console.log('Filter by category:', category);
    }

    async setPagination(count) {
        console.log('Set pagination:', count);
    }

    async previousPage() {
        console.log('Previous page');
    }

    async nextPage() {
        console.log('Next page');
    }

    async viewWikiPage(slug) {
        window.location.hash = `wiki/${slug}`;
    }

    async viewSite(name) {
        window.location.hash = `site/${name}`;
    }

    async refreshAgents() {
        await this.renderCurrentView();
    }

    async saveSettings() {
        const settings = {
            wikiRoot: document.getElementById('wiki-root')?.value,
            theme: document.getElementById('theme')?.value,
            autoRefresh: parseInt(document.getElementById('auto-refresh')?.value),
            language: document.getElementById('language')?.value
        };

        try {
            await this.api.saveSettings(settings);
            this.settings = { ...this.settings, ...settings };
            this.applyTheme();
            alert('Settings saved successfully');
        } catch (error) {
            alert(`Failed to save settings: ${error.message}`);
        }
    }

    async changeTimeRange(range) {
        console.log('Change time range:', range);
    }

    checkOnboarding() {
        const hasCompletedOnboarding = localStorage.getItem('onboarding-completed');
        if (!hasCompletedOnboarding) {
            this.showOnboarding();
        }
    }

    showOnboarding() {
        const overlay = document.createElement('div');
        overlay.className = 'onboarding-overlay';
        overlay.innerHTML = `
            <div class="onboarding-card">
                <h2>Welcome to GRID Network Wiki</h2>
                <p>Let's get you started with the dashboard:</p>
                <ol class="steps">
                    <li>Run discovery to scan your infrastructure</li>
                    <li>Check monitoring status for service health</li>
                    <li>Browse the wiki to explore documentation</li>
                    <li>Review change kanban for pending changes</li>
                </ol>
                <div class="flex justify-end gap-2 mt-4">
                    <button class="btn btn-secondary" onclick="dashboardApp.skipOnboarding()">Skip</button>
                    <button class="btn btn-primary" onclick="dashboardApp.completeOnboarding()">Get Started</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);
    }

    completeOnboarding() {
        localStorage.setItem('onboarding-completed', 'true');
        const overlay = document.querySelector('.onboarding-overlay');
        if (overlay) overlay.remove();
    }

    skipOnboarding() {
        localStorage.setItem('onboarding-completed', 'true');
        const overlay = document.querySelector('.onboarding-overlay');
        if (overlay) overlay.remove();
    }

    startAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        this.refreshInterval = setInterval(() => {
            this.renderCurrentView();
        }, (this.settings.autoRefresh || 30) * 1000);
    }

    retry() {
        this.renderCurrentView();
    }
}

// Initialize the dashboard
let dashboardApp;
document.addEventListener('DOMContentLoaded', () => {
    dashboardApp = new DashboardApp();
    dashboardApp.init();
});
