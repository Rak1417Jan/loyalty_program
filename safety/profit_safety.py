"""
Profit Safety Checker
Validates that rewards are profitable for the platform
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Player, PlayerMetrics, RewardHistory, Transaction, TransactionType
from config import settings
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ProfitSafety:
    """Ensure reward profitability"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_house_edge(self, game_type: Optional[str] = None) -> float:
        """
        Get house edge for a game type
        
        Args:
            game_type: Type of game (slots, poker, etc.)
        
        Returns:
            House edge as decimal (e.g., 0.05 = 5%)
        """
        # In production, this would be configurable per game
        house_edges = {
            "slots": 0.05,
            "roulette": 0.027,
            "blackjack": 0.005,
            "poker": 0.05,  # Rake
            "default": settings.default_house_edge
        }
        
        return house_edges.get(game_type, house_edges["default"])
    
    def calculate_expected_future_wager(
        self,
        player_id: str,
        lookback_days: int = 30
    ) -> float:
        """
        Calculate expected future wager based on historical average
        
        Args:
            player_id: Player ID
            lookback_days: Days to look back for average
        
        Returns:
            Expected wager amount for next period
        """
        metrics = self.db.query(PlayerMetrics).filter(
            PlayerMetrics.player_id == player_id
        ).first()
        
        if not metrics or not metrics.last_wager_at:
            return 0.0
        
        # Get recent wager history
        cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)
        recent_wagers = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.player_id == player_id,
            Transaction.transaction_type == TransactionType.WAGER,
            Transaction.created_at >= cutoff_date
        ).scalar() or 0.0
        
        # Calculate daily average and project forward
        daily_avg = recent_wagers / lookback_days if lookback_days > 0 else 0.0
        
        # Project for next 30 days
        expected_wager = daily_avg * 30
        
        return expected_wager
    
    def get_retention_multiplier(self, segment: str, reward_type: str) -> float:
        """
        Get retention multiplier based on segment and reward type
        
        This estimates how much more a player will play after receiving a reward
        
        Args:
            segment: Player segment
            reward_type: Type of reward
        
        Returns:
            Multiplier (e.g., 1.5 = 50% increase in activity)
        """
        # Empirical data - would be tuned based on actual results
        multipliers = {
            "LOSING": {
                "BONUS_BALANCE": 1.8,  # Losing players respond well to bonuses
                "CASHBACK": 1.5,
                "LOYALTY_POINTS": 1.2,
            },
            "BREAKEVEN": {
                "BONUS_BALANCE": 1.5,
                "CASHBACK": 1.4,
                "LOYALTY_POINTS": 1.3,
            },
            "WINNING": {
                "BONUS_BALANCE": 1.1,  # Winning players less motivated by bonuses
                "CASHBACK": 1.1,
                "LOYALTY_POINTS": 1.2,
            },
            "NEW": {
                "BONUS_BALANCE": 2.0,  # New players very responsive
                "CASHBACK": 1.6,
                "LOYALTY_POINTS": 1.4,
            },
            "VIP": {
                "BONUS_BALANCE": 1.3,
                "CASHBACK": 1.4,
                "LOYALTY_POINTS": 1.5,
            }
        }
        
        return multipliers.get(segment, {}).get(reward_type, 1.0)
    
    def calculate_expected_value(
        self,
        player_id: str,
        reward_amount: float,
        reward_type: str
    ) -> Dict[str, float]:
        """
        Calculate expected value of a reward
        
        Formula:
        Expected Revenue = Expected Future Wager * House Edge
        Expected Profit = Expected Revenue - Reward Cost
        ROI = Expected Profit / Reward Cost
        
        Args:
            player_id: Player ID
            reward_amount: Reward amount
            reward_type: Type of reward
        
        Returns:
            Dict with EV calculations
        """
        player = self.db.query(Player).filter(Player.player_id == player_id).first()
        if not player:
            raise ValueError(f"Player {player_id} not found")
        
        # Get expected future wager
        base_wager = self.calculate_expected_future_wager(player_id)
        
        # Apply retention multiplier
        retention_mult = self.get_retention_multiplier(
            player.segment.value,
            reward_type
        )
        expected_wager = base_wager * retention_mult
        
        # Calculate expected revenue
        house_edge = self.get_house_edge()
        expected_revenue = expected_wager * house_edge
        
        # Calculate profit
        reward_cost = reward_amount
        expected_profit = expected_revenue - reward_cost
        
        # Calculate ROI
        roi = (expected_profit / reward_cost * 100) if reward_cost > 0 else 0.0
        
        return {
            "base_wager": base_wager,
            "retention_multiplier": retention_mult,
            "expected_wager": expected_wager,
            "house_edge": house_edge,
            "expected_revenue": expected_revenue,
            "reward_cost": reward_cost,
            "expected_profit": expected_profit,
            "roi_percent": roi
        }
    
    def validate_reward_profitability(
        self,
        player_id: str,
        reward_amount: float,
        reward_type: str,
        min_roi: float = 0.0
    ) -> tuple[bool, str]:
        """
        Validate if a reward is profitable
        
        Args:
            player_id: Player ID
            reward_amount: Reward amount
            reward_type: Type of reward
            min_roi: Minimum acceptable ROI (default 0 = break-even)
        
        Returns:
            Tuple of (is_valid, reason)
        """
        try:
            ev = self.calculate_expected_value(player_id, reward_amount, reward_type)
            
            # Check if profitable
            if ev["expected_profit"] < 0:
                return False, f"Negative expected profit: {ev['expected_profit']:.2f}"
            
            # Check ROI threshold
            if ev["roi_percent"] < min_roi:
                return False, f"ROI {ev['roi_percent']:.1f}% below minimum {min_roi}%"
            
            logger.info(
                f"Reward validated for player {player_id}: "
                f"Amount={reward_amount}, Expected Profit={ev['expected_profit']:.2f}, "
                f"ROI={ev['roi_percent']:.1f}%"
            )
            
            return True, "Profitable"
        
        except Exception as e:
            logger.error(f"Error validating reward profitability: {e}")
            return False, f"Validation error: {str(e)}"
    
    def check_reward_caps(
        self,
        player_id: str,
        reward_amount: float,
        period: str = "daily"
    ) -> tuple[bool, str]:
        """
        Check if reward exceeds caps
        
        Args:
            player_id: Player ID
            reward_amount: Reward amount
            period: "daily", "weekly", or "monthly"
        
        Returns:
            Tuple of (is_valid, reason)
        """
        # Get period cap
        if period == "daily":
            cap = settings.max_daily_reward_per_player
            days = 1
        elif period == "weekly":
            cap = settings.max_weekly_reward_per_player
            days = 7
        elif period == "monthly":
            cap = settings.max_monthly_reward_per_player
            days = 30
        else:
            return False, f"Invalid period: {period}"
        
        # Calculate rewards in period
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        period_rewards = self.db.query(func.sum(RewardHistory.amount)).filter(
            RewardHistory.player_id == player_id,
            RewardHistory.issued_at >= cutoff_date
        ).scalar() or 0.0
        
        # Check if adding this reward would exceed cap
        total_with_new = period_rewards + reward_amount
        
        if total_with_new > cap:
            return False, (
                f"{period.capitalize()} cap exceeded: "
                f"{total_with_new:.2f} > {cap:.2f}"
            )
        
        remaining = cap - period_rewards
        logger.info(
            f"Player {player_id} {period} rewards: {period_rewards:.2f}/{cap:.2f} "
            f"(remaining: {remaining:.2f})"
        )
        
        return True, f"Within {period} cap"
    
    def validate_reward(
        self,
        player_id: str,
        reward_amount: float,
        reward_type: str,
        min_roi: float = 0.0
    ) -> tuple[bool, str]:
        """
        Complete reward validation (profitability + caps)
        
        Args:
            player_id: Player ID
            reward_amount: Reward amount
            reward_type: Type of reward
            min_roi: Minimum acceptable ROI
        
        Returns:
            Tuple of (is_valid, reason)
        """
        # Check profitability
        is_profitable, reason = self.validate_reward_profitability(
            player_id, reward_amount, reward_type, min_roi
        )
        
        if not is_profitable:
            return False, f"Profitability check failed: {reason}"
        
        # Check daily cap
        is_valid, reason = self.check_reward_caps(player_id, reward_amount, "daily")
        if not is_valid:
            return False, reason
        
        # Check weekly cap
        is_valid, reason = self.check_reward_caps(player_id, reward_amount, "weekly")
        if not is_valid:
            return False, reason
        
        # Check monthly cap
        is_valid, reason = self.check_reward_caps(player_id, reward_amount, "monthly")
        if not is_valid:
            return False, reason
        
        return True, "All validations passed"
