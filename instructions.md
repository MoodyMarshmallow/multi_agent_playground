# Agent Goal-Based Testing System Design

## Overview

This document outlines the design for a comprehensive testing system that allows writing tests for LLM agents in the form of goals that agents must accomplish. The system will integrate with the existing multi-agent playground framework and provide observable, measurable tests for agent behavior.

## Architecture Components

### 1. AgentGoalTest Class

The core test definition class that specifies:
- **Initial World State**: How the world should be configured before the test
- **Agent Configuration**: Agent persona, starting location, inventory
- **Goal Definition**: What the agent should accomplish
- **Success Criteria**: Conditions that determine test success
- **Failure Criteria**: Conditions that determine test failure (timeout, impossible actions)
- **Expected Behavior**: Optional patterns of expected intermediate actions

```python
class AgentGoalTest:
    def __init__(self, 
                 name: str,
                 description: str,
                 initial_world_state: WorldStateConfig,
                 agent_config: AgentConfig,
                 goal: AgentGoal,
                 success_criteria: List[SuccessCriterion],
                 failure_criteria: List[FailureCriterion],
                 max_turns: int = 50,
                 timeout_seconds: int = 300):
        ...
```

### 2. Goal Types

Different types of goals agents can be tested against:

#### LocationGoal
- Agent must reach a specific location
- `LocationGoal(target_location="Kitchen", description="Move to the kitchen")`

#### InventoryGoal  
- Agent must acquire/drop specific items
- `InventoryGoal(must_have=["apple", "key"], must_not_have=["trash"])`

#### InteractionGoal
- Agent must interact with specific objects or characters
- `InteractionGoal(target="alex_001", interaction_type="give_item", item="apple")`

#### ActionSequenceGoal
- Agent must perform a sequence of actions
- `ActionSequenceGoal(actions=["go kitchen", "get apple", "go bedroom"])`

#### CustomGoal
- Custom predicate function for complex scenarios
- `CustomGoal(predicate=lambda game_state: custom_validation(game_state))`

### 3. Success/Failure Criteria

#### Success Criteria
- `LocationCriterion(location="Kitchen")` - Agent reaches specific location
- `InventoryCriterion(has_items=["apple"])` - Agent has specific items
- `ActionCriterion(action_type="give_item")` - Agent performs specific action
- `StateCriterion(predicate=lambda state: state.custom_condition)` - Custom state check
- `TimeCriterion(max_turns=10)` - Complete within time limit

#### Failure Criteria
- `TimeoutCriterion(max_turns=50)` - Test times out
- `ImpossibleActionCriterion()` - Agent attempts impossible actions repeatedly
- `LoopCriterion(max_repeats=3)` - Agent gets stuck in action loop
- `StateCriterion(predicate=lambda state: state.failure_condition)` - Custom failure

### 4. AgentTestRunner Class

Executes tests and provides detailed results:

```python
class AgentTestRunner:
    def __init__(self, game_builder_func: Callable = build_house_game):
        self.game_builder = game_builder_func
        
    async def run_test(self, test: AgentGoalTest) -> TestResult:
        """Run a single agent goal test"""
        
    async def run_test_suite(self, tests: List[AgentGoalTest]) -> TestSuiteResult:
        """Run multiple tests and aggregate results"""
        
    def generate_report(self, results: TestSuiteResult) -> str:
        """Generate human-readable test report"""
```

### 5. Test Configuration System

YAML/JSON configuration files for test scenarios:

```yaml
# tests/agent_goals/navigation_tests.yaml
test_suite: "Agent Navigation Tests"
tests:
  - name: "move_to_kitchen"
    description: "Agent should move from bedroom to kitchen"
    initial_world_state:
      agent_location: "Bedroom"
      agent_inventory: []
    agent_config:
      persona: "I am a helpful agent who follows instructions."
      name: "test_agent"
    goal:
      type: "location"
      target_location: "Kitchen"
    success_criteria:
      - type: "location"
        location: "Kitchen"
    max_turns: 10
    
  - name: "collect_apple"
    description: "Agent should find and collect an apple"
    initial_world_state:
      agent_location: "Entry Room"
      world_items:
        Kitchen:
          - name: "apple"
            description: "A red apple"
    goal:
      type: "inventory"
      must_have: ["apple"]
    success_criteria:
      - type: "inventory"
        has_items: ["apple"]
    max_turns: 20
```

### 6. Integration with Existing Framework

