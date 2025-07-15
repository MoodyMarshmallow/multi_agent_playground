"""
Test Suite Example
==================

Example of running a comprehensive test suite for agent capabilities.
"""

import asyncio
from backend.testing.agent_goal_test import AgentGoalTest
from backend.testing.agent_test_runner import AgentTestRunner
from backend.testing.goals import LocationGoal, InventoryGoal, InteractionGoal, ActionSequenceGoal
from backend.testing.criteria import LocationCriterion, InventoryCriterion, ActionCriterion
from backend.testing.config import WorldStateConfig, AgentConfig


def create_navigation_tests():
    """Create a suite of navigation tests."""
    tests = []
    
    # Basic navigation test
    tests.append(AgentGoalTest(
        name="basic_navigation",
        description="Navigate from bedroom to kitchen",
        initial_world_state=WorldStateConfig(agent_location="Bedroom"),
        agent_config=AgentConfig(
            persona="I am efficient at navigation and follow directions.",
            name="nav_agent"
        ),
        goal=LocationGoal(target_location="Kitchen"),
        success_criteria=[LocationCriterion(location="Kitchen")],
        max_turns=10
    ))
    
    # Multi-room navigation
    tests.append(AgentGoalTest(
        name="multi_room_navigation",
        description="Navigate from entry to game room",
        initial_world_state=WorldStateConfig(agent_location="Entry Room"),
        agent_config=AgentConfig(
            persona="I am an explorer who navigates efficiently.",
            name="explorer_agent"
        ),
        goal=LocationGoal(target_location="Game Room"),
        success_criteria=[LocationCriterion(location="Game Room")],
        max_turns=15
    ))
    
    # Navigation with efficiency test
    tests.append(AgentGoalTest(
        name="efficient_navigation",
        description="Navigate efficiently to bathroom",
        initial_world_state=WorldStateConfig(agent_location="Kitchen"),
        agent_config=AgentConfig(
            persona="I take the shortest path and am very efficient.",
            name="efficient_agent"
        ),
        goal=LocationGoal(target_location="Bathroom"),
        success_criteria=[LocationCriterion(location="Bathroom")],
        max_turns=8
    ))
    
    return tests


def create_item_interaction_tests():
    """Create a suite of item interaction tests."""
    tests = []
    
    # Basic item collection
    tests.append(AgentGoalTest(
        name="item_collection",
        description="Find and collect an apple",
        initial_world_state=WorldStateConfig(
            agent_location="Entry Room",
            world_items={"Kitchen": [{"name": "apple", "description": "A red apple"}]}
        ),
        agent_config=AgentConfig(
            persona="I am helpful and collect items when needed.",
            name="collector_agent"
        ),
        goal=InventoryGoal(must_have=["apple"]),
        success_criteria=[InventoryCriterion(has_items=["apple"])],
        max_turns=20
    ))
    
    # Container interaction
    tests.append(AgentGoalTest(
        name="container_interaction",
        description="Open closet and get jacket",
        initial_world_state=WorldStateConfig(agent_location="Bedroom"),
        agent_config=AgentConfig(
            persona="I am thorough and check containers for items.",
            name="container_agent"
        ),
        goal=InventoryGoal(must_have=["jacket"]),
        success_criteria=[InventoryCriterion(has_items=["jacket"])],
        max_turns=15
    ))
    
    # Multiple item collection
    tests.append(AgentGoalTest(
        name="multiple_items",
        description="Collect multiple items from different locations",
        initial_world_state=WorldStateConfig(
            agent_location="Entry Room",
            world_items={
                "Kitchen": [{"name": "apple", "description": "A red apple"}],
                "Bedroom": [{"name": "book", "description": "A interesting book"}]
            }
        ),
        agent_config=AgentConfig(
            persona="I am organized and collect items systematically.",
            name="multi_collector"
        ),
        goal=InventoryGoal(must_have=["apple", "book"]),
        success_criteria=[InventoryCriterion(has_items=["apple", "book"])],
        max_turns=30
    ))
    
    return tests


