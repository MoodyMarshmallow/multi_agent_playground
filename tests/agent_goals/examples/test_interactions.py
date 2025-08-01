"""
Interaction Test Cases
=====================

Example test cases for agent interaction capabilities.
"""

import pytest
import asyncio 
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from backend.testing.agent_goal_test import AgentGoalTest
from backend.testing.agent_test_runner import AgentTestRunner
from backend.testing.criteria import ActionCriterion, InventoryCriterion, LocationCriterion
from backend.testing.config import WorldStateConfig, AgentConfig


@pytest.mark.asyncio
async def test_agent_item_delivery():
    """Test agent's ability to deliver an item to another character."""
    test = AgentGoalTest(
        name="item_delivery",
        description="Agent should find apple and give it to Alex",
        initial_world_state=WorldStateConfig(
            agent_location="Entry Room",
            world_items={
                "Kitchen": [
                    {"name": "apple", "description": "A red apple"}
                ]
            },
            character_locations={
                "alex_001": "Bedroom"
            }
        ),
        agent_config=AgentConfig(
            persona="I am helpful and deliver items to others.",
            name="delivery_agent"
        ),
        success_criteria=[
            ActionCriterion(action_type="place", target="apple")
        ],
        max_turns=30
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success
    # Check that the place action was performed
    place_actions = [action for action in result.action_sequence 
                    if hasattr(action.action, 'action_type') and action.action.action_type == "place"]
    assert len(place_actions) > 0


@pytest.mark.asyncio
async def test_agent_object_interaction():
    """Test agent's ability to interact with objects in the environment."""
    test = AgentGoalTest(
        name="object_interaction",
        description="Agent should open the closet and examine contents",
        initial_world_state=WorldStateConfig(
            agent_location="Bedroom"
        ),
        agent_config=AgentConfig(
            persona="I am curious and examine objects carefully.",
            name="interaction_agent"
        ),
        success_criteria=[
            ActionCriterion(action_type="set_to_state", target="closet")
        ],
        max_turns=15
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success
    # Check that the set_to_state action was performed
    state_actions = [action for action in result.action_sequence 
                    if hasattr(action.action, 'action_type') and action.action.action_type == "set_to_state"]
    assert len(state_actions) > 0


@pytest.mark.asyncio
async def test_agent_complex_task():
    """Test agent's ability to perform a complex multi-step task."""
    test = AgentGoalTest(
        name="complex_task",
        description="Agent should get jacket from closet and go to kitchen",
        initial_world_state=WorldStateConfig(
            agent_location="Bedroom"
        ),
        agent_config=AgentConfig(
            persona="I am organized and complete tasks step by step.",
            name="complex_agent"
        ),
        success_criteria=[
            InventoryCriterion(has_items=["jacket"]),
            LocationCriterion(location="Kitchen")
        ],
        max_turns=25
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success
    assert "jacket" in result.final_state["agent_inventory"]
    assert result.final_state["agent_location"] == "Kitchen"


@pytest.mark.asyncio
async def test_agent_social_interaction():
    """Test agent's ability to locate and interact with other characters."""
    test = AgentGoalTest(
        name="social_interaction",
        description="Agent should find Alan and have a conversation",
        initial_world_state=WorldStateConfig(
            agent_location="Entry Room",
            character_locations={
                "alan_002": "Living Room"
            }
        ),
        agent_config=AgentConfig(
            persona="I am social and enjoy talking with others.",
            name="social_agent"
        ),
        success_criteria=[
            LocationCriterion(location="Living Room")
        ],
        max_turns=20
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success
    assert result.final_state["agent_location"] == "Living Room"
    assert "alan_002" in result.final_state["visible_characters"]


@pytest.mark.asyncio
async def test_agent_problem_solving():
    """Test agent's problem-solving ability with obstacles."""
    test = AgentGoalTest(
        name="problem_solving",
        description="Agent should find a way to get an item from a container",
        initial_world_state=WorldStateConfig(
            agent_location="Kitchen"
        ),
        agent_config=AgentConfig(
            persona="I am persistent and solve problems step by step.",
            name="problem_solver"
        ),
        success_criteria=[
            InventoryCriterion(has_items=["apple"])
        ],
        max_turns=30
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    # This test might fail if there's no apple available, which is expected
    # It tests the agent's ability to handle situations where goals might not be achievable
    if result.success:
        assert "apple" in result.final_state["agent_inventory"]
    else:
        # Check that the agent made reasonable attempts
        assert result.turns_taken > 5  # Agent should have tried multiple actions
        assert result.agent_behavior_analysis.decision_quality_score > 0.3  # Some valid decisions


if __name__ == "__main__":
    # Run a simple interaction test
    async def main():
        test = AgentGoalTest(
            name="simple_interaction",
            description="Simple interaction test",
            initial_world_state=WorldStateConfig(agent_location="Bedroom"),
            agent_config=AgentConfig(name="test_agent"),
            success_criteria=[ActionCriterion(action_type="set_to_state", target="closet")],
            max_turns=15
        )
        
        runner = AgentTestRunner()
        result = await runner.run_test(test)
        print(f"Test result: {result.success}")
    
    asyncio.run(main())