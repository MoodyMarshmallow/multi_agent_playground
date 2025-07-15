"""
Navigation Test Cases
====================

Example test cases for agent navigation capabilities.
"""

import pytest
import asyncio
from backend.testing.agent_goal_test import AgentGoalTest
from backend.testing.agent_test_runner import AgentTestRunner
from backend.testing.goals import LocationGoal, InventoryGoal
from backend.testing.criteria import LocationCriterion, InventoryCriterion
from backend.testing.config import WorldStateConfig, AgentConfig


@pytest.mark.asyncio
async def test_agent_basic_navigation():
    """Test that agent can navigate from bedroom to kitchen."""
    test = AgentGoalTest(
        name="basic_navigation",
        description="Agent should navigate from bedroom to kitchen",
        initial_world_state=WorldStateConfig(
            agent_location="Bedroom"
        ),
        agent_config=AgentConfig(
            persona="I am helpful and follow directions to move around.",
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
    
    assert result.success
    assert result.turns_taken <= 5  # Should be efficient
    assert result.final_state["agent_location"] == "Kitchen"


@pytest.mark.asyncio
async def test_agent_multi_room_navigation():
    """Test agent navigation through multiple rooms."""
    test = AgentGoalTest(
        name="multi_room_navigation",
        description="Agent should navigate from entry to game room",
        initial_world_state=WorldStateConfig(
            agent_location="Entry Room"
        ),
        agent_config=AgentConfig(
            persona="I am an explorer who navigates efficiently.",
            name="multi_nav_agent"
        ),
        goal=LocationGoal(
            target_location="Game Room",
            description="Navigate to the game room"
        ),
        success_criteria=[
            LocationCriterion(location="Game Room")
        ],
        max_turns=15
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success
    assert result.final_state["agent_location"] == "Game Room"


@pytest.mark.asyncio
async def test_agent_item_collection():
    """Test that agent can find and collect an item."""
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
            persona="I am helpful and collect items when asked.",
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
    
    assert result.success
    assert "apple" in result.final_state["agent_inventory"]


@pytest.mark.asyncio
async def test_agent_exploration():
    """Test agent's ability to explore and find items in different locations."""
    test = AgentGoalTest(
        name="exploration_test",
        description="Agent should explore and find a key somewhere in the house",
        initial_world_state=WorldStateConfig(
            agent_location="Entry Room",
            world_items={
                "Bedroom": [
                    {"name": "key", "description": "A small brass key"}
                ]
            }
        ),
        agent_config=AgentConfig(
            persona="I am a curious explorer who searches thoroughly.",
            name="explorer_agent"
        ),
        goal=InventoryGoal(
            must_have=["key"],
            description="Find and collect the key"
        ),
        success_criteria=[
            InventoryCriterion(has_items=["key"])
        ],
        max_turns=25
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success
    assert "key" in result.final_state["agent_inventory"]


@pytest.mark.asyncio
async def test_navigation_efficiency():
    """Test that agent navigates efficiently without getting lost."""
    test = AgentGoalTest(
        name="navigation_efficiency",
        description="Agent should navigate efficiently to bathroom",
        initial_world_state=WorldStateConfig(
            agent_location="Kitchen"
        ),
        agent_config=AgentConfig(
            persona="I am efficient and take the shortest path.",
            name="efficient_agent"
        ),
        goal=LocationGoal(
            target_location="Bathroom",
            description="Navigate to bathroom efficiently"
        ),
        success_criteria=[
            LocationCriterion(location="Bathroom")
        ],
        max_turns=8  # Strict turn limit to test efficiency
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success
    assert result.turns_taken <= 6  # Should be very efficient
    assert result.agent_behavior_analysis.efficiency_score >= 0.5


if __name__ == "__main__":
    # Run a simple test
    async def main():
        test = AgentGoalTest(
            name="simple_nav_test",
            description="Simple navigation test",
            initial_world_state=WorldStateConfig(agent_location="Bedroom"),
            agent_config=AgentConfig(name="test_agent"),
            goal=LocationGoal(target_location="Kitchen"),
            success_criteria=[LocationCriterion(location="Kitchen")],
            max_turns=10
        )
        
        runner = AgentTestRunner()
        result = await runner.run_test(test)
        print(f"Test result: {result.success}")
    
    asyncio.run(main())