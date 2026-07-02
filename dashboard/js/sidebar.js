// Sidebar Navigation
class Sidebar {
    constructor() {
        this.currentView = 'dashboard';
        this.init();
    }

    init() {
        this.setupNavigation();
        this.handleResize();
        window.addEventListener('resize', () => this.handleResize());
    }

    setupNavigation() {
        const links = document.querySelectorAll('.sidebar-link');
        links.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const href = link.getAttribute('href');
                if (href) {
                    window.location.hash = href.slice(1);
                }
            });
        });

        // Update active state based on current hash
        this.updateActiveState();
        window.addEventListener('hashchange', () => this.updateActiveState());
    }

    updateActiveState() {
        const hash = window.location.hash.slice(1) || 'dashboard';
        this.currentView = hash;
        
        document.querySelectorAll('.sidebar-link').forEach(link => {
            const linkHash = link.getAttribute('href').slice(1);
            link.classList.toggle('active', linkHash === hash);
        });
    }

    handleResize() {
        const sidebar = document.querySelector('.sidebar');
        const toggle = document.querySelector('.sidebar-toggle');
        
        if (window.innerWidth <= 768) {
            if (sidebar) sidebar.classList.remove('open');
            if (toggle) toggle.style.display = 'flex';
        } else {
            if (sidebar) sidebar.classList.remove('open');
            if (toggle) toggle.style.display = 'none';
        }
    }

    toggle() {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.classList.toggle('open');
        }
    }

    close() {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.classList.remove('open');
        }
    }
}

// Initialize sidebar
document.addEventListener('DOMContentLoaded', () => {
    window.sidebar = new Sidebar();
});
