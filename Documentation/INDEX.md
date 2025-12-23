# Documentation Index

Welcome to the **Gaming Loyalty & Reward Program** documentation.

## 📚 Documentation Structure

### 📖 Main Documentation
- **[README.md](README.md)** - Complete project overview, installation, and usage guide
- **[walkthrough.md](walkthrough.md)** - Detailed implementation walkthrough with architecture diagrams

### 📋 Planning Documents
- **[Planning/implementation_plan.md](Planning/implementation_plan.md)** - Technical implementation plan with component breakdown
- **[Planning/task.md](Planning/task.md)** - Task breakdown and completion checklist

### 🏗️ Architecture Documentation
- **[Architecture/database_schema.md](Architecture/database_schema.md)** - Database schema and model documentation
- **[Architecture/system_architecture.md](Architecture/system_architecture.md)** - System architecture overview
- **[Architecture/data_flow.md](Architecture/data_flow.md)** - Data flow diagrams and explanations

### 🔌 API Documentation
- **[API/endpoints.md](API/endpoints.md)** - Complete API endpoint reference
- **[API/schemas.md](API/schemas.md)** - Request/response schema documentation
- **[API/authentication.md](API/authentication.md)** - Authentication and authorization guide

### 📘 User Guides
- **[Guides/QUICK_REFERENCE.md](Guides/QUICK_REFERENCE.md)** - Quick reference for common tasks
- **[Guides/setup_guide.md](Guides/setup_guide.md)** - Detailed setup and installation guide
- **[Guides/excel_import_guide.md](Guides/excel_import_guide.md)** - Excel/CSV import format and usage
- **[Guides/reward_rules_guide.md](Guides/reward_rules_guide.md)** - Creating and managing reward rules
- **[Guides/configuration_guide.md](Guides/configuration_guide.md)** - Configuration options and environment variables

### 💡 Examples
- **[Examples/api_examples.py](Examples/api_examples.py)** - API usage examples with curl commands
- **[Examples/rule_examples.md](Examples/rule_examples.md)** - Sample reward rule configurations
- **[Examples/workflow_examples.md](Examples/workflow_examples.md)** - Common workflow examples

---

## 🚀 Quick Start

1. **New to the project?** Start with [README.md](README.md)
2. **Setting up?** Follow [Guides/setup_guide.md](Guides/setup_guide.md)
3. **Need quick reference?** Check [Guides/QUICK_REFERENCE.md](Guides/QUICK_REFERENCE.md)
4. **Understanding the system?** Read [walkthrough.md](walkthrough.md)
5. **Using the API?** See [API/endpoints.md](API/endpoints.md) and [Examples/api_examples.py](Examples/api_examples.py)

---

## 📊 Key Concepts

### Player Segmentation
Players are automatically classified into segments:
- 🟢 **WINNING** - Profitable players
- 🟡 **BREAKEVEN** - Neutral P&L
- 🔴 **LOSING** - Negative P&L (retention focus)
- 🔵 **NEW** - Low activity
- 👑 **VIP** - High volume

### Loyalty Currencies
- 🎯 **LP** (Loyalty Points) - Tier progression
- 🎁 **RP** (Reward Points) - Redeemable benefits
- 💰 **Bonus Balance** - Play-only money with wagering requirements
- 🎟️ **Tickets** - Event/contest entry

### Tier System
- 🥉 **Bronze** (0-999 LP)
- 🥈 **Silver** (1K-9.9K LP)
- 🥇 **Gold** (10K-49.9K LP)
- 💎 **Platinum** (50K+ LP)

---

## 🔧 Core Features

✅ **Automatic Player Segmentation** - Dynamic classification based on behavior  
✅ **Rule-Based Rewards** - Flexible JSON-based reward rules  
✅ **Profit Safety** - Expected value calculations ensure profitability  
✅ **Fraud Detection** - Automated abuse detection and prevention  
✅ **Multi-Currency Wallet** - Separate balances with restrictions  
✅ **Excel Import** - Bulk data import from Excel/CSV  
✅ **REST API** - Complete CRUD operations  
✅ **Analytics Dashboard** - ROI tracking and metrics  

---

## 📞 Support

- **Issues?** Check the troubleshooting section in [README.md](README.md)
- **Questions?** Review the [Guides](Guides/) section
- **API help?** See [Examples/api_examples.py](Examples/api_examples.py)

---

**Built with**: Python, FastAPI, SQLAlchemy, PostgreSQL, Pandas
