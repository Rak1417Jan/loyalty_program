"""
SQLAlchemy models for the Loyalty & Reward Program
"""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, 
    ForeignKey, Enum, JSON, Index, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum
from datetime import datetime


# Enums
class PlayerSegment(str, enum.Enum):
    """Player segmentation categories"""
    NEW = "NEW"
    WINNING = "WINNING"
    BREAKEVEN = "BREAKEVEN"
    LOSING = "LOSING"
    VIP = "VIP"


class TierLevel(str, enum.Enum):
    """Loyalty tier levels"""
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"
    DIAMOND = "DIAMOND"


class CurrencyType(str, enum.Enum):
    """Loyalty currency types"""
    LOYALTY_POINTS = "LP"  # Loyalty Points
    REWARD_POINTS = "RP"   # Reward Points
    BONUS_BALANCE = "BONUS"  # Play-only money
    TICKETS = "TICKETS"    # Event/contest entry
    CASH = "CASH"          # Real money


class RewardType(str, enum.Enum):
    """Types of rewards"""
    CASHBACK = "CASHBACK"
    BONUS_BALANCE = "BONUS_BALANCE"
    FREE_PLAY = "FREE_PLAY"
    LOYALTY_POINTS = "LOYALTY_POINTS"
    REWARD_POINTS = "REWARD_POINTS"
    TICKETS = "TICKETS"
    VIP_PERKS = "VIP_PERKS"


class TransactionType(str, enum.Enum):
    """Transaction types"""
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    WAGER = "WAGER"
    WIN = "WIN"
    REWARD = "REWARD"
    BONUS_ISSUED = "BONUS_ISSUED"
    BONUS_EXPIRED = "BONUS_EXPIRED"
    LP_EARNED = "LP_EARNED"
    LP_REDEEMED = "LP_REDEEMED"
    LP_EXPIRED = "LP_EXPIRED"
    KYC_COMPLETED = "KYC_COMPLETED"
    PROFILE_COMPLETED = "PROFILE_COMPLETED"
    ACTION = "ACTION"


class RewardStatus(str, enum.Enum):
    """Reward status"""
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


# Models
class Player(Base):
    """Core player profile"""
    __tablename__ = "players"
    
    player_id = Column(String(50), primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=True)
    name = Column(String(255), nullable=True)
    
    # Segmentation
    segment = Column(Enum(PlayerSegment), default=PlayerSegment.NEW, index=True)
    tier = Column(Enum(TierLevel), default=TierLevel.BRONZE, index=True)
    risk_score = Column(Integer, default=0)  # 0-100
    
    # Status
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_activity_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    metrics = relationship("PlayerMetrics", back_populates="player", uselist=False)
    balances = relationship("LoyaltyBalance", back_populates="player", uselist=False)
    transactions = relationship("Transaction", back_populates="player")
    rewards = relationship("RewardHistory", back_populates="player")
    abuse_signals = relationship("AbuseSignal", back_populates="player")
    actions = relationship("PlayerAction", back_populates="player")
    point_entries = relationship("LoyaltyPointEntry", back_populates="player")
    redemptions = relationship("LoyaltyRedemption", back_populates="player")
    
    __table_args__ = (
        Index('idx_player_segment_tier', 'segment', 'tier'),
    )


class PlayerMetrics(Base):
    """Player financial and behavioral metrics"""
    __tablename__ = "player_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String(50), ForeignKey("players.player_id"), unique=True, index=True)
    
    # Financial Metrics
    total_deposited = Column(Float, default=0.0)
    total_wagered = Column(Float, default=0.0)
    total_won = Column(Float, default=0.0)
    net_pnl = Column(Float, default=0.0)  # Win - Loss
    house_edge_contribution = Column(Float, default=0.0)
    
    # Behavioral Metrics
    total_sessions = Column(Integer, default=0)
    total_playtime_hours = Column(Float, default=0.0)
    avg_session_duration = Column(Float, default=0.0)
    total_bets = Column(Integer, default=0)
    avg_bet_size = Column(Float, default=0.0)
    games_played = Column(JSON, default=dict)  # {"slots": 50, "poker": 20}
    
    # Risk Metrics
    win_loss_ratio = Column(Float, default=0.0)
    volatility_score = Column(Float, default=0.0)
    bonus_abuse_score = Column(Integer, default=0)
    
    # Timestamps
    last_deposit_at = Column(DateTime(timezone=True), nullable=True)
    last_wager_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    player = relationship("Player", back_populates="metrics")


