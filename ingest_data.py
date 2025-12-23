import csv
import requests
import time

API_URL = "http://localhost:8000/api"

def ingest_data():
    try:
        with open('sample_players.csv', 'r') as f:
            reader = csv.DictReader(f)
            players = list(reader)
            
        print(f"Found {len(players)} players to ingest...")
        
        for p in players:
            # 1. Create Player
            player_data = {
                "player_id": p['player_id'],
                "email": p['email'],
                # "name": p['name'], # API might not take name if not in schema, let's check. 
                # If schema fails, we'll know. Assuming basic fields first.
                "country": "US", # Defaulting
                "join_date": "2023-01-01" 
            }
            
            # Helper to safely create
            try:
                res = requests.post(f"{API_URL}/players", json=player_data)
                if res.status_code == 200 or res.status_code == 201:
                    print(f"Created player {p['player_id']}")
                elif res.status_code == 400 and "already exists" in res.text:
                    print(f"Player {p['player_id']} already exists")
                else:
                    print(f"Failed to create {p['player_id']}: {res.text}")
            except Exception as e:
                print(f"Error creating {p['player_id']}: {e}")

            # 2. Add Wallet Balance (Simulating Deposit/Winnings)
            # We'll add some LP based on 'total_deposited' just to show data
            try:
                amount = int(p.get('total_deposited', 0)) // 10 # 1 LP per $10
                if amount > 0:
                    res = requests.post(f"{API_URL}/wallet/add-lp", json={
                        "player_id": p['player_id'],
                        "amount": amount,
                        "source": "import",
                        "description": "Initial Import"
                    })
                    if res.status_code == 200:
                        print(f"  Added {amount} LP")
            except Exception as e:
                print(f"  Error adding LP: {e}")
                
            time.sleep(0.1) # Be nice to the server

        print("Ingestion complete!")

    except FileNotFoundError:
        print("sample_players.csv not found!")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    ingest_data()
