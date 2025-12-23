"""
Comprehensive API Test Script for Loyalty & Reward Program
Tests all endpoints and logs results to a file
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Configuration
BASE_URL = "http://localhost:8001"
API_BASE = f"{BASE_URL}/api"
LOG_FILE = "api_test_results.txt"

# Test data
TEST_PLAYER_ID = f"TEST_PLAYER_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
TEST_RULE_ID = f"TEST_RULE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


class APITester:
    """API Testing Framework"""
    
    def __init__(self, base_url: str, log_file: str):
        self.base_url = base_url
        self.log_file = log_file
        self.test_results = []
        self.passed = 0
        self.failed = 0
        self.test_data = {}  # Store created resources for cleanup
        
    def log(self, message: str, level: str = "INFO"):
        """Log message to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    
    def log_separator(self, title: str = ""):
        """Log a separator line"""
        separator = "=" * 80
        if title:
            self.log(f"\n{separator}")
            self.log(f"  {title}")
            self.log(separator)
        else:
            self.log(separator)
    
    def test_api(
        self, 
        test_id: str,
        description: str,
        method: str,
        endpoint: str,
        data: Dict = None,
        params: Dict = None,
        expected_status: int = 200,
        files: Dict = None
    ) -> Tuple[bool, Any]:
        """
        Execute API test and log results
        
        Returns:
            Tuple of (success: bool, response_data: Any)
        """
        url = f"{self.base_url}{endpoint}"
        
        self.log(f"\n[{test_id}] {description}")
        self.log(f"  Method: {method}")
        self.log(f"  URL: {url}")
        
        if params:
            self.log(f"  Params: {json.dumps(params, indent=2)}")
        if data:
            self.log(f"  Request Body: {json.dumps(data, indent=2)}")
        
        try:
            # Make API request
            if method == "GET":
                response = requests.get(url, params=params)
            elif method == "POST":
                if files:
                    response = requests.post(url, files=files)
                else:
                    response = requests.post(url, json=data, params=params)
            elif method == "PUT":
                response = requests.put(url, json=data, params=params)
            elif method == "DELETE":
                response = requests.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # Log response
            self.log(f"  Status Code: {response.status_code}")
            
            # Try to parse JSON response
            try:
                response_data = response.json()
                self.log(f"  Response: {json.dumps(response_data, indent=2)}")
            except:
                response_data = response.text
                self.log(f"  Response: {response_data}")
            
            # Check if test passed
            success = response.status_code == expected_status
            
            if success:
                self.log(f"  ✅ PASSED", "SUCCESS")
                self.passed += 1
            else:
                self.log(f"  ❌ FAILED - Expected {expected_status}, got {response.status_code}", "ERROR")
                self.failed += 1
            
            self.test_results.append({
                "test_id": test_id,
                "description": description,
                "passed": success,
                "status_code": response.status_code,
                "expected_status": expected_status
            })
            
            return success, response_data
            
        except Exception as e:
            self.log(f"  ❌ EXCEPTION: {str(e)}", "ERROR")
            self.failed += 1
            self.test_results.append({
                "test_id": test_id,
                "description": description,
                "passed": False,
                "error": str(e)
            })
            return False, None
    
    def run_all_tests(self):
        """Execute all API tests"""
        self.log_separator("LOYALTY & REWARD PROGRAM - API TEST SUITE")
        self.log(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"Base URL: {self.base_url}")
        
        # Clear log file
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write("")
        
        # Run test suites
        self.test_system_health()
        self.test_player_management()
        self.test_reward_rules()
        self.test_tier_management()
        self.test_wallet_operations()
        self.test_analytics()
        self.test_edge_cases()
        
        # Print summary
        self.print_summary()
    
    def test_system_health(self):
        """Test system health endpoints"""
        self.log_separator("1. SYSTEM HEALTH TESTS")
        
        # Test 1: Root endpoint
        self.test_api(
            "SH-001",
            "Get API root information",
            "GET",
            "/",
            expected_status=200
        )
        
        # Test 2: Health check
        self.test_api(
            "SH-002",
            "Health check endpoint",
            "GET",
            "/health",
            expected_status=200
        )
    
    def test_player_management(self):
        """Test player management endpoints"""
        self.log_separator("2. PLAYER MANAGEMENT TESTS")
        
        # Test 1: Create player
        success, response = self.test_api(
            "PM-001",
            "Create new player",
            "POST",
            "/api/players",
            data={
                "player_id": TEST_PLAYER_ID,
                "email": f"{TEST_PLAYER_ID}@example.com",
                "name": "Test Player"
            },
            expected_status=201
        )
        
        if success:
            self.test_data['player_id'] = TEST_PLAYER_ID
        
        # Test 2: Get player details
        self.test_api(
            "PM-002",
            "Get player details",
            "GET",
            f"/api/players/{TEST_PLAYER_ID}",
            expected_status=200
        )
        
        # Test 3: List all players
        self.test_api(
            "PM-003",
            "List all players",
            "GET",
            "/api/players",
            expected_status=200
        )
        
        # Test 4: List players with filters
        self.test_api(
            "PM-004",
            "List players filtered by segment",
            "GET",
            "/api/players",
            params={"segment": "NEW"},
            expected_status=200
        )
        
        # Test 5: List players with pagination
        self.test_api(
            "PM-005",
            "List players with pagination",
            "GET",
            "/api/players",
            params={"skip": 0, "limit": 10},
            expected_status=200
        )
        
        # Test 6: Update player
        self.test_api(
            "PM-006",
            "Update player information",
            "PUT",
            f"/api/players/{TEST_PLAYER_ID}",
            data={
                "email": f"updated_{TEST_PLAYER_ID}@example.com",
                "name": "Updated Test Player"
            },
            expected_status=200
        )
        
        # Test 7: Get non-existent player (should fail)
        self.test_api(
            "PM-007",
            "Get non-existent player (negative test)",
            "GET",
            "/api/players/NONEXISTENT_PLAYER",
            expected_status=404
        )
        
        # Test 8: Create duplicate player (should fail)
        self.test_api(
            "PM-008",
            "Create duplicate player (negative test)",
            "POST",
            "/api/players",
            data={
                "player_id": TEST_PLAYER_ID,
                "email": "duplicate@example.com"
            },
            expected_status=400
        )
    
    def test_reward_rules(self):
        """Test reward rules endpoints"""
        self.log_separator("3. REWARD RULES TESTS")
        
        # Test 1: Create reward rule
        success, response = self.test_api(
            "RR-001",
            "Create new reward rule",
            "POST",
            "/api/rules",
            data={
                "rule_id": TEST_RULE_ID,
                "name": "Test Cashback Rule",
                "description": "Test rule for API testing",
                "priority": 100,
                "is_active": True,
                "conditions": {
                    "segment": "LOSING",
                    "net_loss_min": 100
                },
                "reward_config": {
                    "type": "BONUS_BALANCE",
                    "formula": "net_loss * 0.10",
                    "max_amount": 500,
                    "wagering_requirement": 10
                }
            },
            expected_status=201
        )
        
        if success:
            self.test_data['rule_id'] = TEST_RULE_ID
        
        # Test 2: Get rule details
        self.test_api(
            "RR-002",
            "Get rule details",
            "GET",
            f"/api/rules/{TEST_RULE_ID}",
            expected_status=200
        )
        
        # Test 3: List all rules
        self.test_api(
            "RR-003",
            "List all reward rules",
            "GET",
            "/api/rules",
            expected_status=200
        )
        
        # Test 4: List active rules only
        self.test_api(
            "RR-004",
            "List active rules only",
            "GET",
            "/api/rules",
            params={"is_active": True},
            expected_status=200
        )
        
        # Test 5: Update rule
        self.test_api(
            "RR-005",
            "Update reward rule",
            "PUT",
            f"/api/rules/{TEST_RULE_ID}",
            data={
                "priority": 150,
                "is_active": False
            },
            expected_status=200
        )
        
        # Test 6: Test rule against player
        if 'player_id' in self.test_data:
            self.test_api(
                "RR-006",
                "Test rule against player",
                "POST",
                f"/api/rules/{TEST_RULE_ID}/test",
                data={"player_id": TEST_PLAYER_ID},
                expected_status=200
            )
        
        # Test 7: Get non-existent rule (should fail)
        self.test_api(
            "RR-007",
            "Get non-existent rule (negative test)",
            "GET",
            "/api/rules/NONEXISTENT_RULE",
            expected_status=404
        )
    
    def test_tier_management(self):
        """Test tier management endpoints"""
        self.log_separator("4. TIER MANAGEMENT TESTS")
        
        # Test 1: List all tiers
        self.test_api(
            "TM-001",
            "List all tiers",
            "GET",
            "/api/tiers",
            expected_status=200
        )
        
        # Test 2: Create new tier (may fail if already exists)
        self.test_api(
            "TM-002",
            "Create new tier (may fail if exists)",
            "POST",
            "/api/tiers",
            data={
                "tier_level": "GOLD",
                "lp_min": 10000,
                "lp_max": 49999,
                "benefits": {
                    "cashback_multiplier": 1.5,
                    "free_plays_per_month": 10
                }
            },
            expected_status=201
        )
    
    def test_wallet_operations(self):
        """Test wallet operations"""
        self.log_separator("5. WALLET OPERATIONS TESTS")
        
        if 'player_id' not in self.test_data:
            self.log("Skipping wallet tests - no test player created", "WARNING")
            return
        
        # Test 1: Add loyalty points
        self.test_api(
            "WO-001",
            "Add loyalty points to player",
            "POST",
            "/api/wallet/add-lp",
            data={
                "player_id": TEST_PLAYER_ID,
                "amount": 500.0,
                "source": "TEST",
                "description": "Test loyalty points"
            },
            expected_status=200
        )
        
        # Test 2: Add bonus balance
        self.test_api(
            "WO-002",
            "Add bonus balance to player",
            "POST",
            "/api/wallet/add-bonus",
            data={
                "player_id": TEST_PLAYER_ID,
                "amount": 100.0,
                "wagering_requirement": 1000.0,
                "expiry_hours": 168,
                "max_bet": 50.0,
                "eligible_games": ["slots", "roulette"],
                "description": "Test bonus"
            },
            expected_status=200
        )
        
        # Test 3: Add LP with zero amount
        self.test_api(
            "WO-003",
            "Add zero loyalty points (edge case)",
            "POST",
            "/api/wallet/add-lp",
            data={
                "player_id": TEST_PLAYER_ID,
                "amount": 0.0,
                "source": "TEST"
            },
            expected_status=200
        )
        
        # Test 4: Add LP to non-existent player
        self.test_api(
            "WO-004",
            "Add LP to non-existent player (negative test)",
            "POST",
            "/api/wallet/add-lp",
            data={
                "player_id": "NONEXISTENT_PLAYER",
                "amount": 100.0,
                "source": "TEST"
            },
            expected_status=400
        )
    
    def test_analytics(self):
        """Test analytics endpoints"""
        self.log_separator("6. ANALYTICS & REPORTING TESTS")
        
        # Test 1: Get dashboard metrics
        self.test_api(
            "AN-001",
            "Get dashboard metrics",
            "GET",
            "/api/analytics/dashboard",
            expected_status=200
        )
        
        # Test 2: Get all rewards
        self.test_api(
            "AN-002",
            "Get reward history (all)",
            "GET",
            "/api/analytics/rewards",
            expected_status=200
        )
        
        # Test 3: Get rewards for specific player
        if 'player_id' in self.test_data:
            self.test_api(
                "AN-003",
                "Get reward history for player",
                "GET",
                "/api/analytics/rewards",
                params={"player_id": TEST_PLAYER_ID},
                expected_status=200
            )
        
        # Test 4: Get rewards with status filter
        self.test_api(
            "AN-004",
            "Get active rewards only",
            "GET",
            "/api/analytics/rewards",
            params={"status": "ACTIVE"},
            expected_status=200
        )
        
        # Test 5: Get transactions for player
        if 'player_id' in self.test_data:
            self.test_api(
                "AN-005",
                "Get transaction history for player",
                "GET",
                "/api/analytics/transactions",
                params={"player_id": TEST_PLAYER_ID},
                expected_status=200
            )
        
        # Test 6: Get transactions with pagination
        if 'player_id' in self.test_data:
            self.test_api(
                "AN-006",
                "Get transactions with pagination",
                "GET",
                "/api/analytics/transactions",
                params={"player_id": TEST_PLAYER_ID, "skip": 0, "limit": 5},
                expected_status=200
            )
    
    def test_edge_cases(self):
        """Test edge cases and error scenarios"""
        self.log_separator("7. EDGE CASES & ERROR HANDLING TESTS")
        
        # Test 1: Invalid segment filter
        self.test_api(
            "EC-001",
            "Invalid segment filter (negative test)",
            "GET",
            "/api/players",
            params={"segment": "INVALID_SEGMENT"},
            expected_status=422
        )
        
        # Test 2: Invalid tier filter
        self.test_api(
            "EC-002",
            "Invalid tier filter (negative test)",
            "GET",
            "/api/players",
            params={"tier": "INVALID_TIER"},
            expected_status=422
        )
        
        # Test 3: Missing required field in player creation
        self.test_api(
            "EC-003",
            "Create player without player_id (negative test)",
            "POST",
            "/api/players",
            data={"email": "test@example.com"},
            expected_status=422
        )
        
        # Test 4: Very large pagination limit
        self.test_api(
            "EC-004",
            "Very large pagination limit",
            "GET",
            "/api/players",
            params={"limit": 10000},
            expected_status=200
        )
        
        # Test 5: Negative pagination skip
        self.test_api(
            "EC-005",
            "Negative pagination skip",
            "GET",
            "/api/players",
            params={"skip": -1},
            expected_status=422
        )
    
    def cleanup(self):
        """Clean up test data"""
        self.log_separator("CLEANUP")
        
        # Delete test rule
        if 'rule_id' in self.test_data:
            self.test_api(
                "CLEANUP-001",
                "Delete test rule",
                "DELETE",
                f"/api/rules/{self.test_data['rule_id']}",
                expected_status=200
            )
        
        # Deactivate test player (soft delete)
        if 'player_id' in self.test_data:
            self.test_api(
                "CLEANUP-002",
                "Deactivate test player",
                "DELETE",
                f"/api/players/{self.test_data['player_id']}",
                expected_status=200
            )
    
    def print_summary(self):
        """Print test summary"""
        self.log_separator("TEST SUMMARY")
        
        total_tests = self.passed + self.failed
        pass_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        self.log(f"\nTotal Tests: {total_tests}")
        self.log(f"Passed: {self.passed} ✅")
        self.log(f"Failed: {self.failed} ❌")
        self.log(f"Pass Rate: {pass_rate:.2f}%")
        
        if self.failed > 0:
            self.log("\nFailed Tests:", "WARNING")
            for result in self.test_results:
                if not result['passed']:
                    self.log(f"  - [{result['test_id']}] {result['description']}", "ERROR")
        
        self.log(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"Results saved to: {self.log_file}")
        self.log_separator()


def main():
    """Main test execution"""
    print("\n" + "="*80)
    print("  LOYALTY & REWARD PROGRAM - API TEST SUITE")
    print("="*80 + "\n")
    
    # Initialize tester
    tester = APITester(BASE_URL, LOG_FILE)
    
    # Run all tests
    try:
        tester.run_all_tests()
        
        # Cleanup
        tester.cleanup()
        
    except KeyboardInterrupt:
        tester.log("\n\nTest interrupted by user", "WARNING")
    except Exception as e:
        tester.log(f"\n\nUnexpected error: {str(e)}", "ERROR")
    
    print(f"\n✅ Test results saved to: {LOG_FILE}")
    print(f"📊 Total: {tester.passed + tester.failed} | Passed: {tester.passed} | Failed: {tester.failed}\n")


if __name__ == "__main__":
    main()
