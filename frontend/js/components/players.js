import { api } from '../api.js';
import { formatCurrency, formatDate, getBadgeClass } from '../utils.js';

export async function renderPlayers(container) {
    container.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Players</h3>
                <div>
                     <button id="btn-create-player" class="btn btn-primary btn-sm">
                        <span class="icon">+</span> Create Player
                    </button>
                    <button id="btn-import-players" class="btn btn-secondary btn-sm" style="margin-left: 10px;">
                        <span class="icon">📂</span> Bulk Import
                    </button>
                </div>
            </div>
            <div class="table-container">
                <table id="players-table">
                    <thead>
                        <tr>
                            <th>Player ID</th>
                            <th>Segment</th>
                            <th>Tier</th>
                            <th>Status</th>
                            <th>Metrics</th>
                            <th>Created</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td colspan="6" style="text-align: center;">Loading players...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Create Player Modal -->
        <dialog id="create-player-modal" style="padding: 0; border: none; border-radius: var(--radius-lg); box-shadow: var(--shadow-xl);">
            <form id="create-player-form" style="padding: var(--spacing-lg); width: 400px;">
                <h3 style="margin-bottom: var(--spacing-md);">Create New Player</h3>
                
                <div class="form-group">
                    <label for="cp-id">Player ID</label>
                    <input type="text" id="cp-id" name="player_id" required placeholder="e.g. USER_123">
                </div>
                
                <div class="form-group">
                    <label for="cp-email">Email</label>
                    <input type="email" id="cp-email" name="email" placeholder="user@example.com">
                </div>
                
                <div class="form-group">
                    <label for="cp-name">Name</label>
                    <input type="text" id="cp-name" name="name" placeholder="John Doe">
                </div>

                <div style="display: flex; gap: var(--spacing-sm); justify-content: flex-end; margin-top: var(--spacing-lg);">
                    <button type="button" class="btn btn-secondary" id="btn-cancel-create">Cancel</button>
                    <button type="submit" class="btn btn-primary">Create</button>
                </div>
            </form>
        </dialog>

        <!-- Import Players Modal -->
        <dialog id="import-player-modal" style="padding: 0; border: none; border-radius: var(--radius-lg); box-shadow: var(--shadow-xl);">
            <form id="import-player-form" style="padding: var(--spacing-lg); width: 400px;">
                <h3 style="margin-bottom: var(--spacing-md);">Bulk Import Players</h3>
                <p style="font-size: 0.875rem; color: var(--text-muted); margin-bottom: var(--spacing-md);">
                    Upload an Excel (.xlsx) or CSV (.csv) file.
                    <br>Required columns: <code>player_id</code>, <code>total_deposited</code>, <code>total_wagered</code>, <code>total_won</code>.
                </p>
                
                <div class="form-group">
                    <label for="ip-file">Select File</label>
                    <input type="file" id="ip-file" name="file" accept=".csv, .xlsx" required>
                </div>

                <div style="display: flex; gap: var(--spacing-sm); justify-content: flex-end; margin-top: var(--spacing-lg);">
                    <button type="button" class="btn btn-secondary" id="btn-cancel-import">Cancel</button>
                    <button type="submit" class="btn btn-primary">Upload & Process</button>
                </div>
            </form>
        </dialog>

        <!-- Player Details View (Hidden by default) -->
        <div id="player-details-view" style="display: none; margin-top: var(--spacing-lg);"></div>
    `;

    // Fetch and Render Players
    await loadPlayers();

    // Event Listeners
    setupEventListeners(container);
}

async function loadPlayers() {
    const tbody = document.querySelector('#players-table tbody');
    try {
        const players = await api.getPlayers();

        if (players.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align: center;">No players found. Create one!</td></tr>`;
            return;
        }

        tbody.innerHTML = players.map(player => `
            <tr style="cursor: pointer;" onclick="document.dispatchEvent(new CustomEvent('view-player', { detail: '${player.player_id}' }))">
                <td>
                    <div style="font-weight: 500;">${player.player_id}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">${player.email || 'No email'}</div>
                </td>
                <td><span class="${getBadgeClass(player.segment, 'status')}">${player.segment}</span></td>
                <td><span class="${getBadgeClass(player.tier, 'tier')}">${player.tier}</span></td>
                <td>
                    <span class="${getBadgeClass(player.is_active, 'status')}">
                        ${player.is_active ? 'Active' : 'Inactive'}
                    </span>
                    ${player.is_blocked ? '<span class="badge badge-red" style="margin-left: 5px;">BLOCKED</span>' : ''}
                </td>
                <td>
                    <div style="font-size: 0.875rem;">
                        <div>Dep: ${formatCurrency(player.metrics.total_deposited, 'CASH')}</div>
                        <div style="${player.metrics.net_pnl < 0 ? 'color: var(--accent-green);' : 'color: var(--accent-red);'}">
                            PnL: ${formatCurrency(player.metrics.net_pnl, 'CASH')}
                        </div>
                    </div>
                </td>
                <td>${formatDate(player.created_at)}</td>
            </tr>
        `).join('');

    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="6" style="color: var(--accent-red);">Error loading players: ${error.message}</td></tr>`;
    }
}

function setupEventListeners(container) {
    // Create Player Modal
    const modalCreate = document.getElementById('create-player-modal');
    const btnCreate = document.getElementById('btn-create-player');
    const btnCancelCreate = document.getElementById('btn-cancel-create');
    const formCreate = document.getElementById('create-player-form');

    btnCreate.addEventListener('click', () => modalCreate.showModal());
    btnCancelCreate.addEventListener('click', () => modalCreate.close());

    formCreate.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(formCreate);
        const data = Object.fromEntries(formData.entries());

        try {
            await api.createPlayer(data);
            modalCreate.close();
            formCreate.reset();
            await loadPlayers();
        } catch (error) {
            alert(`Failed to create player: ${error.message}`);
        }
    });

    // Import Players Modal
    const modalImport = document.getElementById('import-player-modal');
    const btnImport = document.getElementById('btn-import-players');
    const btnCancelImport = document.getElementById('btn-cancel-import');
    const formImport = document.getElementById('import-player-form');

    btnImport.addEventListener('click', () => modalImport.showModal());
    btnCancelImport.addEventListener('click', () => modalImport.close());

    formImport.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fileInput = document.getElementById('ip-file');
        const file = fileInput.files[0];

        if (!file) {
            alert('Please select a file');
            return;
        }

        const btnSubmit = formImport.querySelector('button[type="submit"]');
        const originalText = btnSubmit.textContent;
        btnSubmit.textContent = 'Uploading...';
        btnSubmit.disabled = true;

        try {
            const result = await api.importPlayers(file);
            alert(`Import Complete!\n\nPlayers Created: ${result.players_created}\nPlayers Updated: ${result.players_updated}\nRewards Issued: ${result.rewards_issued}\n\n${result.errors.length > 0 ? 'See console for errors.' : ''}`);
            if (result.errors.length > 0) console.warn('Import Errors:', result.errors);

            modalImport.close();
            formImport.reset();
            await loadPlayers();
        } catch (error) {
            alert(`Import Failed: ${error.message}`);
        } finally {
            btnSubmit.textContent = originalText;
            btnSubmit.disabled = false;
        }
    });

    document.addEventListener('view-player', async (e) => {
        const playerId = e.detail;
        await renderPlayerDetails(playerId);
    });
}

async function renderPlayerDetails(playerId) {
    const detailsContainer = document.getElementById('player-details-view');
    detailsContainer.innerHTML = '<div class="spinner"></div>';
    detailsContainer.style.display = 'block';

    // Scroll to details
    detailsContainer.scrollIntoView({ behavior: 'smooth' });

    try {
        const p = await api.getPlayer(playerId);

        detailsContainer.innerHTML = `
            <div class="card" style="border-top: 4px solid var(--primary);">
                <div class="card-header">
                    <div>
                        <h3 class="card-title">${p.name || p.player_id} <span style="font-weight: normal; color: var(--text-muted);">(${p.player_id})</span></h3>
                        <div style="margin-top: 5px; display: flex; gap: 5px;">
                            <span class="${getBadgeClass(p.segment, 'status')}">${p.segment}</span>
                            <span class="${getBadgeClass(p.tier, 'tier')}">${p.tier}</span>
                        </div>
                    </div>
                    <button class="btn btn-secondary btn-sm" onclick="document.getElementById('player-details-view').style.display = 'none'">Close</button>
                </div>

                <div class="card-actions" style="margin-bottom: var(--spacing-md); display: flex; gap: 10px; padding: 0 var(--spacing-md);">
                    <button class="btn btn-sm btn-primary" onclick="triggerKYC('${p.player_id}')">
                        <span class="icon">🆔</span> Verify KYC
                    </button>
                    <button class="btn btn-sm btn-primary" onclick="triggerProfileDepth('${p.player_id}')">
                        <span class="icon">📝</span> Complete Profile
                    </button>
                </div>

                <div class="grid grid-3">
                    <!-- Balances -->
                    <div style="background-color: var(--bg-body); padding: var(--spacing-md); border-radius: var(--radius-md);">
                        <h4 style="margin-bottom: var(--spacing-sm); font-size: 0.875rem; text-transform: uppercase; color: var(--text-muted);">Wallet Balances</h4>
                        <div style="display: flex; flex-direction: column; gap: var(--spacing-xs);">
                            <div style="display: flex; justify-content: space-between;">
                                <span>Loyalty Points:</span>
                                <span style="font-weight: 600;">${formatCurrency(p.balances?.lp_balance || 0, 'LP')}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span>Reward Points:</span>
                                <span style="font-weight: 600;">${formatCurrency(p.balances?.rp_balance || 0, 'RP')}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span>Bonus Balance:</span>
                                <span style="font-weight: 600; color: var(--accent-green);">${formatCurrency(p.balances?.bonus_balance || 0, 'BONUS_BALANCE')}</span>
                            </div>
                             <div style="display: flex; justify-content: space-between;">
                                <span>Tickets:</span>
                                <span style="font-weight: 600;">${formatCurrency(p.balances?.tickets_balance || 0, 'TICKETS')}</span>
                            </div>
                        </div>
                    </div>

                    <!-- Risk & Behavior -->
                    <div style="background-color: var(--bg-body); padding: var(--spacing-md); border-radius: var(--radius-md);">
                         <h4 style="margin-bottom: var(--spacing-sm); font-size: 0.875rem; text-transform: uppercase; color: var(--text-muted);">Risk & Behavior</h4>
                         <div style="display: flex; flex-direction: column; gap: var(--spacing-xs);">
                            <div style="display: flex; justify-content: space-between;">
                                <span>Risk Score:</span>
                                <span style="font-weight: 600; ${p.risk_score > 50 ? 'color: var(--accent-red);' : ''}">${p.risk_score} / 100</span>
                            </div>
                             <div style="display: flex; justify-content: space-between;">
                                <span>Win/Loss Ratio:</span>
                                <span style="font-weight: 600;">${(p.metrics?.win_loss_ratio || 0).toFixed(2)}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span>Bonus Abuse Score:</span>
                                <span style="font-weight: 600;">${p.metrics?.bonus_abuse_score || 0}</span>
                            </div>
                        </div>
                    </div>

                    <!-- Lifetime Stats -->
                     <div style="background-color: var(--bg-body); padding: var(--spacing-md); border-radius: var(--radius-md);">
                         <h4 style="margin-bottom: var(--spacing-sm); font-size: 0.875rem; text-transform: uppercase; color: var(--text-muted);">Lifetime Stats</h4>
                         <div style="display: flex; flex-direction: column; gap: var(--spacing-xs);">
                            <div style="display: flex; justify-content: space-between;">
                                <span>Total Sessions:</span>
                                <span style="font-weight: 600;">${p.metrics?.total_sessions || 0}</span>
                            </div>
                             <div style="display: flex; justify-content: space-between;">
                                <span>Total Wagered:</span>
                                <span style="font-weight: 600;">${formatCurrency(p.metrics?.total_wagered || 0, 'CASH')}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span>Net PnL (Player):</span>
                                <span style="font-weight: 600; ${(p.metrics?.net_pnl || 0) > 0 ? 'color: var(--accent-green);' : 'color: var(--accent-red);'}">
                                    ${formatCurrency(p.metrics?.net_pnl || 0, 'CASH')}
                                </span>
                            </div>
                        </div>
                     </div>
                </div>
            </div>
        `;
    } catch (error) {
        detailsContainer.innerHTML = `<div class="card" style="color: var(--accent-red);">Error loading details: ${error.message}</div>`;
    }
}

// Global scope helpers for onclick handlers
window.triggerKYC = async (playerId) => {
    try {
        const result = await api.completeKYC(playerId);
        alert(`KYC Completed! Rewards triggered: ${result.rewards_triggered}`);
        document.dispatchEvent(new CustomEvent('view-player', { detail: playerId }));
    } catch (error) {
        alert('Error: ' + error.message);
    }
};

window.triggerProfileDepth = async (playerId) => {
    const depth = prompt('Enter profile completion depth (0-100):', '100');
    if (depth === null) return;

    try {
        const result = await api.updateProfileDepth(playerId, parseInt(depth));
        alert(`Profile updated to ${depth}%! Rewards triggered: ${result.rewards_triggered}`);
        document.dispatchEvent(new CustomEvent('view-player', { detail: playerId }));
    } catch (error) {
        alert('Error: ' + error.message);
    }
};
