// Utility Functions

export const formatCurrency = (value, type) => {
    switch (type) {
        case 'BONUS_BALANCE':
        case 'CASH':
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD'
            }).format(value);
        case 'LP':
            return `${value.toLocaleString()} LP`;
        case 'RP':
            return `${value.toLocaleString()} RP`;
        case 'TICKETS':
            return `${value} 🎫`;
        default:
            return value.toLocaleString();
    }
};

export const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

export const capitalize = (str) => {
    if (!str) return '';
    return str.replace('_', ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
};

export const getBadgeClass = (value, type) => {
    if (type === 'tier') {
        const tier = (value || '').toLowerCase();
        return `badge badge-${tier}`;
    }

    if (type === 'status') {
        switch (value) {
            case true: return 'badge badge-green'; // Active
            case false: return 'badge badge-red'; // Inactive/Blocked
            case 'NEW': return 'badge badge-blue';
            case 'VIP': return 'badge badge-purple';
            case 'LOSING': return 'badge badge-red';
            case 'WINNING': return 'badge badge-green';
            case 'BREAKEVEN': return 'badge badge-yellow';
            default: return 'badge badge-gray';
        }
    }
    return 'badge badge-gray';
};
