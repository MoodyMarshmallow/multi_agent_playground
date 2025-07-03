#!/usr/bin/env python3
"""
Godot "R" Key Press Simulation Test
==================================
Simulates the exact workflow that happens when a user presses "R" in the Godot frontend
to trigger AI actions for agents.

This test covers:
1. Initial agent state loading (like Godot would on startup)
2. Perception data collection (simulating what Godot sees)
3. Action planning request (triggered by "R" key)
4. Action execution simulation
5. Action confirmation (completion feedback)

This ensures the backend can handle the most common Godot interaction pattern.
"""

import requests
import json
import time
import sys
import random
from datetime import datetime
from typing import Dict, Any, List

BASE_URL = "http://localhost:8000"

class GodotSimulator:
    """Simulates Godot frontend behavior for testing backend integration."""
    
    def __init__(self):
        self.agents = []
        self.current_agent_index = 0
        self.simulation_time = datetime.now().strftime("%dT%H:%M:%S")
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def simulate_startup(self) -> bool:
        """Simulate Godot frontend startup - loading agents."""
        self.log("🎮 Simulating Godot startup...")
        
        try:
            response = requests.get(f"{BASE_URL}/agents/init")
            if response.status_code == 200:
                self.agents = response.json()
                self.log(f"✅ Loaded {len(self.agents)} agents: {[a['agent_id'] for a in self.agents]}")
                return True
            else:
                self.log(f"❌ Failed to load agents: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Connection failed: {e}", "ERROR")
            return False
    
    def get_current_agent(self) -> Dict[str, Any]:
        """Get the currently selected agent (like in Godot UI)."""
        if not self.agents:
            return None
        return self.agents[self.current_agent_index % len(self.agents)]
    
    def simulate_perception_data(self, agent: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate perception data that Godot would collect from the game world."""
        # Get agent's current position
        curr_tile = agent.get("curr_tile", [0, 0])
        
        # Simulate other agents in view (like Godot would detect)
        other_agents = [a["agent_id"] for a in self.agents if a["agent_id"] != agent["agent_id"]]
        visible_agents = random.sample(other_agents, min(2, len(other_agents)))
        chatable_agents = random.sample(visible_agents, min(1, len(visible_agents)))
        
        # Simulate objects in view (typical house objects)
        visible_objects = {}
        if random.random() < 0.7:  # 70% chance to see objects
            sample_objects = [
                {"name": "bed", "room": "bedroom", "state": "messy"},
                {"name": "desk", "room": "office", "state": "cluttered"},
                {"name": "coffee_machine", "room": "kitchen", "state": "off"},
                {"name": "bookshelf", "room": "living_room", "state": "organized"},
                {"name": "wardrobe", "room": "bedroom", "state": "open"}
            ]
            
            for obj in random.sample(sample_objects, random.randint(0, 3)):
                visible_objects[obj["name"]] = {
                    "room": obj["room"],
                    "position": [curr_tile[0] + random.randint(-2, 2), 
                               curr_tile[1] + random.randint(-2, 2)],
                    "state": obj["state"]
                }
        
        # Simulate heard messages (conversations)
        heard_messages = []
        if random.random() < 0.3:  # 30% chance to hear messages
            heard_messages = [
                {
                    "sender": random.choice(visible_agents) if visible_agents else "unknown",
                    "receiver": agent["agent_id"],
                    "message": random.choice([
                        "Hey, how's it going?",
                        "Want to grab some coffee?",
                        "Did you see that interesting book?",
                        "The weather is nice today!"
                    ]),
                    "timestamp": self.simulation_time
                }
            ]
        
        perception = {
            "timestamp": self.simulation_time,
            "current_tile": curr_tile,
            "visible_objects": visible_objects,
            "visible_agents": visible_agents,
            "chatable_agents": chatable_agents,
            "heard_messages": heard_messages
        }
        
        self.log(f"🎯 Simulated perception for {agent['agent_id']}: "
                f"objects={len(visible_objects)}, agents={len(visible_agents)}, "
                f"messages={len(heard_messages)}")
        
        return perception
    
    def simulate_r_key_press(self) -> bool:
        """Simulate pressing 'R' key to trigger AI action planning."""
        self.log("⌨️  Simulating 'R' key press - triggering AI action planning...")
        
        current_agent = self.get_current_agent()
        if not current_agent:
            self.log("❌ No agent available for R key simulation", "ERROR")
            return False
        
        # Step 1: Collect perception data (what Godot sees)
        perception_data = self.simulate_perception_data(current_agent)
        
        # Step 2: Send action planning request (triggered by R key)
        plan_request = [{
            "agent_id": current_agent["agent_id"],
            "perception": perception_data
        }]
        
        try:
            self.log(f"📤 Sending action plan request for {current_agent['agent_id']}...")
            response = requests.post(f"{BASE_URL}/agent_act/plan", json=plan_request)
            
            if response.status_code == 200:
                plan_response = response.json()
                action_data = plan_response[0]
                
                self.log(f"✅ Received action plan: {action_data['action']['action']['action_type']} "
                        f"with emoji {action_data['action']['emoji']}")
                
                # Step 3: Simulate action execution and confirmation
                return self.simulate_action_execution(current_agent, action_data, perception_data)
            else:
                self.log(f"❌ Action planning failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Action planning error: {e}", "ERROR")
            return False
    
    def simulate_action_execution(self, agent: Dict[str, Any], action_data: Dict[str, Any], 
                                perception_data: Dict[str, Any]) -> bool:
        """Simulate executing the planned action in Godot."""
        action = action_data["action"]["action"]
        action_type = action["action_type"]
        
        self.log(f"🎬 Simulating action execution: {action_type}")
        
        # Simulate time passing during action execution
        time.sleep(0.5)
        
        # Update perception based on action (simulate Godot updating world state)
        updated_perception = perception_data.copy()
        
        if action_type == "move":
            destination = action.get("destination_tile")
            if destination:
                updated_perception["current_tile"] = list(destination)
                self.log(f"🚶 Agent moved to {destination}")
        
        elif action_type == "chat":
            message_data = action.get("message", {})
            self.log(f"💬 Agent chatted: '{message_data.get('message', 'Unknown message')}'")
        
        elif action_type == "interact":
            obj_name = action.get("object", "unknown")
            self.log(f"🤏 Agent interacted with {obj_name}")
        
        elif action_type == "perceive":
            self.log(f"👀 Agent observed surroundings")
        
        # Step 4: Send confirmation (action completed)
        return self.simulate_action_confirmation(agent, action_data["action"], updated_perception)
    
    def simulate_action_confirmation(self, agent: Dict[str, Any], action: Dict[str, Any], 
                                   perception: Dict[str, Any]) -> bool:
        """Simulate sending action confirmation to backend."""
        self.log("📋 Sending action confirmation...")
        
        confirm_request = [{
            "agent_id": agent["agent_id"],
            "action": action["action"],
            "in_progress": False,  # Action completed
            "perception": perception
        }]
        
        try:
            response = requests.post(f"{BASE_URL}/agent_act/confirm", json=confirm_request)
            
            if response.status_code == 200:
                confirm_response = response.json()
                self.log(f"✅ Action confirmed: {confirm_response[0]['status']}")
                return True
            else:
                self.log(f"❌ Action confirmation failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Action confirmation error: {e}", "ERROR")
            return False
    
    def run_multiple_r_key_presses(self, count: int = 3) -> Dict[str, int]:
        """Simulate multiple R key presses with different agents."""
        self.log(f"🔄 Running {count} R key press simulations...")
        
        results = {"successful": 0, "failed": 0}
        
        for i in range(count):
            self.log(f"\n--- R Key Press Simulation #{i+1} ---")
            
            # Switch to different agent for variety
            self.current_agent_index = i % len(self.agents)
            
            # Update simulation time
            self.simulation_time = datetime.now().strftime("%dT%H:%M:%S")
            
            if self.simulate_r_key_press():
                results["successful"] += 1
            else:
                results["failed"] += 1
            
            # Brief pause between simulations
            time.sleep(1)
        
        return results

def main():
    print("🎮 Godot 'R' Key Press Simulation Test")
    print("=" * 60)
    
    simulator = GodotSimulator()
    
    # Step 1: Simulate Godot startup
    if not simulator.simulate_startup():
        print("\n❌ FAILED: Could not initialize simulation (server not running?)")
        return 1
    
    # Step 2: Run health check
    try:
        health_response = requests.get(f"{BASE_URL}/health")
        if health_response.status_code != 200:
            print("\n❌ FAILED: Backend health check failed")
            return 1
        simulator.log("✅ Backend health check passed")
    except:
        print("\n❌ FAILED: Cannot connect to backend server")
        return 1
    
    # Step 3: Simulate single R key press
    print("\n🎯 TESTING SINGLE R KEY PRESS")
    print("-" * 40)
    
    single_test_success = simulator.simulate_r_key_press()
    
    # Step 4: Simulate multiple R key presses
    print("\n🔄 TESTING MULTIPLE R KEY PRESSES")
    print("-" * 40)
    
    multi_results = simulator.run_multiple_r_key_presses(count=3)
    
    # Step 5: Summary
    print("\n" + "=" * 60)
    print("📊 SIMULATION RESULTS")
    print("=" * 60)
    
    print(f"Single R Key Test: {'✅ PASS' if single_test_success else '❌ FAIL'}")
    print(f"Multiple R Key Tests: {multi_results['successful']}/{multi_results['successful'] + multi_results['failed']} passed")
    
    total_tests = 1 + multi_results['successful'] + multi_results['failed']
    total_passed = (1 if single_test_success else 0) + multi_results['successful']
    
    if total_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED! Godot R key simulation working perfectly!")
        print("✅ Backend properly handles Godot AI trigger workflow")
        print("✅ Action planning pipeline operational")
        print("✅ Action confirmation system working")
        print("✅ Multi-agent interaction handling verified")
        print("\n🚀 Ready for Godot frontend integration!")
        return 0
    else:
        print(f"\n⚠️  {total_tests - total_passed} test(s) failed out of {total_tests}")
        print("Backend needs attention before Godot integration")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 