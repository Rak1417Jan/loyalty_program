"""
Example script to create sample reward rules
"""
from database import SessionLocal
from models import RewardRule

def create_sample_rules():
    """Create sample reward rules for testing"""
    db = SessionLocal()
    
    rules = [
        # Rule 1: Losing Player Cashback
        RewardRule(
            rule_id="LOSING_PLAYER_CASHBACK",
            name="Losing Player 10% Cashback",
            description="Give 10% cashback to losing players who have lost more than $100",
            priority=10,
            is_active=True,
            conditions={
                "segment": "LOSING",
                "net_loss_min": 100,
                "session_count_min": 3
            },
            reward_config={
                "type": "BONUS_BALANCE",
                "formula": "net_loss * 0.10",
                "max_amount": 500,
                "wagering_requirement": 10,
                "expiry_hours": 48,
                "eligible_games": ["slots", "roulette"]
            }
        ),
        
        # Rule 2: Breakeven Player Bonus
        RewardRule(
            rule_id="BREAKEVEN_PLAYER_BONUS",
            name="Breakeven Player Volume Bonus",
            description="Encourage breakeven players to play more",
            priority=8,
            is_active=True,
            conditions={
                "segment": "BREAKEVEN",
                "total_wagered_min": 1000,
                "session_count_min": 5
            },
            reward_config={
                "type": "BONUS_BALANCE",
                "formula": "total_wagered * 0.05",
                "max_amount": 300,
                "wagering_requirement": 5,
                "expiry_hours": 72
            }
        ),
        
        # Rule 3: New Player Welcome Bonus
        RewardRule(
            rule_id="NEW_PLAYER_WELCOME",
            name="New Player Welcome Bonus",
            description="Welcome bonus for new players after first deposit",
            priority=15,
            is_active=True,
            conditions={
                "segment": "NEW",
                "total_deposited_min": 100
            },
            reward_config={
                "type": "BONUS_BALANCE",
                "formula": "total_deposited * 0.50",
                "max_amount": 200,
                "wagering_requirement": 15,
                "expiry_hours": 168  # 7 days
            }
        ),
        
        # Rule 4: VIP Loyalty Points
        RewardRule(
            rule_id="VIP_LOYALTY_POINTS",
            name="VIP Loyalty Points Multiplier",
            description="VIP players earn 2x loyalty points",
            priority=12,
            is_active=True,
            conditions={
                "segment": "VIP"
            },
            reward_config={
                "type": "LOYALTY_POINTS",
                "formula": "total_wagered * 0.02",
                "max_amount": 1000
            }
        ),
        
        # Rule 5: Winning Player Tournament Tickets
        RewardRule(
            rule_id="WINNING_PLAYER_TOURNAMENT",
            name="Winning Player Tournament Entry",
            description="Give tournament tickets to winning players",
            priority=7,
            is_active=True,
            conditions={
                "segment": "WINNING",
                "total_wagered_min": 5000
            },
            reward_config={
                "type": "TICKETS",
                "formula": "5",  # Fixed 5 tickets
                "max_amount": 10
            }
        ),
        
        # Rule 6: Inactive Player Reactivation
        RewardRule(
            rule_id="INACTIVE_REACTIVATION",
            name="Inactive Player Reactivation Bonus",
            description="Bring back inactive players",
            priority=9,
            is_active=True,
            conditions={
                "days_since_last_deposit": {"min": 7, "max": 30},
                "total_wagered_min": 1000
            },
            reward_config={
                "type": "BONUS_BALANCE",
                "formula": "100",  # Fixed $100
                "max_amount": 100,
                "wagering_requirement": 8,
                "expiry_hours": 48
            }
        )
    ]
    
    for rule in rules:
        # Check if exists
        existing = db.query(RewardRule).filter(
            RewardRule.rule_id == rule.rule_id
        ).first()
        
        if not existing:
            db.add(rule)
            print(f"Created rule: {rule.rule_id}")
        else:
            print(f"Rule already exists: {rule.rule_id}")
    
    db.commit()
    db.close()
    
    print("\nSample rules created successfully!")


if __name__ == "__main__":
    create_sample_rules()
