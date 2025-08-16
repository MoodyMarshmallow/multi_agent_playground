#!/usr/bin/env python3
"""
Backend Server Comprehensive Test
================================
Tests all endpoints to verify the backend is working correctly.
"""

import requests
import json
import time
import sys
import pytest

BASE_URL = "http://localhost:8000"

def make_request(name, method, url, data=None, expected_status=200):
    """Test an endpoint and return results."""
    print(f"\n🔍 Testing {name}...")
    
    response = None
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        if response is not None:
            print(f"   Status: {response.status_code}")
            
            if response.status_code == expected_status:
                try:
                    json_data = response.json()
                    print(f"   ✅ Success - Response: {json.dumps(json_data, indent=2)[:200]}...")
                    return True, json_data
                except json.JSONDecodeError:
                    print(f"   ✅ Success - Text Response: {response.text[:100]}...")
                    return True, response.text
            else:
                print(f"   ❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text}")
                return False, None
        else:
            print(f"   ❌ Invalid method: {method}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection failed - Is server running on {BASE_URL}?")
        return False, None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False, None

def test_backend_endpoints():
    """Test all backend endpoints"""
    print("🚀 Backend Server Comprehensive Test")
    print("=" * 50)
    
    # Test 1: Health Check
    success1, _ = make_request(
        "Health Check",
        "GET",
        f"{BASE_URL}/health"
    )
    
    # Test 2: Agent Initialization
    success2, agents_data = make_request(
        "Agent Initialization",
        "GET", 
        f"{BASE_URL}/agents/init"
    )
    
    # Test 3: Action Planning
    plan_request_data = [{
        "agent_id": "alex_001",
        "perception": {
            "timestamp": "01T04:35:20",
            "current_tile": [12, 8],
            "visible_objects": {},
            "visible_agents": ["alan_002"],
            "chatable_agents": ["alan_002"],
            "heard_messages": []
        }
    }]
    
    success3, plan_data = make_request(
        "Action Planning",
        "POST",
        f"{BASE_URL}/agent_act/plan",
        plan_request_data
    )
    
    # Test 4: Action Confirmation
    confirm_request_data = [{
        "agent_id": "alex_001",
        "action": {
            "action_type": "perceive"
        },
        "in_progress": False,
        "perception": {
            "timestamp": "01T04:35:20",
            "current_tile": [12, 8],
            "visible_objects": {},
            "visible_agents": ["alan_002"],
            "chatable_agents": ["alan_002"],
            "heard_messages": []
        }
    }]
    
    success4, confirm_data = make_request(
        "Action Confirmation",
        "POST",
        f"{BASE_URL}/agent_act/confirm",
        confirm_request_data
    )
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    tests = [
        ("Health Check", success1),
        ("Agent Initialization", success2),
        ("Action Planning", success3),  
        ("Action Confirmation", success4)
    ]
    
    passed = sum(1 for _, success in tests if success)
    total = len(tests)
    
    for test_name, success in tests:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Backend server is fully operational!")
        print("✅ All endpoints working correctly")
        print("✅ Ready for frontend integration")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Server needs attention.")
        
    # Use pytest assertions for proper test reporting
    assert passed == total, f"{total - passed} tests failed"

if __name__ == "__main__":
    # For manual testing
    test_backend_endpoints() 