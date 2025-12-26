"""
Wallet Manager
Manages multi-currency balances with restrictions and wagering requirements
"""
from sqlalchemy.orm import Session
from models import (
    LoyaltyBalance, Transaction, TransactionType, CurrencyType,
    RewardHistory, RewardStatus, Player, LoyaltyPointEntry,
    RedemptionRule, LoyaltyRedemption
)
from typing import Optional, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WalletManager:
    """Manage player wallets and balances"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_balance(self, player_id: str) -> LoyaltyBalance:
        """Get or create balance record for player"""
        balance = self.db.query(LoyaltyBalance).filter(
            LoyaltyBalance.player_id == player_id
        ).first()
        
        if not balance:
            balance = LoyaltyBalance(player_id=player_id)
            self.db.add(balance)
            self.db.commit()
            self.db.refresh(balance)
        
        return balance
    
    def create_transaction(
        self,
        player_id: str,
        transaction_type: TransactionType,
        currency_type: CurrencyType,
        amount: float,
        balance_before: float,
        balance_after: float,
        description: Optional[str] = None,
        reference_id: Optional[str] = None,
        meta_data: Optional[Dict] = None
    ) -> Transaction:
        """Create a transaction record"""
        transaction = Transaction(
            player_id=player_id,
            transaction_type=transaction_type,
            currency_type=currency_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            description=description,
            reference_id=reference_id,
            meta_data=meta_data or {}
        )
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    def add_loyalty_points(
        self,
        player_id: str,
        amount: float,
        source: str = "REWARD",
        description: Optional[str] = None,
        expiry_days: Optional[int] = None
    ) -> Transaction:
        """
        Add loyalty points to player balance
        
        Args:
            player_id: Player ID
            amount: LP amount to add
            source: Source of LP (REWARD, WAGER, etc.)
            description: Optional description
        
        Returns:
            Transaction object
        """
        balance = self.get_or_create_balance(player_id)
        
        balance_before = balance.lp_balance
        balance.lp_balance += amount
        balance_after = balance.lp_balance
        
        transaction = self.create_transaction(
            player_id=player_id,
            transaction_type=TransactionType.LP_EARNED,
            currency_type=CurrencyType.LOYALTY_POINTS,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            description=description or f"Loyalty points from {source}",
            meta_data={"source": source}
        )
        
        self.db.commit()
        
        # Add FIFO point entry
        expires_at = None
        if expiry_days:
            from datetime import timedelta
            expires_at = datetime.utcnow() + timedelta(days=expiry_days)
            
        point_entry = LoyaltyPointEntry(
            player_id=player_id,
            amount=amount,
            remaining_amount=amount,
            source_type=source,
            expires_at=expires_at
        )
        self.db.add(point_entry)
        self.db.commit()
        
        logger.info(f"Added {amount} LP to player {player_id} (Expires: {expires_at})")
        
        # Update player tier based on new LP balance
        try:
            from analytics.tier_service import TierService
            tier_service = TierService(self.db)
            tier_service.update_player_tier(player_id)
        except Exception as e:
            logger.error(f"Error updating tier for player {player_id}: {str(e)}")
        
        return transaction
    
    def add_bonus_balance(
        self,
        player_id: str,
        amount: float,
        wagering_requirement: float = 0.0,
        expiry: Optional[datetime] = None,
        max_bet: Optional[float] = None,
        eligible_games: Optional[list] = None,
        reward_id: Optional[int] = None,
        description: Optional[str] = None
    ) -> Transaction:
        """
        Add bonus balance with restrictions
        
        Args:
            player_id: Player ID
            amount: Bonus amount
            wagering_requirement: Total amount to wager (e.g., amount * 10)
            expiry: Expiry datetime
            max_bet: Maximum bet size with bonus
            eligible_games: List of eligible game types
            reward_id: Associated reward ID
            description: Optional description
        
        Returns:
            Transaction object
        """
        balance = self.get_or_create_balance(player_id)
        
        balance_before = balance.bonus_balance
        balance.bonus_balance += amount
        balance_after = balance.bonus_balance
        
        # Update bonus restrictions
        balance.bonus_wagering_required += wagering_requirement
        if expiry:
            balance.bonus_expiry = expiry
        if max_bet:
            balance.bonus_max_bet = max_bet
        if eligible_games:
            balance.bonus_eligible_games = eligible_games
        
        transaction = self.create_transaction(
            player_id=player_id,
            transaction_type=TransactionType.BONUS_ISSUED,
            currency_type=CurrencyType.BONUS_BALANCE,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            description=description or "Bonus balance issued",
            reference_id=str(reward_id) if reward_id else None,
            meta_data={
                "wagering_required": wagering_requirement,
                "expiry": expiry.isoformat() if expiry else None,
                "max_bet": max_bet,
                "eligible_games": eligible_games or []
            }
        )
        
        self.db.commit()
        logger.info(
            f"Added {amount} bonus balance to player {player_id} "
            f"(wagering: {wagering_requirement})"
        )
        
        return transaction
    
    def deduct_balance(
        self,
        player_id: str,
        currency_type: CurrencyType,
        amount: float,
        description: Optional[str] = None
    ) -> Transaction:
        """
        Deduct from player balance
        
        Args:
            player_id: Player ID
            currency_type: Currency to deduct from
            amount: Amount to deduct
            description: Optional description
        
        Returns:
            Transaction object
        
        Raises:
            ValueError: If insufficient balance
        """
        balance = self.get_or_create_balance(player_id)
        
        # Get current balance
        if currency_type == CurrencyType.LOYALTY_POINTS:
            current_balance = balance.lp_balance
        elif currency_type == CurrencyType.REWARD_POINTS:
            current_balance = balance.rp_balance
        elif currency_type == CurrencyType.BONUS_BALANCE:
            current_balance = balance.bonus_balance
        elif currency_type == CurrencyType.TICKETS:
            current_balance = balance.tickets_balance
        else:
            raise ValueError(f"Unknown currency type: {currency_type}")
        
        # Check sufficient balance
        if current_balance < amount:
            raise ValueError(
                f"Insufficient {currency_type.value} balance. "
                f"Required: {amount}, Available: {current_balance}"
            )
        
        balance_before = current_balance
        new_balance = current_balance - amount
        
        # Update balance
        if currency_type == CurrencyType.LOYALTY_POINTS:
            balance.lp_balance = new_balance
        elif currency_type == CurrencyType.REWARD_POINTS:
            balance.rp_balance = new_balance
        elif currency_type == CurrencyType.BONUS_BALANCE:
            balance.bonus_balance = new_balance
        elif currency_type == CurrencyType.TICKETS:
            balance.tickets_balance = int(new_balance)
        
        transaction = self.create_transaction(
            player_id=player_id,
            transaction_type=TransactionType.LP_REDEEMED,  # Or appropriate type
            currency_type=currency_type,
            amount=-amount,  # Negative for deduction
            balance_before=balance_before,
            balance_after=new_balance,
            description=description or f"Deducted {currency_type.value}"
        )
        
        self.db.commit()
        logger.info(f"Deducted {amount} {currency_type.value} from player {player_id}")
        
        # If LP, handle FIFO point entries
        if currency_type == CurrencyType.LOYALTY_POINTS:
            self._deduct_lp_fifo(player_id, amount)
            
        return transaction

    def _deduct_lp_fifo(self, player_id: str, amount: float):
        """Deduct points from individual entries using FIFO"""
        remaining_to_deduct = amount
        # Get active entries ordered by oldest first
        entries = self.db.query(LoyaltyPointEntry).filter(
            LoyaltyPointEntry.player_id == player_id,
            LoyaltyPointEntry.remaining_amount > 0,
            LoyaltyPointEntry.is_expired == False
        ).order_by(LoyaltyPointEntry.issued_at.asc()).all()
        
        for entry in entries:
            if remaining_to_deduct <= 0:
                break
            
            if entry.remaining_amount <= remaining_to_deduct:
                remaining_to_deduct -= entry.remaining_amount
                entry.remaining_amount = 0
            else:
                entry.remaining_amount -= remaining_to_deduct
                remaining_to_deduct = 0
                
        self.db.commit()

    def redeem_points(
        self,
        player_id: str,
        rule_id: int
    ) -> LoyaltyRedemption:
        """
        Redeem loyalty points for a reward based on a rule
        """
        player = self.db.query(Player).filter(Player.player_id == player_id).first()
        rule = self.db.query(RedemptionRule).filter(RedemptionRule.id == rule_id).first()
        
        if not rule or not rule.is_active:
            raise ValueError("Redemption rule not found or inactive")
            
        # Check tier requirement
        if rule.tier_requirement and player.tier.value < rule.tier_requirement.value:
            raise ValueError(f"Tier {rule.tier_requirement.value} required for this redemption")
            
        # Check LP balance
        balance = self.get_or_create_balance(player_id)
        if balance.lp_balance < rule.lp_cost or balance.lp_balance < rule.min_lp_balance:
            raise ValueError(f"Insufficient LP balance for redemption. Cost: {rule.lp_cost}")
            
        # Deduct LP
        self.deduct_balance(
            player_id=player_id,
            currency_type=CurrencyType.LOYALTY_POINTS,
            amount=rule.lp_cost,
            description=f"Redemption: {rule.name}"
        )
        
        # Give value (Cash or Bonus)
        if rule.target_balance == "CASH":
            # In a real system, this would add to a real money wallet
            # For this demo, we'll just log it as a transaction
            self.create_transaction(
                player_id=player_id,
                transaction_type=TransactionType.REWARD,
                currency_type=CurrencyType.CASH,
                amount=rule.currency_value,
                balance_before=0, # Simplified
                balance_after=rule.currency_value,
                description=f"Cash from LP redemption: {rule.name}"
            )
        elif rule.target_balance == "BONUS":
            self.add_bonus_balance(
                player_id=player_id,
                amount=rule.currency_value,
                description=f"Bonus from LP redemption: {rule.name}"
            )
            
        # Create redemption record
        redemption = LoyaltyRedemption(
            player_id=player_id,
            rule_id=rule.id,
            lp_amount=rule.lp_cost,
            value_received=rule.currency_value,
            currency_type=rule.currency_type
        )
        self.db.add(redemption)
        self.db.commit()
        self.db.refresh(redemption)
        
        logger.info(f"Player {player_id} redeemed {rule.lp_cost} LP for {rule.currency_value} {rule.target_balance}")
        return redemption

    def process_point_expiry(self) -> int:
        """Find and expire points that have passed their expiry date"""
        now = datetime.utcnow()
        expired_entries = self.db.query(LoyaltyPointEntry).filter(
            LoyaltyPointEntry.is_expired == False,
            LoyaltyPointEntry.expires_at <= now,
            LoyaltyPointEntry.remaining_amount > 0
        ).all()
        
        total_expired = 0
        for entry in expired_entries:
            amount = entry.remaining_amount
            # Deduct from main balance
            balance = self.get_or_create_balance(entry.player_id)
            balance_before = balance.lp_balance
            balance.lp_balance -= amount
            
            # Create transaction
            self.create_transaction(
                player_id=entry.player_id,
                transaction_type=TransactionType.LP_EXPIRED,
                currency_type=CurrencyType.LOYALTY_POINTS,
                amount=-amount,
                balance_before=balance_before,
                balance_after=balance.lp_balance,
                description=f"Points expired (Entry #{entry.id})"
            )
            
            # Mark entry as expired
            entry.is_expired = True
            entry.remaining_amount = 0
            total_expired += 1
            
        self.db.commit()
        return total_expired
    
    def record_wager(
        self,
        player_id: str,
        amount: float,
        game_type: Optional[str] = None
    ) -> Optional[float]:
        """
        Record a wager and update bonus wagering progress
        
        Args:
            player_id: Player ID
            amount: Wager amount
            game_type: Type of game (for bonus eligibility check)
        
        Returns:
            Wagering progress percentage (0-100) if bonus active, None otherwise
        """
        balance = self.get_or_create_balance(player_id)
        
        # Check if player has active bonus with wagering requirement
        if balance.bonus_wagering_required > 0:
            # Check if game is eligible
            eligible_games = balance.bonus_eligible_games
            if eligible_games and game_type and game_type not in eligible_games:
                logger.warning(
                    f"Wager on {game_type} does not count toward bonus wagering "
                    f"for player {player_id}"
                )
                return None
            
            # Check max bet restriction
            if balance.bonus_max_bet and amount > balance.bonus_max_bet:
                logger.warning(
                    f"Wager amount {amount} exceeds max bet {balance.bonus_max_bet} "
                    f"for player {player_id}"
                )
                # Could enforce by rejecting bet or capping contribution
            
            # Update wagering progress
            balance.bonus_wagering_completed += amount
            
            # Calculate progress
            progress = (
                balance.bonus_wagering_completed / balance.bonus_wagering_required * 100
            )
            
            # Check if wagering complete
            if balance.bonus_wagering_completed >= balance.bonus_wagering_required:
                logger.info(f"Player {player_id} completed bonus wagering requirement")
                # Could unlock bonus or convert to withdrawable
                balance.bonus_wagering_required = 0
                balance.bonus_wagering_completed = 0
                progress = 100.0
            
            self.db.commit()
            return progress
        
        return None
    
    def expire_bonuses(self) -> int:
        """
        Expire bonuses that have passed their expiry date
        
        Returns:
            Number of bonuses expired
        """
        expired_count = 0
        
        # Find all balances with expired bonuses
        balances = self.db.query(LoyaltyBalance).filter(
            LoyaltyBalance.bonus_balance > 0,
            LoyaltyBalance.bonus_expiry <= datetime.utcnow()
        ).all()
        
        for balance in balances:
            amount = balance.bonus_balance
            
            # Create expiry transaction
            self.create_transaction(
                player_id=balance.player_id,
                transaction_type=TransactionType.BONUS_EXPIRED,
                currency_type=CurrencyType.BONUS_BALANCE,
                amount=-amount,
                balance_before=amount,
                balance_after=0.0,
                description="Bonus expired"
            )
            
            # Clear bonus
            balance.bonus_balance = 0.0
            balance.bonus_wagering_required = 0.0
            balance.bonus_wagering_completed = 0.0
            balance.bonus_expiry = None
            
            expired_count += 1
            logger.info(f"Expired {amount} bonus balance for player {balance.player_id}")
        
        self.db.commit()
        logger.info(f"Expired {expired_count} bonuses")
        
        return expired_count
    
    def issue_reward(self, reward_id: int) -> Transaction:
        """
        Issue a reward to player's wallet
        
        Args:
            reward_id: RewardHistory ID
        
        Returns:
            Transaction object
        """
        reward = self.db.query(RewardHistory).filter(
            RewardHistory.id == reward_id
        ).first()
        
        if not reward:
            raise ValueError(f"Reward {reward_id} not found")
        
        if reward.status != RewardStatus.PENDING:
            raise ValueError(f"Reward {reward_id} is not pending (status: {reward.status})")
        
        # Issue based on currency type
        if reward.currency_type == CurrencyType.LOYALTY_POINTS:
            transaction = self.add_loyalty_points(
                player_id=reward.player_id,
                amount=reward.amount,
                source="REWARD",
                description=f"Reward from rule {reward.rule_id}",
                expiry_days=reward.meta_data.get("lp_expiry_days")
            )
        
        elif reward.currency_type == CurrencyType.BONUS_BALANCE:
            transaction = self.add_bonus_balance(
                player_id=reward.player_id,
                amount=reward.amount,
                wagering_requirement=reward.wagering_required,
                expiry=reward.expires_at,
                max_bet=reward.meta_data.get("max_bet"),
                eligible_games=reward.meta_data.get("eligible_games"),
                reward_id=reward.id,
                description=f"Bonus from rule {reward.rule_id}"
            )
        
        else:
            # Handle other currency types
            raise NotImplementedError(f"Currency type {reward.currency_type} not implemented")
        
        # Update reward status
        reward.status = RewardStatus.ACTIVE
        self.db.commit()
        
        logger.info(f"Issued reward {reward_id} to player {reward.player_id}")
        
        return transaction
