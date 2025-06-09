"""
Multi-Agent Playground - Character Agent Example
==========================================
Example script demonstrating how to use the Character agent implementation.

Before running this script, make sure to:
1. Install dependencies: pip install -r requirements.txt
2. Set your OpenAI API key: export OPENAI_API_KEY="your-api-key-here"
3. Ensure you have agent data in data/agents/{agent_id}/
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to Python path for imports
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from kani_implementation import LLMAgent
from config.llm_config import LLMConfig


def check_prerequisites():
    """Check if all prerequisites are met before running the demo."""
    print("🔍 Checking prerequisites...")
    
    # Check OpenAI API key
    try:
        api_key = LLMConfig.get_openai_api_key()
        print(f"✅ OpenAI API key found (starts with: {api_key[:10]}...)")
    except ValueError as e:
        print(f"❌ OpenAI API key not found: {e}")
        return False
    
    # Check agent data
    agent_dir = Path(__file__).parent.parent.parent / "data" / "agents" / "alex"
    if agent_dir.exists():
        print(f"✅ Agent data directory found: {agent_dir}")
        agent_json = agent_dir / "agent.json"
        if agent_json.exists():
            print(f"✅ Agent JSON file found: {agent_json}")
        else:
            print(f"❌ Agent JSON file not found: {agent_json}")
            return False
    else:
        print(f"❌ Agent data directory not found: {agent_dir}")
        return False
    
    return True


async def demo_llm_agent():
    """Demonstrate Character agent functionality."""
    
    # Example agent state (this would normally come from the agent files)
    agent_state = {
        "agent_id": "alex",
        "name": "Alex",
        "curr_tile": [5, 5],
        "daily_req": ["work on computer", "eat lunch", "socialize"],
        "memory": [],
        "visible_objects": {
            "computer": {"state": "off", "location": [5, 6]},
            "chair": {"state": "empty", "location": [5, 5]}
        },
        "visible_agents": [],
        "currently": "idle"
    }
    
    # Example perception data
    perception_data = {
        "visible_objects": {
            "computer": {"state": "off", "location": [5, 6]},
            "chair": {"state": "empty", "location": [5, 5]},
            "coffee_mug": {"state": "empty", "location": [4, 5]}
        },
        "visible_agents": ["bob"],
        "current_time": "2024-01-15T09:00:00Z",
        "self_state": "standing in room"
    }
    
    print("🤖 Multi-Agent LLM Demo")
    print("=" * 40)
    
    try:
        # Test the direct async function
        print("Testing async Character agent function...")
        result = await LLMAgent.call_llm_for_action(agent_state, perception_data)
        print(f"📤 LLM Action Result:")
        print(f"   Agent ID: {result['agent_id']}")
        print(f"   Action Type: {result['action_type']}")
        print(f"   Content: {result['content']}")
        print(f"   Emoji: {result['emoji']}")
        
    except Exception as e:
        print(f"❌ Error testing Character agent: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        print("Make sure:")
        print("1. OPENAI_API_KEY environment variable is set")
        print("2. Agent data exists in data/agents/alex/")
        print("3. Internet connection is available")


def demo_sync_wrapper():
    """Demonstrate the synchronous wrapper function."""
    
    # Same test data as above
    agent_state = {
        "agent_id": "alex",
        "name": "Alex",
        "curr_tile": [5, 5],
        "daily_req": ["work on computer", "eat lunch", "socialize"],
        "memory": [],
        "visible_objects": {},
        "visible_agents": [],
        "currently": "idle"
    }
    
    perception_data = {
        "visible_objects": {
            "computer": {"state": "off", "location": [5, 6]}
        },
        "visible_agents": [],
        "current_time": "2024-01-15T09:00:00Z"
    }
    
    print("\n🔄 Testing synchronous wrapper function...")
    
    try:
        # Test the synchronous wrapper (this is what the controller uses)
        result = LLMAgent.call_llm_agent(agent_state, perception_data)
        print(f"📤 Sync Wrapper Result:")
        print(f"   Agent ID: {result['agent_id']}")
        print(f"   Action Type: {result['action_type']}")
        print(f"   Content: {result['content']}")
        print(f"   Emoji: {result['emoji']}")
        
    except Exception as e:
        print(f"❌ Error testing sync wrapper: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()


if __name__ == "__main__":
    print("Starting LLM Agent Demo...")
    
    # Check prerequisites first
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above and try again.")
        sys.exit(1)
    
    # Test async version
    asyncio.run(demo_llm_agent())
    
    # Test sync version
    demo_sync_wrapper()
    
    print("\n✅ Demo completed!")
    print("\nTo use in your application:")
    print("1. Import: from character_agent.llm_agent import call_llm_agent")
    print("2. Call: result = call_llm_agent(agent_state, perception_data)")
    print("3. The result will be a JSON dict ready for the frontend!") 