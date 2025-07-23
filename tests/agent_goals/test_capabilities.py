"""
Capability Test Cases
====================

Test cases for capability discovery and usage in the object-centric architecture.
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
    CapabilityDiscoveryCriterion, CapabilityUsageCriterion, ActionSequenceCriterion,
    ObjectStateCriterion, InventoryCriterion, LocationCriterion
)
from backend.testing.config import WorldStateConfig, AgentConfig


@pytest.mark.asyncio
async def test_activatable_capability_discovery():
    """Test agent discovers and uses Activatable capability on appliances."""
    test = AgentGoalTest(
        name="activatable_discovery",
        description="Agent should discover and use Activatable capability on sink and TV",
        initial_world_state=WorldStateConfig(
            agent_location="Kitchen"
        ),
        agent_config=AgentConfig(
            persona="I like to test and operate electronic devices and appliances.",
            name="capability_tester"
        ),
        success_criteria=[
            CapabilityDiscoveryCriterion("sink", ["Activatable"]),
            CapabilityUsageCriterion("sink", "Activatable")
        ],
        max_turns=20
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success


@pytest.mark.asyncio
async def test_usable_capability_discovery():
    """Test agent discovers and uses Usable capability on furniture."""
    test = AgentGoalTest(
        name="usable_discovery",
        description="Agent should discover and use Usable capability on bed",
        initial_world_state=WorldStateConfig(
            agent_location="Bedroom"
        ),
        agent_config=AgentConfig(
            persona="I want to rest and use furniture properly.",
            name="furniture_user"
        ),
        success_criteria=[
            CapabilityDiscoveryCriterion("bed", ["Usable"]),
            CapabilityUsageCriterion("bed", "Usable")
        ],
        max_turns=15
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success


@pytest.mark.asyncio
async def test_container_capability_discovery():
    """Test agent discovers and uses Container capability."""
    test = AgentGoalTest(
        name="container_discovery",
        description="Agent should discover Container capability on closet and bookshelf",
        initial_world_state=WorldStateConfig(
            agent_location="Bedroom"
        ),
        agent_config=AgentConfig(
            persona="I like to organize things and put items in containers.",
            name="organizer"
        ),
        success_criteria=[
            CapabilityDiscoveryCriterion("closet", ["Container", "Openable"]),
            CapabilityUsageCriterion("closet", "Container")
        ],
        max_turns=25
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success


@pytest.mark.asyncio
async def test_consumable_capability_discovery():
    """Test agent discovers and uses Consumable capability on food items."""
    test = AgentGoalTest(
        name="consumable_discovery",
        description="Agent should discover and use Consumable capability on apple",
        initial_world_state=WorldStateConfig(
            agent_location="Kitchen"
        ),
        agent_config=AgentConfig(
            persona="I am hungry and want to eat food items.",
            name="food_lover"
        ),
        success_criteria=[
            CapabilityDiscoveryCriterion("apple", ["Consumable"]),
            CapabilityUsageCriterion("apple", "Consumable"),
            InventoryCriterion(lacks_items=["apple"])
        ],
        max_turns=20
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success


@pytest.mark.asyncio
async def test_examinable_capability_discovery():
    """Test agent discovers and uses Examinable capability on various objects."""
    test = AgentGoalTest(
        name="examinable_discovery",
        description="Agent should examine multiple objects to discover their capabilities",
        initial_world_state=WorldStateConfig(
            agent_location="Living Room"
        ),
        agent_config=AgentConfig(
            persona="I am curious and examine everything carefully.",
            name="examiner"
        ),
        success_criteria=[
            CapabilityUsageCriterion("tv", "Examinable"),
            CapabilityUsageCriterion("couch", "Examinable"),
            CapabilityUsageCriterion("bookshelf", "Examinable")
        ],
        max_turns=25
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success


@pytest.mark.asyncio
async def test_multi_capability_object():
    """Test agent discovers and uses multiple capabilities on the same object."""
    test = AgentGoalTest(
        name="multi_capability",
        description="Agent should use multiple capabilities on TV (Activatable, Usable, Examinable)",
        initial_world_state=WorldStateConfig(
            agent_location="Living Room"
        ),
        agent_config=AgentConfig(
            persona="I want to fully interact with the TV - examine it, turn it on, and watch it.",
            name="comprehensive_user"
        ),
        success_criteria=[
            CapabilityDiscoveryCriterion("tv", ["Activatable", "Usable", "Examinable"]),
            CapabilityUsageCriterion("tv", "Activatable"),
            CapabilityUsageCriterion("tv", "Usable"),
            CapabilityUsageCriterion("tv", "Examinable")
        ],
        max_turns=30
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success


@pytest.mark.asyncio
async def test_capability_sequence():
    """Test agent performs capability-based actions in logical sequence."""
    test = AgentGoalTest(
        name="capability_sequence",
        description="Agent should examine closet, open it, take jacket, examine jacket",
        initial_world_state=WorldStateConfig(
            agent_location="Bedroom"
        ),
        agent_config=AgentConfig(
            persona="I am methodical and examine things before and after interacting with them.",
            name="methodical_agent"
        ),
        success_criteria=[
            ActionSequenceCriterion(["examine", "set_to_state", "take", "examine"], strict_order=True),
            CapabilityUsageCriterion("closet", "Examinable"),
            CapabilityUsageCriterion("closet", "Openable"),
            CapabilityUsageCriterion("jacket", "Examinable"),
            InventoryCriterion(has_items=["jacket"])
        ],
        max_turns=35
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success


@pytest.mark.asyncio
async def test_capability_adaptation():
    """Test agent adapts to different object capabilities across rooms."""
    test = AgentGoalTest(
        name="capability_adaptation",
        description="Agent should navigate and interact with different object types",
        initial_world_state=WorldStateConfig(
            agent_location="Entry Room"
        ),
        agent_config=AgentConfig(
            persona="I am adaptive and interact appropriately with different types of objects.",
            name="adaptive_agent"
        ),
        success_criteria=[
            LocationCriterion(location="Kitchen"),
            CapabilityUsageCriterion("sink", "Activatable"),
            LocationCriterion(location="Living Room"),
            CapabilityUsageCriterion("couch", "Usable"),
            LocationCriterion(location="Bedroom"),
            CapabilityUsageCriterion("closet", "Openable")
        ],
        max_turns=40
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success


@pytest.mark.asyncio
async def test_capability_error_handling():
    """Test agent handles objects without expected capabilities gracefully."""
    test = AgentGoalTest(
        name="capability_error_handling",
        description="Agent should handle objects appropriately based on their actual capabilities",
        initial_world_state=WorldStateConfig(
            agent_location="Dining Room"
        ),
        agent_config=AgentConfig(
            persona="I try to interact with objects but adapt when they don't support certain actions.",
            name="adaptive_handler"
        ),
        success_criteria=[
            CapabilityUsageCriterion("dining table", "Examinable"),  # Table only has Examinable
            CapabilityUsageCriterion("dining chair", "Usable")       # Chair has Usable
        ],
        max_turns=20
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success


@pytest.mark.asyncio
async def test_capability_efficiency():
    """Test agent efficiently discovers and uses capabilities without excessive exploration."""
    test = AgentGoalTest(
        name="capability_efficiency",
        description="Agent should efficiently discover and use object capabilities",
        initial_world_state=WorldStateConfig(
            agent_location="Kitchen"
        ),
        agent_config=AgentConfig(
            persona="I am efficient and quickly identify how to interact with objects.",
            name="efficient_agent"
        ),
        success_criteria=[
            CapabilityUsageCriterion("sink", "Activatable"),
            CapabilityUsageCriterion("kitchen cabinet", "Openable"),
            CapabilityUsageCriterion("apple", "Consumable")
        ],
        max_turns=20  # Strict limit to test efficiency
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success
    assert result.turns_taken <= 15  # Should be efficient
    assert result.agent_behavior_analysis.efficiency_score >= 0.6


if __name__ == "__main__":
    # Run a simple capability test
    async def main():
        test = AgentGoalTest(
            name="simple_capability_test",
            description="Simple capability discovery test",
            initial_world_state=WorldStateConfig(agent_location="Kitchen"),
            agent_config=AgentConfig(name="test_agent"),
            success_criteria=[CapabilityDiscoveryCriterion("sink", ["Activatable"])],
            max_turns=15
        )
        
        runner = AgentTestRunner()
        result = await runner.run_test(test)
        print(f"Test result: {result.success}")
    
    asyncio.run(main())