class LoyaltyBalance(Base):
    """Multi-currency wallet for each player"""
    __tablename__ = "loyalty_balances"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String(50), ForeignKey("players.player_id"), unique=True, index=True)
    
    # Currency Balances
    lp_balance = Column(Float, default=0.0)  # Loyalty Points
    rp_balance = Column(Float, default=0.0)  # Reward Points
    bonus_balance = Column(Float, default=0.0)  # Bonus money
    tickets_balance = Column(Integer, default=0)  # Tickets
    
    # Bonus Restrictions
    bonus_wagering_required = Column(Float, default=0.0)  # Amount to wager
    bonus_wagering_completed = Column(Float, default=0.0)  # Amount wagered
    bonus_expiry = Column(DateTime(timezone=True), nullable=True)
    bonus_max_bet = Column(Float, nullable=True)
    bonus_eligible_games = Column(JSON, default=list)  # ["slots", "roulette"]
    
    # Timestamps
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    player = relationship("Player", back_populates="balances")
    
    __table_args__ = (
        CheckConstraint('lp_balance >= 0', name='check_lp_positive'),
        CheckConstraint('rp_balance >= 0', name='check_rp_positive'),
        CheckConstraint('bonus_balance >= 0', name='check_bonus_positive'),
        CheckConstraint('tickets_balance >= 0', name='check_tickets_positive'),
    )


class Tier(Base):
    """Loyalty tier configuration"""
    __tablename__ = "tiers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tier_level = Column(Enum(TierLevel), unique=True, index=True)
    lp_min = Column(Integer, nullable=False)
    lp_max = Column(Integer, nullable=True)
    
    # Benefits (JSON)
    benefits = Column(JSON, default=dict)
    # Example: {"cashback_multiplier": 1.5, "free_plays_per_month": 10}
    
    # Requirements (JSON)
    requirements = Column(JSON, default=dict)
    # Example: {"lp_min": 1000, "kyc_required": true, "min_active_days_monthly": 5}
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RewardRule(Base):
    """Configurable reward rules"""
    __tablename__ = "reward_rules"
    
    rule_id = Column(String(100), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    
    # Rule Configuration
    priority = Column(Integer, default=0)  # Higher = evaluated first
    is_active = Column(Boolean, default=True)
    
    # Conditions (JSON)
    conditions = Column(JSON, nullable=False)
    # Example: {"segment": "LOSING", "net_loss_min": 100, "session_count_min": 3}
    
    # Reward Configuration (JSON)
    reward_config = Column(JSON, nullable=False)
    # Example: {"type": "BONUS_BALANCE", "formula": "net_loss * 0.10", "max_amount": 500}
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_rule_priority_active', 'priority', 'is_active'),
    )


