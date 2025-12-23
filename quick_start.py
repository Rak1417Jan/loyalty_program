"""
Quick Start Guide - Gaming Loyalty & Reward Program
"""

# Step 1: Install dependencies
print("Step 1: Installing dependencies...")
print("Run: pip install -r requirements.txt")
print()

# Step 2: Setup database
print("Step 2: Setting up PostgreSQL database...")
print("Commands:")
print("  createdb loyalty_db")
print("  # Or use your existing PostgreSQL database")
print()

# Step 3: Initialize database
print("Step 3: Initializing database tables...")
from database import init_db
try:
    init_db()
    print("✓ Database initialized successfully!")
except Exception as e:
    print(f"✗ Error: {e}")
    print("Make sure PostgreSQL is running and DATABASE_URL in .env is correct")
print()

# Step 4: Create tiers
print("Step 4: Creating tier configuration...")
try:
    from create_tiers import create_tiers
    create_tiers()
    print("✓ Tiers created!")
except Exception as e:
    print(f"✗ Error: {e}")
print()

# Step 5: Create sample rules
print("Step 5: Creating sample reward rules...")
try:
    from create_sample_rules import create_sample_rules
    create_sample_rules()
    print("✓ Sample rules created!")
except Exception as e:
    print(f"✗ Error: {e}")
print()

# Step 6: Import sample data
print("Step 6: Importing sample player data...")
try:
    from database import SessionLocal
    from data.excel_importer import ExcelImporter
    
    db = SessionLocal()
    importer = ExcelImporter(db)
    result = importer.import_player_data("sample_players.csv")
    
    print(f"✓ Import completed!")
    print(f"  - Players created: {result['players_created']}")
    print(f"  - Players updated: {result['players_updated']}")
    print(f"  - Rewards issued: {result['rewards_issued']}")
    
    db.close()
except Exception as e:
    print(f"✗ Error: {e}")
print()

# Step 7: Start API server
print("Step 7: Starting API server...")
print("Run: python main.py")
print()
print("API will be available at: http://localhost:8000")
print("API docs: http://localhost:8000/docs")
print()

print("=" * 60)
print("QUICK START COMPLETE!")
print("=" * 60)
print()
print("Next steps:")
print("1. Visit http://localhost:8000/docs to explore the API")
print("2. Check dashboard: GET /api/analytics/dashboard")
print("3. View players: GET /api/players")
print("4. Test reward rules: POST /api/rules/{rule_id}/test")
print()
