#!/usr/bin/env python3
"""
Reset transactions and metrics for P001-P010 to allow clean re-import
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import models

def reset_data():
    db = SessionLocal()
    try:
        player_ids = [f"P{i:03d}" for i in range(1, 11)]
        print(f"Resetting data for {len(player_ids)} players...")
        
        # Delete transactions
        tx_count = db.query(models.Transaction).filter(
            models.Transaction.player_id.in_(player_ids)
        ).delete(synchronize_session=False)
        print(f"  Deleted {tx_count} transactions")
        
        # Reset metrics
        metrics = db.query(models.PlayerMetrics).filter(
            models.PlayerMetrics.player_id.in_(player_ids)
        ).all()
        for m in metrics:
            m.total_deposited = 0
            m.total_wagered = 0
            m.total_won = 0
            m.net_pnl = 0
            m.total_sessions = 0
            
        print(f"  Reset metrics for {len(metrics)} players")
        
        # Reset LP to fresh start (except what we want to test)
        # Actually let's just let the import handle it
        
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    reset_data()
