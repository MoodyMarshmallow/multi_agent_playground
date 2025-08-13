# Phase 7: Clean Architecture Reorganization Plan

## Overview
After completing Phase 6 cleanup, we need to properly organize the remaining `backend/text_adventure_games/` components into the clean architecture layers established in earlier phases. This will complete the hexagonal architecture transformation.

## Current State Analysis

### Remaining in `backend/text_adventure_games/`
```
text_adventure_games/
├── actions/          # Action system - DOMAIN LOGIC
├── capabilities.py   # Entity protocols - DOMAIN LOGIC  
├── command/          # Command parsing - APPLICATION LOGIC
├── events/           # Event management - INFRASTRUCTURE/APPLICATION
├── games.py          # Core Game class - INFRASTRUCTURE
├── state/            # State management - APPLICATION/INFRASTRUCTURE
└── things/           # Entity classes - DOMAIN LOGIC
```

## Target Architecture Mapping

### 🎯 **Domain Layer** (`backend/domain/`)
**Pure business logic, no external dependencies**

```
domain/
├── entities/
│   ├── thing.py              # From things/base.py
│   ├── character.py          # From things/characters.py
│   ├── item.py               # From things/items.py  
│   ├── location.py           # From things/locations.py
│   ├── container.py          # From things/containers.py
│   └── object.py             # From things/objects.py
├── value_objects/
│   └── capabilities.py       # From capabilities.py (protocols)
├── services/
│   ├── action_executor.py    # Core action execution logic
│   └── world_state_service.py # Pure world state logic
└── actions/
    ├── base_action.py        # From actions/base.py
    ├── movement_actions.py   # Movement-related actions
    ├── interaction_actions.py # Object interaction actions
    └── state_actions.py      # State change actions
```

### 🏗️ **Application Layer** (`backend/application/`)
**Use cases and coordination, already partially populated**

```
application/
├── services/
│   ├── game_orchestrator.py      # ✅ Already exists
│   ├── command_processor.py      # From command/parser.py
│   └── action_discovery.py       # From actions/discovery.py
├── config/
│   ├── world_builder.py          # ✅ Already exists
│   └── agent_strategy_loader.py  # ✅ Already exists
└── handlers/
    ├── command_handler.py         # Command processing coordination
    └── state_query_handler.py     # From state/world_state.py
```

### 🔧 **Infrastructure Layer** (`backend/infrastructure/`)
**External concerns and implementations**

```
infrastructure/
├── game/
│   ├── game_engine.py            # From games.py (core Game class)
│   ├── parser_adapter.py         # From command/matcher.py
│   └── description_engine.py     # From state/descriptions.py
├── events/
│   ├── async_event_bus.py        # ✅ Already exists
│   ├── event_manager.py          # From events/event_manager.py
│   └── schema_exporter.py        # From events/schema_export.py
├── agents/
│   └── kani_agent.py             # ✅ Already exists
└── persistence/
    └── state_manager.py          # From state/character_manager.py
```

### 🌐 **Interfaces Layer** (`backend/interfaces/`)
**External interfaces, already established**

```
interfaces/
└── http/
    └── main.py                   # ✅ Already exists
```

## Migration Strategy

### **Phase 7A: Domain Entity Migration** 
**Priority: High | Risk: Medium**

1. **Move Entity Classes**
   ```bash
   # Create domain entity structure
   mkdir -p backend/domain/entities
   mkdir -p backend/domain/value_objects  
   mkdir -p backend/domain/actions
   
   # Move and rename entity files
   mv backend/text_adventure_games/things/base.py -> backend/domain/entities/thing.py
   mv backend/text_adventure_games/things/characters.py -> backend/domain/entities/character.py
   mv backend/text_adventure_games/things/items.py -> backend/domain/entities/item.py
   mv backend/text_adventure_games/things/locations.py -> backend/domain/entities/location.py
   mv backend/text_adventure_games/things/containers.py -> backend/domain/entities/container.py
   mv backend/text_adventure_games/things/objects.py -> backend/domain/entities/object.py
   ```

2. **Move Capabilities and Actions**
   ```bash
   mv backend/text_adventure_games/capabilities.py -> backend/domain/value_objects/capabilities.py
   mv backend/text_adventure_games/actions/base.py -> backend/domain/actions/base_action.py
   mv backend/text_adventure_games/actions/generic.py -> backend/domain/actions/interaction_actions.py
   # Split other action files by domain concern
   ```

3. **Update Import Paths**
   - Update all imports from `text_adventure_games.things` -> `domain.entities`
   - Update all imports from `text_adventure_games.capabilities` -> `domain.value_objects.capabilities`
   - Update all imports from `text_adventure_games.actions` -> `domain.actions`

