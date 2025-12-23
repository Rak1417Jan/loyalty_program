"""
Pydantic Schemas for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from models import PlayerSegment, TierLevel, RewardType, RewardStatus, CurrencyType


# Player Schemas
class PlayerBase(BaseModel):
    player_id: str
    email: Optional[str] = None
    name: Optional[str] = None


class PlayerCreate(PlayerBase):
    pass


class PlayerUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None
    is_blocked: Optional[bool] = None


class PlayerMetricsResponse(BaseModel):
    total_deposited: float
    total_wagered: float
    total_won: float
    net_pnl: float
    total_sessions: int
    total_playtime_hours: float
    win_loss_ratio: float
    bonus_abuse_score: int
    
    class Config:
        from_attributes = True


class PlayerBalanceResponse(BaseModel):
    lp_balance: float
    rp_balance: float
    bonus_balance: float
    tickets_balance: int
    bonus_wagering_required: float
    bonus_wagering_completed: float
    bonus_expiry: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PlayerResponse(PlayerBase):
    segment: PlayerSegment
    tier: TierLevel
    risk_score: int
    is_active: bool
    is_blocked: bool
    created_at: datetime
    last_activity_at: Optional[datetime] = None
    metrics: Optional[PlayerMetricsResponse] = None
    balances: Optional[PlayerBalanceResponse] = None
    
    class Config:
        from_attributes = True


# Reward Rule Schemas
class RewardRuleBase(BaseModel):
    rule_id: str
    name: str
    description: Optional[str] = None
    priority: int = 0
    is_active: bool = True
    conditions: Dict[str, Any]
    reward_config: Dict[str, Any]


class RewardRuleCreate(RewardRuleBase):
    pass


class RewardRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None
    conditions: Optional[Dict[str, Any]] = None
    reward_config: Optional[Dict[str, Any]] = None


class RewardRuleResponse(RewardRuleBase):
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RuleTestRequest(BaseModel):
    player_id: str


class RuleTestResponse(BaseModel):
    matches: bool
    reward_amount: Optional[float] = None
    player_state: Dict[str, Any]


# Tier Schemas
class TierBase(BaseModel):
    tier_level: TierLevel
    lp_min: int
    lp_max: Optional[int] = None
    benefits: Dict[str, Any] = {}


class TierCreate(TierBase):
    pass


class TierUpdate(BaseModel):
    lp_min: Optional[int] = None
    lp_max: Optional[int] = None
    benefits: Optional[Dict[str, Any]] = None


class TierResponse(TierBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Reward History Schemas
class RewardHistoryResponse(BaseModel):
    id: int
    player_id: str
    rule_id: Optional[str] = None
    reward_type: RewardType
    amount: float
    currency_type: CurrencyType
    status: RewardStatus
    wagering_required: float
    wagering_completed: float
    issued_at: datetime
    expires_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any]
    
    class Config:
        from_attributes = True


# Transaction Schemas
class TransactionResponse(BaseModel):
    id: int
    player_id: str
    transaction_type: str
    currency_type: Optional[str] = None
    amount: float
    balance_before: float
    balance_after: float
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Import Schemas
class ImportRequest(BaseModel):
    file_path: str


class ImportResponse(BaseModel):
    success: bool
    total_rows: int
    players_created: int
    players_updated: int
    rewards_issued: int
    errors: List[str]


# Analytics Schemas
class SegmentDistributionResponse(BaseModel):
    segment: str
    count: int
    percentage: float


class DashboardResponse(BaseModel):
    total_players: int
    active_players: int
    total_rewards_issued: int
    total_reward_cost: float
    segment_distribution: List[SegmentDistributionResponse]


class ROIResponse(BaseModel):
    rule_id: str
    rule_name: str
    rewards_issued: int
    total_cost: float
    expected_revenue: float
    expected_profit: float
    roi_percent: float


class ProfitReportResponse(BaseModel):
    period_start: datetime
    period_end: datetime
    total_reward_cost: float
    total_revenue: float
    net_profit: float
    roi_percent: float
    by_segment: Dict[str, Dict[str, float]]


# Batch Operations
class BatchProcessRequest(BaseModel):
    player_ids: List[str]
    trigger_rewards: bool = True


class BatchProcessResponse(BaseModel):
    processed: int
    rewards_issued: int


# Wallet Operations
class AddLoyaltyPointsRequest(BaseModel):
    player_id: str
    amount: float
    source: str = "MANUAL"
    description: Optional[str] = None


class AddBonusRequest(BaseModel):
    player_id: str
    amount: float
    wagering_requirement: float = 0.0
    expiry_hours: Optional[int] = None
    max_bet: Optional[float] = None
    eligible_games: Optional[List[str]] = None
    description: Optional[str] = None


class WalletOperationResponse(BaseModel):
    success: bool
    transaction_id: int
    new_balance: float
    message: str
