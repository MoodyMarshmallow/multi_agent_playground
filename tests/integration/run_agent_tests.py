#!/usr/bin/env python3
"""
Agent Goal Testing Runner
========================

Simple script to run agent goal tests and see the results.
"""

import asyncio
import sys
import os
import logging

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables from .env file won't be loaded.")

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Configure logging
def setup_logging(debug=False):
    """Setup logging configuration.
    
    Args:
        debug: If True, enable debug level logging for action debugging
    """
    if debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format='[%(name)s] %(levelname)s: %(message)s',
            handlers=[logging.StreamHandler()]
        )
        # Set specific loggers for action debugging
        parsing_logger = logging.getLogger('backend.text_adventure_games.parsing')
        parsing_logger.setLevel(logging.DEBUG)
        
        # Make sure the parsing logger uses the console handler
        if not parsing_logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter('[%(name)s] %(levelname)s: %(message)s'))
            parsing_logger.addHandler(console_handler)
        print("Debug logging enabled for action parsing")
    else:
        # Default logging level
        logging.basicConfig(level=logging.WARNING)

from backend.testing.agent_goal_test import AgentGoalTest
from backend.testing.agent_test_runner import AgentTestRunner
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
    # Check for debug and verbose flags in command line arguments
    debug_mode = '--debug' in sys.argv or '-d' in sys.argv
    verbose_mode = '--verbose' in sys.argv or '-v' in sys.argv
    
    if debug_mode:
        setup_logging(debug=debug_mode)
    else:
        # Use centralized logging configuration
        from backend.log_config import setup_logging as setup_main_logging
        setup_main_logging(verbose=verbose_mode)
    
    print("Agent Goal-Based Testing System")
    print("="*50)
    
    try:
        # Run simple tests
        # await run_simple_test()
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