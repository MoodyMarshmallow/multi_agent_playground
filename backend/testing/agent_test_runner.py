"""
Agent Test Runner
================

Executes agent goal tests and provides detailed results.
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Callable, Optional
from copy import deepcopy

from .agent_goal_test import AgentGoalTest, TestResult, TestSuiteResult
from ..infrastructure.game.game_engine import Game
from ..domain.entities import Character
from ..domain.entities.item import Item
from ..agent import AgentManager, KaniAgent
from ..application.config.world_builder import WorldBuilder
# Import from config directory at project root
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)
from config.schema import AgentActionOutput

# Module-level logger
logger = logging.getLogger(__name__)


class AgentTestRunner:
    """
    Executes agent goal tests and provides detailed results.
    """
    
    def __init__(self, game_builder_func: Optional[Callable] = None):
        self.game_builder = game_builder_func
    
    async def run_test(self, test: AgentGoalTest) -> TestResult:
        """
        Run a single agent goal test.
        
        Args:
            test: The AgentGoalTest to execute
            
        Returns:
            TestResult with detailed information about the test execution
        """
        logger.info(f"RUNNING TEST: {test.name}")
        logger.info(f"Description: {test.description}")
        logger.info(f"Success criteria: {len(test.success_criteria)}")
        logger.info(f"Max turns: {test.max_turns}")
        
        start_time = time.time()
        action_history = []
        error_message = None
        
        try:
            # Build the game world
            game = self._setup_game_world(test)
            
            # Create and configure the test agent  
            agent_char = self._create_test_agent(test, game)
            
            # Create KaniAgent for the character
            kani_agent = KaniAgent(
                character_name=agent_char.name,
                persona=test.agent_config.persona,
                model=test.agent_config.model,
                api_key=test.agent_config.api_key
            )
            
            # Setup agent manager
            agent_manager = AgentManager(game)
            agent_manager.register_agent_strategy(agent_char.name, kani_agent)
            
            # No special goal tracking needed - criteria handle everything
            
            # Main test loop
            for turn in range(test.max_turns):
                logger.info(f"--- Turn {turn + 1} ---")
                
                # Get current game state
                current_state = self._get_current_state(agent_char, game)
                
                # Check for success
                success, success_reasons = test.check_success(current_state, action_history)
                if success:
                    logger.info(f"[SUCCESS] Test PASSED after {turn + 1} turns!")
                    for reason in success_reasons:
                        logger.info(f"  - {reason}")
                    break
                
                # Check for failure
                failed, failure_reasons = test.check_failure(current_state, action_history)
                if failed:
                    logger.warning(f"[FAILURE] Test FAILED after {turn + 1} turns!")
                    for reason in failure_reasons:
                        logger.warning(f"  - {reason}")
                    break
                
                # Execute agent turn
                try:
                    action_output, action_ended_turn = await agent_manager.execute_agent_turn(agent_char)
                    if action_output:
                        action_history.append(action_output)
                        turn_status = " (ended turn)" if action_ended_turn else " (continued turn)"
                        logger.info(f"Agent action: {action_output.action.action_type}{turn_status}")
                        # Check if the action has a target attribute (some actions like LookAction and NoOpAction don't)
                        action = action_output.action
                        target = getattr(action, 'target', None)
                        if target is not None:
                            logger.info(f"  Target: {target}")
                        logger.info(f"  Location: {action_output.current_room}")
                        if action_output.description:
                            logger.info(f"  Result: {action_output.description}")
                    else:
                        logger.warning("No action output received")
                        
                except Exception as e:
                    logger.error(f"Error during agent turn: {e}")
                    error_message = str(e)
                    break
                
                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.1)
            
            # Final state check
            final_state = self._get_current_state(agent_char, game)
            
            # Determine final result
            success, success_reasons = test.check_success(final_state, action_history)
            failed, failure_reasons = test.check_failure(final_state, action_history)
            
            if not success and not failed:
                # Test didn't succeed but also didn't explicitly fail
                failed = True
                failure_reasons = ["Test completed without achieving goal"]
            
        except Exception as e:
            logger.error(f"[ERROR] Test ERROR: {e}")
            error_message = str(e)
            success = False
            failed = True
            failure_reasons = [f"Test error: {e}"]
            success_reasons = []
            final_state = test.get_initial_state()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Analyze behavior
        behavior_analysis = test.analyze_behavior(action_history)
        
        # Create result
        result = TestResult(
            test_name=test.name,
            success=success,
            duration_seconds=duration,
            turns_taken=len(action_history),
            final_state=final_state,
            action_sequence=action_history,
            success_criteria_met=success_reasons,
            failure_reasons=failure_reasons,
            agent_behavior_analysis=behavior_analysis,
            error_message=error_message
        )
        
        # Log summary
        result_level = logging.INFO if success else logging.WARNING
        logger.log(result_level, f"TEST RESULT: {'PASSED' if success else 'FAILED'}")
        logger.info(f"Duration: {duration:.2f}s")
        logger.info(f"Turns taken: {len(action_history)}")
        logger.info(f"Efficiency score: {behavior_analysis.efficiency_score:.2f}")
        logger.info(f"Decision quality: {behavior_analysis.decision_quality_score:.2f}")
        if behavior_analysis.invalid_actions:
            logger.warning(f"Invalid actions: {len(behavior_analysis.invalid_actions)}")
        if behavior_analysis.loop_detection:
            logger.warning(f"Loops detected: {len(behavior_analysis.loop_detection)}")
        
        return result
    
    async def run_test_suite(self, tests: List[AgentGoalTest], suite_name: str = "Agent Test Suite") -> TestSuiteResult:
        """
        Run multiple tests and aggregate results.
        
        Args:
            tests: List of AgentGoalTest instances
            suite_name: Name for the test suite
            
        Returns:
            TestSuiteResult with aggregated information
        """
        logger.info(f"RUNNING TEST SUITE: {suite_name}")
        logger.info(f"Total tests: {len(tests)}")
        
        start_time = time.time()
        results = []
        passed = 0
        failed = 0
        
        for i, test in enumerate(tests, 1):
            logger.info(f"[{i}/{len(tests)}] Starting test: {test.name}")
            
            result = await self.run_test(test)
            results.append(result)
            
            if result.success:
                passed += 1
            else:
                failed += 1
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        suite_result = TestSuiteResult(
            suite_name=suite_name,
            total_tests=len(tests),
            passed_tests=passed,
            failed_tests=failed,
            results=results,
            total_duration=total_duration
        )
        
        # Log suite summary
        logger.info(f"TEST SUITE COMPLETE: {suite_name}")
        logger.info(f"Total tests: {suite_result.total_tests}")
        logger.info(f"Passed: {suite_result.passed_tests}")
        logger.info(f"Failed: {suite_result.failed_tests}")
        logger.info(f"Success rate: {suite_result.success_rate:.1f}%")
        logger.info(f"Total duration: {suite_result.total_duration:.2f}s")
        
        return suite_result
    
    def generate_report(self, results: TestSuiteResult) -> str:
        """
        Generate a human-readable test report.
        
        Args:
            results: TestSuiteResult to generate report for
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("# Agent Goal Test Report")
        report.append("=" * 50)
        report.append(f"Test Suite: {results.suite_name}")
        report.append(f"Total Tests: {results.total_tests}")
        report.append(f"Passed: {results.passed_tests}")
        report.append(f"Failed: {results.failed_tests}")
        report.append(f"Success Rate: {results.success_rate:.1f}%")
        report.append(f"Total Duration: {results.total_duration:.2f}s")
        report.append("")
        
        # Individual test results
        report.append("## Individual Test Results")
        report.append("-" * 30)
        
        for result in results.results:
            status = "PASSED" if result.success else "FAILED"
            report.append(f"### {result.test_name} - {status}")
            report.append(f"Duration: {result.duration_seconds:.2f}s")
            report.append(f"Turns: {result.turns_taken}")
            report.append(f"Efficiency: {result.agent_behavior_analysis.efficiency_score:.2f}")
            report.append(f"Decision Quality: {result.agent_behavior_analysis.decision_quality_score:.2f}")
            
            if result.success:
                report.append("Success Criteria Met:")
                for criterion in result.success_criteria_met:
                    report.append(f"  - {criterion}")
            else:
                report.append("Failure Reasons:")
                for reason in result.failure_reasons:
                    report.append(f"  - {reason}")
            
            if result.error_message:
                report.append(f"Error: {result.error_message}")
            
            report.append("")
        
        return "\n".join(report)
    
    def _setup_game_world(self, test: AgentGoalTest) -> Game:
        """Setup the game world according to test configuration."""
        # Use WorldBuilder with default house configuration for testing
        world_builder = WorldBuilder()
        
        try:
            # Try to use default house world configuration
            # Navigate to project root (from backend/testing/ -> ../.. -> project_root)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            house_config_path = os.path.join(project_root, "config", "worlds", "house.yaml")
            game = world_builder.build_world_from_file(house_config_path)
        except Exception as e:
            logger.error(f"Failed to build world from YAML, falling back to custom game builder: {e}")
            if self.game_builder:
                game = self.game_builder()
            else:
                raise RuntimeError("No game builder available and YAML world building failed")
        
        # Modify world state based on test configuration
        world_state = test.initial_world_state
        
        # Add custom items to locations
        for location_name, items in world_state.world_items.items():
            if location_name in game.locations:
                location = game.locations[location_name]
                for item_data in items:
                    item = Item(
                        name=item_data["name"],
                        description=item_data["description"],
                        examine_text=item_data.get("long_description", item_data["description"])
                    )
                    # Set default properties for items created in tests
                    item.set_property("gettable", True)
                    location.add_item(item)
        
        # Set character locations
        for char_name, location_name in world_state.character_locations.items():
            if char_name in game.characters and location_name in game.locations:
                character = game.characters[char_name]
                new_location = game.locations[location_name]
                
                # Remove from current location
                if character.location:
                    character.location.remove_character(character)
                
                # Add to new location
                new_location.add_character(character)
                character.location = new_location
        
        return game
    
    def _create_test_agent(self, test: AgentGoalTest, game: Game) -> Character:
        """Create and configure the test agent."""
        # Create the character
        agent_char = Character(
            name=test.agent_config.name,
            description=f"Test agent: {test.description}",
            persona=test.agent_config.persona
        )
        
        # Set initial location
        start_location = game.locations.get(test.initial_world_state.agent_location)
        if start_location:
            start_location.add_character(agent_char)
            agent_char.location = start_location
        
        # Add initial inventory
        for item_name in test.initial_world_state.agent_inventory:
            item = Item(item_name, f"{item_name}", f"{item_name}")
            agent_char.add_to_inventory(item)
        
        # Add to game
        game.add_character(agent_char)
        
        return agent_char
    
    def _get_current_state(self, agent: Character, game: Game) -> Dict[str, Any]:
        """Get the current game state."""
        return {
            "agent_location": agent.location.name if agent.location else None,
            "agent_inventory": list(agent.inventory.keys()),
            "visible_items": [item.name for item in agent.location.items.values()] if agent.location else [],
            "visible_characters": [char.name for char in agent.location.characters.values() if char.name != agent.name] if agent.location else [],
            "available_exits": list(agent.location.connections.keys()) if agent.location else []
        }
    