### **Phase 7B: Application Service Migration**
**Priority: Medium | Risk: Low**

1. **Move Command Processing**
   ```bash
   mv backend/text_adventure_games/command/parser.py -> backend/application/services/command_processor.py
   mv backend/text_adventure_games/actions/discovery.py -> backend/application/services/action_discovery.py
   mv backend/text_adventure_games/state/world_state.py -> backend/application/handlers/state_query_handler.py
   ```

2. **Create Application Services**
   - Extract pure business logic from command processing
   - Create use case handlers for complex operations
   - Maintain separation from infrastructure concerns

### **Phase 7C: Infrastructure Migration**
**Priority: Medium | Risk: Medium**

1. **Move Infrastructure Components**
   ```bash
   mkdir -p backend/infrastructure/game
   mkdir -p backend/infrastructure/persistence
   
   mv backend/text_adventure_games/games.py -> backend/infrastructure/game/game_engine.py
   mv backend/text_adventure_games/command/matcher.py -> backend/infrastructure/game/parser_adapter.py
   mv backend/text_adventure_games/state/descriptions.py -> backend/infrastructure/game/description_engine.py
   mv backend/text_adventure_games/state/character_manager.py -> backend/infrastructure/persistence/state_manager.py
   mv backend/text_adventure_games/events/* -> backend/infrastructure/events/
   ```

2. **Update Game Engine**
   - Refactor `Game` class to use dependency injection
   - Remove direct dependencies on domain entities
   - Implement repository patterns for entity management

### **Phase 7D: Final Cleanup**
**Priority: High | Risk: Low**

1. **Remove Empty Directories**
   ```bash
   rm -rf backend/text_adventure_games/
   ```

2. **Update Documentation**
   - Update all CLAUDE.md files to reflect new structure
   - Update import examples in documentation
   - Update developer guidelines

3. **Fix Remaining Issues**
   - Update test files and debug utilities
   - Fix any remaining import errors
   - Update agent_test_runner.py to use new structure

## Import Path Changes

### **Before (Current)**
```python
from backend.text_adventure_games.things import Character, Location, Item
from backend.text_adventure_games.capabilities import Examinable, Container
from backend.text_adventure_games.actions.generic import GenericTakeAction
from backend.text_adventure_games.games import Game
```

### **After (Target)**
```python
from backend.domain.entities import Character, Location, Item
from backend.domain.value_objects.capabilities import Examinable, Container  
from backend.domain.actions.interaction_actions import GenericTakeAction
from backend.infrastructure.game.game_engine import Game
```

## Risk Mitigation

### **Dependency Management**
- Use dependency injection to decouple layers
- Implement abstract interfaces for cross-layer communication
- Maintain clear dependency direction (outer → inner layers)

### **Testing Strategy**
- Run endpoint tests after each phase
- Test WorldBuilder with new entity locations
- Verify agent system continues to work
- Test debug utilities and manual scripts

### **Rollback Plan**
- Keep git history for easy rollback
- Complete each phase incrementally with validation
- Test critical paths (HTTP endpoints, agent execution) after each phase

## Expected Benefits

### **Code Quality**
- **Clear Separation**: Domain logic separated from infrastructure
- **Better Testability**: Domain entities can be unit tested in isolation
- **Reduced Coupling**: Each layer depends only on inner layers
- **Explicit Dependencies**: Clear interfaces between layers

### **Maintainability**
- **Easier Navigation**: Related code grouped by architectural concern
- **Simpler Changes**: Business logic changes isolated to domain layer
- **Better Documentation**: Structure matches architectural intent
- **Clearer Responsibilities**: Each layer has well-defined purpose

### **Scalability**
- **Plugin Architecture**: Easy to add new infrastructure implementations
- **Multiple Interfaces**: Can add CLI, gRPC, WebSocket interfaces easily
- **Configurable Components**: Infrastructure can be swapped without domain changes
- **Independent Evolution**: Layers can evolve independently

## Timeline

**Total Estimated Time**: 1-2 weeks

- **Phase 7A (Domain Migration)**: 3-4 days
- **Phase 7B (Application Migration)**: 2-3 days  
- **Phase 7C (Infrastructure Migration)**: 2-3 days
- **Phase 7D (Final Cleanup)**: 1-2 days

## Success Criteria

- [ ] All HTTP endpoints continue to work identically
- [ ] Agent system functions without changes  
- [ ] WorldBuilder works with new entity locations
- [ ] No circular dependencies between layers
- [ ] All tests pass
- [ ] Clean import structure with clear layer boundaries
- [ ] `backend/text_adventure_games/` directory completely removed

This completes the transformation to a proper hexagonal architecture with clear separation of concerns and maintainable code organization.