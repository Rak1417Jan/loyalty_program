import { ROUTES } from './config.js';
import { api } from './api.js';

// View Imports (Dynamic imports would be better for larger apps, but static is fine here)
import { renderDashboard } from './components/dashboard.js';
import { renderPlayers } from './components/players.js';
import { renderRules } from './components/rules.js';
import { renderTiers } from './components/tiers.js';
import { renderWallet } from './components/wallet.js';
import { renderAnalytics } from './components/analytics.js';
import { renderRedemption } from './components/redemption.js';

class App {
    constructor() {
        this.currentView = null;
        this.appContainer = document.getElementById('app-view');
        this.pageTitle = document.getElementById('page-title');
        this.pageSubtitle = document.getElementById('page-subtitle');
        this.navLinks = document.querySelectorAll('.nav-item');

        this.routes = {
            [ROUTES.DASHBOARD]: {
                render: renderDashboard,
                title: 'Dashboard',
                subtitle: 'Overview of program performance'
            },
            [ROUTES.PLAYERS]: {
                render: renderPlayers,
                title: 'Player Management',
                subtitle: 'View and manage player profiles'
            },
            [ROUTES.RULES]: {
                render: renderRules,
                title: 'Reward Rules',
                subtitle: 'Configure loyalty logic and conditions'
            },
            [ROUTES.TIERS]: {
                render: renderTiers,
                title: 'Tiers & Benefits',
                subtitle: 'Manage loyalty levels and perks'
            },
            [ROUTES.WALLET]: {
                render: renderWallet,
                title: 'Wallet Simulator',
                subtitle: 'Test transactions and balance updates'
            },
            [ROUTES.ANALYTICS]: {
                render: renderAnalytics,
                title: 'Analytics',
                subtitle: 'Deep dive into program data'
            },
            [ROUTES.REDEMPTION]: {
                render: renderRedemption,
                title: 'Redemption Rules',
                subtitle: 'Manage point-to-value conversion'
            }
        };

        this.init();
    }

    init() {
        // Handle Navigation
        window.addEventListener('hashchange', () => this.handleRoute());

        // Initial Route
        this.handleRoute();

        // Check Backend Health
        this.checkHealth();
    }

    async checkHealth() {
        try {
            await api.request('/health');
            document.querySelector('.status-indicator').classList.remove('offline');
            document.querySelector('.status-indicator').classList.add('online');
            document.querySelector('.status-indicator').innerHTML = '<span class="dot"></span> Backend Online';
        } catch (error) {
            document.querySelector('.status-indicator').classList.remove('online');
            document.querySelector('.status-indicator').classList.add('offline');
            document.querySelector('.status-indicator').innerHTML = '<span class="dot"></span> Backend Offline';
        }
    }

    handleRoute() {
        const hash = window.location.hash.slice(1) || '/';
        const routeName = hash === '/' ? ROUTES.DASHBOARD : hash.substring(1); // Remove leading slash

        // Simple router logic: handle /players vs /players/123 later if needed.
        // For now, exact match on registered routes.

        const routeKey = Object.keys(this.routes).find(key => routeName.startsWith(key));
        const activeRoute = this.routes[routeKey] || this.routes[ROUTES.DASHBOARD];

        this.updateUI(routeKey || ROUTES.DASHBOARD, activeRoute);
        this.renderView(activeRoute);
    }

    updateUI(activeKey, routeConfig) {
        // Update Sidebar
        this.navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('data-view') === activeKey) {
                link.classList.add('active');
            }
        });

        // Update Header
        this.pageTitle.textContent = routeConfig.title;
        this.pageSubtitle.textContent = routeConfig.subtitle;
    }

    async renderView(routeConfig) {
        this.appContainer.innerHTML = `
            <div class="loading-state">
                <div class="spinner"></div>
                <p>Loading view...</p>
            </div>
        `;

        try {
            await routeConfig.render(this.appContainer);
        } catch (error) {
            console.error('Render Error:', error);
            this.appContainer.innerHTML = `
                <div class="card" style="border-color: var(--accent-red); color: var(--accent-red);">
                    <h3>Error Loading View</h3>
                    <p>${error.message}</p>
                </div>
            `;
        }
    }
}

// Initialize App
const app = new App();
