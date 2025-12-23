# API Endpoints Reference

Complete reference for all REST API endpoints.

**Base URL**: `http://localhost:8000`  
**API Documentation**: `http://localhost:8000/docs` (Swagger UI)

---

## Player Management

### List Players

```http
GET /api/players
```

**Query Parameters**:
- `segment` (optional): Filter by segment (NEW, WINNING, BREAKEVEN, LOSING, VIP)
- `tier` (optional): Filter by tier (BRONZE, SILVER, GOLD, PLATINUM)
- `is_active` (optional): Filter by active status (true/false)
- `skip` (optional): Pagination offset (default: 0)
- `limit` (optional): Results per page (default: 100, max: 100)

**Response**: `200 OK`
```json
[
  {
    "player_id": "P001",
    "email": "player@example.com",
    "name": "John Doe",
    "segment": "LOSING",
    "tier": "BRONZE",
    "risk_score": 15,
    "is_active": true,
    "is_blocked": false,
    "created_at": "2025-12-23T10:00:00Z",
    "metrics": {
      "total_deposited": 5000.0,
      "total_wagered": 15000.0,
      "total_won": 12000.0,
      "net_pnl": -3000.0
    },
    "balances": {
      "lp_balance": 150.0,
      "bonus_balance": 50.0
    }
  }
]
```

---

### Get Player Details

```http
GET /api/players/{player_id}
```

**Response**: `200 OK` - Same structure as list players  
**Errors**: `404 Not Found` - Player not found

---

### Create Player

```http
POST /api/players
```

**Request Body**:
```json
{
  "player_id": "P001",
  "email": "player@example.com",
  "name": "John Doe"
}
```

**Response**: `200 OK` - Created player object  
**Errors**: `400 Bad Request` - Player already exists

---

### Update Player

```http
PUT /api/players/{player_id}
```

**Request Body**:
```json
{
  "email": "newemail@example.com",
  "is_active": true,
  "is_blocked": false
}
```

**Response**: `200 OK` - Updated player object  
**Errors**: `404 Not Found` - Player not found

---

### Delete Player

```http
DELETE /api/players/{player_id}
```

**Response**: `200 OK`
```json
{
  "message": "Player P001 deactivated"
}
```

**Errors**: `404 Not Found` - Player not found

---

## Reward Rules Management

### List Rules

```http
GET /api/rules
```

**Query Parameters**:
- `is_active` (optional): Filter by active status

**Response**: `200 OK`
```json
[
  {
    "rule_id": "LOSING_PLAYER_CASHBACK",
    "name": "Losing Player 10% Cashback",
    "description": "Give 10% cashback to losing players",
    "priority": 10,
    "is_active": true,
    "conditions": {
      "segment": "LOSING",
      "net_loss_min": 100,
      "session_count_min": 3
    },
    "reward_config": {
      "type": "BONUS_BALANCE",
      "formula": "net_loss * 0.10",
      "max_amount": 500,
      "wagering_requirement": 10,
      "expiry_hours": 48
    },
    "created_at": "2025-12-23T10:00:00Z"
  }
]
```

---

### Get Rule

```http
GET /api/rules/{rule_id}
```

**Response**: `200 OK` - Rule object  
**Errors**: `404 Not Found` - Rule not found

---

### Create Rule

```http
POST /api/rules
```

**Request Body**:
```json
{
  "rule_id": "CUSTOM_RULE_001",
  "name": "Weekend Bonus",
  "description": "Bonus for weekend players",
  "priority": 5,
  "is_active": true,
  "conditions": {
    "total_wagered_min": 500,
    "session_count_min": 2
  },
  "reward_config": {
    "type": "BONUS_BALANCE",
    "formula": "total_wagered * 0.05",
    "max_amount": 200,
    "wagering_requirement": 8,
    "expiry_hours": 48
  }
}
```

**Response**: `200 OK` - Created rule object  
**Errors**: `400 Bad Request` - Rule already exists

---

### Update Rule

```http
PUT /api/rules/{rule_id}
```

**Request Body**: (all fields optional)
```json
{
  "name": "Updated Name",
  "priority": 15,
  "is_active": false
}
```

**Response**: `200 OK` - Updated rule object  
**Errors**: `404 Not Found` - Rule not found

---

### Delete Rule

```http
DELETE /api/rules/{rule_id}
```

**Response**: `200 OK`
```json
{
  "message": "Rule CUSTOM_RULE_001 deleted"
}
```

---

### Test Rule

```http
POST /api/rules/{rule_id}/test
```

**Request Body**:
```json
{
  "player_id": "P001"
}
```

