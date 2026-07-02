// API Client for GRID Wiki Dashboard
class API {
    constructor(baseURL = '') {
        this.baseURL = baseURL || window.location.origin;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        if (options.body && typeof options.body === 'object') {
            config.body = JSON.stringify(options.body);
        }

        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                const error = await response.json().catch(() => ({ error: response.statusText }));
                throw new Error(error.error || `HTTP ${response.status}`);
            }
            return response.json();
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    post(endpoint, body) {
        return this.request(endpoint, { method: 'POST', body });
    }

    put(endpoint, body) {
        return this.request(endpoint, { method: 'PUT', body });
    }

    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    // Dashboard specific methods
    async getDashboardStatus() {
        return this.get('/api/dashboard/status');
    }

    async getMonitoringStatus() {
        return this.get('/api/monitoring-status');
    }

    async getWikiIndex() {
        return this.get('/api/wiki-index');
    }

    async getWikiPage(slug) {
        return this.get(`/api/wiki/${slug}`);
    }

    async getDriftReports() {
        return this.get('/api/drift-reports');
    }

    async getKanbanCards(column) {
        return this.get(`/api/kanban/${column || 'all'}`);
    }

    async getActiveTasks() {
        return this.get('/api/active-tasks');
    }

    async getProjectManifest() {
        return this.get('/api/project-manifest');
    }

    async startDiscovery() {
        return this.post('/api/discovery/start', {});
    }

    async getDiscoveryStatus() {
        return this.get('/api/discovery/status');
    }

    async getSettings() {
        return this.get('/api/settings');
    }

    async saveSettings(settings) {
        return this.post('/api/settings', settings);
    }

    async searchWiki(query) {
        return this.get(`/api/wiki/search?q=${encodeURIComponent(query)}`);
    }

    async getSites() {
        return this.get('/api/sites');
    }

    async getServiceDetails(name) {
        return this.get(`/api/service/${name}`);
    }

    // SSE connection for real-time updates
    connectSSE(url, onmessage, onerror, onopen) {
        const eventSource = new EventSource(url);
        
        if (onopen) {
            eventSource.onopen = onopen;
        }
        
        if (onmessage) {
            eventSource.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    onmessage(data);
                } catch (e) {
                    console.error('SSE parse error:', e);
                }
            };
        }
        
        if (onerror) {
            eventSource.onerror = onerror;
        }
        
        return eventSource;
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = API;
}
