# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multi-agent simulation framework with a FastAPI backend and Godot frontend. The project allows LLM-powered agents to interact in a text adventure game world with real-time visualization.

## Key Architecture

### Backend Structure
- **FastAPI Server** (`backend/main.py`): HTTP endpoints for frontend communication
- **Game Loop** (`backend/game_loop.py`): Main controller managing turn-based agent execution
- **Agent Manager** (`backend/agent_manager.py`): Connects AI agents to game characters using Kani library
- **Text Adventure Framework** (`backend/text_adventure_games/`): Core game engine with locations, items, and actions
- **Schema Definitions** (`backend/config/schema.py`): Pydantic models for API responses and game actions

### Frontend Structure
- **Godot Project** (`frontend/Godot-Multi-Agent-Playground/`): Real-time visualization and interaction
- **Agent Components** (`frontend/.../scenes/characters/agents/`): Visual representation of AI agents
- **HTTP Manager** (`frontend/.../components/http_manager/`): Communication with backend API

### Data Flow
1. Game Loop executes agent turns sequentially
2. Agents use Kani (OpenAI) to select actions based on world state
3. Actions are executed through the text adventure framework
4. Results are converted to AgentActionOutput schema and queued for frontend polling
5. Frontend polls `/agent_act/next` endpoint for latest actions

## Development Commands

### Backend
```bash
# Start backend server
python -m uvicorn backend.main:app --reload

# Run tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_backend_endpoints.py

# Quick API test
python test_api.py

# Run agent goal tests
python run_agent_tests.py

# Run agent goal test suite
python -m pytest tests/agent_goals/
```

### Frontend (Godot)
- Open project: `frontend/Godot-Multi-Agent-Playground/project.godot`
- Run scene: `frontend/Godot-Multi-Agent-Playground/scenes/test/test_scene_multi_agent.tscn`
- Controls: Arrow keys (move), Right-click (move to position), R key (request action)

## Key Dependencies

### Python (Backend)
- `fastapi` - Web framework for HTTP endpoints
- `kani[openai]` - LLM agent framework with OpenAI integration
- `pydantic` - Data validation and serialization
- `uvicorn` - ASGI server
- `python-dotenv` - Environment variable management

### Environment Setup
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Important Implementation Details

### Agent System & Prompt Construction
- Characters are defined in `backend/text_adventure_games/house.py`
- AI agents (KaniAgent) are registered in `backend/game_loop.py:_setup_agents()`
- Agent personas and behaviors are defined during KaniAgent initialization
- Agents use function calling to select actions from available options

#### How Prompts Are Built and Passed to AI Agents

The prompt construction flow follows this pattern:

1. **System Prompt Creation** (`backend/agent/agent_strategies.py:72-94`):
   - Built in `KaniAgent.__init__()` with character name and persona
   - Includes role definition, world interaction instructions, and function calling guidance
   - Example: `"You are {character_name}, a character in a text adventure game. Your persona: {persona}..."`

2. **World State Formatting** (`backend/agent/agent_strategies.py:201-244`):
   - `_format_world_state()` converts game state dict into readable observation text
   - Includes: location, inventory, visible items, characters, exits, and available actions
   - Added to each turn as context for the LLM

3. **Turn Execution Flow**:
   - `AgentManager.execute_agent_turn()` → `KaniAgent.select_action()` → Kani framework
   - World state retrieved via `Game.get_world_state_for_agent()` 
   - Formatted observation + recent actions context sent to LLM
   - Agent uses `@ai_function() submit_command()` for structured action selection

4. **Function Calling Integration**:
   - Kani's `full_round()` method enables function calling with `max_function_rounds=1`
   - Agent must call `submit_command(command: str)` to select actions
   - Command validation against available actions list prevents invalid moves

5. **Message Flow**:
   - Game Loop (`backend/game_loop.py:90-104`) orchestrates agent turns
   - Each agent receives fresh world state perception per turn
   - Results converted to `AgentActionOutput` schema for frontend consumption

The Kani framework handles the low-level LLM communication, prompt assembly, and function call mechanics, while this codebase focuses on world state perception and action validation.

### Game World
- World is built using the house layout in `backend/text_adventure_games/house.py`
- Locations are connected in a grid pattern (Entry -> Kitchen -> Bedroom, etc.)
- Items and containers are placed in specific rooms with properties
- Custom actions are defined in `backend/text_adventure_games/actions/`

### API Endpoints
- `/agent_act/next` - Poll for latest agent actions (removes from queue)
- `/world_state` - Get complete game state
- `/game/events` - Get events since specific ID
- `/game/reset` - Reset entire game state
- `/game/status` - Get current game status

### Schema System
- All actions inherit from base action types with `action_type` discriminator
- `AgentActionOutput` is the primary data structure for frontend communication
- Actions are validated using Pydantic models in `backend/config/schema.py`

## Testing

### Standard Tests
- Backend endpoints: `tests/test_backend_endpoints.py`
- Godot integration: `tests/test_godot_r_key_simulation.py`
- Individual component tests throughout the codebase

### Agent Goal-Based Testing Framework
The project includes a comprehensive testing framework for LLM agents located in `backend/testing/`:

#### Core Components
- **AgentGoalTest** (`backend/testing/agent_goal_test.py`): Define tests with goals, success/failure criteria
- **AgentTestRunner** (`backend/testing/agent_test_runner.py`): Execute tests and analyze results
- **Goal Types** (`backend/testing/goals.py`): LocationGoal, InventoryGoal, InteractionGoal, etc.
- **Criteria** (`backend/testing/criteria.py`): Success/failure conditions and behavior analysis

#### Running Agent Tests
```bash
# Run simple agent tests
python run_agent_tests.py

# Run specific agent test categories
python -m pytest tests/agent_goals/test_navigation.py
python -m pytest tests/agent_goals/test_interactions.py

# Run comprehensive test suite
python tests/agent_goals/test_suite_example.py
```

#### Example Agent Test
```python
test = AgentGoalTest(
    name="navigation_test",
    description="Agent should move from bedroom to kitchen",
    initial_world_state=WorldStateConfig(agent_location="Bedroom"),
    agent_config=AgentConfig(persona="I am helpful and follow directions."),
    goal=LocationGoal(target_location="Kitchen"),
    success_criteria=[LocationCriterion(location="Kitchen")],
    max_turns=10
)

runner = AgentTestRunner()
result = await runner.run_test(test)
```

## Common Development Patterns

### Adding New Agent Actions
1. Define action class in `backend/config/schema.py`
2. Add to `HouseAction` union type
3. Implement action logic in `backend/text_adventure_games/actions/`
4. Register action in house game builder

### Adding New Agents
1. Create KaniAgent instance in `backend/game_loop.py:_setup_agents()`
2. Define character in `backend/text_adventure_games/house.py`
3. Register agent strategy with AgentManager

### Modifying World State
1. Edit locations/items in `backend/text_adventure_games/house.py`
2. Update schema if new properties are needed
3. Ensure frontend can handle new state information

## Environment Variables

- `OPENAI_API_KEY` - Required for LLM agent functionality
- SSL certificate handling is automated for Windows environments