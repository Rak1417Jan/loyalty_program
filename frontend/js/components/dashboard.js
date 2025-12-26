// Dashboard Component
import { api } from '../api.js';
import { formatCurrency, getBadgeClass } from '../utils.js';

export async function renderDashboard(container) {
    try {
        const metrics = await api.getDashboardMetrics();

        container.innerHTML = `
            <div class="grid grid-4">
                <div class="card stat-card">
                    <div class="stat-icon" style="background-color: var(--primary-light); color: var(--primary);">👥</div>
                    <div class="stat-info">
                        <span class="stat-value">${metrics.total_players}</span>
                        <span class="stat-label">Total Players</span>
                        <span class="stat-change text-positive">Active: ${metrics.active_players}</span>
                    </div>
                </div>
                <div class="card stat-card">
                    <div class="stat-icon" style="background-color: var(--primary-light); color: var(--accent-gold);">🏆</div>
                    <div class="stat-info">
                        <span class="stat-value">${metrics.total_rewards_issued}</span>
                        <span class="stat-label">Rewards Issued</span>
                    </div>
                </div>
                <!-- More metrics can go here -->
            </div>
            
            <!-- We will expand this with a recent activity table later -->
            <div class="card" style="margin-top: 2rem;">
                 <div class="card-header">
                    <h3 class="card-title">Welcome to LoyaltyPro</h3>
                 </div>
                 <p>Select a module from the sidebar to get started.</p>
            </div>
        `;
    } catch (error) {
        throw error;
    }
}
