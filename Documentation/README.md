# Gaming Loyalty & Reward Program

> **A scalable, customizable, profit-safe loyalty and reward system for gaming platforms**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)]()

---

## 🎯 Overview

This system increases player lifetime value (LTV), reduces churn, and ensures platform profitability through:

- **Intelligent Player Segmentation** - Automatic classification into NEW, WINNING, BREAKEVEN, LOSING, and VIP segments
- **Rule-Based Rewards** - Flexible JSON-based reward rules with conditions and formulas
- **Profit Safety** - Expected value calculations ensure every reward is profitable
- **Fraud Detection** - Automated abuse detection and prevention
- **Multi-Currency Wallet** - Loyalty Points, Reward Points, Bonus Balance, and Tickets
- **Complete REST API** - 20+ endpoints for full system control

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup database
createdb loyalty_db

# 3. Initialize system
python quick_start.py

# 4. Start API server
python main.py

# Visit: http://localhost:8000/docs
```

**That's it!** The system is now running with sample data and rules.

---

## 📚 Documentation

- **[📖 Complete Documentation Index](Documentation/INDEX.md)** - Start here
- **[🏗️ System Architecture](Documentation/Architecture/system_architecture.md)** - Architecture overview
- **[🗄️ Database Schema](Documentation/Architecture/database_schema.md)** - Data model
- **[🔌 API Reference](Documentation/API/endpoints.md)** - All endpoints
- **[📘 Setup Guide](Documentation/Guides/setup_guide.md)** - Detailed installation
- **[⚡ Quick Reference](Documentation/Guides/QUICK_REFERENCE.md)** - Common tasks

---

## ✨ Key Features

### 🎮 Player Segmentation

Players are automatically classified based on behavior:

| Segment | Description | Reward Strategy |
|---------|-------------|-----------------|
| 🟢 WINNING | Profitable players | Limit rewards, offer VIP perks |
| 🟡 BREAKEVEN | Neutral P&L | Encourage volume |
| 🔴 LOSING | Negative P&L | Retention with cashback |
| 🔵 NEW | Low activity | Welcome bonuses |
| 👑 VIP | High volume | Premium benefits |

### 💰 Multi-Currency System

- **🎯 LP** (Loyalty Points) - Tier progression
- **🎁 RP** (Reward Points) - Redeemable benefits
- **💵 Bonus Balance** - Play-only money with wagering requirements
- **🎟️ Tickets** - Event/contest entry

### 🏆 Tier System

| Tier | LP Range | Benefits |
|------|----------|----------|
| 🥉 Bronze | 0-999 | Basic benefits |
| 🥈 Silver | 1K-9.9K | 1.2x cashback |
| 🥇 Gold | 10K-49.9K | 1.5x cashback + tournaments |
| 💎 Platinum | 50K+ | 2x cashback + VIP perks |

### 🎲 Rule-Based Rewards

Create custom reward rules with JSON:

```json
{
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
  }
}
```

### 🛡️ Safety Mechanisms

✅ **Profit Safety** - Expected value calculations  
✅ **Fraud Detection** - Abuse pattern recognition  
✅ **Reward Caps** - Daily/weekly/monthly limits  
✅ **Wagering Requirements** - Bonus restrictions  
✅ **Risk Scoring** - Automated penalties  

---

## 📊 System Architecture

```
Excel/CSV → Data Importer → Player Analytics → Segmentation
                                    ↓
                            Rules Engine
                                    ↓
                    Profit Safety ← → Fraud Detector
                                    ↓
                            Wallet Manager
                                    ↓
                            PostgreSQL Database
```

---

## 🔧 Technology Stack

| Component | Technology |
|-----------|-----------|
| API Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Data Processing | Pandas |
| Server | Uvicorn |
| Testing | Pytest |

---

## 📁 Project Structure

```
Loyalty_Reward_program/
├── Documentation/          # Complete documentation
│   ├── INDEX.md           # Documentation index
│   ├── README.md          # This file
│   ├── walkthrough.md     # Implementation details
│   ├── Planning/          # Implementation plan & tasks
│   ├── Architecture/      # System & database architecture
│   ├── API/              # API documentation
│   ├── Guides/           # User guides
│   └── Examples/         # Code examples
│
├── analytics/            # Player analytics & segmentation
├── engine/              # Reward rules engine
├── wallet/              # Balance management
├── safety/              # Profit & fraud checks
├── data/                # Excel/CSV import
├── api/                 # REST API endpoints
├── tests/               # Unit tests
│
├── models.py            # Database models
├── main.py              # FastAPI application
├── quick_start.py       # Setup script
├── demo.py              # Feature demo
└── sample_players.csv   # Sample data
```

---

## 💡 Usage Examples

### Import Player Data

```bash
curl -X POST "http://localhost:8000/api/import/excel" \
  -F "file=@players.csv"
```

### Create Reward Rule

```bash
curl -X POST "http://localhost:8000/api/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "rule_id": "WEEKEND_BONUS",
    "name": "Weekend Warrior Bonus",
    "priority": 5,
    "conditions": {"total_wagered_min": 500},
    "reward_config": {
      "type": "BONUS_BALANCE",
      "formula": "total_wagered * 0.05",
      "max_amount": 200
    }
  }'
```

### View Dashboard

```bash
curl "http://localhost:8000/api/analytics/dashboard"
```

More examples in [Documentation/Examples/api_examples.py](Documentation/Examples/api_examples.py)

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run demo
python demo.py
```

---

## 📈 Excel Import Format

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

See `sample_players.csv` for example.

---

## ⚙️ Configuration

Edit `.env` file:

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
```

---

## 🚀 Production Deployment

For production:
1. Use cloud-hosted PostgreSQL (RDS, Cloud SQL)
2. Deploy API in Docker containers
3. Add authentication/authorization
4. Set up Redis for caching
5. Configure load balancer
6. Enable monitoring and logging

See [Architecture Documentation](Documentation/Architecture/system_architecture.md) for details.

---

## 📞 Support

- **Setup Issues**: Check [Setup Guide](Documentation/Guides/setup_guide.md)
- **API Questions**: See [API Reference](Documentation/API/endpoints.md)
- **Examples**: Browse [Examples](Documentation/Examples/)
- **Quick Help**: [Quick Reference](Documentation/Guides/QUICK_REFERENCE.md)

---

## 📄 License

Proprietary - All rights reserved

---

## 🎯 What Makes This System Unique

✅ **Profit-First Design** - Every reward is validated for profitability  
✅ **Scalable Architecture** - Handles millions of players  
✅ **Flexible Rules** - JSON-based configuration, no code changes  
✅ **Fraud-Resistant** - Automated abuse detection  
✅ **Production-Ready** - Complete API, documentation, and tests  
✅ **Easy to Use** - Setup in 3 commands  

---

**Built with ❤️ for gaming platforms that care about profitability and player retention**
