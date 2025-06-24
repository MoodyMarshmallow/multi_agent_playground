#!/usr/bin/env python3
"""
Simple test for salience evaluation integration.
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent  # Go up one level from tests/ to backend/
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from character_agent.agent import Agent
from server.controller import evaluate_event_salience

def test_simple_salience():
    """Test the salience evaluation integration in controller"""
    print("Testing simple salience evaluation...")
    
    try:
        # Load a real agent  
        agent_dir = "../../data/agents/alex_001"
        agent = Agent(agent_dir)
        
        # Test different events
        test_events = [
            "I saw a pen on the desk",
            "I had lunch", 
            "I discovered something surprising",
        ]
        
        print(f"\nTesting with agent: {agent.first_name} {agent.last_name}")
        print("=" * 50)
        
        for event in test_events:
            try:
                print(f"Event: '{event}'")
                salience = evaluate_event_salience(agent, event)
                print(f"Salience: {salience}/10")
                print("-" * 30)
            except Exception as e:
                print(f"Error evaluating '{event}': {e}")
                print("-" * 30)
        
        print("\n✅ Simple salience test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run the test"""
    try:
        test_simple_salience()
    except Exception as e:
        print(f"❌ Failed to run test: {e}")
        print("Note: Make sure you have OpenAI API key configured")

if __name__ == "__main__":
    main() 