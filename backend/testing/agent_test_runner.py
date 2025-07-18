"""
Agent Test Runner
================

Executes agent goal tests and provides detailed results.
"""

import asyncio
import time
from typing import Dict, List, Any, Callable, Optional
from copy import deepcopy

from .agent_goal_test import AgentGoalTest, TestResult, TestSuiteResult
from ..text_adventure_games.games import Game
from ..text_adventure_games.house import build_house_game
from ..text_adventure_games.things import Character, Item, Location
from ..agent import AgentManager, KaniAgent
from ..agent.config.schema import AgentActionOutput


class AgentTestRunner:
    """
    Executes agent goal tests and provides detailed results.
    """
    
    def __init__(self, game_builder_func: Callable = build_house_game):
        self.game_builder = game_builder_func
    
    async def run_test(self, test: AgentGoalTest) -> TestResult:
        """
        Run a single agent goal test.
        
        Args:
            test: The AgentGoalTest to execute
            
        Returns:
            TestResult with detailed information about the test execution
        """
        print(f"\n{'='*60}")
        print(f"RUNNING TEST: {test.name}")
        print(f"{'='*60}")
        print(f"Description: {test.description}")
        print(f"Success criteria: {len(test.success_criteria)}")
        print(f"Max turns: {test.max_turns}")
        print(f"{'='*60}")
        
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
                print(f"\n--- Turn {turn + 1} ---")
                
                # Get current game state
                current_state = self._get_current_state(agent_char, game)
                
                # Check for success
                success, success_reasons = test.check_success(current_state, action_history)
                if success:
                    print(f"[SUCCESS] Test PASSED after {turn + 1} turns!")
                    for reason in success_reasons:
                        print(f"  - {reason}")
                    break
                
                # Check for failure
                failed, failure_reasons = test.check_failure(current_state, action_history)
                if failed:
                    print(f"[FAILURE] Test FAILED after {turn + 1} turns!")
                    for reason in failure_reasons:
                        print(f"  - {reason}")
                    break
                
                # Execute agent turn
                try:
                    action_output = await agent_manager.execute_agent_turn(agent_char)
                    if action_output:
                        action_history.append(action_output)
                        print(f"Agent action: {action_output.action.action_type}")
                        if hasattr(action_output.action, 'target'):
                            print(f"  Target: {action_output.action.target}")
                        print(f"  Location: {action_output.current_room}")
                        if action_output.description:
                            print(f"  Result: {action_output.description}")
                    else:
                        print("No action output received")
                        
                except Exception as e:
                    print(f"Error during agent turn: {e}")
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
            print(f"[ERROR] Test ERROR: {e}")
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
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"TEST RESULT: {'PASSED' if success else 'FAILED'}")
        print(f"Duration: {duration:.2f}s")
        print(f"Turns taken: {len(action_history)}")
        print(f"Efficiency score: {behavior_analysis.efficiency_score:.2f}")
        print(f"Decision quality: {behavior_analysis.decision_quality_score:.2f}")
        if behavior_analysis.invalid_actions:
            print(f"Invalid actions: {len(behavior_analysis.invalid_actions)}")
        if behavior_analysis.loop_detection:
            print(f"Loops detected: {len(behavior_analysis.loop_detection)}")
        print(f"{'='*60}")
        
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
        print(f"\n{'='*80}")
        print(f"RUNNING TEST SUITE: {suite_name}")
        print(f"Total tests: {len(tests)}")
        print(f"{'='*80}")
        
        start_time = time.time()
        results = []
        passed = 0
        failed = 0
        
        for i, test in enumerate(tests, 1):
            print(f"\n[{i}/{len(tests)}] Starting test: {test.name}")
            
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
        
        # Print suite summary
        print(f"\n{'='*80}")
        print(f"TEST SUITE COMPLETE: {suite_name}")
        print(f"{'='*80}")
        print(f"Total tests: {suite_result.total_tests}")
        print(f"Passed: {suite_result.passed_tests}")
        print(f"Failed: {suite_result.failed_tests}")
        print(f"Success rate: {suite_result.success_rate:.1f}%")
        print(f"Total duration: {suite_result.total_duration:.2f}s")
        print(f"{'='*80}")
        
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
        game = self.game_builder()
        
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
            item = Item(item_name, f"a {item_name}", f"A {item_name}")
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
    
