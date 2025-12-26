#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from analytics.player_analytics import PlayerAnalytics
from analytics.segmentation import PlayerSegmentation
import models
from models import Transaction, TransactionType, CurrencyType, PlayerSegment

def finalize_database():
    db = SessionLocal()
    try:
        analytics = PlayerAnalytics(db)
        segmentation = PlayerSegmentation(db)
        
        player_ids = [f"P{i:03d}" for i in range(1, 11)]
        print(f"Resetting transactions/metrics for {len(player_ids)} players...")
        db.query(models.Transaction).filter(models.Transaction.player_id.in_(player_ids)).delete(synchronize_session=False)
        metrics = db.query(models.PlayerMetrics).filter(models.PlayerMetrics.player_id.in_(player_ids)).all()
        for m in metrics:
            m.total_deposited = m.total_wagered = m.total_won = m.net_pnl = 0.0
            m.total_sessions = 0
            m.win_loss_ratio = 0.0
        db.commit()

        # 1. P004 -> VIP (Needs > 100k wager, > 100 sessions)
        print("Diversifying P004 -> VIP...")
        db.add_all([
            Transaction(player_id="P004", transaction_type=TransactionType.DEPOSIT, currency_type=CurrencyType.CASH, amount=50000, balance_before=0, balance_after=50000, description="VIP Deposit"),
            Transaction(player_id="P004", transaction_type=TransactionType.WAGER, currency_type=CurrencyType.CASH, amount=150000, balance_before=50000, balance_after=0, description="VIP High Volume Wager"),
            Transaction(player_id="P004", transaction_type=TransactionType.WIN, currency_type=CurrencyType.CASH, amount=120000, balance_before=0, balance_after=120000, description="VIP Winning")
        ])
        db.commit() # Commit transactions first
        analytics.update_player_metrics("P004", {"sessions": 120, "playtime_hours": 200.0})

        # 2. P005 -> WINNING (+PnL, W/L > 1.1)
        print("Diversifying P005 -> WINNING...")
        db.add_all([
            Transaction(player_id="P005", transaction_type=TransactionType.DEPOSIT, currency_type=CurrencyType.CASH, amount=5000, balance_before=0, balance_after=5000, description="Deposit"),
            Transaction(player_id="P005", transaction_type=TransactionType.WAGER, currency_type=CurrencyType.CASH, amount=5000, balance_before=5000, balance_after=0, description="Wager"),
            Transaction(player_id="P005", transaction_type=TransactionType.WIN, currency_type=CurrencyType.CASH, amount=15000, balance_before=0, balance_after=15000, description="Profit")
        ])
        db.commit()
        analytics.update_player_metrics("P005", {"sessions": 10})

        # 3. P006 -> BREAKEVEN (|PnL| < 5% of wager)
        print("Diversifying P006 -> BREAKEVEN...")
        db.add_all([
            Transaction(player_id="P006", transaction_type=TransactionType.DEPOSIT, currency_type=CurrencyType.CASH, amount=10000, balance_before=0, balance_after=10000, description="Deposit"),
            Transaction(player_id="P006", transaction_type=TransactionType.WAGER, currency_type=CurrencyType.CASH, amount=10000, balance_before=10000, balance_after=0, description="Wager"),
            Transaction(player_id="P006", transaction_type=TransactionType.WIN, currency_type=CurrencyType.CASH, amount=10200, balance_before=0, balance_after=10200, description="Breakeven Win")
        ])
        db.commit()
        analytics.update_player_metrics("P006", {"sessions": 15})

        # 4. P010 -> WINNING
        print("Diversifying P010 -> WINNING...")
        db.add_all([
            Transaction(player_id="P010", transaction_type=TransactionType.DEPOSIT, currency_type=CurrencyType.CASH, amount=1000, balance_before=0, balance_after=1000, description="Deposit"),
            Transaction(player_id="P010", transaction_type=TransactionType.WAGER, currency_type=CurrencyType.CASH, amount=1000, balance_before=1000, balance_after=0, description="Wager"),
            Transaction(player_id="P010", transaction_type=TransactionType.WIN, currency_type=CurrencyType.CASH, amount=2500, balance_before=0, balance_after=2500, description="Profit")
        ])
        db.commit()
        analytics.update_player_metrics("P010", {"sessions": 5})

        # 5. P009 -> LOSING (Needs wager > 1k and PnL < 0)
        print("Diversifying P009 -> LOSING...")
        db.add_all([
            Transaction(player_id="P009", transaction_type=TransactionType.DEPOSIT, currency_type=CurrencyType.CASH, amount=20000, balance_before=0, balance_after=20000, description="Large Deposit"),
            Transaction(player_id="P009", transaction_type=TransactionType.WAGER, currency_type=CurrencyType.CASH, amount=20000, balance_before=20000, balance_after=0, description="Large Wager"),
            Transaction(player_id="P009", transaction_type=TransactionType.WIN, currency_type=CurrencyType.CASH, amount=5000, balance_before=0, balance_after=5000, description="Small Win")
        ])
        db.commit()
        analytics.update_player_metrics("P009", {"sessions": 8})

        print("Reclassifying players...")
        segmentation.batch_reclassify_players()
        db.commit()
        
        print("\nFinal Result Verification:")
        for pid in player_ids:
            p = db.query(models.Player).filter(models.Player.player_id == pid).first()
            m = p.metrics
            print(f"[{pid}] Segment: {p.segment.value:10} | Wager: {m.total_wagered:8.1f} | PnL: {m.net_pnl:8.1f} | Ratio: {m.win_loss_ratio:5.2f} | Sessions: {m.total_sessions}")

    finally:
        db.close()

if __name__ == "__main__":
    finalize_database()
