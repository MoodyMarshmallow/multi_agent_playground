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
- **house.py**: Main world definition with locations, items, and characters
- **actions/**: Action implementations (generic, location-specific, thing-specific)
- **things/**: Game entities (locations, items, containers, characters)
- **blocks/**: Environmental blocks and doors
- **capabilities.py**: Entity capability system
- **games.py**: Game builder and world initialization

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
3. Implement logic in `text_adventure_games/actions/`
4. Register in house.py if location-specific

### Adding New Agents
1. Create KaniAgent instance in `game_loop.py:_setup_agents()`
2. Define character in `text_adventure_games/house.py`
3. Configure persona and behavior during initialization

### Modifying World
1. Edit world structure in `text_adventure_games/house.py`
2. Update schema.py if new properties needed
3. Ensure action compatibility with world changes

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
python -m uvicorn backend.main:app --reload

# Run tests
python -m pytest tests/

# Test API
python test_api.py

# Agent goal tests
python run_agent_tests.py
```