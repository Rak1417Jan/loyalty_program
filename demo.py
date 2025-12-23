"""
Demo script showing how to use the loyalty program system
"""
from database import SessionLocal
from models import Player, PlayerSegment
from analytics.player_analytics import PlayerAnalytics
from analytics.segmentation import PlayerSegmentation
from engine.rules_engine import RulesEngine
from wallet.wallet_manager import WalletManager
from safety.profit_safety import ProfitSafety
from safety.fraud_detector import FraudDetector

def demo_player_analytics():
    """Demo: Player analytics and segmentation"""
    print("\n" + "="*60)
    print("DEMO 1: Player Analytics & Segmentation")
    print("="*60)
    
    db = SessionLocal()
    analytics = PlayerAnalytics(db)
    segmentation = PlayerSegmentation(db)
    
    # Get a player
    player = db.query(Player).first()
    if not player:
        print("No players found. Import sample data first.")
        db.close()
        return
    
    player_id = player.player_id
    print(f"\nAnalyzing player: {player_id}")
    
    # Get player state
    state = analytics.get_player_state(player_id)
    print(f"\nPlayer State:")
    print(f"  Segment: {state['segment']}")
    print(f"  Tier: {state['tier']}")
    print(f"  Total Deposited: ${state['total_deposited']:.2f}")
    print(f"  Total Wagered: ${state['total_wagered']:.2f}")
    print(f"  Total Won: ${state['total_won']:.2f}")
    print(f"  Net P&L: ${state['net_pnl']:.2f}")
    print(f"  Risk Score: {state['risk_score']}")
    
    # Get segment distribution
    distribution = segmentation.get_segment_distribution()
    print(f"\nSegment Distribution:")
    for segment, count in distribution.items():
        print(f"  {segment}: {count} players")
    
    db.close()


def demo_reward_rules():
    """Demo: Reward rule evaluation"""
    print("\n" + "="*60)
    print("DEMO 2: Reward Rule Evaluation")
    print("="*60)
    
    db = SessionLocal()
    rules_engine = RulesEngine(db)
    analytics = PlayerAnalytics(db)
    
    # Get a losing player
    player = db.query(Player).filter(
        Player.segment == PlayerSegment.LOSING
    ).first()
    
    if not player:
        print("No losing players found.")
        db.close()
        return
    
    player_id = player.player_id
    print(f"\nEvaluating rules for player: {player_id}")
    
    # Get player state
    state = analytics.get_player_state(player_id)
    print(f"  Segment: {state['segment']}")
    print(f"  Net Loss: ${state['net_loss']:.2f}")
    
    # Get applicable rules
    applicable_rules = rules_engine.get_applicable_rules(player_id, state)
    
    print(f"\nApplicable Rules: {len(applicable_rules)}")
    for rule in applicable_rules:
        amount = rules_engine.calculate_reward_amount(rule, state)
        amount = rules_engine.apply_caps(amount, rule.reward_config)
        
        print(f"\n  Rule: {rule.name}")
        print(f"  Reward Amount: ${amount:.2f}")
        print(f"  Type: {rule.reward_config['type']}")
        print(f"  Wagering Req: {rule.reward_config.get('wagering_requirement', 0)}x")
    
    db.close()


