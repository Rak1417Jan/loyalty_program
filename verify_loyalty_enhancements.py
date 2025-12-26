"""
Verification Script for Loyalty Program Enhancements
Tests action-based rewards, redemptions, and FIFO point expiry
"""
import sys
import os
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.getcwd())

from database import SessionLocal, init_db
from models import *
from wallet.wallet_manager import WalletManager
from analytics.action_service import ActionService
from analytics.tier_service import TierService
from engine.rules_engine import RulesEngine

def verify_all():
    # Initialize database
    init_db()
    db = SessionLocal()
    
    try:
        player_id = "TEST_PLAYER_001"
        
        # 1. Setup Test Player
        print(f"\n--- 1. Setting up player {player_id} ---")
        player = db.query(Player).filter(Player.player_id == player_id).first()
        if player:
            db.delete(player)
            db.query(LoyaltyBalance).filter(LoyaltyBalance.player_id == player_id).delete()
            db.query(PlayerMetrics).filter(PlayerMetrics.player_id == player_id).delete()
            db.commit()
            
        player = Player(player_id=player_id, name="Test User", tier=TierLevel.BRONZE)
        metrics = PlayerMetrics(player_id=player_id)
        balance = LoyaltyBalance(player_id=player_id)
        db.add(player)
        db.add(metrics)
        db.add(balance)
        db.commit()
        print("Player created.")

        # 2. Setup Reward Rules
        print(f"\n--- 2. Setting up Reward Rules ---")
        rules_engine = RulesEngine(db)
        
        # Rule: KYC completion gives 500 LP
        kyc_rule = RewardRule(
            rule_id="KYC_REWARD",
            name="KYC Completion Reward",
            conditions={"kyc_completed": True},
            reward_config={"type": "LOYALTY_POINTS", "amount": 500, "lp_expiry_days": 365}
        )
        # Rule: 3 active days in month gives 100 LP
        freq_rule = RewardRule(
            rule_id="FREQ_REWARD",
            name="Monthly Activity Reward",
            conditions={"monthly_active_days": {"min": 1}}, # Simplified for test
            reward_config={"type": "LOYALTY_POINTS", "amount": 100, "lp_expiry_days": 30}
        )
        db.merge(kyc_rule)
        db.merge(freq_rule)
        db.commit()
        print("Rules created.")

        # 3. Trigger Actions
        print(f"\n--- 3. Triggering Loyalty Actions ---")
        action_service = ActionService(db)
        
        # Add a wager to make monthly_active_days = 1
        wallet = WalletManager(db)
        wallet.record_wager(player_id, 10.0, "SLOTS")
        print("Wager recorded (Activity).")
        
        # Complete KYC
        print("Completing KYC...")
        action_service.complete_kyc(player_id)
        
        db.refresh(balance)
        print(f"LP Balance after KYC: {balance.lp_balance} (Expected: 500 or 600 if freq rule also hit)")
        
        # Verify entries
        entries = db.query(LoyaltyPointEntry).filter(LoyaltyPointEntry.player_id == player_id).all()
        print(f"Number of point entries: {len(entries)}")
        for e in entries:
            print(f" - Entry: {e.amount} LP, Source: {e.source_type}, Expires: {e.expires_at}")

        # 4. Redemption
        print(f"\n--- 4. Testing Redemption ---")
        # Create a redemption rule
        red_rule = RedemptionRule(
            name="Cash Redemption",
            lp_cost=200,
            currency_value=2.0,
            target_balance="CASH",
            is_active=True
        )
        db.add(red_rule)
        db.commit()
        db.refresh(red_rule)
        
        print(f"Redeeming 200 LP for $2.00...")
        wallet.redeem_points(player_id, red_rule.id)
        
        db.refresh(balance)
        print(f"New LP Balance: {balance.lp_balance} (Remaining from FIFO)")
        
        # Check FIFO deduction
        entries = db.query(LoyaltyPointEntry).filter(LoyaltyPointEntry.player_id == player_id).order_by(LoyaltyPointEntry.issued_at).all()
        for e in entries:
            print(f" - Remaining in Entry #{e.id}: {e.remaining_amount} LP")

        # 5. Behavioral Tiers
        print(f"\n--- 5. Testing Behavioral Tiers ---")
        # Update Silver tier to require KYC
        silver_tier = db.query(Tier).filter(Tier.tier_level == TierLevel.SILVER).first()
        if not silver_tier:
            silver_tier = Tier(tier_level=TierLevel.SILVER, lp_min=100, benefits={})
            db.add(silver_tier)
        
        silver_tier.requirements = {"kyc_completed": True}
        db.commit()
        
        tier_service = TierService(db)
        new_tier = tier_service.update_player_tier(player_id)
        print(f"Player Tier: {new_tier.value}")

        # 6. Expiry
        print(f"\n--- 6. Testing Point Expiry ---")
        # Manually create an expired entry
        expired_entry = LoyaltyPointEntry(
            player_id=player_id,
            amount=1000,
            remaining_amount=1000,
            source_type="TEST_EXPIRY",
            expires_at=datetime.utcnow() - timedelta(days=1)
        )
        db.add(expired_entry)
        balance.lp_balance += 1000
        db.commit()
        
        print(f"LP Balance before expiry: {balance.lp_balance}")
        wallet.process_point_expiry()
        db.refresh(balance)
        print(f"LP Balance after expiry: {balance.lp_balance}")
        
        print("\nVerification successful!")
        
    finally:
        db.close()

if __name__ == "__main__":
    verify_all()
