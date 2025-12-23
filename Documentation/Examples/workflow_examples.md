# Loyalty Program - Sample Workflows

This document provides detailed walk-throughs of common scenarios in the Loyalty Program.

## 1. New Player Journey

**Scenario**: A new player signs up, makes their first deposit, and plays their first session.

### Step 1: Data Import
The player data enters the system via Excel import or API.

- **Action**: Import New Player
- **Input Data**:
  ```json
  {
    "player_id": "NEW_001",
    "total_deposited": 500,
    "total_wagered": 300,
    "sessions": 1
  }
  ```

### Step 2: Metrics & Segmentation
The system automatically calculates metrics and assigns a segment.

- **Calculated Metrics**:
  - `net_pnl`: -200 (Player lost 200)
  - `avg_bet_size`: 10
- **Assigned Segment**: `NEW` (based on low wager volume)
- **Assigned Tier**: `BRONZE` (0 LP)

### Step 3: Reward Evaluation
The system checks if any rules apply to the `NEW` segment.

- **Rule Triggered**: `WELCOME_BONUS`
  - *Condition*: `segment == 'NEW'` AND `total_deposited >= 500`
  - *Reward*: 50 Bonus Balance

### Step 4: Wallet Update
The reward is issued to the player's wallet.

- **Transaction**: Credit 50 Bonus
- **Wallet State**:
  - `lp_balance`: 0
  - `bonus_balance`: 50 (Locked)
  - `wagering_required`: 500 (10x wager)

---

## 2. High Roller Cashback

**Scenario**: A VIP player typically wagers high amounts but had a losing week.

### Step 1: Weekly Batch Process
The system runs a weekly job to evaluate performance.

- **Player ID**: `VIP_999`
- **Weekly Stats**:
  - `wagered`: $50,000
  - `won`: $40,000
  - `net_loss`: $10,000

### Step 2: Safety Check
Before issuing a reward, the system checks profitability.

- **Reward Rule**: `VIP_WEEKLY_CASHBACK` (10% of losses)
- **Proposed Reward**: $1,000
- **Profit Safety Check**:
  - `expected_future_value`: High (Retaining VIP is valuable)
  - `reward_cost`: $1,000
  - `Result`: **APPROVED** ✅

### Step 3: Reward Issuance
- **Action**: Credit $1,000 Real Money (or 1x Wager Bonus)
- **Notification**: Email sent to player "Sorry for the bad luck! Here is $1,000 back."

---

## 3. Bonus Abuse Detection

**Scenario**: A player tries to abuse the sign-up bonus by betting minimum amounts to wash the bonus.

### Step 1: Warning Signs
Player `ABUSER_007` received a $100 bonus with 10x wagering ($1,000).

- **Activity**:
  - Uses strictly minimum bets ($0.10) on safe bets (Red/Black roulette).
  - Withdraws immediately after unlocking funds.

### Step 2: Fraud Detection Trigger
The `FraudDetector` analyzes patterns.

- **Signals Detected**:
  - `BET_KIND`: Low volatility/safe bets only.
  - `WITHDRAWAL`: Immediate attempt.
- **Abuse Score**: 85/100 (High Risk)

### Step 3: Auto-Action
The system automatically reacts based on the score.

- **Action**: **BLOCK_WITHDRAWAL** and **FLAG_FOR_REVIEW**.
- **Admin Alert**: "Suspicious activity detected for ABUSER_007."

---

## 4. Tier Progression

**Scenario**: A regular player crosses the threshold for Silver Tier.

### Step 1: Activity Accumulation
Player `REGULAR_JOE` plays slots over the weekend.

- **Wagers**: $5,000 total
- **LP Earned**: 1 LP per $10 wager = 500 LP.
- **New Total LP**: 1,200 (Threshold for Silver is 1,000).

### Step 2: Tier Upgrade
The system updates the tier in real-time or end-of-day.

- **Old Tier**: `BRONZE`
- **New Tier**: `SILVER`

### Step 3: Benefits Activation
- **New Multiplier**: Cashback now 1.2x.
- **One-time Reward**: 100 Free Spin Tickets issued.

---

## 5. Reward Creation (Admin)

**Scenario**: Admin wants to create a "Friday Happy Hour" promotion.

### Step 1: Define Rule
Admin sends a POST request to `/api/rules`.

```json
{
  "rule_id": "FRIDAY_HAPPY_HOUR",
  "conditions": {
    "day_of_week": "FRIDAY",
    "deposit_min": 50
  },
  "reward_config": {
    "type": "BONUS_BALANCE",
    "formula": "deposit_amount * 0.50",
    "max_amount": 100
  }
}
```

### Step 2: Simulation
Admin tests the rule against a sample player.

- **Input**: Player P001 (Deposited 100 on Friday)
- **Result**: Reward would be 50.
- **Status**: Rule Activated.