def demo_profit_safety():
    """Demo: Profit safety validation"""
    print("\n" + "="*60)
    print("DEMO 3: Profit Safety Validation")
    print("="*60)
    
    db = SessionLocal()
    profit_safety = ProfitSafety(db)
    
    player = db.query(Player).first()
    if not player:
        print("No players found.")
        db.close()
        return
    
    player_id = player.player_id
    reward_amount = 100.0
    reward_type = "BONUS_BALANCE"
    
    print(f"\nValidating reward for player: {player_id}")
    print(f"  Reward Amount: ${reward_amount:.2f}")
    print(f"  Reward Type: {reward_type}")
    
    # Calculate expected value
    ev = profit_safety.calculate_expected_value(player_id, reward_amount, reward_type)
    
    print(f"\nExpected Value Analysis:")
    print(f"  Base Wager: ${ev['base_wager']:.2f}")
    print(f"  Retention Multiplier: {ev['retention_multiplier']:.2f}x")
    print(f"  Expected Wager: ${ev['expected_wager']:.2f}")
    print(f"  House Edge: {ev['house_edge']:.2%}")
    print(f"  Expected Revenue: ${ev['expected_revenue']:.2f}")
    print(f"  Reward Cost: ${ev['reward_cost']:.2f}")
    print(f"  Expected Profit: ${ev['expected_profit']:.2f}")
    print(f"  ROI: {ev['roi_percent']:.1f}%")
    
    # Validate profitability
    is_valid, reason = profit_safety.validate_reward(player_id, reward_amount, reward_type)
    
    print(f"\nValidation Result: {'✓ APPROVED' if is_valid else '✗ REJECTED'}")
    print(f"  Reason: {reason}")
    
    db.close()


def demo_fraud_detection():
    """Demo: Fraud detection"""
    print("\n" + "="*60)
    print("DEMO 4: Fraud Detection")
    print("="*60)
    
    db = SessionLocal()
    fraud_detector = FraudDetector(db)
    
    player = db.query(Player).first()
    if not player:
        print("No players found.")
        db.close()
        return
    
    player_id = player.player_id
    print(f"\nRunning fraud detection for player: {player_id}")
    
    # Detect abuse signals
    signals = fraud_detector.detect_abuse_signals(player_id)
    
    print(f"\nAbuse Signals Detected: {len(signals)}")
    for signal in signals:
        print(f"  - {signal.signal_type} (Severity: {signal.severity}/10)")
        print(f"    {signal.description}")
    
    # Calculate abuse score
    score = fraud_detector.calculate_abuse_score(player_id)
    print(f"\nAbuse Score: {score}/100")
    
    # Apply penalty if needed
    action = fraud_detector.apply_abuse_penalty(player_id)
    print(f"Action Taken: {action}")
    
    db.close()


def demo_wallet_operations():
    """Demo: Wallet operations"""
    print("\n" + "="*60)
    print("DEMO 5: Wallet Operations")
    print("="*60)
    
    db = SessionLocal()
    wallet = WalletManager(db)
    
    player = db.query(Player).first()
    if not player:
        print("No players found.")
        db.close()
        return
    
    player_id = player.player_id
    print(f"\nWallet operations for player: {player_id}")
    
    # Get current balance
    balance = wallet.get_or_create_balance(player_id)
    print(f"\nCurrent Balances:")
    print(f"  Loyalty Points: {balance.lp_balance:.2f}")
    print(f"  Reward Points: {balance.rp_balance:.2f}")
    print(f"  Bonus Balance: ${balance.bonus_balance:.2f}")
    print(f"  Tickets: {balance.tickets_balance}")
    
    if balance.bonus_wagering_required > 0:
        progress = (balance.bonus_wagering_completed / balance.bonus_wagering_required * 100)
        print(f"\nBonus Wagering Progress:")
        print(f"  Required: ${balance.bonus_wagering_required:.2f}")
        print(f"  Completed: ${balance.bonus_wagering_completed:.2f}")
        print(f"  Progress: {progress:.1f}%")
    
    db.close()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("LOYALTY & REWARD PROGRAM - DEMO")
    print("="*60)
    
    try:
        demo_player_analytics()
        demo_reward_rules()
        demo_profit_safety()
        demo_fraud_detection()
        demo_wallet_operations()
        
        print("\n" + "="*60)
        print("DEMO COMPLETE!")
        print("="*60)
        print("\nExplore more features via the API:")
        print("  http://localhost:8000/docs")
        print()
        
    except Exception as e:
        print(f"\n✗ Error running demo: {e}")
        print("Make sure you've run quick_start.py first!")
