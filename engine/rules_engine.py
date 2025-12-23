"""
Reward Rules Engine
Evaluates JSON-based reward rules and calculates rewards
"""
from sqlalchemy.orm import Session
from models import RewardRule, RewardHistory, RewardType, RewardStatus, CurrencyType
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)


class RulesEngine:
    """Evaluate reward rules and calculate rewards"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def evaluate_condition(self, condition: Dict[str, Any], player_state: Dict[str, Any]) -> bool:
        """
        Evaluate a single condition against player state
        
        Condition examples:
        - {"segment": "LOSING"} → player_state["segment"] == "LOSING"
        - {"net_loss_min": 100} → player_state["net_loss"] >= 100
        - {"session_count_min": 3} → player_state["session_count"] >= 3
        - {"days_since_last_deposit": {"max": 7}} → player_state["days_since_last_deposit"] <= 7
        
        Args:
            condition: Dict with condition key-value pairs
            player_state: Dict with player data
        
        Returns:
            True if condition matches, False otherwise
        """
        for key, value in condition.items():
            # Handle nested conditions (e.g., {"max": 7, "min": 1})
            if isinstance(value, dict):
                player_value = player_state.get(key)
                if player_value is None:
                    return False
                
                if "min" in value and player_value < value["min"]:
                    return False
                if "max" in value and player_value > value["max"]:
                    return False
                if "equals" in value and player_value != value["equals"]:
                    return False
            
            # Handle list conditions (e.g., {"segment": ["LOSING", "BREAKEVEN"]})
            elif isinstance(value, list):
                player_value = player_state.get(key)
                if player_value not in value:
                    return False
            
            # Handle suffix-based conditions
            elif key.endswith("_min"):
                # Extract base key (e.g., "net_loss_min" → "net_loss")
                base_key = key[:-4]
                player_value = player_state.get(base_key)
                if player_value is None or player_value < value:
                    return False
            
            elif key.endswith("_max"):
                base_key = key[:-4]
                player_value = player_state.get(base_key)
                if player_value is None or player_value > value:
                    return False
            
            # Handle exact match
            else:
                player_value = player_state.get(key)
                if player_value != value:
                    return False
        
        return True
    
    def evaluate_rule(self, rule: RewardRule, player_state: Dict[str, Any]) -> bool:
        """
        Evaluate if a rule matches player state
        
        Args:
            rule: RewardRule object
            player_state: Player state dict from PlayerAnalytics.get_player_state()
        
        Returns:
            True if all conditions match
        """
        if not rule.is_active:
            return False
        
        conditions = rule.conditions
        return self.evaluate_condition(conditions, player_state)
    
    def calculate_reward_amount(
        self, 
        rule: RewardRule, 
        player_state: Dict[str, Any]
    ) -> float:
        """
        Calculate reward amount based on rule formula
        
        Formula examples:
        - "net_loss * 0.10" → 10% of net loss
        - "100" → Fixed amount
        - "total_wagered * 0.01" → 1% of wagered
        
        Args:
            rule: RewardRule object
            player_state: Player state dict
        
        Returns:
            Calculated reward amount (before caps)
        """
        reward_config = rule.reward_config
        formula = reward_config.get("formula", "0")
        
        # If formula is a number, return it
        try:
            return float(formula)
        except ValueError:
            pass
        
        # Evaluate formula as expression
        # Replace variables with player state values
        expression = formula
        for key, value in player_state.items():
            if isinstance(value, (int, float)):
                expression = expression.replace(key, str(value))
        
        try:
            # Safe eval (only math operations)
            result = eval(expression, {"__builtins__": {}}, {})
            return float(result)
        except Exception as e:
            logger.error(f"Error evaluating formula '{formula}': {e}")
            return 0.0
    
    def apply_caps(self, amount: float, reward_config: Dict[str, Any]) -> float:
        """Apply max_amount cap if specified"""
        max_amount = reward_config.get("max_amount")
        if max_amount and amount > max_amount:
            return max_amount
        return amount
    
    def get_applicable_rules(
        self, 
        player_id: str,
        player_state: Optional[Dict[str, Any]] = None
    ) -> List[RewardRule]:
        """
        Get all rules that apply to a player
        
        Args:
            player_id: Player ID
            player_state: Optional pre-calculated player state
        
        Returns:
            List of matching RewardRule objects, sorted by priority
        """
        # Get player state if not provided
        if not player_state:
            from analytics.player_analytics import PlayerAnalytics
            analytics = PlayerAnalytics(self.db)
            player_state = analytics.get_player_state(player_id)
        
        # Get all active rules, ordered by priority
        all_rules = self.db.query(RewardRule).filter(
            RewardRule.is_active == True
        ).order_by(RewardRule.priority.desc()).all()
        
        # Filter rules that match player state
        applicable_rules = []
        for rule in all_rules:
            if self.evaluate_rule(rule, player_state):
                applicable_rules.append(rule)
                logger.info(f"Rule {rule.rule_id} matches player {player_id}")
        
        return applicable_rules
    
    def create_reward(
        self,
        player_id: str,
        rule: RewardRule,
        amount: float,
        player_state: Dict[str, Any]
    ) -> RewardHistory:
        """
        Create a reward record
        
        Args:
            player_id: Player ID
            rule: RewardRule that triggered
            amount: Reward amount
            player_state: Player state for metadata
        
        Returns:
            RewardHistory object
        """
        reward_config = rule.reward_config
        
        # Determine reward type and currency
        reward_type_str = reward_config.get("type", "BONUS_BALANCE")
        reward_type = RewardType[reward_type_str]
        
        # Map reward type to currency
        currency_map = {
            RewardType.LOYALTY_POINTS: CurrencyType.LOYALTY_POINTS,
            RewardType.REWARD_POINTS: CurrencyType.REWARD_POINTS,
            RewardType.BONUS_BALANCE: CurrencyType.BONUS_BALANCE,
            RewardType.FREE_PLAY: CurrencyType.BONUS_BALANCE,
            RewardType.TICKETS: CurrencyType.TICKETS,
            RewardType.CASHBACK: CurrencyType.BONUS_BALANCE,
        }
        currency_type = currency_map.get(reward_type, CurrencyType.BONUS_BALANCE)
        
        # Get wagering requirement
        wagering_required = amount * reward_config.get("wagering_requirement", 0)
        
        # Calculate expiry
        expiry_hours = reward_config.get("expiry_hours")
        expires_at = None
        if expiry_hours:
            expires_at = datetime.utcnow() + timedelta(hours=expiry_hours)
        
        # Create reward record
        reward = RewardHistory(
            player_id=player_id,
            rule_id=rule.rule_id,
            reward_type=reward_type,
            amount=amount,
            currency_type=currency_type,
            status=RewardStatus.PENDING,
            wagering_required=wagering_required,
            wagering_completed=0.0,
            expires_at=expires_at,
            metadata={
                "rule_name": rule.name,
                "player_segment": player_state.get("segment"),
                "player_tier": player_state.get("tier"),
                "eligible_games": reward_config.get("eligible_games", []),
                "max_bet": reward_config.get("max_bet")
            }
        )
        
        self.db.add(reward)
        self.db.commit()
        self.db.refresh(reward)
        
        logger.info(
            f"Created reward {reward.id} for player {player_id}: "
            f"{amount} {currency_type.value} from rule {rule.rule_id}"
        )
        
        return reward
    
    def evaluate_and_create_rewards(
        self,
        player_id: str,
        limit: int = 1
    ) -> List[RewardHistory]:
        """
        Evaluate all rules for a player and create rewards
        
        Args:
            player_id: Player ID
            limit: Maximum number of rewards to create (default 1 - highest priority)
        
        Returns:
            List of created RewardHistory objects
        """
        from analytics.player_analytics import PlayerAnalytics
        
        # Get player state
        analytics = PlayerAnalytics(self.db)
        player_state = analytics.get_player_state(player_id)
        
        # Get applicable rules
        applicable_rules = self.get_applicable_rules(player_id, player_state)
        
        if not applicable_rules:
            logger.info(f"No applicable rules for player {player_id}")
            return []
        
        # Create rewards (limited by limit parameter)
        created_rewards = []
        for rule in applicable_rules[:limit]:
            # Calculate reward amount
            amount = self.calculate_reward_amount(rule, player_state)
            amount = self.apply_caps(amount, rule.reward_config)
            
            if amount <= 0:
                logger.warning(f"Rule {rule.rule_id} calculated amount <= 0, skipping")
                continue
            
            # Check profit safety (will implement in safety module)
            # For now, create reward
            reward = self.create_reward(player_id, rule, amount, player_state)
            created_rewards.append(reward)
        
        return created_rewards
