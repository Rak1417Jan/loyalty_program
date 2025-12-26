import { api } from '../api.js';

export async function renderTiers(container) {
    container.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Loyalty Tiers</h3>
                <button id="btn-create-tier" class="btn btn-primary btn-sm">
                    <span class="icon">+</span> Configure Tier
                </button>
            </div>
            <div class="table-container">
                <table id="tiers-table">
                    <thead>
                        <tr>
                            <th>Level</th>
                            <th>Min LP</th>
                            <th>Max LP</th>
                            <th>Requirements</th>
                            <th>Benefits</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td colspan="4" style="text-align: center;">Loading tiers...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Create Tier Modal -->
        <dialog id="create-tier-modal" style="padding: 0; border: none; border-radius: var(--radius-lg); box-shadow: var(--shadow-xl);">
            <form id="create-tier-form" style="padding: var(--spacing-lg); width: 450px;">
                <h3 style="margin-bottom: var(--spacing-md);">Configure Tier Level</h3>
                
                <div class="form-group">
                    <label for="ct-level">Tier Level</label>
                    <select id="ct-level" name="tier_level" required>
                        <option value="BRONZE">BRONZE</option>
                        <option value="SILVER">SILVER</option>
                        <option value="GOLD">GOLD</option>
                        <option value="PLATINUM">PLATINUM</option>
                    </select>
                </div>

                <div class="grid grid-2" style="gap: var(--spacing-md);">
                    <div class="form-group">
                        <label for="ct-min">Min LP</label>
                        <input type="number" id="ct-min" name="lp_min" required>
                    </div>
                    <div class="form-group">
                        <label for="ct-max">Max LP</label>
                        <input type="number" id="ct-max" name="lp_max">
                        <small style="color: var(--text-light);">Leave empty for infinite (top tier)</small>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Behavioral Requirements (JSON)</label>
                    <textarea id="ct-requirements" name="requirements" rows="4" style="font-family: monospace; font-size: 0.8rem;">
{
    "kyc_completed": true,
    "monthly_active_days_min": 5
}
                    </textarea>
                    <small style="color: var(--text-light);">Additional conditions besides LP balance</small>
                </div>

                <div class="form-group">
                    <label>Benefits (JSON)</label>
                    <textarea id="ct-benefits" name="benefits" rows="4" style="font-family: monospace; font-size: 0.8rem;">
{
    "cashback_multiplier": 1.0,
    "free_plays_per_month": 5
}
                    </textarea>
                </div>

                <div style="display: flex; gap: var(--spacing-sm); justify-content: flex-end; margin-top: var(--spacing-lg);">
                    <button type="button" class="btn btn-secondary" id="btn-cancel-tier">Cancel</button>
                    <button type="submit" class="btn btn-primary">Save Tier</button>
                </div>
            </form>
        </dialog>
    `;

    await loadTiers();
    setupTierListeners();
}

async function loadTiers() {
    const tbody = document.querySelector('#tiers-table tbody');
    try {
        const tiers = await api.getTiers();

        if (tiers.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" style="text-align: center;">No tiers configured.</td></tr>`;
            return;
        }

        // Sort by min LP
        tiers.sort((a, b) => a.lp_min - b.lp_min);

        tbody.innerHTML = tiers.map(tier => `
            <tr>
                <td><span class="badge badge-${tier.tier_level.toLowerCase()}" style="font-size: 0.9rem;">${tier.tier_level}</span></td>
                <td>${tier.lp_min.toLocaleString()}</td>
                <td>${tier.lp_max ? tier.lp_max.toLocaleString() : '∞'}</td>
                <td>
                    <pre style="font-size: 0.75rem; background: var(--bg-body); padding: 4px; border-radius: 4px;">${JSON.stringify(tier.requirements || {}, null, 1)}</pre>
                </td>
                <td>
                    <pre style="font-size: 0.75rem; background: var(--bg-body); padding: 4px; border-radius: 4px;">${JSON.stringify(tier.benefits, null, 1)}</pre>
                </td>
            </tr>
        `).join('');

    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="4" style="color: var(--accent-red);">Error loading tiers: ${error.message}</td></tr>`;
    }
}

function setupTierListeners() {
    const modal = document.getElementById('create-tier-modal');
    const btnCreate = document.getElementById('btn-create-tier');
    const btnCancel = document.getElementById('btn-cancel-tier');
    const formCreate = document.getElementById('create-tier-form');

    btnCreate.addEventListener('click', () => modal.showModal());
    btnCancel.addEventListener('click', () => modal.close());

    formCreate.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(formCreate);

        try {
            const data = {
                tier_level: formData.get('tier_level'),
                lp_min: parseInt(formData.get('lp_min')),
                lp_max: formData.get('lp_max') ? parseInt(formData.get('lp_max')) : null,
                requirements: JSON.parse(formData.get('requirements') || '{}'),
                benefits: JSON.parse(formData.get('benefits') || '{}')
            };

            await api.createTier(data);
            modal.close();
            formCreate.reset();
            await loadTiers();
        } catch (error) {
            alert(`Failed to save tier: ${error.message}`);
        }
    });
}
