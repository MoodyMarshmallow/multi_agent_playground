#!/usr/bin/env python3
"""
Direct test for salience evaluation function.
"""

import sys
import asyncio
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent  # Go up one level from tests/ to backend/
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from character_agent.agent import Agent
from character_agent.agent_manager import create_llm_agent

async def test_direct_salience():
    """Test the salience evaluation function directly"""
    print("Testing direct salience evaluation...")
    
    try:
        # Load a real agent
        agent_dir = "../../data/agents/alex_001"
        agent = Agent(agent_dir)
        
        print(f"Testing with agent: {agent.first_name} {agent.last_name}")
        print(f"Agent personality: {agent.personality}")
        print("=" * 50)
        
        # Create LLM agent using the manager
        llm_agent = create_llm_agent(agent.agent_id)
        
        # Test a simple event
        event = "I saw a coffee mug on the kitchen counter"
        print(f"Event: '{event}'")
        
        # Directly test the action function
        from character_agent.actions import ActionsMixin
        actions = ActionsMixin()
        actions.agent_id = agent.agent_id
        
        # Call the function directly
        result = actions.evaluate_event_salience(event, 2)
        print(f"Direct function result: {result}")
        
        print("\n✅ Direct salience test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run the test"""
    try:
        asyncio.run(test_direct_salience())
    except Exception as e:
        print(f"❌ Failed to run test: {e}")

if __name__ == "__main__":
    main() 