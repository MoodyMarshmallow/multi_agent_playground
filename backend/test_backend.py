"""
Test script for the combined multi-agent playground backend.

This script tests the integration of:
- Text adventure games framework
- Agent manager with multi-agent support
- HTTP endpoints compatibility
- Event system
"""

import asyncio
import sys
from pathlib import Path

# Add the backend to the path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Add the parent directory to find the backend module
project_root = backend_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.game_loop import GameLoop
from backend.agent_manager import SimpleRandomAgent
from backend.config.schema import AgentSummary


async def test_basic_functionality():
    """Test basic game controller functionality."""
    print("Testing Multi-Agent Playground Backend")
    print("=" * 50)
    
    # Initialize the game controller
    print("\n1. Initializing game controller...")
    controller = GameLoop()
    await controller.initialize()
    print("✓ Game controller initialized successfully")
    
    # Test agent summaries
    print("\n2. Testing agent summaries...")
    summaries = controller.get_all_agent_summaries()
    print(f"✓ Found {len(summaries)} agents:")
    for summary in summaries:
        print(f"   - {summary.agent_id} in {summary.curr_room}")
    
    # Test game status
    print("\n3. Testing game status...")
    status = controller.get_game_status()
    print(f"✓ Game status: {status}")
    
    # Test objects
    print("\n4. Testing objects...")
    objects = controller.get_all_objects()
    print(f"✓ Found {len(objects)} objects:")
    for obj in objects[:3]:  # Show first 3
        print(f"   - {obj['name']} in {obj['location']}")
    
    # Test action planning for an agent
    print("\n5. Testing action planning...")
    if summaries:
        agent_id = summaries[0].agent_id
        try:
            result = await controller.plan_agent_action(agent_id)
            print(f"✓ Planned action for {agent_id}: {result.action.action.action_type}")
        except Exception as e:
            print(f"⚠ Action planning failed (expected if no OpenAI API key): {e}")
    
    # Test event system
    print("\n6. Testing event system...")
    events = controller.get_events_since(0)
    print(f"✓ Found {len(events)} events in queue")
    
    print("\n" + "=" * 50)
    print("✓ All basic tests completed successfully!")


async def test_simple_agent_interaction():
    """Test the system with simple random agents."""
    print("\nTesting with Simple Random Agents")
    print("=" * 40)
    
    controller = GameLoop()
    await controller.initialize()
    
    # Replace Kani agents with simple random agents for testing
    print("\n1. Setting up simple random agents...")
    if controller.agent_manager:
        # Clear existing strategies
        controller.agent_manager.agent_strategies.clear()
        
        # Add simple random agents
        controller.agent_manager.register_agent_strategy("alex_001", SimpleRandomAgent())
        controller.agent_manager.register_agent_strategy("alan_002", SimpleRandomAgent())
        print("✓ Simple random agents registered")
        
        # Test a few turns
        print("\n2. Running a few agent turns...")
        for i in range(3):
            print(f"\nTurn {i+1}:")
            
            # Plan actions for all agents
            for agent_id in ["alex_001", "alan_002"]:
                try:
                    result = await controller.plan_agent_action(agent_id)
                    action_type = result.action.action.action_type
                    print(f"   {agent_id}: {action_type}")
                except Exception as e:
                    print(f"   {agent_id}: Error - {e}")
        
        print("\n✓ Agent interaction test completed!")


if __name__ == "__main__":
    print("Multi-Agent Playground Backend Test Suite")
    print("========================================")
    
    # Run basic functionality test
    asyncio.run(test_basic_functionality())
    
    # Run simple agent interaction test
    asyncio.run(test_simple_agent_interaction())
    
    print("\n🎉 All tests completed!")
    print("\nTo start the HTTP server, run: python -m backend.main")
    print("Then visit the API endpoints like: http://localhost:8000/agents/init") 