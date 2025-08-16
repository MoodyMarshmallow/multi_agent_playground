# Multi-Agent Playground

![Multi-Agent Playground Demo](assets/multi_agent_playground_demo.gif)

A multi-agent simulation framework with LLM-powered agents and Godot frontend visualization. Features a house with multi-stage, interactable objects and items and a visualisation system made in Godot. Made with [Kani](https://github.com/zhudotexe/kani).

## Tech Stack
- **Backend**: FastAPI, Kani (LLM), OpenAI API
- **Frontend**: Godot Engine

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

## Configuration

Agent configurations are externalized to YAML files:

- **`backend/config/llm.yaml`**: LLM engine settings
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

