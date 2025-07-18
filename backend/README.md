# Multi-Agent Playground Backend

This is the combined backend for the Multi-Agent Playground that integrates:

- **Text Adventure Games Framework**: A complete game engine with locations, characters, items, and actions
- **Multi-Agent Support**: Turn-based system where multiple AI agents can act independently  
- **Kani LLM Integration**: OpenAI-powered intelligent agents using the Kani library
- **HTTP API**: FastAPI endpoints for frontend communication
- **Event System**: Real-time event tracking for frontend visualization

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   HTTP API       │    │  Game Engine    │
│   (Godot)       │◄──►│   (FastAPI)      │◄──►│  (Text Adv.)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                         │
                                ▼                         ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Game Controller │    │  Agent Manager  │
                       │  (Orchestrator)  │◄──►│  (Multi-Agent)  │
                       └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │   Kani Agents   │
                                               │   (LLM-powered) │
                                               └─────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
pip install fastapi uvicorn kani openai python-dotenv
```

### 2. Set Up Environment

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run the Server

```bash
# From project root
python run_backend.py

# Or directly
python -m backend.main
```

### 4. Test the API

Visit `http://localhost:8000/docs` for interactive API documentation.

Key endpoints:
- `GET /agents/init` - Get all agents for frontend initialization
- `POST /agent_act/plan` - Plan actions for agents  
- `POST /agent_act/confirm` - Confirm action execution
- `GET /objects` - Get all interactive objects
- `GET /game/events` - Get events for frontend visualization

## Key Components

### Game Controller (`game_controller.py`)

The main orchestrator that:
- Initializes the game world (house environment)
- Manages agent lifecycle and turn ordering
- Handles action planning and execution  
- Tracks events for frontend synchronization
- Provides world state and perception data

### Agent Manager (`agent_manager.py`)

Manages AI agents:
- **AgentStrategy Protocol**: Interface for different agent types
- **KaniAgent**: LLM-powered agents using OpenAI
- **SimpleRandomAgent**: Basic random agents for testing
- **Turn Management**: Coordinates agent actions
- **World State**: Provides rich context to agents

### Text Adventure Framework (`text_adventure_games/`)

Complete game engine with:
- **Locations**: Rooms with connections and descriptions
- **Characters**: Players and NPCs with inventories 
- **Items**: Interactive objects with properties
- **Actions**: Movement, interaction, communication
- **Parser**: Natural language command interpretation

### HTTP API (`main.py`)

FastAPI endpoints that maintain compatibility with the original backend:
- Same endpoint structure as old backend
- Compatible request/response formats
- Support for batched agent actions
- Real-time event streaming

## Agent Development

### Creating Custom Agents

```python
from backend.agent_manager import AgentStrategy

class MyAgent(AgentStrategy):
    async def select_action(self, world_state: dict) -> str:
        # Analyze world_state and return a command
        available_actions = world_state['available_actions']
        return available_actions[0]['command']  # Pick first action

# Register with agent manager
agent_manager.register_agent_strategy("my_character", MyAgent())
```

### World State Format

Agents receive rich world state information:

```python
{
    'agent_name': 'alex_001',
    'location': {
        'name': 'Living Room',
        'description': 'A cozy living room...'
    },
    'inventory': ['book', 'apple'],
    'visible_items': [
        {'name': 'couch', 'description': 'a comfortable couch'}
    ],
    'visible_characters': [
        {'name': 'alan_002', 'description': 'Alan, a thoughtful person'}
    ],
    'available_exits': ['north', 'east'],
    'available_actions': [
        {'command': 'go north', 'description': 'Move north to Kitchen'},
        {'command': 'get book', 'description': 'Pick up the mystery novel'}
    ]
}
```

## Game World

The default game world is a house with:

- **Living Room**: Starting location with couch, TV, and book
- **Kitchen**: Modern kitchen with refrigerator and apple
- **Bedroom**: Peaceful bedroom with bed and dresser  
- **Bathroom**: Clean bathroom with bathtub and towel
- **Dining Room**: Formal dining room with table

Characters:
- **Player**: Main character (controlled by frontend)
- **Alex** (alex_001): Friendly, social character in bedroom
- **Alan** (alan_002): Quiet, thoughtful character in kitchen

## Testing

Run the test suite to verify everything works:

```bash
python backend/test_backend.py
```

This tests:
- Game initialization
- Agent management  
- Action planning
- Event system
- Multi-agent interactions

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Required for Kani LLM agents
- `PYTHONPATH`: Automatically set by startup scripts

### Agent Personas

Modify agent personalities in `game_controller.py`:

```python
alex_agent = KaniAgent(
    character_name="alex_001",
    persona="I am Alex, a friendly person who loves to explore and help others..."
)
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running from the project root
2. **OpenAI API Errors**: Check your API key in `.env` file
3. **Port Already in Use**: Change port in `run_backend.py`

### Debug Mode

Enable debug logging by modifying `run_backend.py`:

```python
uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug", reload=True)
```

### Fallback Agents

If Kani agents fail (e.g., no API key), the system automatically falls back to SimpleRandomAgent for testing.

## Extensions

### Adding New Actions

1. Create action class in `text_adventure_games/actions/`
2. Register in game's custom_actions
3. Add to parser's action recognition

### Custom Game Worlds

Replace `_build_house_environment()` in GameController to create different environments.

### Additional Agent Types

Implement the `AgentStrategy` protocol to create new agent behaviors:
- Rule-based agents
- Planning agents  
- Multi-LLM agents
- Human-in-the-loop agents

## API Reference

See the auto-generated API docs at `http://localhost:8000/docs` when the server is running.

Key schemas are defined in `config/schema.py`:
- `AgentSummary`: Agent metadata for frontend (room-based locations only)
- `AgentPerception`: What agents can observe
- `AgentActionInput/Output`: Action requests and responses
- `BackendAction`: Different action types (move, chat, interact, perceive)

## Contributing

This backend follows the refactoring plan in `docs/REFACTOR.md`. When adding features:

1. Maintain compatibility with existing HTTP endpoints
2. Use the text adventure framework for game logic
3. Keep agent strategies modular and testable
4. Update event system for frontend visualization
5. Add comprehensive tests 