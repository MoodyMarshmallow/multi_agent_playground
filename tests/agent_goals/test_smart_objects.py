"""
Smart Object Test Cases
======================

Test cases for smart object interactions with the new object-centric architecture.
"""

import pytest
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables from .env file won't be loaded.")

from backend.testing.agent_goal_test import AgentGoalTest
from backend.testing.agent_test_runner import AgentTestRunner
from backend.testing.criteria import (
    ObjectStateCriterion, CapabilityUsageCriterion, SmartObjectInteractionCriterion,
    ContainerOperationCriterion, FurnitureUsageCriterion, InventoryCriterion, LocationCriterion
)
from backend.testing.config import WorldStateConfig, AgentConfig


@pytest.mark.asyncio
async def test_sink_activation():
    """Test agent's ability to activate and deactivate the sink."""
    test = AgentGoalTest(
        name="sink_activation",
        description="Agent should turn the sink on and off",
        initial_world_state=WorldStateConfig(
            agent_location="Kitchen"
        ),
        agent_config=AgentConfig(
            persona="I am helpful and test appliances by turning them on and off.",
            name="appliance_tester"
        ),
        success_criteria=[
            CapabilityUsageCriterion("sink", "Activatable"),
            ObjectStateCriterion("sink", "is_active", True)
        ],
        max_turns=15
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success
    # Check that sink was actually activated
    assert result.final_state.get("sink_is_active", False)


@pytest.mark.asyncio
async def test_tv_interaction():
    """Test agent's ability to interact with TV (activate and use)."""
    test = AgentGoalTest(
        name="tv_interaction",
        description="Agent should turn on the TV and start watching",
        initial_world_state=WorldStateConfig(
            agent_location="Living Room"
        ),
        agent_config=AgentConfig(
            persona="I enjoy watching TV and know how to operate electronics.",
            name="tv_watcher"
        ),
        success_criteria=[
            CapabilityUsageCriterion("tv", "Activatable"),
            CapabilityUsageCriterion("tv", "Usable"),
            ObjectStateCriterion("tv", "is_active", True)
        ],
        max_turns=20
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success


@pytest.mark.asyncio
async def test_closet_container_operations():
    """Test agent's ability to perform complete container operations."""
    test = AgentGoalTest(
        name="closet_operations",
        description="Agent should open closet, take jacket, and close closet",
        initial_world_state=WorldStateConfig(
            agent_location="Bedroom"
        ),
        agent_config=AgentConfig(
            persona="I am organized and perform tasks step by step.",
            name="organizer_agent"
        ),
        success_criteria=[
            ContainerOperationCriterion("closet", ["open", "remove_item", "close"], strict_order=True),
            InventoryCriterion(has_items=["jacket"]),
            ObjectStateCriterion("closet", "is_open", False)  # Should be closed at end
        ],
        max_turns=25
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success
    assert "jacket" in result.final_state["agent_inventory"]


@pytest.mark.asyncio
async def test_bed_furniture_usage():
    """Test agent's ability to use furniture (bed for sleeping)."""
    test = AgentGoalTest(
        name="bed_usage",
        description="Agent should use the bed for sleeping",
        initial_world_state=WorldStateConfig(
            agent_location="Bedroom"
        ),
        agent_config=AgentConfig(
            persona="I am tired and want to sleep on the bed.",
            name="sleepy_agent"
        ),
        success_criteria=[
            FurnitureUsageCriterion("bed", "sleep"),
            CapabilityUsageCriterion("bed", "Usable")
        ],
        max_turns=15
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success


@pytest.mark.asyncio
async def test_cabinet_storage():
    """Test agent's ability to use cabinet for storage."""
    test = AgentGoalTest(
        name="cabinet_storage",
        description="Agent should open kitchen cabinet and place utensils",
        initial_world_state=WorldStateConfig(
            agent_location="Kitchen"
        ),
        agent_config=AgentConfig(
            persona="I am organized and like to put things in their proper place.",
            name="storage_agent"
        ),
        success_criteria=[
            ContainerOperationCriterion("kitchen cabinet", ["open"], strict_order=False),
            CapabilityUsageCriterion("kitchen cabinet", "Container"),
            CapabilityUsageCriterion("kitchen cabinet", "Openable")
        ],
        max_turns=20
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success


@pytest.mark.asyncio
async def test_apple_consumption():
    """Test agent's ability to consume the apple."""
    test = AgentGoalTest(
        name="apple_consumption",
        description="Agent should find and eat the apple",
        initial_world_state=WorldStateConfig(
            agent_location="Entry Room"
        ),
        agent_config=AgentConfig(
            persona="I am hungry and want to eat the apple in the kitchen.",
            name="hungry_agent"
        ),
        success_criteria=[
            LocationCriterion(location="Kitchen"),
            CapabilityUsageCriterion("apple", "Consumable"),
            InventoryCriterion(lacks_items=["apple"])  # Apple should be consumed
        ],
        max_turns=25
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success
    assert "apple" not in result.final_state["agent_inventory"]


@pytest.mark.asyncio
async def test_chair_sitting():
    """Test agent's ability to sit on furniture."""
    test = AgentGoalTest(
        name="chair_sitting",
        description="Agent should sit on the couch in living room",
        initial_world_state=WorldStateConfig(
            agent_location="Living Room"
        ),
        agent_config=AgentConfig(
            persona="I want to sit down and relax on the couch.",
            name="relaxing_agent"
        ),
        success_criteria=[
            FurnitureUsageCriterion("couch", "sit"),
            CapabilityUsageCriterion("couch", "Usable")
        ],
        max_turns=10
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success


@pytest.mark.asyncio
async def test_bookshelf_interaction():
    """Test agent's ability to interact with bookshelf and books."""
    test = AgentGoalTest(
        name="bookshelf_interaction",
        description="Agent should examine bookshelf and take a book",
        initial_world_state=WorldStateConfig(
            agent_location="Living Room"
        ),
        agent_config=AgentConfig(
            persona="I love reading and want to find an interesting book.",
            name="reader_agent"
        ),
        success_criteria=[
            CapabilityUsageCriterion("bookshelf", "Examinable"),
            CapabilityUsageCriterion("bookshelf", "Container"),
            InventoryCriterion(has_items=["novel"])  # Should take a book
        ],
        max_turns=20
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success
    assert "novel" in result.final_state["agent_inventory"]


@pytest.mark.asyncio
async def test_toilet_usage():
    """Test agent's ability to use bathroom facilities."""
    test = AgentGoalTest(
        name="toilet_usage",
        description="Agent should use the toilet in the bathroom",
        initial_world_state=WorldStateConfig(
            agent_location="Bathroom"
        ),
        agent_config=AgentConfig(
            persona="I need to use the bathroom facilities.",
            name="bathroom_user"
        ),
        success_criteria=[
            FurnitureUsageCriterion("toilet", "use"),
            CapabilityUsageCriterion("toilet", "Usable")
        ],
        max_turns=10
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success


@pytest.mark.asyncio
async def test_complex_multi_object_task():
    """Test agent's ability to interact with multiple smart objects in sequence."""
    test = AgentGoalTest(
        name="multi_object_task",
        description="Agent should turn on TV, sit on couch, and watch TV",
        initial_world_state=WorldStateConfig(
            agent_location="Living Room"
        ),
        agent_config=AgentConfig(
            persona="I want to relax and watch TV comfortably.",
            name="entertainment_agent"
        ),
        success_criteria=[
            CapabilityUsageCriterion("tv", "Activatable"),
            CapabilityUsageCriterion("couch", "Usable"),
            CapabilityUsageCriterion("tv", "Usable"),
            ObjectStateCriterion("tv", "is_active", True)
        ],
        max_turns=30
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success


@pytest.mark.asyncio
async def test_clothing_examination():
    """Test agent's ability to examine clothing items."""
    test = AgentGoalTest(
        name="clothing_examination",
        description="Agent should open closet and examine clothing items",
        initial_world_state=WorldStateConfig(
            agent_location="Bedroom"
        ),
        agent_config=AgentConfig(
            persona="I am curious about the clothes in the closet.",
            name="fashion_agent"
        ),
        success_criteria=[
            ContainerOperationCriterion("closet", ["open"], strict_order=False),
            CapabilityUsageCriterion("jacket", "Examinable"),
            CapabilityUsageCriterion("hat", "Examinable")
        ],
        max_turns=25
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success


if __name__ == "__main__":
    # Run a simple test
    async def main():
        test = AgentGoalTest(
            name="simple_smart_object_test",
            description="Simple smart object test",
            initial_world_state=WorldStateConfig(agent_location="Kitchen"),
            agent_config=AgentConfig(name="test_agent"),
            success_criteria=[CapabilityUsageCriterion("sink", "Activatable")],
            max_turns=15
        )
        
        runner = AgentTestRunner()
        result = await runner.run_test(test)
        print(f"Test result: {result.success}")
    
    asyncio.run(main())