# Tests Module - CLAUDE.md

This file provides guidance to Claude Code when working with the tests module of the multi-agent simulation framework.

## Module Overview

The tests module contains comprehensive testing infrastructure including backend endpoint tests, Godot integration tests, and advanced agent goal-based testing framework.

## Directory Structure

### Backend Integration Tests
- **test_backend_endpoints.py**: HTTP endpoint validation and API response testing
- **test_godot_r_key_simulation.py**: Godot frontend integration and R-key simulation testing

### Agent Goal-Based Testing (`agent_goals/`)
Advanced LLM agent behavior testing framework:

#### Core Test Files
- **agent_movement_test.py**: Agent navigation and movement behavior tests
- **test_capabilities.py**: Agent capability and action execution tests
- **test_smart_objects.py**: Agent interaction with complex objects and containers

#### Example Test Suites (`examples/`)
- **test_interactions.py**: Agent-to-agent and agent-to-environment interaction tests
- **test_navigation.py**: Comprehensive navigation and pathfinding tests
- **test_suite_example.py**: Complete test suite demonstration

## Testing Framework Architecture

### Agent Goal Testing System
Located in `backend/testing/`, the framework provides:
- **AgentGoalTest**: Define tests with goals and success criteria
- **AgentTestRunner**: Execute tests and analyze results
- **Goal Types**: LocationGoal, InventoryGoal, InteractionGoal
- **Criteria System**: Success/failure conditions and behavior analysis

### Test Execution Flow
1. Define agent test with goal and criteria
2. Initialize world state and agent configuration
3. Execute agent turns within max turn limit
4. Analyze results against success criteria
5. Generate detailed test reports

## Development Guidelines

### Running Tests

#### Standard Tests
```bash
# Run all tests
python -m pytest tests/

# Backend endpoints
python -m pytest tests/test_backend_endpoints.py

# Godot integration
python -m pytest tests/test_godot_r_key_simulation.py
```

#### Agent Goal Tests
```bash
# Run simple agent tests
python run_agent_tests.py

# Specific test categories
python -m pytest tests/agent_goals/test_navigation.py
python -m pytest tests/agent_goals/test_interactions.py

# Example test suite
python tests/agent_goals/test_suite_example.py
```

### Writing New Tests

#### Backend Endpoint Tests
1. Add test functions to `test_backend_endpoints.py`
2. Use FastAPI TestClient for HTTP requests
3. Validate response schemas and status codes
4. Test error conditions and edge cases

#### Agent Goal Tests
1. Import testing framework from `backend.testing`
2. Define test with clear goal and success criteria
3. Configure initial world state and agent persona
4. Set appropriate max_turns limit
5. Use specific goal types (LocationGoal, InventoryGoal, etc.)

### Example Agent Test Structure
```python
from backend.testing import AgentGoalTest, AgentTestRunner
from backend.testing.goals import LocationGoal
from backend.testing.criteria import LocationCriterion

test = AgentGoalTest(
    name="navigation_test",
    description="Agent should move from bedroom to kitchen",
    initial_world_state=WorldStateConfig(agent_location="Bedroom"),
    agent_config=AgentConfig(persona="I follow directions carefully."),
    goal=LocationGoal(target_location="Kitchen"),
    success_criteria=[LocationCriterion(location="Kitchen")],
    max_turns=10
)

runner = AgentTestRunner()
result = await runner.run_test(test)
```

## Test Categories

### Unit Tests
- Individual component functionality
- Action execution validation
- Schema validation and serialization

### Integration Tests
- Backend API endpoint functionality
- Frontend-backend communication
- Agent-world interaction

### Behavioral Tests
- Agent goal achievement
- Multi-agent interactions
- Complex scenario execution

### Performance Tests
- Response time validation
- Resource usage monitoring
- Concurrent agent execution

## Testing Best Practices

### Agent Tests
- Use realistic personas and goals
- Set appropriate turn limits (typically 5-20 turns)
- Test both success and failure scenarios
- Include edge cases and boundary conditions

### Backend Tests
- Mock external dependencies (OpenAI API)
- Test all HTTP methods and endpoints
- Validate error responses and status codes
- Use test fixtures for consistent setup

### Integration Tests
- Test complete user workflows
- Validate data persistence
- Check frontend-backend synchronization
- Test real-time updates and polling

## Common Test Patterns

### Agent Movement Testing
- Test navigation between all locations
- Validate pathfinding and obstacle avoidance
- Check location-specific action availability

### Interaction Testing
- Agent-to-agent communication
- Object manipulation and container interactions
- Action chaining and complex behaviors

### Error Handling
- Invalid action attempts
- Network connectivity issues
- LLM API failures and retries

## Debugging Tests

### Agent Test Debugging
- Review agent conversation logs
- Check action results and feedback
- Analyze turn-by-turn decision making
- Verify goal and criteria definitions

### Backend Test Debugging
- Check API response details
- Validate request formatting
- Review server logs and error messages
- Test individual endpoints in isolation

## Continuous Integration

### Test Requirements
- All tests must pass before merge
- New features require corresponding tests
- Agent tests should cover realistic scenarios
- Performance benchmarks must be maintained

### Test Data Management
- Use separate test data directories
- Clean up test state between runs
- Mock external API calls appropriately
- Preserve test logs for debugging