#### Game World Setup
- Use existing `build_house_game()` function as base
- Modify world state based on test configuration
- Place agents in specific starting locations
- Add/remove items as needed for test scenarios

#### Agent Management
- Create isolated AgentManager instances for each test
- Use existing KaniAgent class with test-specific personas
- Monitor agent actions through existing AgentActionOutput schema

#### Action Monitoring
- Intercept and log all agent actions
- Track action patterns and decision-making
- Detect action loops and impossible attempts
- Measure decision quality and efficiency

### 7. Test Result Analysis

#### TestResult Class
```python
class TestResult:
    test_name: str
    success: bool
    duration_seconds: float
    turns_taken: int
    final_state: dict
    action_sequence: List[AgentActionOutput]
    success_criteria_met: List[str]
    failure_reasons: List[str]
    agent_behavior_analysis: BehaviorAnalysis
```

#### BehaviorAnalysis Class
```python
class BehaviorAnalysis:
    decision_quality_score: float  # 0-1 scale
    efficiency_score: float  # 0-1 scale
    action_diversity: float  # How varied were the actions
    loop_detection: List[ActionLoop]  # Detected repetitive behavior
    invalid_actions: List[str]  # Actions that failed
    reasoning_quality: str  # Analysis of agent's reasoning
```

## Implementation Strategy

### Phase 1: Core Framework
1. Implement `AgentGoalTest` class with basic goal types
2. Create `AgentTestRunner` with simple test execution
3. Build integration layer with existing game framework
4. Create basic success/failure criteria

### Phase 2: Advanced Features
1. Add complex goal types (sequences, interactions)
2. Implement detailed behavior analysis
3. Add test configuration file support
4. Create comprehensive reporting system

### Phase 3: Test Suite Development
1. Create test suites for different agent capabilities
2. Add performance benchmarking
3. Implement regression testing
4. Add visual test result dashboard

## Usage Examples

### Basic Navigation Test
```python
async def test_agent_navigation():
    test = AgentGoalTest(
        name="move_to_kitchen",
        description="Agent should navigate to kitchen",
        initial_world_state=WorldStateConfig(
            agent_location="Bedroom"
        ),
        agent_config=AgentConfig(
            persona="I am helpful and follow directions.",
            name="nav_test_agent"
        ),
        goal=LocationGoal(target_location="Kitchen"),
        success_criteria=[
            LocationCriterion(location="Kitchen")
        ],
        max_turns=10
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    assert result.success
    assert result.turns_taken <= 5  # Efficient navigation
    assert "Kitchen" in result.final_state.agent_location
```

### Complex Interaction Test
```python
async def test_agent_item_delivery():
    test = AgentGoalTest(
        name="deliver_apple_to_alex",
        description="Agent should find apple and give it to Alex",
        initial_world_state=WorldStateConfig(
            agent_location="Entry Room",
            world_items={"Kitchen": [{"name": "apple", "description": "A red apple"}]},
            character_locations={"alex_001": "Bedroom"}
        ),
        goal=InteractionGoal(
            target="alex_001",
            interaction_type="give_item",
            item="apple"
        ),
        success_criteria=[
            ActionCriterion(action_type="give_item", target="alex_001", item="apple")
        ],
        max_turns=30
    )
    
    result = await runner.run_test(test)
    assert result.success
    assert "apple" in result.action_sequence[-1].action.item
```

## Integration with pytest

The system will integrate with pytest for standard test discovery and execution:

```python
# tests/test_agent_goals.py
import pytest
from backend.testing.agent_goal_test import AgentTestRunner, AgentGoalTest

@pytest.mark.asyncio
async def test_basic_navigation():
    # Test implementation
    pass

@pytest.mark.asyncio 
async def test_complex_interactions():
    # Test implementation
    pass

def test_suite_from_config():
    # Load tests from YAML configuration
    pass
```

## Benefits

1. **Behavioral Validation**: Verify agents can accomplish real-world tasks
2. **Regression Testing**: Ensure agent improvements don't break existing capabilities
3. **Performance Measurement**: Track agent efficiency and decision quality over time
4. **Debugging Support**: Detailed action logs help identify where agents fail
5. **Scalable Testing**: Easy to add new test scenarios as the system grows
6. **Observable Results**: Visual confirmation of agent behavior in the game world

This system provides a comprehensive framework for testing LLM agents in a structured, measurable way while maintaining integration with the existing multi-agent playground architecture.