"""
API Usage Examples
"""

# Example 1: List all players
"""
GET http://localhost:8000/api/players

Response:
[
  {
    "player_id": "P001",
    "email": "player1@example.com",
    "name": "John Doe",
    "segment": "LOSING",
    "tier": "BRONZE",
    "risk_score": 0,
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
"""

# Example 2: Create a reward rule
"""
POST http://localhost:8000/api/rules
Content-Type: application/json

{
  "rule_id": "CUSTOM_RULE_001",
  "name": "Weekend Warrior Bonus",
  "description": "Bonus for players who play on weekends",
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
"""

# Example 3: Test a rule against a player
"""
POST http://localhost:8000/api/rules/LOSING_PLAYER_CASHBACK/test
Content-Type: application/json

{
  "player_id": "P001"
}

Response:
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
"""

# Example 4: Import Excel file
"""
POST http://localhost:8000/api/import/excel
Content-Type: multipart/form-data

file: [select your Excel/CSV file]

Response:
{
  "success": true,
  "total_rows": 100,
  "players_created": 95,
  "players_updated": 5,
  "rewards_issued": 23,
  "errors": []
}
"""

# Example 5: Get analytics dashboard
"""
GET http://localhost:8000/api/analytics/dashboard

Response:
{
  "total_players": 100,
  "active_players": 95,
  "total_rewards_issued": 234,
  "total_reward_cost": 12500.50,
  "segment_distribution": [
    {"segment": "NEW", "count": 20, "percentage": 20.0},
    {"segment": "LOSING", "count": 35, "percentage": 35.0},
    {"segment": "BREAKEVEN", "count": 25, "percentage": 25.0},
    {"segment": "WINNING", "count": 15, "percentage": 15.0},
    {"segment": "VIP", "count": 5, "percentage": 5.0}
  ]
}
"""

# Example 6: Add loyalty points manually
"""
POST http://localhost:8000/api/wallet/add-lp
Content-Type: application/json

{
  "player_id": "P001",
  "amount": 100.0,
  "source": "MANUAL",
  "description": "Compensation for technical issue"
}

Response:
{
  "success": true,
  "transaction_id": 1234,
  "new_balance": 250.0,
  "message": "Added 100.0 LP"
}
"""

# Example 7: Add bonus balance
"""
POST http://localhost:8000/api/wallet/add-bonus
Content-Type: application/json

{
  "player_id": "P001",
  "amount": 50.0,
  "wagering_requirement": 500.0,
  "expiry_hours": 48,
  "max_bet": 10.0,
  "eligible_games": ["slots", "roulette"],
  "description": "Special promotion bonus"
}

Response:
{
  "success": true,
  "transaction_id": 1235,
  "new_balance": 100.0,
  "message": "Added 50.0 bonus balance"
}
"""

# Example 8: Get player reward history
"""
GET http://localhost:8000/api/analytics/rewards?player_id=P001

Response:
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
"""

# Example 9: Batch process players
"""
POST http://localhost:8000/api/batch/process
Content-Type: application/json

{
  "player_ids": ["P001", "P002", "P003"],
  "trigger_rewards": true
}

Response:
{
  "processed": 3,
  "rewards_issued": 2
}
"""

# Example 10: Update player
"""
PUT http://localhost:8000/api/players/P001
Content-Type: application/json

{
  "email": "newemail@example.com",
  "is_blocked": false
}

Response:
{
  "player_id": "P001",
  "email": "newemail@example.com",
  "segment": "LOSING",
  "tier": "BRONZE",
  "is_blocked": false
}
"""

print("API Examples loaded. Use these as reference for API calls.")
print("Full API documentation available at: http://localhost:8000/docs")