**Response**: `200 OK`
```json
{
  "matches": true,
  "reward_amount": 300.0,
  "player_state": {
    "player_id": "P001",
    "segment": "LOSING",
    "net_loss": 3000.0,
    "session_count": 25
  }
}
```

---

## Tier Management

### List Tiers

```http
GET /api/tiers
```

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "tier_level": "BRONZE",
    "lp_min": 0,
    "lp_max": 999,
    "benefits": {
      "cashback_multiplier": 1.0,
      "free_plays_per_month": 0
    },
    "created_at": "2025-12-23T10:00:00Z"
  }
]
```

---

### Create Tier

```http
POST /api/tiers
```

**Request Body**:
```json
{
  "tier_level": "DIAMOND",
  "lp_min": 100000,
  "lp_max": null,
  "benefits": {
    "cashback_multiplier": 3.0,
    "free_plays_per_month": 50
  }
}
```

---

### Update Tier

```http
PUT /api/tiers/{tier_id}
```

**Request Body**: (all fields optional)
```json
{
  "lp_min": 50000,
  "benefits": {
    "cashback_multiplier": 2.5
  }
}
```

---

## Data Import

### Import Excel/CSV

```http
POST /api/import/excel
Content-Type: multipart/form-data
```

**Form Data**:
- `file`: Excel or CSV file

**Response**: `200 OK`
```json
{
  "success": true,
  "total_rows": 100,
  "players_created": 95,
  "players_updated": 5,
  "rewards_issued": 23,
  "errors": []
}
```

---

### Batch Process Players

```http
POST /api/batch/process
```

**Request Body**:
```json
{
  "player_ids": ["P001", "P002", "P003"],
  "trigger_rewards": true
}
```

**Response**: `200 OK`
```json
{
  "processed": 3,
  "rewards_issued": 2
}
```

---

## Analytics

### Dashboard

```http
GET /api/analytics/dashboard
```

**Response**: `200 OK`
```json
{
  "total_players": 100,
  "active_players": 95,
  "total_rewards_issued": 234,
  "total_reward_cost": 12500.50,
  "segment_distribution": [
    {"segment": "NEW", "count": 20, "percentage": 20.0},
    {"segment": "LOSING", "count": 35, "percentage": 35.0}
  ]
}
```

---

### Reward History

```http
GET /api/analytics/rewards
```

**Query Parameters**:
- `player_id` (optional): Filter by player
- `status` (optional): Filter by status (PENDING, ACTIVE, COMPLETED, EXPIRED)
- `skip` (optional): Pagination offset
- `limit` (optional): Results per page

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "player_id": "P001",
    "rule_id": "LOSING_PLAYER_CASHBACK",
    "reward_type": "BONUS_BALANCE",
    "amount": 300.0,
    "currency_type": "BONUS",
    "status": "ACTIVE",
    "wagering_required": 3000.0,
    "wagering_completed": 1500.0,
    "issued_at": "2025-12-23T10:00:00Z",
    "expires_at": "2025-12-25T10:00:00Z"
  }
]
```

---

### Transaction History

```http
GET /api/analytics/transactions?player_id={player_id}
```

**Query Parameters**:
- `player_id` (required): Player ID
- `skip` (optional): Pagination offset
- `limit` (optional): Results per page

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "player_id": "P001",
    "transaction_type": "DEPOSIT",
    "currency_type": null,
    "amount": 1000.0,
    "balance_before": 0.0,
    "balance_after": 1000.0,
    "description": "Initial deposit",
    "created_at": "2025-12-23T10:00:00Z"
  }
]
```

---

## Wallet Operations

### Add Loyalty Points

```http
POST /api/wallet/add-lp
```

**Request Body**:
```json
{
  "player_id": "P001",
  "amount": 100.0,
  "source": "MANUAL",
  "description": "Compensation bonus"
}
```

**Response**: `200 OK`
```json
{
  "success": true,
  "transaction_id": 1234,
  "new_balance": 250.0,
  "message": "Added 100.0 LP"
}
```

---

### Add Bonus Balance

```http
POST /api/wallet/add-bonus
```

**Request Body**:
```json
{
  "player_id": "P001",
  "amount": 50.0,
  "wagering_requirement": 500.0,
  "expiry_hours": 48,
  "max_bet": 10.0,
  "eligible_games": ["slots", "roulette"],
  "description": "Special promotion"
}
```

**Response**: `200 OK`
```json
{
  "success": true,
  "transaction_id": 1235,
  "new_balance": 100.0,
  "message": "Added 50.0 bonus balance"
}
```

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

Currently not implemented. Recommended for production:
- 100 requests/minute per IP for general endpoints
- 10 requests/minute for import endpoints

---

## Authentication

Currently not implemented. Recommended for production:
- JWT token-based authentication
- API key for server-to-server communication
- Role-based access control
