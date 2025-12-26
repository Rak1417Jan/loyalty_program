#!/usr/bin/env python3
"""
Refresh all player metrics and segments
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from analytics.player_analytics import PlayerAnalytics
from analytics.segmentation import PlayerSegmentation
from database import Base, engine
import models

def refresh_all():
    db = SessionLocal()
    try:
        analytics = PlayerAnalytics(db)
        segmentation = PlayerSegmentation(db)
        
        players = db.query(models.Player).all()
        print(f"Refreshing {len(players)} players...")
        
        for p in players:
            # Update metrics
            analytics.update_player_metrics(p.player_id)
            # Update segment
            segmentation.update_player_segment(p.player_id)
            print(f"  ✓ Refreshed {p.player_id}: {p.segment.value} - {p.tier.value}")
            
    finally:
        db.close()

if __name__ == "__main__":
    refresh_all()
