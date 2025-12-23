"""
Configuration management for the Loyalty & Reward Program
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    database_url: str = "sqlite:///./loyalty.db"
    
    # Application
    app_name: str = "Gaming Loyalty & Reward Program"
    app_version: str = "1.0.0"
    debug: bool = True
    secret_key: str = "change-this-in-production"
    
    # Reward System
    default_house_edge: float = 0.05
    max_daily_reward_per_player: float = 1000.0
    max_weekly_reward_per_player: float = 5000.0
    max_monthly_reward_per_player: float = 20000.0
    
    # Tier Thresholds
    tier_silver_lp: int = 1000
    tier_gold_lp: int = 10000
    tier_platinum_lp: int = 50000
    
    # Segmentation Thresholds
    new_player_wager_threshold: float = 1000.0
    vip_wager_threshold: float = 100000.0
    vip_session_threshold: int = 100
    breakeven_tolerance: float = 0.05
    
    # Fraud Detection
    abuse_score_threshold: int = 70
    max_bonus_abuse_signals: int = 3
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/loyalty_program.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
