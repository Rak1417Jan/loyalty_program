import { api } from '../api.js';
import { formatCurrency, formatDate, getBadgeClass } from '../utils.js';

export async function renderAnalytics(container) {
    container.innerHTML = `
        <div class="grid grid-2" style="gap: var(--spacing-lg);">
            <!-- Segments Chart (Simulated with bars) -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Player Segmentation</h3>
                </div>
                <div id="segment-chart">Loading...</div>
            </div>

            <!-- Recent Rewards -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Recent Rewards Issued</h3>
                </div>
                <div class="table-container" style="max-height: 400px; overflow-y: auto;">
                    <table id="rewards-table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Player</th>
                                <th>Type</th>
                                <th>Amount</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>
    `;

    // Load Data Parallelly
    await Promise.all([loadSegmentation(), loadRewards()]);
}

async function loadSegmentation() {
    const chart = document.getElementById('segment-chart');
    try {
        const data = await api.getDashboardMetrics();
        const dist = data.segment_distribution;

        chart.innerHTML = dist.map(item => `
            <div style="margin-bottom: var(--spacing-md);">
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-weight: 500;">${item.segment}</span>
                    <span style="color: var(--text-muted);">${item.count} players (${item.percentage.toFixed(1)}%)</span>
                </div>
                <div style="background-color: var(--bg-body); height: 8px; border-radius: 4px; overflow: hidden;">
                    <div style="width: ${item.percentage}%; background-color: var(--primary); height: 100%;"></div>
                </div>
            </div>
        `).join('');

        if (dist.length === 0) {
            chart.innerHTML = '<p>No data available.</p>';
        }

    } catch (e) {
        chart.innerHTML = `<p style="color: var(--accent-red)">Error: ${e.message}</p>`;
    }
}

async function loadRewards() {
    const tbody = document.querySelector('#rewards-table tbody');
    try {
        const rewards = await api.getRewardHistory();

        if (rewards.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align: center;">No rewards found.</td></tr>`;
            return;
        }

        tbody.innerHTML = rewards.map(r => `
            <tr>
                <td style="font-size: 0.875rem;">${formatDate(r.issued_at)}</td>
                <td style="font-weight: 500;">${r.player_id}</td>
                <td>${r.reward_type}</td>
                <td>${formatCurrency(r.amount, r.currency_type)}</td>
                <td><span class="${getBadgeClass(r.status, 'status')}">${r.status}</span></td>
            </tr>
        `).join('');

    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="5" style="color: var(--accent-red)">Error: ${e.message}</td></tr>`;
    }
}
