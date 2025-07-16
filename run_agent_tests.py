#!/usr/bin/env python3
"""
Agent Goal Testing Runner
========================

Simple script to run agent goal tests and see the results.
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.testing.agent_goal_test import AgentGoalTest
from backend.testing.agent_test_runner import AgentTestRunner
from backend.testing.goals import LocationGoal, InventoryGoal
from backend.testing.criteria import LocationCriterion, InventoryCriterion
from backend.testing.config import WorldStateConfig, AgentConfig


async def run_simple_test():
    """Run a simple navigation test."""
    print("Running simple navigation test...")
    
    test = AgentGoalTest(
        name="simple_navigation",
        description="Agent should navigate from bedroom to kitchen",
        initial_world_state=WorldStateConfig(
            agent_location="Bedroom"
        ),
        agent_config=AgentConfig(
            persona="I am hungry and want to go to the kitchen.",
            name="nav_test_agent"
        ),
        goal=LocationGoal(
            target_location="Kitchen",
            description="Move to the kitchen"
        ),
        success_criteria=[
            LocationCriterion(location="Kitchen")
        ],
        max_turns=10
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    print(f"\nTest completed: {'PASSED' if result.success else 'FAILED'}")
    print(f"Turns taken: {result.turns_taken}")
    print(f"Duration: {result.duration_seconds:.2f}s")
    print(f"Final location: {result.final_state.get('agent_location', 'Unknown')}")
    
    return result


async def run_collection_test():
    """Run an item collection test."""
    print("\nRunning item collection test...")
    
    test = AgentGoalTest(
        name="item_collection",
        description="Agent should find and collect an apple",
        initial_world_state=WorldStateConfig(
            agent_location="Entry Room",
            world_items={
                "Kitchen": [
                    {"name": "apple", "description": "A red apple"}
                ]
            }
        ),
        agent_config=AgentConfig(
            persona="You want should find and collect an apple.",
            name="collector_agent"
        ),
        goal=InventoryGoal(
            must_have=["apple"],
            description="Collect an apple"
        ),
        success_criteria=[
            InventoryCriterion(has_items=["apple"])
        ],
        max_turns=20
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    print(f"\nTest completed: {'PASSED' if result.success else 'FAILED'}")
    print(f"Turns taken: {result.turns_taken}")
    print(f"Duration: {result.duration_seconds:.2f}s")
    print(f"Final inventory: {result.final_state.get('agent_inventory', [])}")
    
    return result


async def main():
    """Main function to run various test scenarios."""
    print("Agent Goal-Based Testing System")
    print("="*50)
    
    try:
        # Run simple tests
        await run_simple_test()
        await run_collection_test()
        
        print(f"\nOverall Results:")
        # print(f"Suite success rate: {suite_result.success_rate:.1f}%")
        # print(f"Total duration: {suite_result.total_duration:.2f}s")
        
    except Exception as e:
        print(f"Error running tests: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key to run these tests.")
        sys.exit(1)
    
    asyncio.run(main())