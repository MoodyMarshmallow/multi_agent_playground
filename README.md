# Multi-Agent Playground

![Multi-Agent Playground Demo](assets/multi_agent_playground_demo.gif)

A multi-agent simulation framework with LLM-powered agents and real-time Godot frontend visualization. Features a turn-based agent execution in a text adventure game world with comprehensive testing framework.

## Project Structure
- **`backend/`**: FastAPI server, LLM agents (Kani), text adventure framework
- **`frontend/Godot-Multi-Agent-Playground/`**: Real-time visualization and interaction
- **`tests/`**: Comprehensive testing including agent goal-based tests
- **`data/`**: Game world and agent configurations

## Tech Stack
- **Backend**: FastAPI, Kani (LLM framework), OpenAI API, Pydantic
- **Frontend**: Godot Engine 4.x
- **Testing**: Agent goal-based testing framework, pytest
- **Logging**: Centralized logging with verbose mode support

---
## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd multi_agent_playground
```

### 2. Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure OpenAI API
```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
# Or create a .env file with:
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### 4. Backend Server

#### Option A: Standard uvicorn (Recommended)
```bash
# Clean output (errors/warnings only)
python -m uvicorn backend.interfaces.http.main:app --reload

# Verbose mode (detailed logging)
# Linux/Mac:
VERBOSE=true python -m uvicorn backend.interfaces.http.main:app --reload
# Windows:
set VERBOSE=true && python -m uvicorn backend.interfaces.http.main:app --reload

# Custom port with verbose mode
VERBOSE=true python -m uvicorn backend.interfaces.http.main:app --reload --port 8001
```

#### Option B: Direct Python (Alternative)
```bash
# With command line arguments
python backend/main.py --verbose --reload --port 8000

# User-friendly startup script
python tests/manual/run_backend.py --verbose
```

### 5. Frontend Setup (Godot)
1. **Install Godot Engine 4.x** (version 4.0 or later)
2. **Open Project**: `frontend/Godot-Multi-Agent-Playground/project.godot`
3. **Run Test Scene**: `scenes/test/test_scene_multi_agent.tscn`

#### Frontend Controls:
- **Arrow Keys**: Move agent manually
- **Right-click**: Move agent to position
- **R Key**: Request next action from backend

## Usage Examples

### Backend Server
```bash
# Standard uvicorn (clean output)
python -m uvicorn backend.interfaces.http.main:app --reload

# Uvicorn with verbose logging
VERBOSE=true python -m uvicorn backend.interfaces.http.main:app --reload

# Direct Python with arguments
python backend/main.py --verbose --reload
```

### Text Adventure Demo
```bash
# Interactive text game (clean)
python backend/text_game_demo.py

# With verbose debugging
python backend/text_game_demo.py --verbose
```

### Agent Testing
```bash
# Run agent goal tests (clean)
python tests/integration/run_agent_tests.py

# With verbose test progress
python tests/integration/run_agent_tests.py --verbose

# Full test suite
python -m pytest tests/agent_goals/
```

## Logging System

### Default Mode (Clean Output)
- Shows only **errors** and **warnings**
- Perfect for production and clean development
- Critical issues always visible

### Verbose Mode (`--verbose` flag)
- Shows **detailed operational information**
- Agent decisions and actions
- Game flow and turn progression
- Test execution progress
- API request/response details

### Debug Logging
- All messages logged to `debug.log` file
- Includes detailed LLM interactions
- Function call debugging
- Internal state information

### API Endpoints
Once the backend is running, access:
- **API Documentation**: http://localhost:8000/docs
- **Agent Actions**: http://localhost:8000/agent_act/next
- **World State**: http://localhost:8000/world_state
- **Game Events**: http://localhost:8000/game/events

## Testing Framework

### Agent Goal Testing
The project includes a comprehensive agent testing framework:

```bash
# Run navigation tests
python -m pytest tests/agent_goals/test_navigation.py

# Run interaction tests  
python -m pytest tests/agent_goals/test_interactions.py

# Custom agent test runner
python tests/integration/run_agent_tests.py --verbose
```

### Backend Endpoint Testing
```bash
# Test Phase 2 refactored backend endpoints (recommended)
PYTHONPATH=. python tests/test_backend_endpoints_phase2.py

# Legacy endpoint testing
python tests/test_backend_endpoints.py

# Run pytest
python -m pytest tests/
```

### Test Categories
- **Navigation Tests**: Agent pathfinding and movement
- **Interaction Tests**: Object manipulation and world interaction
- **Behavior Tests**: Decision-making and goal achievement
- **Integration Tests**: End-to-end system validation
- **Architecture Tests**: Phase 2 refactoring validation

