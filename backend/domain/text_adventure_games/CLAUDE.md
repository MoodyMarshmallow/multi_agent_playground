# Text Adventure Games Module - CLAUDE.md

This module contains the core text adventure game engine that powers the multi-agent simulation framework.

## Overview

The text adventure games module provides a flexible, object-oriented framework for creating interactive text-based worlds where AI agents can navigate, interact with objects, and accomplish goals. It features a modular architecture with separated concerns for world building, command processing, state management, and event handling.

## Architecture Overview

The module has been refactored into a clean, modular structure:

```
text_adventure_games/
├── world/          # World building components
├── command/        # Command processing system  
├── actions/        # Action definitions and logic
├── state/          # Game state management
├── events/         # Event system for frontend
├── things/         # Game entities (items, characters, locations)
├── blocks/         # Environmental blocks and doors
├── capabilities/   # Capability system utilities
├── games.py        # Main Game class with managers
├── house.py        # Legacy world builder (delegates)
└── parsing.py      # Legacy parser (delegates)
```

## Key Components

### Game Class (`games.py`)
Central game coordinator using modular managers:

**Manager Architecture:**
- `world_state_manager` - World state queries and building
- `description_manager` - Location and object descriptions
- `event_manager` - Event queue for frontend communication
- `schema_exporter` - Action to API schema conversion
- `agent_manager` - Character/agent turn management (CharacterManager)

**Core Methods:**
- `add_character(character)` - Add character to game
- `register_agent(character)` - Register character as active agent
- `add_event(event_type, data)` - Add event to frontend queue
- `is_game_over()` - Check win/lose conditions

### World Building (`world/`)
Modular world construction system:

**Components:**
- `layout.py` - Room definitions and connections
- `items.py` - Item creation and placement  
- `characters.py` - Character definitions and setup
- `builder.py` - World building orchestration

**Usage:**
```python
from backend.text_adventure_games.world import build_house_game
game = build_house_game()  # Creates complete game world
```

### Command Processing (`command/`)
Flexible command parsing and processing:

**Components:**
- `parser.py` - Core command parsing and intent detection
- `matcher.py` - Item/object matching utilities

**Features:**
- Natural language command interpretation
- Object name matching with fuzzy logic
- Action discovery and validation
- Error handling and feedback

### Actions System (`actions/`)
Comprehensive action framework:

**Components:**
- `base.py` - Base action classes and interfaces
- `generic.py` - Generic action implementations (move, get, drop, etc.)
- `discovery.py` - Action discovery and availability
- `preconditions.py` - Precondition testing logic
- `descriptions.py` - Action description generation

**Key Actions:**
- Movement: go, move in directions
- Object interaction: get, drop, examine, look
- Advanced: use, activate, open, close, lock, unlock
- Social: talk, give, take

### State Management (`state/`)
Centralized state management:

**Components:**
- `world_state.py` - World state queries and utilities
- `character_manager.py` - Character/agent management for game state
- `descriptions.py` - State description utilities

**Features:**
- Agent world state building
- Location and inventory management
- Turn order and agent registration
- State description formatting

### Events System (`events/`)
Frontend communication system:

**Components:**
- `event_manager.py` - Event generation and queuing
- `schema_export.py` - Schema conversion utilities

**Features:**
- Real-time event queuing for frontend
- Action result conversion to API schemas
- Event filtering and retrieval

### Things System (`things/`)
Game entity definitions:

**Components:**
- `base.py` - Base Thing class with capabilities
- `characters.py` - Character and NPC classes
- `items.py` - Item and consumable classes
- `containers.py` - Container and storage classes
- `locations.py` - Location and room classes
- `objects.py` - Interactive objects and furniture

**Capabilities System:**
Objects implement capability protocols for behavior:
- `Activatable` - Can be turned on/off
- `Openable` - Can be opened/closed
- `Lockable` - Can be locked/unlocked
- `Container` - Can hold items
- `Consumable` - Can be eaten/drunk
- `Examinable` - Provides detailed descriptions

## Integration Points

### With Agent System (`../agent/`)
- Agents control character objects in the game world
- Action results provide feedback to agents
- WorldState queries give agents environmental information

### With FastAPI Backend (`../main.py`)
- Game events sent to frontend via HTTP endpoints
- Schema export converts actions to API responses
- Real-time game state monitoring

### With Testing Framework (`../testing/`)
- World building creates test environments
- Agent behavior testing in controlled scenarios
- Goal-based testing with success criteria

## Development Guidelines

### Adding New Actions
1. Define action class in `actions/generic.py`
2. Implement preconditions and effects
3. Add to action discovery system
4. Update schema definitions in `../config/schema.py`
5. Test with agent goal testing framework

### Creating New Object Types
1. Inherit from appropriate base class in `things/`
2. Implement relevant capability protocols
3. Add to world building in `world/`
4. Define object-specific behaviors
5. Test interactions with various actions

### Extending World Building
1. Modify world components in `world/` directory
2. Update layout for new locations
3. Add items and place in locations
4. Create new characters and NPCs
5. Update builder orchestration

### Adding New Capabilities
1. Define protocol in `capabilities.py`
2. Implement in relevant object classes
3. Add to capability discovery system
4. Create corresponding actions
5. Test with capability-aware actions

## Manager-Based Usage

**Direct Manager Access (Recommended):**
```python
# World state queries
world_state = game.world_state_manager.get_world_state_for_agent(agent)

# Descriptions
description = game.description_manager.describe_full_location()

# Events
events = game.event_manager.get_events_since(last_id)

# Schema export
schema = game.schema_exporter.get_schema()

# Character management
game.agent_manager.register_agent(character)
```

## Legacy Support

The module maintains backward compatibility through delegation:
- `house.py` - Delegates to `world.build_house_game()`
- `parsing.py` - Delegates to `command.CommandParser`

Legacy wrapper methods in Game class have been removed for better performance. Use managers directly.

## Common Patterns

### Game Setup
```python
from backend.text_adventure_games.house import build_house_game

# Create game world
game = build_house_game()

# Register agents
from backend.agent import KaniAgent
agent = KaniAgent("Alice", "I am helpful")
game.agent_manager.register_agent(character)
```

### Action Execution
```python
# Parse and execute command
result = game.parser.parse_command("go north", character=agent)

# Get schema response
schema = game.schema_exporter.get_schema()

# Add event for frontend
game.event_manager.add_event("move", {"agent": agent.name, "direction": "north"})
```

### World State Queries
```python
# Get agent's observable world
state = game.world_state_manager.get_world_state_for_agent(agent)

# Get location description
description = game.description_manager.describe_current_location()

# Check agent inventory
inventory = list(agent.inventory.keys())
```

## Dependencies

- `pydantic` - Data validation and schema definitions
- `typing` - Type hints and complex type definitions
- `abc` - Abstract base classes
- `enum` - Enumerated types
- `dataclasses` - Configuration structures

## Performance Considerations

- Manager-based architecture eliminates wrapper overhead
- Capability discovery caches results
- Action preconditions prevent invalid operations
- Event queuing is asynchronous and non-blocking

## Testing

Use the agent goal-based testing framework:
```python
from backend.testing import AgentGoalTest, LocationGoal

test = AgentGoalTest(
    name="navigation_test",
    goal=LocationGoal(target_location="Kitchen"),
    max_turns=10
)
```

## Future Extensions

The modular architecture supports easy extension:
- New action types through `actions/` system
- Custom world layouts through `world/` modules
- Additional object capabilities through protocol system
- Enhanced AI behaviors through agent integration