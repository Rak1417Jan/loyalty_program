"""
Fraud and Abuse Detector
Identifies suspicious patterns and bonus abuse
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Player, AbuseSignal, Transaction, TransactionType, RewardHistory
from config import settings
from typing import List, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class FraudDetector:
    """Detect fraud and abuse patterns"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def detect_bonus_only_play(self, player_id: str) -> bool:
        """
        Detect if player only plays with bonus money
        
        Pattern: Player receives bonuses but never deposits real money
        
        Returns:
            True if suspicious pattern detected
        """
        # Get total deposits
        total_deposits = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.player_id == player_id,
            Transaction.transaction_type == TransactionType.DEPOSIT
        ).scalar() or 0.0
        
        # Get total bonuses received
        total_bonuses = self.db.query(func.sum(RewardHistory.amount)).filter(
            RewardHistory.player_id == player_id
        ).scalar() or 0.0
        
        # Suspicious if bonuses > 0 but deposits = 0
        if total_bonuses > 0 and total_deposits == 0:
            logger.warning(f"Player {player_id}: Bonus-only play detected")
            return True
        
        return False
    
    def detect_immediate_withdrawal(self, player_id: str, hours: int = 24) -> bool:
        """
        Detect immediate withdrawal after bonus/win
        
        Pattern: Player withdraws immediately after receiving bonus or winning
        
        Args:
            player_id: Player ID
            hours: Time window to check
        
        Returns:
            True if suspicious pattern detected
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        # Get recent rewards
        recent_rewards = self.db.query(RewardHistory).filter(
            RewardHistory.player_id == player_id,
            RewardHistory.issued_at >= cutoff
        ).count()
        
        # Get recent withdrawals
        recent_withdrawals = self.db.query(Transaction).filter(
            Transaction.player_id == player_id,
            Transaction.transaction_type == TransactionType.WITHDRAWAL,
            Transaction.created_at >= cutoff
        ).count()
        
        # Suspicious if withdrawal immediately after reward
        if recent_rewards > 0 and recent_withdrawals > 0:
            logger.warning(
                f"Player {player_id}: Immediate withdrawal detected "
                f"({recent_withdrawals} withdrawals after {recent_rewards} rewards)"
            )
            return True
        
        return False
    
    def detect_bet_manipulation(self, player_id: str) -> bool:
        """
        Detect bet size manipulation during wagering requirement
        
        Pattern: Player makes minimum bets to complete wagering, then large bets
        
        Returns:
            True if suspicious pattern detected
        """
        # Get player's metrics
        from models import PlayerMetrics
        metrics = self.db.query(PlayerMetrics).filter(
            PlayerMetrics.player_id == player_id
        ).first()
        
        if not metrics or metrics.total_bets < 10:
            return False
        
        # Get recent bet sizes
        recent_bets = self.db.query(Transaction.amount).filter(
            Transaction.player_id == player_id,
            Transaction.transaction_type == TransactionType.WAGER
        ).order_by(Transaction.created_at.desc()).limit(20).all()
        
        if len(recent_bets) < 10:
            return False
        
        bet_amounts = [bet[0] for bet in recent_bets]
        avg_bet = sum(bet_amounts) / len(bet_amounts)
        min_bet = min(bet_amounts)
        max_bet = max(bet_amounts)
        
        # Suspicious if huge variance (min bet << avg << max bet)
        if min_bet > 0 and max_bet / min_bet > 10:
            logger.warning(
                f"Player {player_id}: Bet manipulation detected "
                f"(min: {min_bet}, avg: {avg_bet:.2f}, max: {max_bet})"
            )
            return True
        
        return False
    
    def detect_multi_accounting(self, player_id: str) -> bool:
        """
        Detect multiple accounts from same source
        
        Pattern: Same IP, device, or payment method
        
        Note: This is a placeholder - requires IP/device tracking
        
        Returns:
            True if suspicious pattern detected
        """
        # In production, would check:
        # - Same IP address
        # - Same device fingerprint
        # - Same payment method
        # - Similar registration patterns
        
        # Placeholder implementation
        return False
    
    def detect_abnormal_win_rate(self, player_id: str) -> bool:
        """
        Detect abnormally high win rate
        
        Pattern: Win rate significantly above expected
        
        Returns:
            True if suspicious pattern detected
        """
        from models import PlayerMetrics
        metrics = self.db.query(PlayerMetrics).filter(
            PlayerMetrics.player_id == player_id
        ).first()
        
        if not metrics or metrics.total_wagered < 1000:
            return False
        
        # Calculate win rate
        win_rate = metrics.total_won / metrics.total_wagered if metrics.total_wagered > 0 else 0
        
        # Suspicious if win rate > 1.2 (20% profit)
        if win_rate > 1.2:
            logger.warning(
                f"Player {player_id}: Abnormal win rate detected ({win_rate:.2%})"
            )
            return True
        
        return False
    
    def create_abuse_signal(
        self,
        player_id: str,
        signal_type: str,
        severity: int,
        description: str,
        metadata: Dict = None
    ) -> AbuseSignal:
        """
        Create an abuse signal record
        
        Args:
            player_id: Player ID
            signal_type: Type of signal
            severity: Severity (1-10)
            description: Description
            metadata: Additional metadata
        
        Returns:
            AbuseSignal object
        """
        signal = AbuseSignal(
            player_id=player_id,
            signal_type=signal_type,
            severity=severity,
            description=description,
            metadata=metadata or {}
        )
        
        self.db.add(signal)
        self.db.commit()
        self.db.refresh(signal)
        
        logger.warning(
            f"Abuse signal created for player {player_id}: "
            f"{signal_type} (severity: {severity})"
        )
        
        return signal
    
    def detect_abuse_signals(self, player_id: str) -> List[AbuseSignal]:
        """
        Run all abuse detection checks for a player
        
        Returns:
            List of newly created AbuseSignal objects
        """
        signals = []
        
        # Check bonus-only play
        if self.detect_bonus_only_play(player_id):
            signal = self.create_abuse_signal(
                player_id=player_id,
                signal_type="BONUS_ONLY_PLAY",
                severity=5,
                description="Player only plays with bonus money, no real deposits"
            )
            signals.append(signal)
        
        # Check immediate withdrawal
        if self.detect_immediate_withdrawal(player_id):
            signal = self.create_abuse_signal(
                player_id=player_id,
                signal_type="IMMEDIATE_WITHDRAWAL",
                severity=7,
                description="Withdrawal immediately after receiving reward"
            )
            signals.append(signal)
        
        # Check bet manipulation
        if self.detect_bet_manipulation(player_id):
            signal = self.create_abuse_signal(
                player_id=player_id,
                signal_type="BET_MANIPULATION",
                severity=8,
                description="Suspicious bet size variance during wagering"
            )
            signals.append(signal)
        
        # Check abnormal win rate
        if self.detect_abnormal_win_rate(player_id):
            signal = self.create_abuse_signal(
                player_id=player_id,
                signal_type="ABNORMAL_WIN_RATE",
                severity=9,
                description="Win rate significantly above expected"
            )
            signals.append(signal)
        
        return signals
    
    def calculate_abuse_score(self, player_id: str) -> int:
        """
        Calculate overall abuse score (0-100)
        
        Returns:
            Abuse score
        """
        # Get unresolved signals
        signals = self.db.query(AbuseSignal).filter(
            AbuseSignal.player_id == player_id,
            AbuseSignal.is_resolved == False
        ).all()
        
        # Calculate score based on severity
        total_severity = sum(signal.severity for signal in signals)
        
        # Cap at 100
        score = min(total_severity * 10, 100)
        
        return score
    
    def apply_abuse_penalty(self, player_id: str) -> str:
        """
        Apply penalty based on abuse score
        
        Penalties:
        - Score 0-30: No action
        - Score 31-60: Reduce reward multiplier
        - Score 61-80: Increase wagering requirements
        - Score 81-100: Block rewards
        
        Returns:
            Action taken
        """
        score = self.calculate_abuse_score(player_id)
        
        player = self.db.query(Player).filter(Player.player_id == player_id).first()
        if not player:
            return "Player not found"
        
        # Update risk score
        player.risk_score = score
        
        if score >= 81:
            # Block player
            player.is_blocked = True
            action = "BLOCKED"
            logger.warning(f"Player {player_id} blocked (abuse score: {score})")
        
        elif score >= 61:
            # Increase wagering requirements (handled in rules engine)
            action = "INCREASED_WAGERING"
            logger.warning(
                f"Player {player_id} flagged for increased wagering (abuse score: {score})"
            )
        
        elif score >= 31:
            # Reduce reward multiplier (handled in rules engine)
            action = "REDUCED_REWARDS"
            logger.warning(
                f"Player {player_id} flagged for reduced rewards (abuse score: {score})"
            )
        
        else:
            action = "NO_ACTION"
        
        self.db.commit()
        
        return action
    
    def flag_for_review(self, player_id: str, reason: str) -> None:
        """
        Flag player for manual review
        
        Args:
            player_id: Player ID
            reason: Reason for review
        """
        signal = self.create_abuse_signal(
            player_id=player_id,
            signal_type="MANUAL_REVIEW_REQUIRED",
            severity=10,
            description=f"Flagged for manual review: {reason}"
        )
        
        logger.critical(f"Player {player_id} flagged for manual review: {reason}")
