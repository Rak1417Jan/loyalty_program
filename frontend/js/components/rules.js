import { api } from '../api.js';
import { getBadgeClass } from '../utils.js';

export async function renderRules(container) {
    container.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Reward Rules</h3>
                <button id="btn-create-rule" class="btn btn-primary btn-sm">
                    <span class="icon">+</span> New Rule
                </button>
            </div>
            <div class="table-container">
                <table id="rules-table">
                    <thead>
                        <tr>
                            <th>Priority</th>
                            <th>Rule Name</th>
                            <th>Description</th>
                            <th>Conditions</th>
                            <th>Reward</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td colspan="7" style="text-align: center;">Loading rules...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Create Rule Modal -->
        <dialog id="create-rule-modal" style="padding: 0; border: none; border-radius: var(--radius-lg); box-shadow: var(--shadow-xl);">
            <form id="create-rule-form" style="padding: var(--spacing-lg); width: 600px;">
                <h3 style="margin-bottom: var(--spacing-md);">Configure New Reward Rule</h3>
                
                <div class="grid grid-2" style="gap: var(--spacing-md);">
                    <div class="form-group">
                        <label for="cr-id">Rule ID</label>
                        <input type="text" id="cr-id" name="rule_id" required placeholder="e.g. CASHBACK_10_PERCENT">
                    </div>
                    <div class="form-group">
                        <label for="cr-priority">Priority</label>
                        <input type="number" id="cr-priority" name="priority" value="100">
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="cr-name">Rule Name</label>
                    <input type="text" id="cr-name" name="name" required placeholder="Display Name">
                </div>

                <div class="form-group">
                    <label for="cr-desc">Description</label>
                    <textarea id="cr-desc" name="description" rows="2" placeholder="Internal description..."></textarea>
                </div>
                
                <div class="grid grid-2" style="gap: var(--spacing-md);">
                    <div class="form-group">
                        <label>Conditions (JSON)</label>
                        <textarea id="cr-conditions" name="conditions" rows="5" style="font-family: monospace; font-size: 0.8rem;">
{
    "kyc_completed": true,
    "monthly_active_days": {"min": 5}
}
                        </textarea>
                    </div>
                    <div class="form-group">
                        <label>Reward Logic (JSON)</label>
                        <textarea id="cr-reward-config" name="reward_config" rows="5" style="font-family: monospace; font-size: 0.8rem;">
{
    "type": "LOYALTY_POINTS",
    "amount": 500,
    "lp_expiry_days": 30
}
                        </textarea>
                    </div>
                </div>

                <div class="form-group">
                    <label>
                        <input type="checkbox" name="is_active" checked> Active Immediately
                    </label>
                </div>

                <div style="display: flex; gap: var(--spacing-sm); justify-content: flex-end; margin-top: var(--spacing-lg);">
                    <button type="button" class="btn btn-secondary" id="btn-cancel-rule">Cancel</button>
                    <button type="submit" class="btn btn-primary">Create Rule</button>
                </div>
            </form>
        </dialog>
    `;

    await loadRules();
    setupRuleListeners();
}

async function loadRules() {
    const tbody = document.querySelector('#rules-table tbody');
    try {
        const rules = await api.getRules();

        if (rules.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align: center;">No rules defined.</td></tr>`;
            return;
        }

        // Sort by priority (descending)
        rules.sort((a, b) => b.priority - a.priority);

        tbody.innerHTML = rules.map(rule => `
            <tr>
                <td style="font-weight: 600;">${rule.priority}</td>
                <td>
                    <div>${rule.name}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">${rule.rule_id}</div>
                </td>
                <td style="max-width: 200px; font-size: 0.875rem;">${rule.description || '-'}</td>
                <td>
                    <pre style="font-size: 0.75rem; background: var(--bg-body); padding: 4px; border-radius: 4px;">${JSON.stringify(rule.conditions, null, 1)}</pre>
                </td>
                <td>
                    <pre style="font-size: 0.75rem; background: var(--bg-body); padding: 4px; border-radius: 4px;">${JSON.stringify(rule.reward_config, null, 1)}</pre>
                </td>
                 <td>
                    <span class="${getBadgeClass(rule.is_active, 'status')}">
                        ${rule.is_active ? 'Active' : 'Inactive'}
                    </span>
                </td>
                <td>
                     <button class="btn btn-sm btn-secondary toggle-rule" data-id="${rule.rule_id}" data-active="${rule.is_active}">
                        ${rule.is_active ? 'Disable' : 'Enable'}
                     </button>
                </td>
            </tr>
        `).join('');

        // Add listeners for toggle buttons
        document.querySelectorAll('.toggle-rule').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const ruleId = e.target.dataset.id;
                const isActive = e.target.dataset.active === 'true';
                try {
                    await api.updateRule(ruleId, { is_active: !isActive });
                    await loadRules();
                } catch (err) {
                    alert('Error updating rule: ' + err.message);
                }
            });
        });

    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="7" style="color: var(--accent-red);">Error loading rules: ${error.message}</td></tr>`;
    }
}

function setupRuleListeners() {
    const modal = document.getElementById('create-rule-modal');
    const btnCreate = document.getElementById('btn-create-rule');
    const btnCancel = document.getElementById('btn-cancel-rule');
    const formCreate = document.getElementById('create-rule-form');

    btnCreate.addEventListener('click', () => modal.showModal());
    btnCancel.addEventListener('click', () => modal.close());

    formCreate.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(formCreate);

        try {
            const data = {
                rule_id: formData.get('rule_id'),
                name: formData.get('name'),
                description: formData.get('description'),
                priority: parseInt(formData.get('priority')),
                is_active: formData.get('is_active') === 'on',
                conditions: JSON.parse(formData.get('conditions')),
                reward_config: JSON.parse(formData.get('reward_config'))
            };

            await api.createRule(data);
            modal.close();
            formCreate.reset();
            await loadRules();
        } catch (error) {
            alert(`Failed to create rule: ${error.message} (Check JSON format)`);
        }
    });
}
