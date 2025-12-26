"""
Action Service
Handles logging of player actions and triggering associated loyalty rewards
"""
from sqlalchemy.orm import Session
from models import Player, PlayerAction, TransactionType
from engine.rules_engine import RulesEngine
import logging

logger = logging.getLogger(__name__)

class ActionService:
    def __init__(self, db: Session):
        self.db = db
        self.rules_engine = RulesEngine(db)

    def log_action(self, player_id: str, action_type: str, value: str = None, meta_data: dict = None):
        """
        Log a player action and evaluate reward rules
        """
        # Create action record
        action = PlayerAction(
            player_id=player_id,
            action_type=action_type,
            value=value,
            meta_data=meta_data or {}
        )
        self.db.add(action)
        self.db.commit()
        
        logger.info(f"Logged action {action_type} for player {player_id}")
        
        # Trigger rule evaluation
        # Note: In a production system, this might be asynchronous
        rewards = self.rules_engine.evaluate_and_create_rewards(player_id)
        
        return {
            "action_id": action.id,
            "rewards_triggered": len(rewards)
        }

    def complete_kyc(self, player_id: str):
        """Specialized method for KYC completion"""
        return self.log_action(player_id, "KYC_COMPLETE")

    def update_profile_depth(self, player_id: str, depth_percentage: int):
        """Specialized method for profile deepening"""
        return self.log_action(player_id, "PROFILE_DEEPENING", value=str(depth_percentage))
