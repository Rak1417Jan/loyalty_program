# Gaming Loyalty & Reward Program - Quick Reference

## 🚀 Quick Start (3 Steps)

### 1. Install & Setup
```bash
pip install -r requirements.txt
createdb loyalty_db  # Or use existing PostgreSQL database
```

### 2. Initialize
```bash
python quick_start.py
```

### 3. Start API
```bash
python main.py
# Visit: http://localhost:8000/docs
```

---

## 📊 System Overview

### Player Segments
- 🟢 **WINNING** - Profitable players (limit rewards)
- 🟡 **BREAKEVEN** - Neutral players (encourage volume)
- 🔴 **LOSING** - Negative P&L (retain with cashback)
- 🔵 **NEW** - Low activity (welcome bonuses)
- 👑 **VIP** - High volume (premium perks)

### Loyalty Currencies
- 🎯 **LP** (Loyalty Points) - Tier progression
- 🎁 **RP** (Reward Points) - Redeemable benefits
- 💰 **Bonus Balance** - Play-only money
- 🎟️ **Tickets** - Event entry

### Tiers
- 🥉 **Bronze** (0-999 LP) - Basic benefits
- 🥈 **Silver** (1K-9.9K LP) - 1.2x cashback
- 🥇 **Gold** (10K-49.9K LP) - 1.5x cashback + tournaments
- 💎 **Platinum** (50K+ LP) - 2x cashback + VIP perks

---

## 🎮 Core Features

### 1. Automatic Segmentation
Players are automatically classified based on behavior and metrics.

### 2. Rule-Based Rewards
Create custom reward rules with JSON conditions:
```json
{
  "conditions": {"segment": "LOSING", "net_loss_min": 100},
  "reward_config": {"formula": "net_loss * 0.10", "max_amount": 500}
}
```

### 3. Profit Safety
Every reward is validated for profitability using expected value calculations.

### 4. Fraud Detection
Automatic detection of:
- Bonus-only play
- Immediate withdrawals
- Bet manipulation
- Abnormal win rates

### 5. Multi-Currency Wallet
Separate balances with restrictions:
- Wagering requirements
- Expiry dates
- Max bet limits
- Eligible games

---

## 📁 File Structure

```
Loyalty_Reward_program/
├── analytics/           # Player metrics & segmentation
├── engine/             # Reward rules evaluation
├── wallet/             # Balance management
├── safety/             # Profit & fraud checks
├── data/               # Excel/CSV import
├── api/                # REST API endpoints
├── tests/              # Unit tests
├── models.py           # Database models
├── main.py             # FastAPI app
└── demo.py             # Feature demo
```

---

## 🔧 Common Tasks

### Import Player Data
```bash
curl -X POST "http://localhost:8000/api/import/excel" \
  -F "file=@players.csv"
```

### Create Reward Rule
```bash
curl -X POST "http://localhost:8000/api/rules" \
  -H "Content-Type: application/json" \
  -d '{"rule_id": "RULE_001", "name": "My Rule", ...}'
```

### View Dashboard
```bash
curl "http://localhost:8000/api/analytics/dashboard"
```

### Test Rule
```bash
curl -X POST "http://localhost:8000/api/rules/RULE_001/test" \
  -H "Content-Type: application/json" \
  -d '{"player_id": "P001"}'
```

---

## 📊 Excel Import Format

Required columns:
- `player_id` (string)
- `total_deposited` (float)
- `total_wagered` (float)
- `total_won` (float)

Optional columns:
- `sessions` (int)
- `playtime_hours` (float)
- `email` (string)
- `name` (string)

---

## ⚙️ Configuration (.env)

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/loyalty_db

# Reward Caps
MAX_DAILY_REWARD_PER_PLAYER=1000
MAX_WEEKLY_REWARD_PER_PLAYER=5000

# Tier Thresholds
TIER_SILVER_LP=1000
TIER_GOLD_LP=10000

# Segmentation
NEW_PLAYER_WAGER_THRESHOLD=1000
VIP_WAGER_THRESHOLD=100000

# Fraud Detection
ABUSE_SCORE_THRESHOLD=70
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run demo
python demo.py
```

---

## 📚 Documentation

- **README.md** - Complete documentation
- **walkthrough.md** - Implementation details
- **api_examples.py** - API usage examples
- **http://localhost:8000/docs** - Interactive API docs

---

## 🎯 Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/players` | GET | List players |
| `/api/players/{id}` | GET | Get player details |
| `/api/rules` | GET/POST | Manage reward rules |
| `/api/rules/{id}/test` | POST | Test rule |
| `/api/import/excel` | POST | Import data |
| `/api/analytics/dashboard` | GET | Dashboard metrics |
| `/api/wallet/add-lp` | POST | Add loyalty points |
| `/api/wallet/add-bonus` | POST | Add bonus balance |

---

## 💡 Example Workflow

1. **Import players** from Excel
2. **System automatically**:
   - Calculates metrics
   - Assigns segments
   - Evaluates reward rules
   - Issues rewards
3. **Monitor** via dashboard
4. **Adjust** rules based on ROI

---

## 🔒 Safety Mechanisms

✅ Expected value calculations  
✅ Daily/weekly/monthly caps  
✅ Wagering requirements  
✅ Bonus restrictions  
✅ Fraud detection  
✅ Abuse scoring  
✅ Automatic penalties  

---

## 📞 Support

For questions or issues:
1. Check README.md
2. Review walkthrough.md
3. Run demo.py
4. Check API docs at /docs

---

**Built with**: Python, FastAPI, SQLAlchemy, PostgreSQL, Pandas
