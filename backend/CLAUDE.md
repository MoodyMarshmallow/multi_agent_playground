# Backend Module - CLAUDE.md

This file provides guidance to Claude Code when working with the backend module of the multi-agent simulation framework.

## Module Overview

The backend module contains the core server infrastructure, AI agent management, and text adventure game engine for the multi-agent simulation framework.

## Key Components

### Core Server (`main.py`)
- FastAPI application with CORS enabled
- HTTP endpoints for frontend communication
- Health check and game state endpoints

### Game Loop (`game_loop.py`)
- Main controller managing turn-based agent execution
- Agent registration and world state initialization
- Sequential agent turn processing with action result feedback

### Agent System (`agent/`)
- **agent_strategies.py**: KaniAgent implementation with OpenAI integration
- **manager.py**: AgentManager handling agent turn execution and action result storage
- **config/**: Agent-specific configuration files

### Configuration (`config/`)
- **schema.py**: Pydantic models for API responses and game actions
- **llm_config.py**: LLM configuration and API key management

### Text Adventure Framework (`text_adventure_games/`)
**Reorganized modular structure for better maintainability:**

- **world/**: World building components
  - `layout.py`: Room definitions and connections
  - `items.py`: Item creation and placement
  - `characters.py`: Character definitions and setup
  - `builder.py`: World building orchestration
- **command/**: Command processing system
  - `parser.py`: Core command parsing and intent detection
  - `matcher.py`: Item/object matching utilities
- **actions/**: Enhanced action system
  - `discovery.py`: Action discovery and availability
  - `preconditions.py`: Precondition testing logic
  - `descriptions.py`: Action description generation
  - `generic.py`: Generic action implementations
- **state/**: State management system
  - `world_state.py`: World state queries and utilities
  - `character_manager.py`: Character/agent management for game state
  - `descriptions.py`: State description utilities
- **events/**: Event system
  - `event_manager.py`: Event generation and queuing
  - `schema_export.py`: Schema conversion utilities
- **capabilities/**: Capability system utilities
  - `discovery.py`: Capability discovery logic
- **things/**: Game entities (locations, items, containers, characters)
- **blocks/**: Environmental blocks and doors
- **capabilities.py**: Entity capability protocols
- **games.py**: Main Game class with integrated managers
- **house.py**: Legacy world builder (delegates to world/)
- **parsing.py**: Legacy parser (delegates to command/)

### Testing Framework (`testing/`)
- **agent_goal_test.py**: Define agent goal-based tests
- **agent_test_runner.py**: Execute and analyze agent test results
- **criteria.py**: Success/failure conditions for agent behavior
- **config.py**: Test configuration management

## Important Implementation Details

### Agent System Architecture
- Uses Kani framework for LLM integration (consult https://kani.readthedocs.io/en/latest/index.html)
- Agents receive action results from previous turn (not full world state)
- Function calling via `@ai_function() submit_command(command: str)`
- Agents must use look action to observe environment after initialization

### Action System
- All actions inherit from base types with `action_type` discriminator
- Actions validated using Pydantic models in `schema.py`
- Custom actions defined in `text_adventure_games/actions/`

### Data Flow
1. Game loop executes agent turns sequentially
2. Agents receive previous action results as feedback
3. Agent uses Kani to select next action via function calling
4. Actions executed through text adventure framework
5. Results converted to AgentActionOutput schema for frontend

## Development Guidelines

### Adding New Actions
1. Define action class in `config/schema.py`
2. Add to appropriate action union type
3. Implement logic in `text_adventure_games/actions/generic.py`
4. Update discovery logic if needed

### Adding New Agents
1. Create KaniAgent instance in `game_loop.py:_setup_agents()`
2. Define character in `text_adventure_games/world/characters.py`
3. Configure persona and behavior during initialization

### Modifying World
1. Edit world structure in `text_adventure_games/world/`
   - Locations: `layout.py`
   - Items: `items.py`
   - Characters: `characters.py`
2. Update schema.py if new properties needed
3. Update world builder in `world/builder.py`

### Working with New Modular Structure
- **World Building**: Use `world/` modules for creating rooms, items, characters
- **Command Processing**: Extend `command/` modules for new parsing logic
- **State Management**: Use `state/` modules for game state queries
- **Events**: Use `events/` modules for frontend communication
- **Backward Compatibility**: Legacy modules (`house.py`, `parsing.py`) still work

### Manager-Based Architecture
The Game class now uses specialized managers instead of monolithic wrapper methods:
- **Direct Manager Access**: Use `game.world_state_manager.get_world_state_for_agent()` instead of removed `game.get_world_state_for_agent()`
- **Description Management**: Use `game.description_manager.describe_full_location()` instead of removed `game.describe()`
- **Event Management**: Use `game.event_manager.get_events_since()` instead of removed `game.get_events_since()`
- **Schema Export**: Use `game.schema_exporter.get_schema()` instead of removed `game.get_schema()`
- **Character Management**: Use `game.agent_manager` (which is a `CharacterManager` instance) for managing game character turns and registration

This improves performance by eliminating wrapper overhead and provides clearer separation of concerns.

### Testing Agents
- Use agent goal-based testing framework in `testing/`
- Define tests with goals, success criteria, and behavior analysis
- Run tests via `python -m pytest tests/agent_goals/`

## Key Dependencies
- `fastapi` - Web framework
- `kani[openai]` - LLM agent framework (REQUIRED for agent features)
- `pydantic` - Data validation
- `uvicorn` - ASGI server
- `python-dotenv` - Environment variables

## Environment Requirements
- `OPENAI_API_KEY` - Required for LLM agent functionality
- SSL certificate handling automated for Windows

## Common Commands
```bash
# Start server
python -m uvicorn backend.interfaces.http.main:app --reload

# Run tests
python -m pytest tests/

# Test API
python test_api.py

# Agent goal tests
python run_agent_tests.py
```