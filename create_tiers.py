"""
Example script to create tier configuration
"""
from database import SessionLocal
from models import Tier, TierLevel

def create_tiers():
    """Create tier configuration"""
    db = SessionLocal()
    
    tiers = [
        Tier(
            tier_level=TierLevel.BRONZE,
            lp_min=0,
            lp_max=999,
            benefits={
                "cashback_multiplier": 1.0,
                "free_plays_per_month": 0,
                "withdrawal_priority": "standard",
                "support_level": "basic"
            }
        ),
        Tier(
            tier_level=TierLevel.SILVER,
            lp_min=1000,
            lp_max=9999,
            benefits={
                "cashback_multiplier": 1.2,
                "free_plays_per_month": 5,
                "withdrawal_priority": "standard",
                "support_level": "priority",
                "bonus_boost": 1.1
            }
        ),
        Tier(
            tier_level=TierLevel.GOLD,
            lp_min=10000,
            lp_max=49999,
            benefits={
                "cashback_multiplier": 1.5,
                "free_plays_per_month": 15,
                "withdrawal_priority": "fast",
                "support_level": "vip",
                "bonus_boost": 1.25,
                "exclusive_tournaments": True
            }
        ),
        Tier(
            tier_level=TierLevel.PLATINUM,
            lp_min=50000,
            lp_max=None,
            benefits={
                "cashback_multiplier": 2.0,
                "free_plays_per_month": 30,
                "withdrawal_priority": "instant",
                "support_level": "dedicated_manager",
                "bonus_boost": 1.5,
                "exclusive_tournaments": True,
                "reduced_fees": True,
                "birthday_bonus": 500
            }
        )
    ]
    
    for tier in tiers:
        # Check if exists
        existing = db.query(Tier).filter(
            Tier.tier_level == tier.tier_level
        ).first()
        
        if not existing:
            db.add(tier)
            print(f"Created tier: {tier.tier_level.value}")
        else:
            print(f"Tier already exists: {tier.tier_level.value}")
    
    db.commit()
    db.close()
    
    print("\nTiers created successfully!")


if __name__ == "__main__":
    create_tiers()
