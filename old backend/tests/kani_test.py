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

from backend.character_agent.kani_agent import LLMAgent
from backend.arush_llm.integration.character_agent_adapter import call_llm_agent, clear_all_llm_agents
from backend.arush_llm.integration.character_agent_adapter import CharacterAgentAdapter as Agent
from backend.config.llm_config import LLMConfig


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
    agent_dir = Path(__file__).parent.parent.parent / "data" / "agents" / "alex_001"
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


def load_real_agent_data(agent_id: str = "alex_001"):
    """Load real agent data from the agent files."""
    agent_dir = Path(__file__).parent.parent.parent / "data" / "agents" / agent_id
    
    print(f"📂 Loading real agent data for {agent_id}...")
    
    # Load the agent using the Agent class
    agent = Agent(str(agent_dir))
    
    # Create example perception data that simulates what the frontend would send
    perception_data = {
        "visible_objects": {
            "easel": {"state": "empty", "location": [23, 9], "room": "art_studio"},
            "paintbrush": {"state": "clean", "location": [22, 8], "room": "art_studio"},
            "canvas": {"state": "blank", "location": [23, 10], "room": "art_studio"}
        },
        "visible_agents": ["alan_002"],
        "chatable_agents": ["alan_002"],
        "heard_messages": [],
        "current_time": "2024-01-15T10:30:00Z",
        "timestamp": "2024-01-15T10:30:00Z",
        "current_tile": agent.curr_tile,
        "self_state": "standing in art studio"
    }
    
    # Update the agent's perception with this data
    agent.update_perception(perception_data)
    
    # Get agent state as used by the LLM system
    agent_state = agent.to_state_dict()
    
    print(f"✅ Successfully loaded agent data:")
    print(f"   Agent ID: {agent_state['agent_id']}")
    print(f"   Name: {agent_state['name']}")
    print(f"   Current tile: {agent_state['curr_tile']}")
    print(f"   Currently: {agent_state['currently']}")
    print(f"   Daily requirements: {len(agent_state['daily_req'])} items")
    print(f"   Memory events: {len(agent_state['memory'])} events")
    print(f"   Visible objects: {len(agent_state['visible_objects'])} objects")
    print(f"   Visible agents: {agent_state['visible_agents']}")
    
    return agent_state, perception_data


async def demo_llm_agent():
    """Demonstrate Character agent functionality using real agent data."""
    
    print("🤖 Multi-Agent LLM Demo (Using Real Agent Data)")
    print("=" * 50)
    
    try:
        # Load real agent data
        agent_state, perception_data = load_real_agent_data("alex_001")
        
        # Test the direct async function
        print("\n🔄 Testing async Character agent function...")
        result = await call_llm_for_action(agent_state, perception_data)
        
        print(f"📤 LLM Action Result:")
        print(f"   Agent ID: {result['agent_id']}")
        print(f"   Action Type: {result['action_type']}")
        print(f"   Content: {result['content']}")
        print(f"   Emoji: {result['emoji']}")
        
        # Show some context about what the agent sees
        print(f"\n📍 Agent Context:")
        print(f"   Current Location: {agent_state['curr_tile']}")
        print(f"   Visible Objects: {list(agent_state['visible_objects'].keys())}")
        print(f"   Recent Activity: {agent_state['currently']}")
        
    except Exception as e:
        print(f"❌ Error testing Character agent: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        print("Make sure:")
        print("1. OPENAI_API_KEY environment variable is set")
        print("2. Agent data exists in data/agents/alex_001/")
        print("3. Internet connection is available")


def demo_sync_wrapper():
    """Demonstrate the synchronous wrapper function using real agent data."""
    
    print("\n🔄 Testing synchronous wrapper function...")
    
    try:
        # Clear any existing agents to avoid state conflicts
        clear_all_llm_agents()
        
        # Load real agent data
        agent_state, perception_data = load_real_agent_data("alex_001")
        
        # Test the synchronous wrapper (this is what the controller uses)
        result = call_llm_agent(agent_state, perception_data)
        
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


def demo_alternative_agent():
    """Test with the other available agent if it exists."""
    
    print("\n🔄 Testing with alternative agent (alan_002)...")
    
    # Check if alan_002 exists
    alan_dir = Path(__file__).parent.parent.parent / "data" / "agents" / "alan_002"
    if not alan_dir.exists():
        print("❌ alan_002 agent not found, skipping alternative agent test")
        return
    
    try:
        # Clear any existing agents to avoid state conflicts
        clear_all_llm_agents()
        
        # Load alan_002 agent data
        agent_state, perception_data = load_real_agent_data("alan_002")
        
        # Test with different perception data for variety
        perception_data["visible_objects"] = {
            "stove": {"state": "off", "location": [15, 10], "room": "kitchen"},
            "cutting_board": {"state": "clean", "location": [14, 10], "room": "kitchen"},
            "refrigerator": {"state": "closed", "location": [13, 9], "room": "kitchen"}
        }
        perception_data["visible_agents"] = ["alex_001"]
        
        # Update agent perception
        alan_agent = Agent(str(alan_dir))
        alan_agent.update_perception(perception_data)
        agent_state = alan_agent.to_state_dict()
        
        # Test the call
        result = call_llm_agent(agent_state, perception_data)
        
        print(f"📤 Alan Agent Result:")
        print(f"   Agent ID: {result['agent_id']}")
        print(f"   Action Type: {result['action_type']}")
        print(f"   Content: {result['content']}")
        print(f"   Emoji: {result['emoji']}")
        
    except Exception as e:
        print(f"❌ Error testing alan_002 agent: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()


if __name__ == "__main__":
    print("Starting LLM Agent Demo with Real Data...")
    
    # Check prerequisites first
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above and try again.")
        sys.exit(1)
    
    # Test async version with real data
    asyncio.run(demo_llm_agent())
    
    # Test sync version with real data
    demo_sync_wrapper()
    
    # Test with alternative agent if available
    demo_alternative_agent()
    
    # Clean up at the end
    clear_all_llm_agents()
    print("\n🧹 Cleaned up LLM agents")
    
    print("\n✅ Demo completed!")
    print("\nTo use in your application:")
    print("1. Import: from character_agent.llm_agent_manager import call_llm_agent")
    print("2. Load agent: agent = Agent('data/agents/alex_001')")
    print("3. Update perception: agent.update_perception(perception_data)")
    print("4. Get state: agent_state = agent.to_state_dict()")
    print("5. Call: result = call_llm_agent(agent_state, perception_data)")
    print("6. The result will be a JSON dict ready for the frontend!") 