def create_social_interaction_tests():
    """Create a suite of social interaction tests."""
    tests = []
    
    # Character location test
    tests.append(AgentGoalTest(
        name="find_character",
        description="Find Alex in the house",
        initial_world_state=WorldStateConfig(
            agent_location="Entry Room",
            character_locations={"alex_001": "Living Room"}
        ),
        agent_config=AgentConfig(
            persona="I am social and enjoy finding and talking to others.",
            name="social_agent"
        ),
        goal=LocationGoal(target_location="Living Room"),
        success_criteria=[LocationCriterion(location="Living Room")],
        max_turns=20
    ))
    
    # Item delivery test
    tests.append(AgentGoalTest(
        name="item_delivery",
        description="Deliver apple to Alex",
        initial_world_state=WorldStateConfig(
            agent_location="Kitchen",
            agent_inventory=["apple"],
            character_locations={"alex_001": "Bedroom"}
        ),
        agent_config=AgentConfig(
            persona="I am helpful and deliver items to others.",
            name="delivery_agent"
        ),
        goal=InteractionGoal(target="alex_001", interaction_type="give_item", item="apple"),
        success_criteria=[ActionCriterion(action_type="give_item", target="alex_001", item="apple")],
        max_turns=25
    ))
    
    return tests


def create_complex_task_tests():
    """Create a suite of complex task tests."""
    tests = []
    
    # Multi-step task
    tests.append(AgentGoalTest(
        name="complex_task",
        description="Get jacket from bedroom and go to kitchen",
        initial_world_state=WorldStateConfig(agent_location="Bedroom"),
        agent_config=AgentConfig(
            persona="I am organized and complete complex tasks step by step.",
            name="complex_agent"
        ),
        goal=InventoryGoal(must_have=["jacket"]),
        success_criteria=[
            InventoryCriterion(has_items=["jacket"]),
            LocationCriterion(location="Kitchen")
        ],
        max_turns=25
    ))
    
    # Action sequence test
    tests.append(AgentGoalTest(
        name="action_sequence",
        description="Perform a specific sequence of actions",
        initial_world_state=WorldStateConfig(agent_location="Entry Room"),
        agent_config=AgentConfig(
            persona="I follow instructions precisely and in order.",
            name="sequence_agent"
        ),
        goal=ActionSequenceGoal(
            actions=["go north", "look", "go east"],
            strict_order=True
        ),
        success_criteria=[LocationCriterion(location="Dining Room")],
        max_turns=15
    ))
    
    return tests


async def run_comprehensive_test_suite():
    """Run a comprehensive test suite covering all agent capabilities."""
    
    # Create test suites
    navigation_tests = create_navigation_tests()
    item_tests = create_item_interaction_tests()
    social_tests = create_social_interaction_tests()
    complex_tests = create_complex_task_tests()
    
    # Combine all tests
    all_tests = navigation_tests + item_tests + social_tests + complex_tests
    
    # Run the test suite
    runner = AgentTestRunner()
    result = await runner.run_test_suite(all_tests, "Comprehensive Agent Capability Suite")
    
    # Generate and print report
    report = runner.generate_report(result)
    print(report)
    
    # Save report to file
    with open("agent_test_report.md", "w") as f:
        f.write(report)
    
    return result


async def run_quick_test_suite():
    """Run a quick test suite with essential tests."""
    
    tests = [
        # Basic navigation
        AgentGoalTest(
            name="quick_navigation",
            description="Quick navigation test",
            initial_world_state=WorldStateConfig(agent_location="Bedroom"),
            agent_config=AgentConfig(name="quick_agent"),
            goal=LocationGoal(target_location="Kitchen"),
            success_criteria=[LocationCriterion(location="Kitchen")],
            max_turns=10
        ),
        
        # Basic item collection
        AgentGoalTest(
            name="quick_collection",
            description="Quick item collection test",
            initial_world_state=WorldStateConfig(
                agent_location="Bedroom",
                world_items={"Kitchen": [{"name": "apple", "description": "A red apple"}]}
            ),
            agent_config=AgentConfig(name="quick_collector"),
            goal=InventoryGoal(must_have=["apple"]),
            success_criteria=[InventoryCriterion(has_items=["apple"])],
            max_turns=15
        )
    ]
    
    runner = AgentTestRunner()
    result = await runner.run_test_suite(tests, "Quick Agent Test Suite")
    
    return result


if __name__ == "__main__":
    # Run the comprehensive test suite
    print("Running comprehensive agent test suite...")
    result = asyncio.run(run_comprehensive_test_suite())
    
    print(f"\nSuite completed with {result.success_rate:.1f}% success rate")
    print(f"Total duration: {result.total_duration:.2f} seconds")
    
    # Also run quick test suite for comparison
    print("\n" + "="*50)
    print("Running quick test suite for comparison...")
    quick_result = asyncio.run(run_quick_test_suite())
    
    print(f"\nQuick suite completed with {quick_result.success_rate:.1f}% success rate")
    print(f"Quick suite duration: {quick_result.total_duration:.2f} seconds")