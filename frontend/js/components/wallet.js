import { api } from '../api.js';
import { formatCurrency, formatDate } from '../utils.js';

export async function renderWallet(container) {
    container.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Wallet Simulator</h3>
            </div>
            
            <div class="grid grid-2" style="gap: var(--spacing-lg);">
                <!-- Simulation Form -->
                <div>
                    <h4 style="margin-bottom: var(--spacing-md);">Credit Player Wallet</h4>
                    <form id="wallet-form">
                        <div class="form-group">
                            <label for="w-player">Select Player</label>
                            <select id="w-player" name="player_id" required>
                                <option value="">Loading players...</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="w-type">Transaction Type</label>
                            <select id="w-type" name="type" required>
                                <option value="LP">Loyalty Points (LP)</option>
                                <option value="BONUS">Bonus Cash</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="w-amount">Amount</label>
                            <input type="number" id="w-amount" name="amount" required min="1" step="0.01">
                        </div>
                        
                        <div id="bonus-fields" style="display: none; padding: var(--spacing-md); background: var(--bg-body); border-radius: var(--radius-md); margin-bottom: var(--spacing-md);">
                             <div class="form-group">
                                <label for="w-wager">Wagering Requirement (Multiplier)</label>
                                <input type="number" id="w-wager" name="wagering_requirement" value="1" min="1">
                            </div>
                             <div class="form-group">
                                <label for="w-expiry">Expiry (Hours)</label>
                                <input type="number" id="w-expiry" name="expiry_hours" value="24" min="1">
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="w-desc">Description</label>
                            <input type="text" id="w-desc" name="description" placeholder="e.g. Manual Adjustment">
                        </div>

                        <button type="submit" class="btn btn-primary" style="width: 100%;">Process Transaction</button>
                    </form>
                </div>

                <!-- Recent Transactions -->
                <div>
                    <h4 style="margin-bottom: var(--spacing-md);">Recent Transactions</h4>
                    <div id="transaction-list" style="max-height: 400px; overflow-y: auto;">
                        <p style="color: var(--text-muted); font-style: italic;">Select a player to view transactions.</p>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Populate Players
    const select = document.getElementById('w-player');
    try {
        const players = await api.getPlayers();
        select.innerHTML = '<option value="">-- Select Player --</option>' +
            players.map(p => `<option value="${p.player_id}">${p.name || p.player_id}</option>`).join('');
    } catch (e) {
        select.innerHTML = '<option value="">Error loading players</option>';
    }

    setupWalletListeners();
}

function setupWalletListeners() {
    const form = document.getElementById('wallet-form');
    const typeSelect = document.getElementById('w-type');
    const playerSelect = document.getElementById('w-player');
    const bonusFields = document.getElementById('bonus-fields');

    // Toggle Bonus Fields
    typeSelect.addEventListener('change', (e) => {
        bonusFields.style.display = e.target.value === 'BONUS' ? 'block' : 'none';
    });

    // Load Transactions on Player Select
    playerSelect.addEventListener('change', async (e) => {
        const playerId = e.target.value;
        if (playerId) {
            await loadTransactions(playerId);
        } else {
            document.getElementById('transaction-list').innerHTML = '<p style="color: var(--text-muted); font-style: italic;">Select a player to view transactions.</p>';
        }
    });

    // Handle Submit
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        const type = formData.get('type');
        const playerId = formData.get('player_id');

        if (!playerId) {
            alert('Please select a player');
            return;
        }

        try {
            if (type === 'LP') {
                await api.addLoyaltyPoints({
                    player_id: playerId,
                    amount: parseInt(formData.get('amount')),
                    description: formData.get('description'),
                    source: 'ADMIN_CONSOLE'
                });
            } else {
                await api.addBonus({
                    player_id: playerId,
                    amount: parseFloat(formData.get('amount')),
                    wagering_requirement: parseFloat(formData.get('wagering_requirement')),
                    expiry_hours: parseInt(formData.get('expiry_hours')),
                    description: formData.get('description')
                });
            }

            alert('Transaction Successful!');
            form.reset();
            // Restore player selection to keep viewing their history
            playerSelect.value = playerId;
            // Trigger change event to reload transactions (or call directly if we want to be cleaner, but simple enough)
            await loadTransactions(playerId);

        } catch (error) {
            alert(`Transaction Failed: ${error.message}`);
        }
    });
}

async function loadTransactions(playerId) {
    const list = document.getElementById('transaction-list');
    list.innerHTML = '<div class="spinner"></div>';

    try {
        const txs = await api.getTransactions(playerId);

        if (txs.length === 0) {
            list.innerHTML = '<p>No transactions found.</p>';
            return;
        }

        list.innerHTML = txs.map(tx => `
            <div style="padding: var(--spacing-sm); border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-weight: 500;">${tx.transaction_type}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">${formatDate(tx.created_at)}</div>
                    <div style="font-size: 0.75rem;">${tx.description || '-'}</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-weight: 600; color: ${tx.amount > 0 ? 'var(--accent-green)' : 'var(--accent-red)'}">
                        ${tx.amount > 0 ? '+' : ''}${tx.amount} ${tx.currency_type}
                    </div>
                </div>
            </div>
        `).join('');

    } catch (e) {
        list.innerHTML = `<p style="color: var(--accent-red)">Error: ${e.message}</p>`;
    }
}