class Transaction(Base):
    """Complete audit trail of all balance changes"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String(50), ForeignKey("players.player_id"), index=True)
    
    # Transaction Details
    transaction_type = Column(Enum(TransactionType), nullable=False, index=True)
    currency_type = Column(Enum(CurrencyType), nullable=False)
    amount = Column(Float, nullable=False)
    balance_before = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=False)
    
    # Metadata
    description = Column(String(500), nullable=True)
    reference_id = Column(String(100), nullable=True)  # External reference
    meta_data = Column(JSON, default=dict)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    player = relationship("Player", back_populates="transactions")
    
    __table_args__ = (
        Index('idx_transaction_player_date', 'player_id', 'created_at'),
    )


class RewardHistory(Base):
    """Track all rewards issued"""
    __tablename__ = "reward_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String(50), ForeignKey("players.player_id"), index=True)
    rule_id = Column(String(100), ForeignKey("reward_rules.rule_id"), nullable=True)
    
    # Reward Details
    reward_type = Column(Enum(RewardType), nullable=False)
    amount = Column(Float, nullable=False)
    currency_type = Column(Enum(CurrencyType), nullable=False)
    
    # Status
    status = Column(Enum(RewardStatus), default=RewardStatus.PENDING, index=True)
    
    # Wagering Requirements
    wagering_required = Column(Float, default=0.0)
    wagering_completed = Column(Float, default=0.0)
    
    # Expiry
    issued_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    meta_data = Column(JSON, default=dict)
    
    # Relationships
    player = relationship("Player", back_populates="rewards")
    
    __table_args__ = (
        Index('idx_reward_player_status', 'player_id', 'status'),
    )


class AbuseSignal(Base):
    """Fraud and abuse detection signals"""
    __tablename__ = "abuse_signals"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String(50), ForeignKey("players.player_id"), index=True)
    
    # Signal Details
    signal_type = Column(String(100), nullable=False)
    # Types: "BONUS_ONLY_PLAY", "IMMEDIATE_WITHDRAWAL", "BET_MANIPULATION", etc.
    
    severity = Column(Integer, default=1)  # 1-10
    description = Column(String(500), nullable=True)
    meta_data = Column(JSON, default=dict)
    
    # Status
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamp
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    player = relationship("Player", back_populates="abuse_signals")
    
    __table_args__ = (
        Index('idx_abuse_player_unresolved', 'player_id', 'is_resolved'),
    )


class PlayerAction(Base):
    """Log of specific player actions (KYC, Profile depth, etc.)"""
    __tablename__ = "player_actions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String(50), ForeignKey("players.player_id"), index=True)
    action_type = Column(String(100), nullable=False, index=True)  # "KYC_COMPLETE", "PROFILE_DEEPENING"
    value = Column(String(255), nullable=True)  # Optional value or detail
    meta_data = Column(JSON, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    player = relationship("Player", back_populates="actions")


class RedemptionRule(Base):
    """Configuration for loyalty point redemptions"""
    __tablename__ = "redemption_rules"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Conversion parameters
    lp_cost = Column(Integer, nullable=False)  # Points required
    currency_value = Column(Float, nullable=False)  # Value in real currency
    currency_type = Column(Enum(CurrencyType), default=CurrencyType.CASH)
    
    # Redirection/Destination
    target_balance = Column(String(50), default="CASH")  # "CASH", "BONUS"
    
    # Constraints
    min_lp_balance = Column(Integer, default=0)
    max_redemptions_per_month = Column(Integer, nullable=True)
    tier_requirement = Column(Enum(TierLevel), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class LoyaltyPointEntry(Base):
    """Individual point entries for FIFO expiry tracking"""
    __tablename__ = "loyalty_point_entries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String(50), ForeignKey("players.player_id"), index=True)
    
    amount = Column(Float, nullable=False)
    remaining_amount = Column(Float, nullable=False)  # For partial redemptions
    
    source_type = Column(String(50), nullable=True)  # "WAGER", "REWARD", "ACTION"
    source_id = Column(String(100), nullable=True)
    
    # Expiry
    issued_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    is_expired = Column(Boolean, default=False, index=True)
    
    player = relationship("Player", back_populates="point_entries")


class LoyaltyRedemption(Base):
    """Audit trail for redemptions"""
    __tablename__ = "loyalty_redemptions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String(50), ForeignKey("players.player_id"), index=True)
    rule_id = Column(Integer, ForeignKey("redemption_rules.id"))
    
    lp_amount = Column(Integer, nullable=False)
    value_received = Column(Float, nullable=False)
    currency_type = Column(Enum(CurrencyType), nullable=False)
    
    status = Column(Enum(RewardStatus), default=RewardStatus.COMPLETED)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    player = relationship("Player", back_populates="redemptions")
