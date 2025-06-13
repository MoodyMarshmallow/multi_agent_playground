#!/usr/bin/env python3
"""
Integration test for salience evaluation in the controller.
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent  # Go up one level from tests/ to backend/
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from character_agent.agent import Agent
from config.schema import AgentActionInput, AgentPerception, MoveFrontendAction
from server.controller import confirm_action_and_update

def test_integration():
    """Test the salience evaluation integration"""
    print("Testing salience evaluation integration...")
    
    try:
        # Create test data
        perception = AgentPerception(
            timestamp="01T10:30:00",
            current_tile=(10, 10),
            visible_objects={
                "coffee_mug": {
                    "room": "kitchen",
                    "position": [10, 11],
                    "state": "empty"
                }
            },
            visible_agents=[],
            chatable_agents=[],
            heard_messages=[]
        )
        
        action = MoveFrontendAction(
            action_type="move",
            destination_tile=(11, 10)
        )
        
        agent_msg = AgentActionInput(
            agent_id="alex_001",
            action=action,
            in_progress=False,
            perception=perception
        )
        
        print("Before test:")
        # Load agent and check memory count
        agent = Agent("../../data/agents/alex_001")
        initial_memory_count = len(agent.memory)
        print(f"Initial memory events: {initial_memory_count}")
        
        # Test the confirm action function
        print("\nTesting confirm_action_and_update with salience evaluation...")
        confirm_action_and_update(agent_msg)
        
        print("After test:")
        # Reload agent and check memory
        agent = Agent("../../data/agents/alex_001")
        final_memory_count = len(agent.memory)
        print(f"Final memory events: {final_memory_count}")
        
        # Check if new memory was added
        if final_memory_count > initial_memory_count:
            new_memory = agent.memory[-1]  # Get the last memory
            print(f"New memory added:")
            print(f"  Event: {new_memory['event']}")
            print(f"  Salience: {new_memory['salience']}")
            print(f"  Location: {new_memory['location']}")
            print(f"  Timestamp: {new_memory['timestamp']}")
        
        print("\n✅ Integration test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run the test"""
    try:
        test_integration()
    except Exception as e:
        print(f"❌ Failed to run test: {e}")

if __name__ == "__main__":
    main() 