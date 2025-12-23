"""Test player analytics"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models import Player, PlayerMetrics, Transaction, TransactionType
from analytics.player_analytics import PlayerAnalytics


@pytest.fixture
def db_session():
    """Create test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_player(db_session):
    """Create a sample player with transactions"""
    player = Player(player_id="TEST001", email="test@example.com")
    db_session.add(player)
    
    metrics = PlayerMetrics(player_id="TEST001")
    db_session.add(metrics)
    
    # Add transactions
    transactions = [
        Transaction(
            player_id="TEST001",
            transaction_type=TransactionType.DEPOSIT,
            currency_type=None,
            amount=1000,
            balance_before=0,
            balance_after=1000
        ),
        Transaction(
            player_id="TEST001",
            transaction_type=TransactionType.WAGER,
            currency_type=None,
            amount=3000,
            balance_before=0,
            balance_after=0
        ),
        Transaction(
            player_id="TEST001",
            transaction_type=TransactionType.WIN,
            currency_type=None,
            amount=2500,
            balance_before=0,
            balance_after=2500
        )
    ]
    
    for tx in transactions:
        db_session.add(tx)
    
    db_session.commit()
    return player


def test_calculate_financial_metrics(db_session, sample_player):
    """Test financial metrics calculation"""
    analytics = PlayerAnalytics(db_session)
    metrics = analytics.calculate_financial_metrics("TEST001")
    
    assert metrics["total_deposited"] == 1000
    assert metrics["total_wagered"] == 3000
    assert metrics["total_won"] == 2500
    assert metrics["net_pnl"] == 1500  # 2500 - 1000
    assert metrics["house_edge_contribution"] == 500  # 3000 - 2500


def test_update_player_metrics(db_session, sample_player):
    """Test updating player metrics"""
    analytics = PlayerAnalytics(db_session)
    
    session_data = {
        "sessions": 10,
        "playtime_hours": 25.5,
        "games": {"slots": 50, "poker": 20}
    }
    
    metrics = analytics.update_player_metrics("TEST001", session_data)
    
    assert metrics.total_deposited == 1000
    assert metrics.total_wagered == 3000
    assert metrics.total_sessions == 10
    assert metrics.total_playtime_hours == 25.5


def test_get_player_state(db_session, sample_player):
    """Test getting complete player state"""
    analytics = PlayerAnalytics(db_session)
    analytics.update_player_metrics("TEST001")
    
    state = analytics.get_player_state("TEST001")
    
    assert state["player_id"] == "TEST001"
    assert state["total_deposited"] == 1000
    assert state["total_wagered"] == 3000
    assert state["net_pnl"] == 1500
    assert "segment" in state
    assert "tier" in state
