# Multi-Agent Playground

![Multi-Agent Playground Demo](assets/multi_agent_playground_demo.gif)

A multi-agent simulation framework with LLM-powered agents and real-time Godot frontend visualization. Features turn-based agent execution in a text adventure world with comprehensive testing.

## Features
- **LLM Agents**: Kani framework with OpenAI integration and YAML configuration
- **Real-time Visualization**: Godot Engine 4.x frontend
- **Agent Goal Testing**: Comprehensive behavioral testing framework
- **Text Adventure Engine**: Modular game world with locations, items, and actions

## Quick Start

### 1. Setup
```bash
git clone <repository-url>
cd multi_agent_playground

# Install dependencies with uv (recommended)
uv sync

# Or use pip
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### 3. Run Backend
```bash
# Start server (recommended)
uv run python -m uvicorn backend.main:app --reload

# Alternative manual startup
uv run python tests/manual/run_backend.py
```

### 4. Run Frontend (Optional)
1. Install [Godot Engine 4.x](https://godotengine.org/)
2. Open `frontend/Godot-Multi-Agent-Playground/project.godot`
3. Run scene `scenes/test/test_scene_multi_agent.tscn`

**Controls**: Arrow keys (move), Right-click (move to position), R key (request action)

## Configuration

Agent configurations are now externalized to YAML files:

- **`backend/config/llm.yaml`**: LLM engine settings (OpenAI, Anthropic)
- **`backend/config/agents.yaml`**: Agent personas and preferences
- **`backend/config/prompts.yaml`**: System prompt templates
- **`backend/config/defaults.yaml`**: Fallback values

## Testing

All tests use `uv run` for proper dependency management:

```bash
# Run all tests
uv run python -m pytest tests/

# Backend API tests
uv run python -m pytest tests/test_backend_endpoints.py

# Agent behavior tests
uv run python -m pytest tests/integration/test_agent_runner.py

# Integration tests
uv run python -m pytest tests/integration/

# Quick API test
uv run python tests/integration/test_api.py
```

### Agent Goal Testing
Test LLM agent capabilities with goal-based scenarios:
- **Navigation**: Pathfinding and movement
- **Interaction**: Object manipulation and world interaction  
- **Behavior**: Decision-making and goal achievement

## API Endpoints

Once running on http://localhost:8000:
- **Documentation**: `/docs`
- **Agent Actions**: `/agent_act/next`
- **World State**: `/world_state`  
- **Game Events**: `/game/events`

## Tech Stack
- **Backend**: FastAPI, Kani (LLM), OpenAI API, Pydantic, YAML configs
- **Frontend**: Godot Engine 4.x
- **Testing**: pytest, pytest-asyncio, agent goal-based testing
- **Package Management**: uv (recommended) or pip

## Project Structure
```
backend/           # FastAPI server & LLM agents
├── config/        # YAML configurations  
├── agent/         # Agent management
├── testing/       # Goal-based test framework
└── text_adventure_games/  # Game engine

frontend/          # Godot visualization
tests/             # Test suites
data/              # Agent memory & world data
```

