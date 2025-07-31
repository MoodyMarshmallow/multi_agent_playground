# Testing Module - CLAUDE.md

This module contains the agent goal-based testing framework for evaluating LLM agent behavior and decision-making in the text adventure game environment.

## Overview

The testing module provides a comprehensive framework for creating, executing, and analyzing goal-oriented tests for AI agents. It enables systematic evaluation of agent capabilities, behavior patterns, and goal achievement.

## Key Components

### Agent Goal Test (`agent_goal_test.py`)
Core test definition and result structures.

**AgentGoalTest Class:**
```python
@dataclass
class AgentGoalTest:
    name: str
    description: str
    initial_world_state: WorldStateConfig
    agent_config: AgentConfig
    goal: Goal
    success_criteria: List[Criterion]
    failure_criteria: List[Criterion] = field(default_factory=list)
    max_turns: int = 10
    timeout_seconds: int = 60
```

**TestResult Class:**
- `success`: Whether test passed
- `duration_seconds`: Test execution time
- `turns_taken`: Number of agent turns
- `action_sequence`: Complete action history
- `success_criteria_met`: Which success criteria were satisfied
- `failure_reasons`: Why test failed (if applicable)
- `agent_behavior_analysis`: Detailed behavior metrics

### Agent Test Runner (`agent_test_runner.py`)
Executes tests and manages game state.

**AgentTestRunner Class:**
```python
async def run_test(self, test: AgentGoalTest) -> TestResult:
    """Execute a single agent goal test."""

async def run_test_suite(self, tests: List[AgentGoalTest], suite_name: str) -> TestSuiteResult:
    """Execute multiple tests with aggregated results."""
```

**Key Features:**
- Isolated test execution with fresh game states
- Timeout handling and error recovery
- Detailed behavior analysis and metrics
- Action sequence recording and analysis
- Support for both single tests and test suites

### Test Criteria (`criteria.py`)
Success and failure condition definitions.

**Base Criterion Class:**
```python
class Criterion(ABC):
    @abstractmethod
    def check(self, game_state: Dict[str, Any], action_history: List[Any]) -> bool:
        """Check if the criterion is met."""
        pass
```

**Built-in Criteria:**
- `LocationCriterion` - Agent reached specific location
- `InventoryCriterion` - Agent has specific items
- `ActionCriterion` - Agent performed specific actions
- `StateCriterion` - World state conditions
- `BehaviorCriterion` - Agent behavior patterns

### Test Configuration (`config.py`)
Test setup and configuration structures.

**Configuration Classes:**
- `WorldStateConfig` - Initial world state setup
- `AgentConfig` - Agent persona and parameters
- `BehaviorAnalysis` - Behavior metrics and analysis
- `Goal` - Abstract goal definitions

## Test Types and Goals

### Navigation Tests
Test agent movement and pathfinding capabilities:
```python
test = AgentGoalTest(
    name="navigation_test",
    description="Agent should move from bedroom to kitchen",
    initial_world_state=WorldStateConfig(agent_location="Bedroom"),
    agent_config=AgentConfig(persona="I follow directions precisely"),
    goal=LocationGoal(target_location="Kitchen"),
    success_criteria=[LocationCriterion(location="Kitchen")],
    max_turns=10
)
```

### Interaction Tests
Test agent object interaction and manipulation:
```python
test = AgentGoalTest(
    name="item_interaction",
    description="Agent should pick up the apple",
    goal=InventoryGoal(required_items=["apple"]),
    success_criteria=[InventoryCriterion(has_items=["apple"])],
    max_turns=5
)
```

### Behavior Tests
Test agent decision-making and behavior patterns:
```python
test = AgentGoalTest(
    name="exploration_behavior",
    description="Agent should explore systematically",
    goal=ExplorationGoal(min_locations_visited=3),
    success_criteria=[BehaviorCriterion(min_unique_locations=3)],
    max_turns=15
)
```

## Integration Points

### With Agent System (`../agent/`)
- Uses `AgentManager` for agent coordination
- Creates `KaniAgent` instances for testing
- Integrates with agent feedback system

### With Game Framework (`../text_adventure_games/`)
- Creates isolated game instances for each test
- Uses world building system for test setup
- Integrates with game state management

### With Configuration (`../config/`)
- Uses schema definitions for action validation
- Leverages LLM configuration for agent setup
- Integrates with API response structures

## Development Guidelines

### Creating New Tests
1. Define test goal and success criteria
2. Configure initial world state
3. Set agent persona and parameters
4. Specify maximum turns and timeout
5. Add failure criteria if needed

### Adding New Criteria
1. Inherit from `Criterion` base class
2. Implement `check()` method
3. Add descriptive `describe()` method
4. Document expected behavior

### Test Organization
- Group related tests in test suites
- Use descriptive test names and descriptions
- Set appropriate timeouts and turn limits
- Include both positive and negative test cases

## Usage Examples

### Single Test Execution
```python
from backend.testing import AgentTestRunner, AgentGoalTest

runner = AgentTestRunner()
result = await runner.run_test(test)

print(f"Test {result.test_name}: {'PASSED' if result.success else 'FAILED'}")
print(f"Turns taken: {result.turns_taken}")
print(f"Duration: {result.duration_seconds:.2f}s")
```

### Test Suite Execution
```python
tests = [navigation_test, interaction_test, behavior_test]
suite_result = await runner.run_test_suite(tests, "basic_capabilities")

print(f"Suite Results: {suite_result.passed_count}/{suite_result.total_count} passed")
```

### Behavior Analysis
```python
analysis = result.agent_behavior_analysis
print(f"Actions per turn: {analysis.actions_per_turn}")
print(f"Unique locations: {analysis.unique_locations_visited}")
print(f"Failed actions: {analysis.failed_action_count}")
```

## Common Test Patterns

### Goal Achievement Tests
Test if agents can accomplish specific objectives within turn/time limits.

### Robustness Tests
Test agent behavior with invalid commands, edge cases, and error conditions.

### Efficiency Tests
Measure how quickly agents achieve goals and optimize action sequences.

### Behavior Consistency Tests
Verify agents maintain consistent behavior across multiple test runs.

## Running Tests

### Command Line
```bash
# Run specific test categories
python -m pytest backend/testing/

# Run agent goal tests
python tests/integration/run_agent_tests.py

# Run comprehensive test suite
python tests/agent_goals/test_suite_example.py
```

### Programmatic Execution
```python
import asyncio
from backend.testing import AgentTestRunner

async def main():
    runner = AgentTestRunner()
    result = await runner.run_test(my_test)
    return result

result = asyncio.run(main())
```

## Dependencies

- `asyncio` - Asynchronous test execution
- `dataclasses` - Test configuration structures
- `typing` - Type hints and annotations
- Backend agent and game framework modules

## Best Practices

- Keep tests focused on single capabilities
- Use realistic personas and scenarios
- Set appropriate timeouts to prevent hanging
- Include both success and failure cases
- Document expected agent behavior clearly
- Analyze behavior patterns for insights