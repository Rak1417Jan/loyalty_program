import { CONFIG } from './config.js';

class ApiClient {
    constructor() {
        this.baseUrl = CONFIG.API_BASE_URL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        try {
            const response = await fetch(url, { ...options, headers });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `API Error: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API Request Failed: ${endpoint}`, error);
            throw error;
        }
    }

    // Players
    async getPlayers(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/api/players?${queryString}`);
    }

    async getPlayer(playerId) {
        return this.request(`/api/players/${playerId}`);
    }

    async createPlayer(playerData) {
        return this.request('/api/players', {
            method: 'POST',
            body: JSON.stringify(playerData)
        });
    }

    async updatePlayer(playerId, updateData) {
        return this.request(`/api/players/${playerId}`, {
            method: 'PUT',
            body: JSON.stringify(updateData)
        });
    }

    async importPlayers(file) {
        const formData = new FormData();
        formData.append('file', file);

        // Use fetch directly for FormData to let browser handle Content-Type boundary
        const url = `${this.baseUrl}/api/import/excel`;
        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Import failed: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Import Failed:', error);
            throw error;
        }
    }

    // Rules
    async getRules(activeOnly = false) {
        const queryString = activeOnly ? '?is_active=true' : '';
        return this.request(`/api/rules${queryString}`);
    }

    async getRule(ruleId) {
        return this.request(`/api/rules/${ruleId}`);
    }

    async createRule(ruleData) {
        return this.request('/api/rules', {
            method: 'POST',
            body: JSON.stringify(ruleData)
        });
    }

    async updateRule(ruleId, updateData) {
        return this.request(`/api/rules/${ruleId}`, {
            method: 'PUT',
            body: JSON.stringify(updateData)
        });
    }

    // Tiers
    async getTiers() {
        return this.request('/api/tiers');
    }

    async createTier(tierData) {
        return this.request('/api/tiers', {
            method: 'POST',
            body: JSON.stringify(tierData)
        });
    }

    // Wallet Operations
    async addLoyaltyPoints(data) {
        return this.request('/api/wallet/add-lp', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async addBonus(data) {
        return this.request('/api/wallet/add-bonus', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async getTransactions(playerId) {
        return this.request(`/api/analytics/transactions?player_id=${playerId}`);
    }

    // Analytics
    async getDashboardMetrics() {
        return this.request('/api/analytics/dashboard');
    }

    async getRewardHistory(status = '') {
        const queryString = status ? `?status=${status}` : '';
        return this.request(`/api/analytics/rewards${queryString}`);
    }

    // New Action & Redemption endpoints
    async completeKYC(playerId) {
        return this.request('/api/actions/kyc', {
            method: 'POST',
            body: JSON.stringify({ player_id: playerId })
        });
    }

    async updateProfileDepth(playerId, depth) {
        return this.request('/api/actions/profile-depth', {
            method: 'POST',
            body: JSON.stringify({ player_id: playerId, depth_percentage: depth })
        });
    }

    async getRedemptionRules() {
        return this.request('/api/redemption/rules');
    }

    async createRedemptionRule(ruleData) {
        return this.request('/api/redemption/rules', {
            method: 'POST',
            body: JSON.stringify(ruleData)
        });
    }

    async redeemPoints(data) {
        return this.request('/api/redemption/redeem', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async runExpiryJob() {
        return this.request('/api/cron/expire-points', {
            method: 'POST'
        });
    }
}

export const api = new ApiClient();
