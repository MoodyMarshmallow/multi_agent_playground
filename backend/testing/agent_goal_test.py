"""
Agent Goal Test
===============

Core test class for defining and executing agent goal tests.
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .criteria import Criterion
from .config import WorldStateConfig, AgentConfig, BehaviorAnalysis
from ...config.schema import AgentActionOutput


@dataclass
class TestResult:
    """Result of running an agent goal test."""
    test_name: str
    success: bool
    duration_seconds: float
    turns_taken: int
    final_state: Dict[str, Any]
    action_sequence: List[AgentActionOutput]
    success_criteria_met: List[str]
    failure_reasons: List[str]
    agent_behavior_analysis: BehaviorAnalysis
    error_message: Optional[str] = None


@dataclass
class TestSuiteResult:
    """Result of running a test suite."""
    suite_name: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    results: List[TestResult]
    total_duration: float
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100.0


class AgentGoalTest:
    """
    Core test class for defining agent goal tests.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        initial_world_state: WorldStateConfig,
        agent_config: AgentConfig,
        success_criteria: List[Criterion],
        failure_criteria: Optional[List[Criterion]] = None,
        max_turns: int = 50,
        timeout_seconds: int = 300
    ):
        self.name = name
        self.description = description
        self.initial_world_state = initial_world_state
        self.agent_config = agent_config
        self.success_criteria = success_criteria
        self.failure_criteria = failure_criteria or []
        self.max_turns = max_turns
        self.timeout_seconds = timeout_seconds
        
        # Add default failure criteria
        from .criteria import TimeoutCriterion, ImpossibleActionCriterion, LoopCriterion
        self.failure_criteria.extend([
            TimeoutCriterion(max_turns=max_turns),
            ImpossibleActionCriterion(),
            LoopCriterion()
        ])
    
    def __str__(self) -> str:
        return f"AgentGoalTest({self.name}): {self.description}"
    
    def __repr__(self) -> str:
        return f"AgentGoalTest(name='{self.name}', criteria={len(self.success_criteria)})"
    
    def get_initial_state(self) -> Dict[str, Any]:
        """Get the initial world state for this test."""
        return {
            "agent_location": self.initial_world_state.agent_location,
            "agent_inventory": self.initial_world_state.agent_inventory.copy(),
            "world_items": self.initial_world_state.world_items.copy(),
            "character_locations": self.initial_world_state.character_locations.copy(),
            "custom_state": self.initial_world_state.custom_state.copy()
        }
    
    def check_success(self, game_state: Dict[str, Any], action_history: List[AgentActionOutput]) -> tuple[bool, List[str]]:
        """
        Check if the test has succeeded.
        
        Returns:
            Tuple of (success, list of criteria met)
        """
        met_criteria = []
        
        # Check success criteria
        for criterion in self.success_criteria:
            if criterion.check(game_state, action_history):
                met_criteria.append(f"Success criterion met: {criterion.describe()}")
        
        # Test succeeds if all success criteria are met
        all_criteria_met = all(criterion.check(game_state, action_history) for criterion in self.success_criteria)
        
        return all_criteria_met, met_criteria
    
    def check_failure(self, game_state: Dict[str, Any], action_history: List[AgentActionOutput]) -> tuple[bool, List[str]]:
        """
        Check if the test has failed.
        
        Returns:
            Tuple of (failed, list of failure reasons)
        """
        failure_reasons = []
        
        for criterion in self.failure_criteria:
            if criterion.check(game_state, action_history):
                failure_reasons.append(f"Failure criterion met: {criterion.describe()}")
        
        return len(failure_reasons) > 0, failure_reasons
    
    def analyze_behavior(self, action_history: List[AgentActionOutput]) -> BehaviorAnalysis:
        """
        Analyze agent behavior during the test.
        """
        analysis = BehaviorAnalysis()
        
        if not action_history:
            return analysis
        
        # Calculate efficiency score (inverse of turns taken, normalized)
        expected_turns = min(10, self.max_turns // 2)  # Reasonable expectation
        actual_turns = len(action_history)
        analysis.efficiency_score = max(0.0, min(1.0, expected_turns / actual_turns))
        
        # Calculate action diversity
        action_types = [action.action.action_type for action in action_history if hasattr(action, 'action')]
        unique_actions = set(action_types)
        if action_types:
            analysis.action_diversity = len(unique_actions) / len(action_types)
        
        # Detect loops
        action_sequence = [action.action.action_type for action in action_history if hasattr(action, 'action')]
        analysis.loop_detection = self._detect_loops(action_sequence)
        
        # Count invalid actions (noops)
        analysis.invalid_actions = [
            f"Turn {i+1}: {action.action.action_type}"
            for i, action in enumerate(action_history)
            if hasattr(action, 'action') and action.action.action_type == "noop"
        ]
        
        # Calculate decision quality score
        invalid_ratio = len(analysis.invalid_actions) / len(action_history) if action_history else 0
        loop_penalty = 0.2 if analysis.loop_detection else 0
        analysis.decision_quality_score = max(0.0, 1.0 - invalid_ratio - loop_penalty)
        
        # Basic reasoning quality assessment
        if analysis.decision_quality_score > 0.8:
            analysis.reasoning_quality = "High - Agent made mostly valid decisions"
        elif analysis.decision_quality_score > 0.6:
            analysis.reasoning_quality = "Medium - Agent made some invalid decisions"
        else:
            analysis.reasoning_quality = "Low - Agent struggled with decision making"
        
        return analysis
    
    def _detect_loops(self, action_sequence: List[str]) -> List[str]:
        """Detect repeated action patterns."""
        loops = []
        
        if len(action_sequence) < 4:
            return loops
        
        # Check for simple repetitions
        for i in range(len(action_sequence) - 3):
            if action_sequence[i] == action_sequence[i+1] == action_sequence[i+2]:
                loops.append(f"Repeated action '{action_sequence[i]}' at positions {i}-{i+2}")
        
        # Check for pattern loops
        for pattern_length in range(2, min(6, len(action_sequence) // 2)):
            for start in range(len(action_sequence) - pattern_length * 2):
                pattern = action_sequence[start:start + pattern_length]
                next_segment = action_sequence[start + pattern_length:start + pattern_length * 2]
                if pattern == next_segment:
                    loops.append(f"Pattern loop detected: {pattern} at position {start}")
        
        return loops