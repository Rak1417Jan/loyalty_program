"""
Player Analytics Engine
Calculates financial, behavioral, and risk metrics for players
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Player, PlayerMetrics, Transaction, TransactionType, Tier, PlayerAction
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PlayerAnalytics:
    """Calculate and update player metrics"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_financial_metrics(self, player_id: str) -> Dict[str, float]:
        """
        Calculate financial metrics from transaction history
        
        Returns:
            Dict with: total_deposited, total_wagered, total_won, net_pnl, house_edge_contribution
        """
        # Get all transactions for player
        deposits = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.player_id == player_id,
            Transaction.transaction_type == TransactionType.DEPOSIT
        ).scalar() or 0.0
        
        wagers = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.player_id == player_id,
            Transaction.transaction_type == TransactionType.WAGER
        ).scalar() or 0.0
        
        wins = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.player_id == player_id,
            Transaction.transaction_type == TransactionType.WIN
        ).scalar() or 0.0
        
        withdrawals = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.player_id == player_id,
            Transaction.transaction_type == TransactionType.WITHDRAWAL
        ).scalar() or 0.0
        
        # Calculate net P&L (wins - deposits + withdrawals)
        net_pnl = wins - deposits + withdrawals
        
        # House edge contribution (amount lost to house)
        house_edge_contribution = wagers - wins
        
        return {
            "total_deposited": deposits,
            "total_wagered": wagers,
            "total_won": wins,
            "net_pnl": net_pnl,
            "house_edge_contribution": house_edge_contribution
        }
    
    def calculate_behavioral_metrics(
        self, 
        player_id: str,
        session_data: Optional[Dict] = None
    ) -> Dict[str, float]:
        """
        Calculate behavioral metrics
        
        Args:
            player_id: Player ID
            session_data: Optional dict with session info from external source
                         {"sessions": 25, "playtime_hours": 48, "games": {"slots": 50}}
        
        Returns:
            Dict with behavioral metrics
        """
        # If session data provided (from Excel), use it
        if session_data:
            total_sessions = session_data.get("sessions", 0)
            total_playtime_hours = session_data.get("playtime_hours", 0.0)
            games_played = session_data.get("games", {})
        else:
            # Calculate from transaction history
            total_sessions = 0  # Would need session tracking
            total_playtime_hours = 0.0
            games_played = {}
        
        # Calculate total bets from transactions
        total_bets = self.db.query(func.count(Transaction.id)).filter(
            Transaction.player_id == player_id,
            Transaction.transaction_type == TransactionType.WAGER
        ).scalar() or 0
        
        # Calculate average bet size
        total_wagered = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.player_id == player_id,
            Transaction.transaction_type == TransactionType.WAGER
        ).scalar() or 0.0
        
        avg_bet_size = total_wagered / total_bets if total_bets > 0 else 0.0
        
        # Average session duration
        avg_session_duration = (
            total_playtime_hours / total_sessions if total_sessions > 0 else 0.0
        )
        
        return {
            "total_sessions": total_sessions,
            "total_playtime_hours": total_playtime_hours,
            "avg_session_duration": avg_session_duration,
            "total_bets": total_bets,
            "avg_bet_size": avg_bet_size,
            "games_played": games_played
        }
    
    def calculate_risk_metrics(self, player_id: str, financial_metrics: Dict = None) -> Dict[str, float]:
        """
        Calculate risk metrics
        
        Returns:
            Dict with: win_loss_ratio, volatility_score, bonus_abuse_score
        """
        # Use provided financial metrics or fetch current from DB
        if financial_metrics:
            total_wagered = financial_metrics.get("total_wagered", 0.0)
            total_won = financial_metrics.get("total_won", 0.0)
        else:
            metrics = self.db.query(PlayerMetrics).filter(
                PlayerMetrics.player_id == player_id
            ).first()
            if not metrics:
                return {
                    "win_loss_ratio": 0.0,
                    "volatility_score": 0.0,
                    "bonus_abuse_score": 0
                }
            total_wagered = metrics.total_wagered
            total_won = metrics.total_won
            
        # Win/Loss ratio
        win_loss_ratio = (
            total_won / total_wagered if total_wagered > 0 else 0.0
        )
        
        # Volatility score (simplified - standard deviation of bet sizes)
        # In production, calculate from actual bet history
        volatility_score = 0.0  # Placeholder
        
        # Bonus abuse score (from abuse signals)
        from models import AbuseSignal
        abuse_count = self.db.query(func.count(AbuseSignal.id)).filter(
            AbuseSignal.player_id == player_id,
            AbuseSignal.is_resolved == False
        ).scalar() or 0
        
        bonus_abuse_score = min(abuse_count * 20, 100)  # Cap at 100
        
        return {
            "win_loss_ratio": win_loss_ratio,
            "volatility_score": volatility_score,
            "bonus_abuse_score": bonus_abuse_score
        }
    
    def calculate_action_metrics(self, player_id: str) -> Dict[str, Any]:
        """
        Calculate action-based metrics (KYC, Profile, etc.)
        """
        # KYC status
        kyc_action = self.db.query(PlayerAction).filter(
            PlayerAction.player_id == player_id,
            PlayerAction.action_type == "KYC_COMPLETE"
        ).first()
        
        # Profile depth (0-100)
        profile_action = self.db.query(PlayerAction).filter(
            PlayerAction.player_id == player_id,
            PlayerAction.action_type == "PROFILE_DEEPENING"
        ).order_by(PlayerAction.created_at.desc()).first()
        
        profile_depth = 0
        if profile_action and profile_action.value:
            try:
                profile_depth = int(profile_action.value)
            except ValueError:
                profile_depth = 0

        # Monthly active days (days with at least one wager in the last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_days = self.db.query(func.count(func.distinct(func.date(Transaction.created_at)))).filter(
            Transaction.player_id == player_id,
            Transaction.transaction_type == TransactionType.WAGER,
            Transaction.created_at >= thirty_days_ago
        ).scalar() or 0
        
        return {
            "kyc_completed": kyc_action is not None,
            "profile_depth": profile_depth,
            "monthly_active_days": active_days
        }
    
    def calculate_risk_score(self, player_id: str) -> int:
        """
        Calculate overall risk score (0-100)
        Higher = more risky
        
        Factors:
        - Bonus abuse signals
        - Win/loss ratio (too high = suspicious)
        - Withdrawal patterns
        - Account age
        """
        risk_metrics = self.calculate_risk_metrics(player_id)
        
        # Start with bonus abuse score
        risk_score = risk_metrics["bonus_abuse_score"]
        
        # Adjust for win/loss ratio (winning too much = suspicious)
        if risk_metrics["win_loss_ratio"] > 1.5:
            risk_score += 20
        
        # Cap at 100
        return min(int(risk_score), 100)
    
    def update_player_metrics(
        self, 
        player_id: str,
        session_data: Optional[Dict] = None
    ) -> PlayerMetrics:
        """
        Update all metrics for a player
        
        Args:
            player_id: Player ID
            session_data: Optional session data from Excel import
        
        Returns:
            Updated PlayerMetrics object
        """
        logger.info(f"Updating metrics for player {player_id}")
        
        # Calculate all metrics
        financial = self.calculate_financial_metrics(player_id)
        behavioral = self.calculate_behavioral_metrics(player_id, session_data)
        risk = self.calculate_risk_metrics(player_id, financial)
        
        # Get or create metrics record
        metrics = self.db.query(PlayerMetrics).filter(
            PlayerMetrics.player_id == player_id
        ).first()
        
        if not metrics:
            metrics = PlayerMetrics(player_id=player_id)
            self.db.add(metrics)
        
        # Update financial metrics
        metrics.total_deposited = financial["total_deposited"]
        metrics.total_wagered = financial["total_wagered"]
        metrics.total_won = financial["total_won"]
        metrics.net_pnl = financial["net_pnl"]
        metrics.house_edge_contribution = financial["house_edge_contribution"]
        
        # Update behavioral metrics
        metrics.total_sessions = behavioral["total_sessions"]
        metrics.total_playtime_hours = behavioral["total_playtime_hours"]
        metrics.avg_session_duration = behavioral["avg_session_duration"]
        metrics.total_bets = behavioral["total_bets"]
        metrics.avg_bet_size = behavioral["avg_bet_size"]
        metrics.games_played = behavioral["games_played"]
        
        # Update risk metrics
        metrics.win_loss_ratio = risk["win_loss_ratio"]
        metrics.volatility_score = risk["volatility_score"]
        metrics.bonus_abuse_score = risk["bonus_abuse_score"]
        
        # Update timestamps
        last_deposit = self.db.query(func.max(Transaction.created_at)).filter(
            Transaction.player_id == player_id,
            Transaction.transaction_type == TransactionType.DEPOSIT
        ).scalar()
        
        last_wager = self.db.query(func.max(Transaction.created_at)).filter(
            Transaction.player_id == player_id,
            Transaction.transaction_type == TransactionType.WAGER
        ).scalar()
        
        metrics.last_deposit_at = last_deposit
        metrics.last_wager_at = last_wager
        
        self.db.commit()
        self.db.refresh(metrics)
        
        logger.info(f"Metrics updated for player {player_id}")
        return metrics
    
    def get_player_state(self, player_id: str) -> Dict:
        """
        Get complete player state for rule evaluation
        
        Returns comprehensive dict with all player data
        """
        player = self.db.query(Player).filter(Player.player_id == player_id).first()
        if not player:
            raise ValueError(f"Player {player_id} not found")
        
        metrics = player.metrics
        balances = player.balances
        
        # Calculate days since last deposit
        days_since_last_deposit = None
        if metrics and metrics.last_deposit_at:
            days_since_last_deposit = (
                datetime.utcnow() - metrics.last_deposit_at
            ).days
        
        state = {
            "player_id": player_id,
            "segment": player.segment.value,
            "tier": player.tier.value,
            "risk_score": player.risk_score,
            "is_active": player.is_active,
            "is_blocked": player.is_blocked,
            
            # Financial
            "total_deposited": metrics.total_deposited if metrics else 0,
            "total_wagered": metrics.total_wagered if metrics else 0,
            "total_won": metrics.total_won if metrics else 0,
            "net_pnl": metrics.net_pnl if metrics else 0,
            "net_loss": abs(metrics.net_pnl) if metrics and metrics.net_pnl < 0 else 0,
            
            # Behavioral
            "session_count": metrics.total_sessions if metrics else 0,
            "total_playtime_hours": metrics.total_playtime_hours if metrics else 0,
            "avg_bet_size": metrics.avg_bet_size if metrics else 0,
            
            # Risk
            "win_loss_ratio": metrics.win_loss_ratio if metrics else 0,
            "bonus_abuse_score": metrics.bonus_abuse_score if metrics else 0,
            
            # Time-based
            "days_since_last_deposit": days_since_last_deposit,
            
            # Balances
            "lp_balance": balances.lp_balance if balances else 0,
            "rp_balance": balances.rp_balance if balances else 0,
            "bonus_balance": balances.bonus_balance if balances else 0,
            "tickets_balance": balances.tickets_balance if balances else 0,
        }
        
        # Add action metrics
        action_metrics = self.calculate_action_metrics(player_id)
        state.update(action_metrics)
        
        # Add tier benefits to state for rule evaluation
        tier_config = self.db.query(Tier).filter(Tier.tier_level == player.tier).first()
        if tier_config and tier_config.benefits:
            state.update(tier_config.benefits)
            
        return state
