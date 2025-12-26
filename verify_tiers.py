#!/usr/bin/env python3
"""
Comprehensive verification of Tier System and Reward Rules
"""
import requests
import json
import time

API_BASE = "http://localhost:8001/api"

def get_player(player_id):
    return requests.get(f"{API_BASE}/players/{player_id}").json()

def test_tier_aware_rewards():
    print("\n--- Testing Tier-Aware Rewards ---")
    
    # 0. Deactivate rule first to ensure fresh evaluation on activation
    print("Deactivating TIER_AWARE_CASHBACK (reset)...")
    requests.put(f"{API_BASE}/rules/TIER_AWARE_CASHBACK", json={"is_active": False})
    
    # 1. Prepare players
    # P002 is LOSING - SILVER (1100 LP)
    # P009 is LOSING - SILVER (1600 LP). Let's make them DIAMOND (10000+ LP).
    
    print("Preparing players P002 (SILVER) and P009 (DIAMOND candidate)...")
    requests.post(f"{API_BASE}/wallet/add-lp", json={"player_id": "P009", "amount": 10000, "source": "TEST"})
    
    # 2. Activate the rule
    print("Activating TIER_AWARE_CASHBACK...")
    requests.put(f"{API_BASE}/rules/TIER_AWARE_CASHBACK", json={"is_active": True})
    
    # Wait for processing
    print("Waiting for rewards to be processed...")
    time.sleep(3)
    
    # 3. Check recent rewards
    rewards = requests.get(f"{API_BASE}/analytics/rewards").json()
    
    players_to_check = ["P002", "P009"]
    for pid in players_to_check:
        p = requests.get(f"{API_BASE}/players/{pid}").json()
        tier = p.get('tier', 'N/A')
        net_loss = p.get('metrics', {}).get('net_loss', 0)
        print(f"Player {pid} ({tier}): {p['balances']['lp_balance']} LP, Net Loss: {net_loss}")
        
        p_rewards = [r for r in rewards if r.get('player_id') == pid and r.get('rule_id') == 'TIER_AWARE_CASHBACK']
        
        if p_rewards:
            latest = p_rewards[0]
            # Formula: net_loss * 0.10 * multiplier
            print(f"  ✓ Reward Issued: {latest.get('amount')} {latest.get('currency_type')} (Rule: {latest.get('rule_id')})")
        else:
            print(f"  ✗ No TIER_AWARE_CASHBACK reward issued for {pid}")

def test_auto_promotion():
    print("\n--- Testing Auto-Promotion ---")
    
    # Find a player who is currently BRONZE
    pid = "P002" 
    p_before = requests.get(f"{API_BASE}/players/{pid}").json()
    print(f"Player {pid} before: {p_before['tier']} ({p_before['balances']['lp_balance']} LP)")
    
    print(f"Adding 500 LP to {pid}...")
    requests.post(f"{API_BASE}/wallet/add-lp", json={
        "player_id": pid,
        "amount": 500,
        "source": "TEST",
        "description": "Verification test"
    })
    
    time.sleep(1)
    p_after = requests.get(f"{API_BASE}/players/{pid}").json()
    print(f"Player {pid} after: {p_after['tier']} ({p_after['balances']['lp_balance']} LP)")
    
    if p_after['tier'] == 'SILVER':
        print(f"  ✓ Successfully promoted {pid} to SILVER!")
    else:
        print(f"  ✗ Promotion failed. Player stayed in {p_after['tier']}")

if __name__ == "__main__":
    try:
        test_tier_aware_rewards()
        test_auto_promotion()
    except Exception as e:
        print(f"Error during verification: {e}")
