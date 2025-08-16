#!/usr/bin/env python3
"""
Simple API test script for the Multi-Agent Playground backend.
"""

import requests
import time
import json

def test_api():
    base_url = "http://localhost:8000"
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(3)
    
    try:
        # Test agents endpoint
        print("\n1. Testing /agents/init endpoint...")
        response = requests.get(f"{base_url}/agents/init")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            agents = response.json()
            print(f"Found {len(agents)} agents:")
            for agent in agents:
                print(f"  - {agent['agent_id']} in {agent['curr_room']}")
        else:
            print(f"Error: {response.text}")
        
        # Test objects endpoint
        print("\n2. Testing /objects endpoint...")
        response = requests.get(f"{base_url}/objects")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            objects = response.json()
            print(f"Found {len(objects)} objects:")
            for obj in objects[:3]:  # Show first 3
                print(f"  - {obj['name']} in {obj['location']}")
        else:
            print(f"Error: {response.text}")
        
        # Test game status endpoint
        print("\n3. Testing /game/status endpoint...")
        response = requests.get(f"{base_url}/game/status")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            status = response.json()
            print(f"Game status: {json.dumps(status, indent=2)}")
        else:
            print(f"Error: {response.text}")
        
        # Test agent plan endpoint
        print("\n4. Testing /agent_act/plan endpoint...")
        response = requests.post(f"{base_url}/agent_act/plan", json=["alex_001"])
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            plans = response.json()
            print(f"Planned actions for {len(plans)} agents:")
            for plan in plans:
                action_type = plan['action']['action']['action_type']
                agent_id = plan['action']['agent_id']
                print(f"  - {agent_id}: {action_type}")
        else:
            print(f"Error: {response.text}")
        
        print("\nAll API tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("Could not connect to server. Make sure it's running on port 8000.")
    except Exception as e:
        print(f"Error testing API: {e}")

if __name__ == "__main__":
    test_api() 