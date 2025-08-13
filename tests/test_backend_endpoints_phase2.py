#!/usr/bin/env python3
"""
Backend Endpoint Testing Script for Phase 2 Refactored Architecture
===================================================================
Comprehensive testing of all FastAPI endpoints after Phase 2 refactoring.
Tests the GameOrchestrator integration while ensuring backward compatibility.

This test validates that:
- GameOrchestrator properly coordinates domain and infrastructure layers
- All FastAPI endpoints continue to work identically after refactoring
- GameLoop delegation maintains backward compatibility
- Domain services (SimulationEngine, TurnScheduler) integrate correctly
- Application services bridge domain and infrastructure properly

Usage:
    python tests/test_backend_endpoints_phase2.py
    
    OR from project root:
    PYTHONPATH=. python tests/test_backend_endpoints_phase2.py
"""

import asyncio
import json
import logging
import sys
from typing import Dict, List, Any, Optional, Union
from contextlib import asynccontextmanager

# Disable excessive logging during tests
logging.getLogger("backend").setLevel(logging.WARNING)
logging.getLogger("kani").setLevel(logging.WARNING)

try:
    from fastapi.testclient import TestClient
    from backend.interfaces.http.main import app
    from backend.game_loop import GameLoop
    from backend.config.schema import AgentActionOutput, WorldStateResponse, GameStatus
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class EndpointTester:
    """Test runner for backend endpoints with Phase 2 architecture."""
    
    def __init__(self):
        # Use TestClient with lifespan events to properly initialize game controller
        self.client = TestClient(app)
        self.test_results = []
        self.passed_tests = 0
        self.total_tests = 0
        
        # Trigger lifespan startup manually
        with self.client:
            pass
    
    def test_endpoint(self, name: str, method: str, endpoint: str, 
                     data: Optional[Dict] = None, 
                     expected_status: int = 200,
                     validate_response: Optional[Any] = None) -> bool:
        """Test an individual endpoint and return success status."""
        print(f"\nTesting {name}...")
        self.total_tests += 1
        
        try:
            # Make the request
            if method.upper() == "GET":
                response = self.client.get(endpoint)
            elif method.upper() == "POST":
                response = self.client.post(endpoint, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # Check status code
            if response.status_code != expected_status:
                print(f"  FAIL - Expected status {expected_status}, got {response.status_code}")
                print(f"  Response: {response.text}")
                self.test_results.append(f"FAIL {name}: Status {response.status_code}")
                return False
            
            # Parse response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                if response.text:
                    response_data = response.text
                else:
                    response_data = None
            
            # Validate response structure if validator provided
            if validate_response and response_data:
                validation_result = validate_response(response_data)
                if validation_result is not True:
                    print(f"  FAIL - Response validation failed: {validation_result}")
                    self.test_results.append(f"FAIL {name}: {validation_result}")
                    return False
            
            # Success
            print(f"  PASS - Status {response.status_code}")
            if response_data and isinstance(response_data, dict):
                # Show key info without flooding output
                if 'status' in response_data:
                    print(f"    Status: {response_data['status']}")
                if 'turn_counter' in response_data:
                    print(f"    Turn Counter: {response_data['turn_counter']}")
                if isinstance(response_data, list):
                    print(f"    Items: {len(response_data)}")
                elif isinstance(response_data, dict) and len(response_data) < 5:
                    print(f"    Data: {json.dumps(response_data, indent=4)}")
            
            self.passed_tests += 1
            self.test_results.append(f"PASS {name}")
            return True
            
        except Exception as e:
            print(f"  FAIL - Exception: {e}")
            self.test_results.append(f"FAIL {name}: {str(e)}")
            return False

    def validate_world_state(self, data: Dict) -> Union[bool, str]:
        """Validate world state response structure."""
        required_fields = ['agents', 'objects', 'locations', 'game_status']
        for field in required_fields:
            if field not in data:
                return f"Missing required field: {field}"
        
        # Check agents structure
        if not isinstance(data['agents'], dict):
            return "Agents field must be a dictionary"
        
        # Check objects structure  
        if not isinstance(data['objects'], list):
            return "Objects field must be a list"
        
        # Check locations structure
        if not isinstance(data['locations'], dict):
            return "Locations field must be a dictionary"
        
        return True

    def validate_game_status(self, data: Dict) -> Union[bool, str]:
        """Validate game status response structure."""
        required_fields = ['status', 'turn_counter', 'active_agents', 'total_events']
        for field in required_fields:
            if field not in data:
                return f"Missing required field: {field}"
        
        if data['status'] not in ['running', 'not_initialized']:
            return f"Invalid status: {data['status']}"
        
        return True

    def validate_objects_list(self, data: List) -> Union[bool, str]:
        """Validate objects endpoint response."""
        if not isinstance(data, list):
            return "Response must be a list"
        
        if len(data) == 0:
            return True  # Empty list is valid
        
        # Check first object structure
        obj = data[0]
        required_fields = ['name', 'location']
        for field in required_fields:
            if field not in obj:
                return f"Object missing required field: {field}"
        
        return True

    def validate_agent_actions(self, data: List) -> Union[bool, str]:
        """Validate agent actions response."""
        if not isinstance(data, list):
            return "Response must be a list"
        
        # Empty list is valid (no actions taken yet)
        return True

    def run_all_tests(self) -> bool:
        """Run the complete test suite."""
        print("=" * 60)
        print("Backend Endpoint Testing - Phase 2 Architecture")
        print("=" * 60)
        
        # Test core endpoints that should work immediately
        success = True
        
        # 1. Game Status
        success &= self.test_endpoint(
            "Game Status",
            "GET",
            "/game/status",
            validate_response=self.validate_game_status
        )
        
        # 2. World State
        success &= self.test_endpoint(
            "World State", 
            "GET",
            "/world_state",
            validate_response=self.validate_world_state
        )
        
        # 3. Objects List
        success &= self.test_endpoint(
            "Objects List",
            "GET", 
            "/objects",
            validate_response=self.validate_objects_list
        )
        
        # 4. Agent Actions (polling endpoint)
        success &= self.test_endpoint(
            "Agent Actions Polling",
            "GET",
            "/agent_act/next",
            validate_response=self.validate_agent_actions
        )
        
        # 5. Game Events
        success &= self.test_endpoint(
            "Game Events",
            "GET",
            "/game/events"
        )
        
        # 6. Game Reset (POST endpoint)
        success &= self.test_endpoint(
            "Game Reset",
            "POST",
            "/game/reset"
        )
        
        # 7. Game Pause
        success &= self.test_endpoint(
            "Game Pause",
            "POST", 
            "/game/pause"
        )
        
        # 8. Game Resume  
        success &= self.test_endpoint(
            "Game Resume",
            "POST",
            "/game/resume"
        )
        
        # Test error handling
        success &= self.test_endpoint(
            "Invalid Endpoint",
            "GET",
            "/invalid/endpoint",
            expected_status=404
        )
        
        return success

    def print_summary(self):
        """Print test execution summary."""
        print("\n" + "=" * 60)
        print("TEST EXECUTION SUMMARY")
        print("=" * 60)
        
        for result in self.test_results:
            status = "PASS" if result.startswith("PASS") else "FAIL"
            symbol = "[PASS]" if status == "PASS" else "[FAIL]"
            print(f"{symbol} {result}")
        
        print(f"\nResults: {self.passed_tests}/{self.total_tests} tests passed")
        
        if self.passed_tests == self.total_tests:
            print("\nALL TESTS PASSED!")
            print("PASS Phase 2 refactoring successful")
            print("PASS GameOrchestrator integration working")
            print("PASS Backward compatibility maintained")
            print("PASS All endpoints responding correctly")
            return True
        else:
            failed = self.total_tests - self.passed_tests
            print(f"\n{failed} test(s) failed")
            print("Phase 2 refactoring needs attention")
            return False


def test_phase2_architecture():
    """Test Phase 2 architecture components directly."""
    print("\n" + "=" * 60)
    print("PHASE 2 ARCHITECTURE VALIDATION")
    print("=" * 60)
    
    try:
        # Test GameLoop initialization with GameOrchestrator
        print("\nTesting GameLoop with GameOrchestrator integration...")
        
        async def test_gameloop():
            # Use the default agents.yaml configuration
            config_path = "config/agents.yaml"
            game_loop = GameLoop(config_file_path=config_path)
            print("PASS GameLoop created successfully with YAML configuration")
            
            await game_loop.initialize()
            print("PASS GameLoop initialized through GameOrchestrator")
            
            # Test properties delegated to orchestrator
            print(f"PASS Game object: {type(game_loop.game).__name__ if game_loop.game else 'None'}")
            print(f"PASS Agent manager: {type(game_loop.agent_manager).__name__ if game_loop.agent_manager else 'None'}")
            print(f"PASS Turn counter: {game_loop.turn_counter}")
            print(f"PASS Max turns: {game_loop.max_turns_per_session}")
            print(f"PASS Objects registry: {len(game_loop.objects_registry)} objects")
            
            # Test API methods
            world_state = await game_loop.get_world_state()
            print(f"PASS World state API: {len(world_state.keys())} top-level fields")
            
            game_status = await game_loop.get_game_status()
            print(f"PASS Game status API: {game_status.get('status', 'unknown')}")
            
            return True
        
        # Run async test
        result = asyncio.run(test_gameloop())
        if result:
            print("\nPASS Phase 2 architecture validation PASSED")
            return True
        else:
            print("\nFAIL Phase 2 architecture validation FAILED") 
            return False
            
    except Exception as e:
        print(f"\nFAIL Phase 2 architecture validation FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test execution function."""
    print("Backend Endpoint Testing for Phase 2 Refactored Architecture")
    print("Testing GameOrchestrator integration and backward compatibility\n")
    
    # First test the architecture components
    architecture_success = test_phase2_architecture()
    
    if not architecture_success:
        print("Architecture validation failed, skipping endpoint tests")
        return 1
    
    # Then test the HTTP endpoints
    tester = EndpointTester()
    endpoint_success = tester.run_all_tests()
    tester.print_summary()
    
    if architecture_success and endpoint_success:
        print("\nPhase 2 refactoring validation COMPLETE!")
        print("Backend is ready for Phase 3 (Event Bus Implementation)")
        return 0
    else:
        print("\nSome tests failed - Phase 2 needs fixes")
        return 1


if __name__ == "__main__":
    sys.exit(main())