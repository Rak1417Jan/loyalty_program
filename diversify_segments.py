#!/usr/bin/env python3
"""
Diversify player segments by injecting specific transaction patterns
"""
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from analytics.player_analytics import PlayerAnalytics
from analytics.segmentation import PlayerSegmentation
import models
from models import Transaction, TransactionType, CurrencyType, PlayerSegment

def inject_data():
    db = SessionLocal()
    try:
        analytics = PlayerAnalytics(db)
        segmentation = PlayerSegmentation(db)
        
        # 1. P004 -> VIP (Needs > 100k wager, > 100 sessions)
        print("Diversifying P004 -> VIP...")
        db.add_all([
            Transaction(player_id="P004", transaction_type=TransactionType.DEPOSIT, currency_type=CurrencyType.CASH, amount=50000, balance_before=0, balance_after=50000, description="VIP Deposit"),
            Transaction(player_id="P004", transaction_type=TransactionType.WAGER, currency_type=CurrencyType.CASH, amount=150000, balance_before=50000, balance_after=0, description="VIP High Volume Wager"),
            Transaction(player_id="P004", transaction_type=TransactionType.WIN, currency_type=CurrencyType.CASH, amount=120000, balance_before=0, balance_after=120000, description="VIP Winning")
        ])
        db.flush()
        tx_count = db.query(models.Transaction).filter(models.Transaction.player_id == "P004").count()
        print(f"  P004 now has {tx_count} transactions")
        analytics.update_player_metrics("P004", {"sessions": 120, "playtime_hours": 200.0})
        
        # 2. P005 -> WINNING (Needs +PnL, W/L ratio > 1.1)
        print("Diversifying P005 -> WINNING...")
        db.add_all([
            Transaction(player_id="P005", transaction_type=TransactionType.DEPOSIT, currency_type=CurrencyType.CASH, amount=5000, balance_before=0, balance_after=5000, description="Deposit"),
            Transaction(player_id="P005", transaction_type=TransactionType.WAGER, currency_type=CurrencyType.CASH, amount=5000, balance_before=5000, balance_after=0, description="Wager"),
            Transaction(player_id="P005", transaction_type=TransactionType.WIN, currency_type=CurrencyType.CASH, amount=15000, balance_before=0, balance_after=15000, description="Big Win")
        ])
        db.flush()
        analytics.update_player_metrics("P005", {"sessions": 10, "playtime_hours": 5.0})

        # 3. P006 -> BREAKEVEN (|PnL| < 5% of wager)
        # Wager: 10000, PnL should be +/- 500
        print("Diversifying P006 -> BREAKEVEN...")
        db.add_all([
            Transaction(player_id="P006", transaction_type=TransactionType.DEPOSIT, currency_type=CurrencyType.CASH, amount=10000, balance_before=0, balance_after=10000, description="Deposit"),
            Transaction(player_id="P006", transaction_type=TransactionType.WAGER, currency_type=CurrencyType.CASH, amount=10000, balance_before=10000, balance_after=0, description="Wager"),
            Transaction(player_id="P006", transaction_type=TransactionType.WIN, currency_type=CurrencyType.CASH, amount=10200, balance_before=0, balance_after=10200, description="Near Breakeven Win")
        ])
        db.flush()
        analytics.update_player_metrics("P006", {"sessions": 15, "playtime_hours": 10.0})

        # 4. P010 -> WINNING
        print("Diversifying P010 -> WINNING...")
        db.add_all([
            Transaction(player_id="P010", transaction_type=TransactionType.DEPOSIT, currency_type=CurrencyType.CASH, amount=1000, balance_before=0, balance_after=1000, description="Deposit"),
            Transaction(player_id="P010", transaction_type=TransactionType.WAGER, currency_type=CurrencyType.CASH, amount=1000, balance_before=1000, balance_after=0, description="Wager"),
            Transaction(player_id="P010", transaction_type=TransactionType.WIN, currency_type=CurrencyType.CASH, amount=2500, balance_before=0, balance_after=2500, description="Profit Win")
        ])
        db.flush()
        analytics.update_player_metrics("P010", {"sessions": 5, "playtime_hours": 2.0})

        db.commit()
        
        # Batch reclassify
        print("Reclassifying all players...")
        segmentation.batch_reclassify_players()
        
        print("Diversification complete!")
        
        # Final check
        players = db.query(models.Player).all()
        for p in players:
             m = p.metrics
             print(f"Player {p.player_id}: {p.segment.value} - {p.tier.value} (Wager: {m.total_wagered}, PnL: {m.net_pnl}, W/L: {m.win_loss_ratio})")
            
    finally:
        db.close()

if __name__ == "__main__":
    inject_data()
