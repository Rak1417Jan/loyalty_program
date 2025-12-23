"""
Excel/CSV Data Importer
Import player data from Excel/CSV files and trigger reward evaluation
"""
from sqlalchemy.orm import Session
from models import Player, PlayerMetrics, LoyaltyBalance, Transaction, TransactionType
from analytics.player_analytics import PlayerAnalytics
from analytics.segmentation import PlayerSegmentation
from engine.rules_engine import RulesEngine
from wallet.wallet_manager import WalletManager
import pandas as pd
from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ExcelImporter:
    """Import and process player data from Excel/CSV"""
    
    def __init__(self, db: Session):
        self.db = db
        self.analytics = PlayerAnalytics(db)
        self.segmentation = PlayerSegmentation(db)
        self.rules_engine = RulesEngine(db)
        self.wallet = WalletManager(db)
    
    def validate_excel_format(self, df: pd.DataFrame) -> List[str]:
        """
        Validate Excel file format
        
        Required columns:
        - player_id
        - total_deposited
        - total_wagered
        - total_won
        
        Optional columns:
        - sessions
        - playtime_hours
        - last_deposit_date
        - email
        - name
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required columns
        required_columns = [
            "player_id",
            "total_deposited",
            "total_wagered",
            "total_won"
        ]
        
        for col in required_columns:
            if col not in df.columns:
                errors.append(f"Missing required column: {col}")
        
        # Check data types
        if "player_id" in df.columns:
            if df["player_id"].isnull().any():
                errors.append("player_id cannot be null")
        
        numeric_columns = ["total_deposited", "total_wagered", "total_won"]
        for col in numeric_columns:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    errors.append(f"{col} must be numeric")
        
        return errors
    
    def import_player_data(self, file_path: str) -> Dict[str, any]:
        """
        Import player data from Excel/CSV file
        
        Args:
            file_path: Path to Excel or CSV file
        
        Returns:
            Dict with import summary
        """
        logger.info(f"Starting import from {file_path}")
        
        # Read file
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        logger.info(f"Loaded {len(df)} rows from file")
        
        # Validate format
        errors = self.validate_excel_format(df)
        if errors:
            logger.error(f"Validation errors: {errors}")
            return {
                "success": False,
                "errors": errors,
                "players_processed": 0
            }
        
        # Process each player
        players_created = 0
        players_updated = 0
        rewards_issued = 0
        errors_list = []
        
        for idx, row in df.iterrows():
            try:
                result = self.process_player_row(row)
                
                if result["created"]:
                    players_created += 1
                else:
                    players_updated += 1
                
                rewards_issued += result["rewards_issued"]
            
            except Exception as e:
                error_msg = f"Row {idx + 2}: {str(e)}"
                errors_list.append(error_msg)
                logger.error(error_msg)
        
        summary = {
            "success": True,
            "total_rows": len(df),
            "players_created": players_created,
            "players_updated": players_updated,
            "rewards_issued": rewards_issued,
            "errors": errors_list
        }
        
        logger.info(f"Import completed: {summary}")
        
        return summary
    
    def process_player_row(self, row: pd.Series) -> Dict[str, any]:
        """
        Process a single player row
        
        Args:
            row: Pandas Series with player data
        
        Returns:
            Dict with processing result
        """
        player_id = str(row["player_id"])
        
        # Get or create player
        player = self.db.query(Player).filter(Player.player_id == player_id).first()
        created = False
        
        if not player:
            player = Player(
                player_id=player_id,
                email=row.get("email"),
                name=row.get("name")
            )
            self.db.add(player)
            self.db.flush()
            created = True
            logger.info(f"Created new player: {player_id}")
        
        # Create or update transactions from totals
        # This is a simplified approach - in production, you'd import individual transactions
        self._create_summary_transactions(player_id, row)
        
        # Prepare session data
        session_data = {
            "sessions": int(row.get("sessions", 0)),
            "playtime_hours": float(row.get("playtime_hours", 0.0)),
            "games": {}  # Could parse from additional columns
        }
        
        # Update metrics
        self.analytics.update_player_metrics(player_id, session_data)
        
        # Update segmentation
        self.segmentation.update_player_segment(player_id)
        
        # Evaluate reward rules
        rewards = self.rules_engine.evaluate_and_create_rewards(player_id, limit=1)
        
        # Issue rewards
        for reward in rewards:
            try:
                self.wallet.issue_reward(reward.id)
            except Exception as e:
                logger.error(f"Error issuing reward {reward.id}: {e}")
        
        self.db.commit()
        
        return {
            "created": created,
            "rewards_issued": len(rewards)
        }
    
    def _create_summary_transactions(self, player_id: str, row: pd.Series):
        """
        Create summary transactions from Excel totals
        
        This is a simplified approach. In production, you'd import individual transactions.
        """
        total_deposited = float(row.get("total_deposited", 0))
        total_wagered = float(row.get("total_wagered", 0))
        total_won = float(row.get("total_won", 0))
        
        # Check if transactions already exist
        existing = self.db.query(Transaction).filter(
            Transaction.player_id == player_id
        ).first()
        
        if existing:
            # Player already has transactions, skip
            return
        
        # Create summary transactions
        if total_deposited > 0:
            deposit_tx = Transaction(
                player_id=player_id,
                transaction_type=TransactionType.DEPOSIT,
                currency_type=None,  # Real money, not loyalty currency
                amount=total_deposited,
                balance_before=0,
                balance_after=total_deposited,
                description="Initial deposit (from Excel import)"
            )
            self.db.add(deposit_tx)
        
        if total_wagered > 0:
            wager_tx = Transaction(
                player_id=player_id,
                transaction_type=TransactionType.WAGER,
                currency_type=None,
                amount=total_wagered,
                balance_before=0,
                balance_after=0,
                description="Total wagered (from Excel import)"
            )
            self.db.add(wager_tx)
        
        if total_won > 0:
            win_tx = Transaction(
                player_id=player_id,
                transaction_type=TransactionType.WIN,
                currency_type=None,
                amount=total_won,
                balance_before=0,
                balance_after=total_won,
                description="Total won (from Excel import)"
            )
            self.db.add(win_tx)
    
    def batch_process_players(
        self,
        player_ids: List[str],
        trigger_rewards: bool = True
    ) -> Dict[str, int]:
        """
        Batch process multiple players
        
        Args:
            player_ids: List of player IDs to process
            trigger_rewards: Whether to evaluate reward rules
        
        Returns:
            Dict with processing summary
        """
        logger.info(f"Batch processing {len(player_ids)} players")
        
        processed = 0
        rewards_issued = 0
        
        for player_id in player_ids:
            try:
                # Update metrics
                self.analytics.update_player_metrics(player_id)
                
                # Update segment
                self.segmentation.update_player_segment(player_id)
                
                # Evaluate rewards if requested
                if trigger_rewards:
                    rewards = self.rules_engine.evaluate_and_create_rewards(player_id)
                    
                    for reward in rewards:
                        self.wallet.issue_reward(reward.id)
                        rewards_issued += 1
                
                processed += 1
            
            except Exception as e:
                logger.error(f"Error processing player {player_id}: {e}")
        
        self.db.commit()
        
        summary = {
            "processed": processed,
            "rewards_issued": rewards_issued
        }
        
        logger.info(f"Batch processing completed: {summary}")
        
        return summary
    
    def trigger_reward_evaluation(self, player_ids: List[str]) -> Dict[str, int]:
        """
        Trigger reward rule evaluation for players
        
        Args:
            player_ids: List of player IDs
        
        Returns:
            Dict with evaluation summary
        """
        logger.info(f"Triggering reward evaluation for {len(player_ids)} players")
        
        rewards_created = 0
        rewards_issued = 0
        
        for player_id in player_ids:
            try:
                rewards = self.rules_engine.evaluate_and_create_rewards(player_id)
                rewards_created += len(rewards)
                
                for reward in rewards:
                    self.wallet.issue_reward(reward.id)
                    rewards_issued += 1
            
            except Exception as e:
                logger.error(f"Error evaluating rewards for player {player_id}: {e}")
        
        self.db.commit()
        
        summary = {
            "players_evaluated": len(player_ids),
            "rewards_created": rewards_created,
            "rewards_issued": rewards_issued
        }
        
        logger.info(f"Reward evaluation completed: {summary}")
        
        return summary
