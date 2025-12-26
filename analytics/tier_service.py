"""
Tier Management Service
Handles player tier upgrades and downgrades based on LP balance
"""
from sqlalchemy.orm import Session
from models import Player, Tier, TierLevel, LoyaltyBalance
import logging

logger = logging.getLogger(__name__)

class TierService:
    """Manage player tiers and benefits"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_tier(self, player_state: dict) -> TierLevel:
        """
        Calculate the appropriate tier based on player state and requirements
        
        Args:
            player_state: Dictionary with player metrics and attributes
            
        Returns:
            TierLevel enum
        """
        lp_balance = player_state.get("lp_balance", 0)
        
        # Get all tiers ordered by lp_min descending
        tiers = self.db.query(Tier).order_by(Tier.lp_min.desc()).all()
        
        for tier in tiers:
            # Check LP requirement
            if lp_balance < tier.lp_min:
                continue
                
            # Check complex requirements if any
            if tier.requirements:
                if self._evaluate_requirements(tier.requirements, player_state):
                    return tier.tier_level
                else:
                    continue # Try next (lower) tier
            
            # If no detailed requirements, LP min is enough
            return tier.tier_level
                
        return TierLevel.BRONZE

    def _evaluate_requirements(self, requirements: dict, player_state: dict) -> bool:
        """Helper to evaluate tier requirements against player state"""
        from engine.rules_engine import RulesEngine
        engine = RulesEngine(self.db)
        return engine.evaluate_condition(requirements, player_state)

    def update_player_tier(self, player_id: str) -> TierLevel:
        """
        Update player's tier in database based on current state
        
        Returns:
            New tier level
        """
        from analytics.player_analytics import PlayerAnalytics
        analytics = PlayerAnalytics(self.db)
        
        try:
            player_state = analytics.get_player_state(player_id)
        except ValueError:
            return TierLevel.BRONZE
            
        player = self.db.query(Player).filter(Player.player_id == player_id).first()
        
        # Calculate appropriate tier
        new_tier = self.calculate_tier(player_state)
        old_tier = player.tier
        
        if old_tier != new_tier:
            logger.info(
                f"Player {player_id} tier changed: {old_tier.value} → {new_tier.value} "
                f"(LP: {player_state.get('lp_balance', 0)})"
            )
            player.tier = new_tier
            self.db.commit()
            
        return new_tier

    def batch_update_all_tiers(self) -> int:
        """
        Update tiers for all active players
        
        Returns:
            Number of tier changes
        """
        players = self.db.query(Player).all()
        changes = 0
        
        for player in players:
            old_tier = player.tier
            new_tier = self.update_player_tier(player.player_id)
            if old_tier != new_tier:
                changes += 1
                
        return changes
