"""
Admin API Endpoints
FastAPI routes for CRUD operations and analytics
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import (
    Player, PlayerMetrics, LoyaltyBalance, RewardRule, Tier,
    RewardHistory, Transaction, PlayerSegment, TierLevel
)
from api.schemas import *
from analytics.player_analytics import PlayerAnalytics
from analytics.segmentation import PlayerSegmentation
from engine.rules_engine import RulesEngine
from wallet.wallet_manager import WalletManager
from safety.profit_safety import ProfitSafety
from safety.fraud_detector import FraudDetector
from data.excel_importer import ExcelImporter
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import os
import shutil

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== Player Management ====================

@router.get("/players", response_model=List[PlayerResponse])
def list_players(
    segment: Optional[PlayerSegment] = None,
    tier: Optional[TierLevel] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List players with optional filters"""
    query = db.query(Player)
    
    if segment:
        query = query.filter(Player.segment == segment)
    if tier:
        query = query.filter(Player.tier == tier)
    if is_active is not None:
        query = query.filter(Player.is_active == is_active)
    
    players = query.offset(skip).limit(limit).all()
    return players


@router.get("/players/{player_id}", response_model=PlayerResponse)
def get_player(player_id: str, db: Session = Depends(get_db)):
    """Get player details"""
    player = db.query(Player).filter(Player.player_id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.post("/players", response_model=PlayerResponse)
def create_player(player: PlayerCreate, db: Session = Depends(get_db)):
    """Create a new player"""
    # Check if player exists
    existing = db.query(Player).filter(Player.player_id == player.player_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Player already exists")
    
    new_player = Player(**player.dict())
    db.add(new_player)
    
    # Create empty metrics and balance
    metrics = PlayerMetrics(player_id=player.player_id)
    balance = LoyaltyBalance(player_id=player.player_id)
    db.add(metrics)
    db.add(balance)
    
    db.commit()
    db.refresh(new_player)
    
    return new_player


@router.put("/players/{player_id}", response_model=PlayerResponse)
def update_player(
    player_id: str,
    player_update: PlayerUpdate,
    db: Session = Depends(get_db)
):
    """Update player details"""
    player = db.query(Player).filter(Player.player_id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Update fields
    for field, value in player_update.dict(exclude_unset=True).items():
        setattr(player, field, value)
    
    db.commit()
    db.refresh(player)
    
    return player


@router.delete("/players/{player_id}")
def delete_player(player_id: str, db: Session = Depends(get_db)):
    """Soft delete a player"""
    player = db.query(Player).filter(Player.player_id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    player.is_active = False
    db.commit()
    
    return {"message": f"Player {player_id} deactivated"}


# ==================== Reward Rules Management ====================

@router.get("/rules", response_model=List[RewardRuleResponse])
def list_rules(
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List all reward rules"""
    query = db.query(RewardRule)
    
    if is_active is not None:
        query = query.filter(RewardRule.is_active == is_active)
    
    rules = query.order_by(RewardRule.priority.desc()).all()
    return rules


@router.get("/rules/{rule_id}", response_model=RewardRuleResponse)
def get_rule(rule_id: str, db: Session = Depends(get_db)):
    """Get a specific rule"""
    rule = db.query(RewardRule).filter(RewardRule.rule_id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.post("/rules", response_model=RewardRuleResponse)
def create_rule(rule: RewardRuleCreate, db: Session = Depends(get_db)):
    """Create a new reward rule"""
    # Check if rule exists
    existing = db.query(RewardRule).filter(RewardRule.rule_id == rule.rule_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Rule already exists")
    
    new_rule = RewardRule(**rule.dict())
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)
    
    logger.info(f"Created reward rule: {rule.rule_id}")
    
    return new_rule


@router.put("/rules/{rule_id}", response_model=RewardRuleResponse)
def update_rule(
    rule_id: str,
    rule_update: RewardRuleUpdate,
    db: Session = Depends(get_db)
):
    """Update a reward rule"""
    rule = db.query(RewardRule).filter(RewardRule.rule_id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    for field, value in rule_update.dict(exclude_unset=True).items():
        setattr(rule, field, value)
    
    db.commit()
    db.refresh(rule)
    
    logger.info(f"Updated reward rule: {rule_id}")
    
    return rule


@router.delete("/rules/{rule_id}")
def delete_rule(rule_id: str, db: Session = Depends(get_db)):
    """Delete a reward rule"""
    rule = db.query(RewardRule).filter(RewardRule.rule_id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db.delete(rule)
    db.commit()
    
    logger.info(f"Deleted reward rule: {rule_id}")
    
    return {"message": f"Rule {rule_id} deleted"}


@router.post("/rules/{rule_id}/test", response_model=RuleTestResponse)
def test_rule(
    rule_id: str,
    request: RuleTestRequest,
    db: Session = Depends(get_db)
):
    """Test a rule against a player"""
    rule = db.query(RewardRule).filter(RewardRule.rule_id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Get player state
    analytics = PlayerAnalytics(db)
    player_state = analytics.get_player_state(request.player_id)
    
    # Evaluate rule
    rules_engine = RulesEngine(db)
    matches = rules_engine.evaluate_rule(rule, player_state)
    
    reward_amount = None
    if matches:
        reward_amount = rules_engine.calculate_reward_amount(rule, player_state)
        reward_amount = rules_engine.apply_caps(reward_amount, rule.reward_config)
    
    return {
        "matches": matches,
        "reward_amount": reward_amount,
        "player_state": player_state
    }


# ==================== Tier Management ====================

@router.get("/tiers", response_model=List[TierResponse])
def list_tiers(db: Session = Depends(get_db)):
    """List all tiers"""
    tiers = db.query(Tier).all()
    return tiers


@router.post("/tiers", response_model=TierResponse)
def create_tier(tier: TierCreate, db: Session = Depends(get_db)):
    """Create a new tier"""
    new_tier = Tier(**tier.dict())
    db.add(new_tier)
    db.commit()
    db.refresh(new_tier)
    return new_tier


@router.put("/tiers/{tier_id}", response_model=TierResponse)
def update_tier(
    tier_id: int,
    tier_update: TierUpdate,
    db: Session = Depends(get_db)
):
    """Update a tier"""
    tier = db.query(Tier).filter(Tier.id == tier_id).first()
    if not tier:
        raise HTTPException(status_code=404, detail="Tier not found")
    
    for field, value in tier_update.dict(exclude_unset=True).items():
        setattr(tier, field, value)
    
    db.commit()
    db.refresh(tier)
    
    return tier


# ==================== Data Import ====================

@router.post("/import/excel", response_model=ImportResponse)
async def import_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import player data from Excel/CSV file"""
    # Save uploaded file
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Import data
    importer = ExcelImporter(db)
    result = importer.import_player_data(file_path)
    
    # Clean up
    os.remove(file_path)
    
    return result


@router.post("/batch/process", response_model=BatchProcessResponse)
def batch_process(request: BatchProcessRequest, db: Session = Depends(get_db)):
    """Batch process players"""
    importer = ExcelImporter(db)
    result = importer.batch_process_players(
        request.player_ids,
        request.trigger_rewards
    )
    return result


# ==================== Analytics ====================

@router.get("/analytics/dashboard", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db)):
    """Get dashboard metrics"""
    total_players = db.query(func.count(Player.player_id)).scalar()
    active_players = db.query(func.count(Player.player_id)).filter(
        Player.is_active == True
    ).scalar()
    
    total_rewards = db.query(func.count(RewardHistory.id)).scalar()
    total_cost = db.query(func.sum(RewardHistory.amount)).scalar() or 0.0
    
    # Segment distribution
    distribution = db.query(
        Player.segment,
        func.count(Player.player_id)
    ).group_by(Player.segment).all()
    
    segment_dist = [
        {
            "segment": seg.value,
            "count": count,
            "percentage": (count / total_players * 100) if total_players > 0 else 0
        }
        for seg, count in distribution
    ]
    
    return {
        "total_players": total_players,
        "active_players": active_players,
        "total_rewards_issued": total_rewards,
        "total_reward_cost": total_cost,
        "segment_distribution": segment_dist
    }


@router.get("/analytics/rewards", response_model=List[RewardHistoryResponse])
def get_rewards(
    player_id: Optional[str] = None,
    status: Optional[RewardStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get reward history"""
    query = db.query(RewardHistory)
    
    if player_id:
        query = query.filter(RewardHistory.player_id == player_id)
    if status:
        query = query.filter(RewardHistory.status == status)
    
    rewards = query.order_by(RewardHistory.issued_at.desc()).offset(skip).limit(limit).all()
    return rewards


@router.get("/analytics/transactions", response_model=List[TransactionResponse])
def get_transactions(
    player_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get transaction history for a player"""
    transactions = db.query(Transaction).filter(
        Transaction.player_id == player_id
    ).order_by(Transaction.created_at.desc()).offset(skip).limit(limit).all()
    
    return transactions


# ==================== Wallet Operations ====================

@router.post("/wallet/add-lp", response_model=WalletOperationResponse)
def add_loyalty_points(request: AddLoyaltyPointsRequest, db: Session = Depends(get_db)):
    """Manually add loyalty points"""
    wallet = WalletManager(db)
    
    try:
        transaction = wallet.add_loyalty_points(
            player_id=request.player_id,
            amount=request.amount,
            source=request.source,
            description=request.description
        )
        
        balance = wallet.get_or_create_balance(request.player_id)
        
        return {
            "success": True,
            "transaction_id": transaction.id,
            "new_balance": balance.lp_balance,
            "message": f"Added {request.amount} LP"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/wallet/add-bonus", response_model=WalletOperationResponse)
def add_bonus(request: AddBonusRequest, db: Session = Depends(get_db)):
    """Manually add bonus balance"""
    wallet = WalletManager(db)
    
    try:
        expiry = None
        if request.expiry_hours:
            expiry = datetime.utcnow() + timedelta(hours=request.expiry_hours)
        
        transaction = wallet.add_bonus_balance(
            player_id=request.player_id,
            amount=request.amount,
            wagering_requirement=request.wagering_requirement,
            expiry=expiry,
            max_bet=request.max_bet,
            eligible_games=request.eligible_games,
            description=request.description
        )
        
        balance = wallet.get_or_create_balance(request.player_id)
        
        return {
            "success": True,
            "transaction_id": transaction.id,
            "new_balance": balance.bonus_balance,
            "message": f"Added {request.amount} bonus balance"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
