#!/usr/bin/env python3
"""
Bulk create sample reward rules from JSON file
"""
import json
import requests
import sys

API_BASE = "http://localhost:8001/api"

def create_rules_from_file(filename):
    """Create all rules from JSON file"""
    with open(filename, 'r') as f:
        rules = json.load(f)
    
    print(f"Creating {len(rules)} sample rules...")
    created = 0
    errors = []
    
    for rule in rules:
        try:
            response = requests.post(
                f"{API_BASE}/rules",
                json=rule,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print(f"✓ Created: {rule['rule_id']} - {rule['name']}")
                created += 1
            else:
                error_msg = f"✗ Failed: {rule['rule_id']} - {response.status_code} - {response.text}"
                print(error_msg)
                errors.append(error_msg)
        
        except Exception as e:
            error_msg = f"✗ Error creating {rule['rule_id']}: {str(e)}"
            print(error_msg)
            errors.append(error_msg)
    
    print(f"\n{'='*60}")
    print(f"Summary: {created}/{len(rules)} rules created successfully")
    if errors:
        print(f"Errors: {len(errors)}")
        for error in errors:
            print(f"  - {error}")
    print(f"{'='*60}")
    
    return created, errors

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "sample_rules.json"
    create_rules_from_file(filename)
