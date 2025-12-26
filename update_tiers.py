#!/usr/bin/env python3
"""
Update or create tier system from JSON file
"""
import json
import requests
import sys

API_BASE = "http://localhost:8001/api"

def update_tiers_from_file(filename):
    """Update/create all tiers from JSON file"""
    with open(filename, 'r') as f:
        new_tiers = json.load(f)
    
    # Get existing tiers
    response = requests.get(f"{API_BASE}/tiers")
    existing_tiers = response.json() if response.status_code == 200 else []
    
    # Create a map of tier_level to tier_id
    tier_map = {tier['tier_level']: tier['id'] for tier in existing_tiers}
    
    print(f"Processing {len(new_tiers)} tiers...")
    print(f"Existing tiers: {list(tier_map.keys())}")
    
    updated = 0
    created = 0
    errors = []
    
    for tier in new_tiers:
        tier_level = tier['tier_level']
        
        try:
            if tier_level in tier_map:
                # Update existing tier
                tier_id = tier_map[tier_level]
                response = requests.put(
                    f"{API_BASE}/tiers/{tier_id}",
                    json=tier,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    print(f"✓ Updated: {tier_level} ({tier['lp_min']}-{tier['lp_max'] or '∞'} LP)")
                    updated += 1
                else:
                    error_msg = f"✗ Failed to update {tier_level}: {response.status_code} - {response.text}"
                    print(error_msg)
                    errors.append(error_msg)
            else:
                # Create new tier
                response = requests.post(
                    f"{API_BASE}/tiers",
                    json=tier,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    print(f"✓ Created: {tier_level} ({tier['lp_min']}-{tier['lp_max'] or '∞'} LP)")
                    created += 1
                else:
                    error_msg = f"✗ Failed to create {tier_level}: {response.status_code} - {response.text}"
                    print(error_msg)
                    errors.append(error_msg)
        
        except Exception as e:
            error_msg = f"✗ Error processing {tier_level}: {str(e)}"
            print(error_msg)
            errors.append(error_msg)
    
    print(f"\n{'='*60}")
    print(f"Summary: {updated} updated, {created} created, {len(errors)} errors")
    if errors:
        for error in errors:
            print(f"  - {error}")
    print(f"{'='*60}")
    
    return updated, created, errors

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "sample_tiers.json"
    update_tiers_from_file(filename)
