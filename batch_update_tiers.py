#!/usr/bin/env python3
"""
Batch update all player tiers based on current LP balances
"""
import sys
import os

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from analytics.tier_service import TierService

def batch_update():
    db = SessionLocal()
    try:
        tier_service = TierService(db)
        print("Starting batch update of player tiers...")
        changes = tier_service.batch_update_all_tiers()
        print(f"Batch update complete. Tier changes: {changes}")
    finally:
        db.close()

if __name__ == "__main__":
    batch_update()
