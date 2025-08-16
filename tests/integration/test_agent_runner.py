#!/usr/bin/env python3
"""
Agent Goal Testing Runner - Pytest Compatible
==============================================

Pytest-compatible version of the agent goal test runner.
"""

import pytest
import asyncio
import os
import logging

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables from .env file won't be loaded.")

from backend.testing.agent_goal_test import AgentGoalTest
from backend.testing.agent_test_runner import AgentTestRunner
from backend.testing.criteria import LocationCriterion, InventoryCriterion
from backend.testing.config import WorldStateConfig, AgentConfig


@pytest.mark.asyncio
async def test_simple_navigation():
    """Test simple navigation from bedroom to kitchen."""
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
    
    assert result.success, f"Navigation test failed: {result.error_message}"
    assert result.turns_taken <= 10, f"Too many turns taken: {result.turns_taken}"


@pytest.mark.asyncio
async def test_item_collection():
    """Test item collection functionality."""
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
            persona="I want to find and collect an apple.",
            name="collector_agent"
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
    
    assert result.success, f"Collection test failed: {result.error_message}"
    assert result.turns_taken <= 20, f"Too many turns taken: {result.turns_taken}"


if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key to run these tests.")
        exit(1)
    
    # Run tests manually if called directly
    asyncio.run(test_simple_navigation())
    asyncio.run(test_item_collection())