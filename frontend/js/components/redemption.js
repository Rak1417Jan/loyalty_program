import { api } from '../api.js';

export async function renderRedemption(container) {
    container.innerHTML = `
        <div class="rules-container">
            <div class="section-header">
                <h2>Redemption Rules</h2>
                <button id="add-redemption-rule-btn" class="btn btn-primary">
                    <span class="icon">＋</span> Add Rule
                </button>
            </div>

            <div id="redemption-rules-list" class="grid-container">
                <div class="loading-state">
                    <div class="spinner"></div>
                    <p>Fetching redemption rules...</p>
                </div>
            </div>

            <div class="section-header" style="margin-top: 2rem;">
                <h2>Execute Redemption</h2>
                <p>Test point conversion for a player</p>
            </div>

            <div class="card">
                <form id="execute-redemption-form" class="horizontal-form">
                    <div class="form-group">
                        <label>Player ID</label>
                        <input type="text" id="redeem-player-id" placeholder="e.g. P001" required>
                    </div>
                    <div class="form-group">
                        <label>Redemption Rule</label>
                        <select id="redeem-rule-id" required>
                            <option value="">Select a rule...</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary" style="align-self: flex-end;">Redeem Now</button>
                </form>
                <div id="redemption-result" class="result-message" style="margin-top: 1rem; display: none;"></div>
            </div>
            
            <div class="section-header" style="margin-top: 2rem;">
                <h2>Maintenance</h2>
            </div>
            <div class="card">
                <div class="action-row">
                    <div>
                        <h3>Process Point Expiry</h3>
                        <p>Manually trigger checking for and expiring old loyalty points.</p>
                    </div>
                    <button id="trigger-expiry-btn" class="btn btn-secondary">Run Expiry Job</button>
                </div>
                <div id="expiry-result" class="result-message" style="margin-top: 1rem; display: none;"></div>
            </div>
        </div>

        <!-- Create Redemption Rule Modal -->
        <dialog id="create-red-rule-modal" style="padding: 0; border: none; border-radius: var(--radius-lg); box-shadow: var(--shadow-xl);">
            <form id="create-red-rule-form" style="padding: var(--spacing-lg); width: 500px;">
                <h3 style="margin-bottom: var(--spacing-md);">New Redemption Rule</h3>
                
                <div class="form-group">
                    <label>Rule Name</label>
                    <input type="text" name="name" required placeholder="e.g. $10 Cash for 1000 LP">
                </div>
                
                <div class="form-group">
                    <label>Description</label>
                    <textarea name="description" rows="2" placeholder="Internal note..."></textarea>
                </div>

                <div class="grid grid-2" style="gap: var(--spacing-md);">
                    <div class="form-group">
                        <label>LP Cost</label>
                        <input type="number" name="lp_cost" required min="1" value="100">
                    </div>
                    <div class="form-group">
                        <label>Value</label>
                        <input type="number" name="currency_value" required min="0.1" step="0.1" value="1.0">
                    </div>
                </div>

                <div class="grid grid-2" style="gap: var(--spacing-md);">
                     <div class="form-group">
                        <label>Target Balance</label>
                         <select name="target_balance">
                            <option value="CASH">CASH</option>
                            <option value="BONUS">BONUS</option>
                            <option value="TICKETS">TICKETS</option>
                        </select>
                    </div>
                     <div class="form-group">
                        <label>Tier Req.</label>
                         <select name="tier_requirement">
                            <option value="">None</option>
                            <option value="BRONZE">BRONZE</option>
                            <option value="SILVER">SILVER</option>
                            <option value="GOLD">GOLD</option>
                            <option value="PLATINUM">PLATINUM</option>
                        </select>
                    </div>
                </div>

                <div class="form-group">
                    <label>
                        <input type="checkbox" name="is_active" checked> Active Immediately
                    </label>
                </div>

                <div style="display: flex; gap: var(--spacing-sm); justify-content: flex-end; margin-top: var(--spacing-lg);">
                    <button type="button" class="btn btn-secondary" id="btn-cancel-red-rule">Cancel</button>
                    <button type="submit" class="btn btn-primary">Create Rule</button>
                </div>
            </form>
        </dialog>
    `;

    const rulesList = container.querySelector('#redemption-rules-list');
    const ruleSelect = container.querySelector('#redeem-rule-id');
    const executeForm = container.querySelector('#execute-redemption-form');
    const resultDiv = container.querySelector('#redemption-result');
    const expiryBtn = container.querySelector('#trigger-expiry-btn');
    const expiryResult = container.querySelector('#expiry-result');

    // Modal elements
    const modalCreate = container.querySelector('#create-red-rule-modal');
    const btnAddRule = container.querySelector('#add-redemption-rule-btn');
    const btnCancelCreate = container.querySelector('#btn-cancel-red-rule');
    const formCreate = container.querySelector('#create-red-rule-form');

    async function fetchRules() {
        try {
            const rules = await api.request('/api/redemption/rules');

            if (rules.length === 0) {
                rulesList.innerHTML = `
                    <div class="empty-state">
                        <p>No redemption rules found. Create one to get started.</p>
                    </div>
                `;
            } else {
                rulesList.innerHTML = rules.map(rule => `
                    <div class="card rule-card">
                        <div class="rule-header">
                            <h3>${rule.name}</h3>
                            <span class="badge ${rule.is_active ? 'badge-success' : 'badge-neutral'}">
                                ${rule.is_active ? 'Active' : 'Inactive'}
                            </span>
                        </div>
                        <p class="description">${rule.description || 'No description'}</p>
                        <div class="rule-details">
                            <div class="detail-item">
                                <span class="label">Cost:</span>
                                <span class="value">${rule.lp_cost} LP</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">Value:</span>
                                <span class="value">$${rule.currency_value}</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">Destination:</span>
                                <span class="value">${rule.target_balance}</span>
                            </div>
                        </div>
                    </div>
                `).join('');

                // Update select dropdown
                ruleSelect.innerHTML = '<option value="">Select a rule...</option>' +
                    rules.filter(r => r.is_active).map(r => `
                        <option value="${r.id}">${r.name} (${r.lp_cost} LP -> $${r.currency_value})</option>
                    `).join('');
            }
        } catch (error) {
            rulesList.innerHTML = `<p class="error">Error: ${error.message}</p>`;
        }
    }

    executeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const playerId = container.querySelector('#redeem-player-id').value;
        const ruleId = ruleSelect.value;

        resultDiv.style.display = 'block';
        resultDiv.className = 'result-message info';
        resultDiv.textContent = 'Processing redemption...';

        try {
            const response = await api.request('/api/redemption/redeem', {
                method: 'POST',
                body: JSON.stringify({
                    player_id: playerId,
                    rule_id: parseInt(ruleId)
                })
            });

            resultDiv.className = 'result-message success';
            resultDiv.innerHTML = `
                <strong>Success!</strong><br>
                Redeemed ${response.lp_deducted} LP for $${response.value_received}.<br>
                New LP Balance: ${response.new_lp_balance}
            `;
        } catch (error) {
            resultDiv.className = 'result-message error';
            resultDiv.textContent = error.message;
        }
    });

    // Expiry Button Listener
    expiryBtn.addEventListener('click', async () => {
        expiryResult.style.display = 'block';
        expiryResult.className = 'result-message info';
        expiryResult.textContent = 'Running expiry job...';

        try {
            const response = await api.request('/api/cron/expire-points', {
                method: 'POST'
            });
            expiryResult.className = 'result-message success';
            expiryResult.textContent = response.message;
        } catch (error) {
            expiryResult.className = 'result-message error';
            expiryResult.textContent = error.message;
        }
    });

    // Create Rule Modal Listeners
    btnAddRule.addEventListener('click', () => modalCreate.showModal());
    btnCancelCreate.addEventListener('click', () => modalCreate.close());

    formCreate.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(formCreate);

        // Build data object
        const data = {
            name: formData.get('name'),
            description: formData.get('description'),
            lp_cost: parseInt(formData.get('lp_cost')),
            currency_value: parseFloat(formData.get('currency_value')),
            target_balance: formData.get('target_balance'),
            is_active: formData.get('is_active') === 'on',
            tier_requirement: formData.get('tier_requirement') || null
        };

        try {
            await api.createRedemptionRule(data);
            modalCreate.close();
            formCreate.reset();
            await fetchRules(); // Refresh list
        } catch (error) {
            alert(`Failed to create rule: ${error.message}`);
        }
    });

    fetchRules();
}
