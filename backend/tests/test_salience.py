#!/usr/bin/env python3
"""
Test script to verify salience evaluation works correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent  # Go up one level from tests/ to backend/
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from character_agent.agent import Agent
from character_agent.kani_implementation import LLMAgent
from config.schema import AgentPerception

async def test_salience_evaluation():
    """Test the salience evaluation functionality"""
    print("Testing salience evaluation...")
    
    try:
        # Use a real agent from the data directory
        agent_dir = "../../data/agents/alex_001"
        agent = Agent(agent_dir)
        
        # Create LLM agent
        llm_agent = LLMAgent(agent)
        
        # Test different types of events
        test_events = [
            "I saw a pen on the desk",  # Should be low salience (routine)
            "I discovered a new scientific formula",  # Should be high salience (achievement)
            "I had a meaningful conversation with a colleague about life",  # Should be moderate salience
            "I witnessed a dangerous accident",  # Should be very high salience
            "I ate lunch",  # Should be very low salience (routine)
        ]
        
        print("\nEvaluating salience for different events:")
        print("=" * 50)
        
        for event in test_events:
            try:
                salience = await llm_agent.evaluate_event_salience(event)
                print(f"Event: '{event}'")
                print(f"Salience: {salience}/10")
                print("-" * 30)
            except Exception as e:
                print(f"Error evaluating '{event}': {e}")
                print("-" * 30)
        
        print("\n✅ Salience evaluation test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run the test"""
    try:
        print("Starting salience evaluation test...")
        asyncio.run(test_salience_evaluation())
    except Exception as e:
        print(f"❌ Failed to run test: {e}")
        print("Note: Make sure you have OpenAI API key configured in your environment")

if __name__ == "__main__":
    main()