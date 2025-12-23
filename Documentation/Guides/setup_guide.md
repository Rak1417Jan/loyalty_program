# Setup Guide

Complete step-by-step guide to set up the Gaming Loyalty & Reward Program.

---

## Prerequisites

### Required Software

1. **Python 3.10 or higher**
   ```bash
   python --version  # Should be 3.10+
   ```

2. **PostgreSQL 12 or higher**
   ```bash
   psql --version  # Should be 12+
   ```

3. **pip** (Python package manager)
   ```bash
   pip --version
   ```

### Optional Software

- **Git** - For version control
- **Docker** - For containerized PostgreSQL (alternative to local install)
- **Postman** or **curl** - For API testing

---

## Installation Steps

### Step 1: Clone/Download Project

```bash
cd /path/to/your/projects
# If using git:
git clone <repository-url> Loyalty_Reward_program
cd Loyalty_Reward_program

# Or download and extract the project folder
```

---

### Step 2: Create Virtual Environment

**macOS/Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows**:
```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

---

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI
- SQLAlchemy
- PostgreSQL driver
- Pandas
- Pydantic
- Uvicorn
- And other dependencies

---

### Step 4: Setup PostgreSQL Database

#### Option A: Local PostgreSQL

1. **Start PostgreSQL** (if not already running)
   ```bash
   # macOS (Homebrew)
   brew services start postgresql@14
   
   # Linux
   sudo systemctl start postgresql
   
   # Windows
   # Start from Services or pgAdmin
   ```

2. **Create Database**
   ```bash
   createdb loyalty_db
   
   # Or using psql:
   psql postgres
   CREATE DATABASE loyalty_db;
   \q
   ```

3. **Verify Connection**
   ```bash
   psql loyalty_db
   \conninfo
   \q
   ```

#### Option B: Docker PostgreSQL

```bash
docker run --name loyalty-postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=loyalty_db \
  -p 5432:5432 \
  -d postgres:14

# Verify
docker ps
```

---

### Step 5: Configure Environment

1. **Copy environment template**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file**
   ```bash
   # Open in your editor
   nano .env  # or vim, code, etc.
   ```

3. **Update database connection**
   ```bash
   # For local PostgreSQL:
   DATABASE_URL=postgresql://your_username:your_password@localhost:5432/loyalty_db
   
   # For Docker PostgreSQL:
   DATABASE_URL=postgresql://postgres:password@localhost:5432/loyalty_db
   
   # Example for macOS with default postgres user:
   DATABASE_URL=postgresql://postgres@localhost:5432/loyalty_db
   ```

4. **Verify other settings** (optional)
   ```bash
   # Reward caps
   MAX_DAILY_REWARD_PER_PLAYER=1000
   MAX_WEEKLY_REWARD_PER_PLAYER=5000
   
   # Tier thresholds
   TIER_SILVER_LP=1000
   TIER_GOLD_LP=10000
   
   # Segmentation
   NEW_PLAYER_WAGER_THRESHOLD=1000
   VIP_WAGER_THRESHOLD=100000
   ```

---

### Step 6: Initialize Database

Run the quick start script:

```bash
python quick_start.py
```

This will:
1. ✅ Create all database tables
2. ✅ Create tier configuration (Bronze, Silver, Gold, Platinum)
3. ✅ Create sample reward rules
4. ✅ Import sample player data

**Expected Output**:
```
Step 1: Installing dependencies...
✓ Database initialized successfully!

Step 2: Setting up PostgreSQL database...
✓ Database initialized successfully!

Step 3: Initializing database tables...
✓ Database initialized successfully!

Step 4: Creating tier configuration...
Created tier: BRONZE
Created tier: SILVER
Created tier: GOLD
Created tier: PLATINUM
✓ Tiers created!

Step 5: Creating sample reward rules...
Created rule: LOSING_PLAYER_CASHBACK
Created rule: BREAKEVEN_PLAYER_BONUS
...
✓ Sample rules created!

Step 6: Importing sample player data...
✓ Import completed!
  - Players created: 10
  - Players updated: 0
  - Rewards issued: 3
```

---

### Step 7: Start API Server

```bash
python main.py
```

**Expected Output**:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

### Step 8: Verify Installation

1. **Check API Health**
   ```bash
   curl http://localhost:8000/health
   ```
   
   Expected: `{"status":"healthy"}`

2. **Open API Documentation**
   
   Visit in browser: `http://localhost:8000/docs`
   
   You should see the Swagger UI with all endpoints.

3. **Test Dashboard Endpoint**
   ```bash
   curl http://localhost:8000/api/analytics/dashboard
   ```
   
   Should return dashboard metrics with sample data.

---

## Verification Checklist

- [ ] Python 3.10+ installed
- [ ] PostgreSQL running
- [ ] Database `loyalty_db` created
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] `.env` file configured
- [ ] Database initialized (tables created)
- [ ] Sample data imported
- [ ] API server running
- [ ] API docs accessible at `/docs`
- [ ] Dashboard endpoint returns data

---

## Troubleshooting

### Issue: "ModuleNotFoundError"

**Solution**: Make sure virtual environment is activated and dependencies are installed
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

### Issue: "Database connection failed"

**Solution**: Check PostgreSQL is running and credentials are correct

```bash
# Check if PostgreSQL is running
pg_isready

# Test connection
psql -U postgres -d loyalty_db

# Verify DATABASE_URL in .env matches your setup
```

---

### Issue: "Port 8000 already in use"

**Solution**: Either stop the other process or change the port

```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or change port in main.py:
# uvicorn.run("main:app", host="0.0.0.0", port=8001)
```

---

### Issue: "Import failed - validation errors"

**Solution**: Check Excel file format matches requirements

Required columns:
- `player_id` (string)
- `total_deposited` (float)
- `total_wagered` (float)
- `total_won` (float)

See `sample_players.csv` for example format.

---

### Issue: "Permission denied" on database

**Solution**: Grant proper permissions

```sql
-- Connect as superuser
psql postgres

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE loyalty_db TO your_username;
```

---

## Next Steps

After successful setup:

1. **Run Demo** to see features in action:
   ```bash
   python demo.py
   ```

2. **Import Your Data**:
   - Prepare Excel/CSV file with player data
   - Use API endpoint: `POST /api/import/excel`

3. **Create Custom Rules**:
   - Use API endpoint: `POST /api/rules`
   - Or modify `create_sample_rules.py`

4. **Explore API**:
   - Visit `http://localhost:8000/docs`
   - Try different endpoints
   - Check `Documentation/Examples/api_examples.py`

---

## Production Deployment

For production deployment, see:
- [Architecture Documentation](../Architecture/system_architecture.md)
- Consider using:
  - Docker containers
  - Cloud-hosted PostgreSQL (RDS, Cloud SQL)
  - Load balancer for multiple API instances
  - Redis for caching
  - Proper authentication/authorization

---

## Getting Help

- **Documentation**: Check `Documentation/INDEX.md`
- **API Reference**: `Documentation/API/endpoints.md`
- **Examples**: `Documentation/Examples/`
- **Quick Reference**: `Documentation/Guides/QUICK_REFERENCE.md`
