"""
Player Segmentation Classifier
Dynamically classifies players into segments based on metrics
"""
from sqlalchemy.orm import Session
from models import Player, PlayerMetrics, PlayerSegment
from config import settings
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class PlayerSegmentation:
    """Classify players into segments"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def classify_player(self, player_id: str) -> PlayerSegment:
        """
        Classify a player into a segment
        
        Segmentation Logic:
        - NEW: Low wagering activity
        - VIP: High volume + high sessions
        - WINNING: Positive P&L + high win/loss ratio
        - BREAKEVEN: P&L near zero
        - LOSING: Negative P&L
        
        Returns:
            PlayerSegment enum
        """
        player = self.db.query(Player).filter(Player.player_id == player_id).first()
        if not player:
            raise ValueError(f"Player {player_id} not found")
        
        metrics = player.metrics
        if not metrics:
            return PlayerSegment.NEW
        
        # Get thresholds from config
        new_threshold = settings.new_player_wager_threshold
        vip_wager = settings.vip_wager_threshold
        vip_sessions = settings.vip_session_threshold
        breakeven_tolerance = settings.breakeven_tolerance
        
        # Classification logic
        total_wagered = metrics.total_wagered
        net_pnl = metrics.net_pnl
        sessions = metrics.total_sessions
        win_loss_ratio = metrics.win_loss_ratio
        
        # NEW player: Low activity
        if total_wagered < new_threshold:
            return PlayerSegment.NEW
        
        # VIP player: High volume + sessions
        if total_wagered > vip_wager and sessions > vip_sessions:
            return PlayerSegment.VIP
        
        # WINNING player: Positive P&L and good win/loss ratio
        if net_pnl > 0 and win_loss_ratio > 1.1:
            return PlayerSegment.WINNING
        
        # BREAKEVEN player: P&L near zero
        breakeven_range = total_wagered * breakeven_tolerance
        if abs(net_pnl) < breakeven_range:
            return PlayerSegment.BREAKEVEN
        
        # LOSING player: Default for negative P&L
        return PlayerSegment.LOSING
    
    def update_player_segment(self, player_id: str) -> PlayerSegment:
        """
        Update player's segment in database
        
        Returns:
            New segment
        """
        new_segment = self.classify_player(player_id)
        
        player = self.db.query(Player).filter(Player.player_id == player_id).first()
        old_segment = player.segment
        
        if old_segment != new_segment:
            logger.info(
                f"Player {player_id} segment changed: {old_segment.value} → {new_segment.value}"
            )
            player.segment = new_segment
            self.db.commit()
        
        return new_segment
    
    def batch_reclassify_players(self, player_ids: List[str] = None) -> Dict[str, int]:
        """
        Reclassify multiple players or all players
        
        Args:
            player_ids: Optional list of player IDs. If None, reclassify all.
        
        Returns:
            Dict with segment counts
        """
        if player_ids:
            players = self.db.query(Player).filter(
                Player.player_id.in_(player_ids)
            ).all()
        else:
            players = self.db.query(Player).all()
        
        segment_counts = {segment.value: 0 for segment in PlayerSegment}
        changes = 0
        
        for player in players:
            old_segment = player.segment
            new_segment = self.classify_player(player.player_id)
            
            if old_segment != new_segment:
                player.segment = new_segment
                changes += 1
            
            segment_counts[new_segment.value] += 1
        
        self.db.commit()
        
        logger.info(
            f"Reclassified {len(players)} players. {changes} segments changed."
        )
        logger.info(f"Segment distribution: {segment_counts}")
        
        return segment_counts
    
    def get_segment_distribution(self) -> Dict[str, int]:
        """Get current distribution of players across segments"""
        from sqlalchemy import func
        
        distribution = self.db.query(
            Player.segment,
            func.count(Player.player_id)
        ).group_by(Player.segment).all()
        
        return {segment.value: count for segment, count in distribution}
    
    def get_players_by_segment(
        self, 
        segment: PlayerSegment,
        limit: int = 100
    ) -> List[Player]:
        """Get players in a specific segment"""
        return self.db.query(Player).filter(
            Player.segment == segment,
            Player.is_active == True
        ).limit(limit).all()
