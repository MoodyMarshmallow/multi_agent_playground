# Backend Refactor Design

## Overview
This document outlines the plan to refactor the backend simulation framework toward a scalable and maintainable architecture. The refactor applies Clean/Hexagonal principles, introduces an event bus, external configuration, and a plugin-based agent strategy system. The goal is to decouple domain logic from infrastructure concerns and enable independent evolution of simulation components.

## Current Architecture Analysis

### Existing Codebase Structure
```
backend/
├── main.py              # FastAPI server (186 lines)
├── game_loop.py         # GameLoop class (433 lines) - MIXED CONCERNS
├── agent/
│   ├── manager.py       # AgentManager (158 lines)
│   └── agent_strategies.py # KaniAgent, AgentStrategy (71+ lines)
├── config/
│   ├── schema.py        # Pydantic models (200+ lines)
│   └── llm_config.py    # LLM configuration
└── text_adventure_games/ # Modular framework (40+ files)
```

### Specific Limitations Identified

**GameLoop Class (433 lines) - Mixed Responsibilities:**
- Lines 36-121: Turn management and agent coordination
- Lines 122-220: World building and agent setup (hardcoded)
- Lines 290-410: Event queue management (simple list)
- Lines 248-287: World state queries and API responses

**Event System Issues:**
- `self.event_queue: List[AgentActionOutput]` (line 52) - in-memory only
- No persistence, no horizontal scaling capability
- Direct list manipulation in `_add_action_event()` (line 290)

**Agent Strategy Coupling:**
- Hardcoded personas in `_setup_agents()` (lines 148-152)
- Strategy creation logic in `_create_agent_strategy()` (lines 179-202)
- No dynamic loading or configuration-based setup

**Configuration Hardcoding:**
- World building in `_build_house_environment()` calls `build_house_game()` directly
- Agent configuration stored as `Dict[str, str]` in GameLoop instance
- No external configuration files for scenarios or agent setups

## Proposed Architecture
### Proposed Layered Architecture

```
backend/
├── domain/                    # Pure simulation logic (no dependencies)
│   ├── entities/              # Agent, World, Turn domain entities
│   ├── services/              # SimulationEngine, TurnScheduler
│   ├── events/                # Domain events and EventBus interface
│   └── repositories/          # Abstract interfaces for persistence
├── application/               # Use cases and coordination
│   ├── services/              # GameOrchestrator, AgentCoordinator
│   ├── config/                # ConfigLoader, WorldBuilder
│   └── handlers/              # Event handlers, use case implementations
├── infrastructure/            # External concerns and implementations
│   ├── persistence/           # Event store, agent state persistence
│   ├── agents/                # KaniAgent, plugin system
│   └── events/                # AsyncIO EventBus implementation
└── interfaces/                # External interfaces
    ├── http/                  # FastAPI endpoints (current main.py)
    └── cli/                   # Command line interfaces
```

**Dependency Rules:**
- `interfaces` → `application` → `domain`
- `infrastructure` → `domain` (implements interfaces)
- No circular dependencies between layers
- Domain layer has zero external dependencies

### Event Bus Implementation

**Domain Interface (`backend/domain/events/event_bus.py`):**
```python
from abc import ABC, abstractmethod
from typing import List, Callable, Any

class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        pass
    
    @abstractmethod
    async def subscribe(self, event_type: str, handler: Callable) -> None:
        pass
    
    @abstractmethod
    async def get_events_since(self, timestamp: str) -> List[DomainEvent]:
        pass
```

**Infrastructure Implementation (`backend/infrastructure/events/async_event_bus.py`):**
```python
class AsyncEventBus(EventBus):
    def __init__(self):
        self._queue = asyncio.Queue()
        self._handlers: Dict[str, List[Callable]] = {}
        self._event_store: List[DomainEvent] = []  # Replace with DB later
```

**Migration from Current System:**
- Replace `GameLoop.event_queue: List[AgentActionOutput]` (line 52)
- Replace `GameLoop._add_action_event()` (line 290) with `event_bus.publish()`
- Update `/agent_act/next` endpoint to consume from event bus
- Maintain backward compatibility during transition

### Plugin-Based Agent Strategy System

**Current Agent Strategy Issues:**
- `KaniAgent` hardcoded in `game_loop.py:_create_agent_strategy()` (lines 179-202)
- Agent personas hardcoded as dictionary (lines 148-152)
- Manual fallback logic embedded in GameLoop

**Proposed Plugin Architecture:**

**Strategy Protocol (`backend/domain/entities/agent_strategy.py`):**
```python
from typing import Protocol

class AgentStrategy(Protocol):
    """Protocol for agent decision-making strategies.
    
    Note: Kani-based agents must extend the Kani class directly,
    so this is a Protocol (structural typing) not an ABC.
    """
    async def select_action(self, action_result: str) -> str:
        """Select next action based on previous action result."""
        ...
    
    @property
    def character_name(self) -> str:
        """Agent's character name."""
        ...
```

**Kani-Compatible Plugin Loader (`backend/application/config/agent_strategy_loader.py`):**
```python
from kani.engines.openai import OpenAIEngine
from kani.engines.anthropic import AnthropicEngine

class AgentStrategyLoader:
    def __init__(self, config_path: str):
        self._strategy_classes: Dict[str, Type] = {}
        self._engines: Dict[str, Any] = {}
        self._load_built_in_strategies()
        self._load_config(config_path)
    
    def create_kani_agent(self, config: AgentConfig) -> AgentStrategy:
        """Create a Kani-based agent with proper engine and configuration."""
        strategy_class = self._strategy_classes.get(config.strategy_type)
        
        # Create appropriate engine based on config
        engine = self._create_engine(config.model_config)
        
        # For Kani agents, pass engine and configuration
        if issubclass(strategy_class, Kani):
            return strategy_class(
                character_name=config.character_name,
                persona=config.persona,
                engine=engine,
                initial_world_state=config.initial_world_state
            )
        else:
            # For non-Kani strategies (e.g., manual agents)
            return strategy_class(config.character_name, config.persona)
    
    def _create_engine(self, model_config: ModelConfig):
        """Create appropriate Kani engine based on model configuration."""
        if model_config.provider == "openai":
            return OpenAIEngine(
                api_key=model_config.api_key,
                model=model_config.model_name,
                temperature=model_config.temperature
            )
        elif model_config.provider == "anthropic":
            return AnthropicEngine(
                api_key=model_config.api_key,
                model=model_config.model_name
            )
        else:
            raise ValueError(f"Unsupported model provider: {model_config.provider}")
```

**Kani-Compatible Plugin Directory Structure:**
```
backend/infrastructure/agents/plugins/
├── __init__.py
├── kani/
│   ├── __init__.py
│   ├── openai_agent.py     # KaniAgent with OpenAI (from agent_strategies.py)
│   ├── anthropic_agent.py  # KaniAgent with Anthropic engine
│   └── custom_kani.py      # Custom Kani-based agent
├── manual/
│   ├── __init__.py
│   └── manual_agent.py     # ManualAgent (from agent_strategies.py)
└── third_party/
    └── custom_agent.py     # Non-Kani custom agents
```

**Important Kani Integration Notes:**
- All Kani-based agents must extend the `Kani` class directly
- Agents have built-in chat history and state management via Kani
- Function calling is central to Kani agent operation (via `@ai_function` decorator)
- Engine abstraction allows OpenAI, Anthropic, HuggingFace, etc.
- Async-first architecture - all agent interactions are `async`

**Configuration Integration:**
- Remove hardcoded strategy creation from GameLoop
- Load strategies from `backend/config/agents.yaml`
- Support dynamic registration via entry points

### External Configuration System

**Current Hardcoded Configuration Issues:**
- Agent personas in `GameLoop._setup_agents()` (lines 148-152):
  ```python
  agent_personas = {
      "alex_001": "I am Alex, a friendly...",
      "alan_002": "I am Alan, a quiet..."
  }
  ```
- World building in `GameLoop._build_house_environment()` calls `build_house_game()` directly
- No way to change scenarios without code modification

**Proposed Configuration Files:**

**Agent Configuration (`backend/config/agents.yaml`):**
```yaml
agents:
  alex_001:
    strategy: "openai_kani_agent"
    persona: "I am Alex, a friendly and social person..."
    model_config:
      provider: "openai"
      model_name: "gpt-4o-mini"
      temperature: 0.7
      api_key_env: "OPENAI_API_KEY"
  alan_002:
    strategy: "openai_kani_agent"
    persona: "I am Alan, a quiet and thoughtful person..."
    model_config:
      provider: "openai"
      model_name: "gpt-4o-mini"
      temperature: 0.5
      api_key_env: "OPENAI_API_KEY"
  claude_test:
    strategy: "anthropic_kani_agent"
    persona: "I am Claude, an AI assistant..."
    model_config:
      provider: "anthropic"
      model_name: "claude-3-haiku-20240307"
      api_key_env: "ANTHROPIC_API_KEY"
  manual_test:
    strategy: "manual_agent"
    persona: "Manual control for testing"
```

**World Configuration (`backend/config/worlds/house.yaml`):**
```yaml
world:
  name: "house"
  builder: "house_builder"
  locations:
    - name: "kitchen"
      description: "A modern kitchen..."
      items: ["fridge", "stove"]
    - name: "bedroom"
      connections: {"north": "kitchen"}
```

**Configuration Loader (`backend/application/config/config_loader.py`):**
```python
class ConfigLoader:
    def load_agent_configs(self, path: str) -> List[AgentConfig]:
        # Replace GameLoop._setup_agents() hardcoding
        pass
    
    def load_world_config(self, world_name: str) -> WorldConfig:
        # Replace GameLoop._build_house_environment() hardcoding
        pass
```

**Migration Steps:**
1. Extract current hardcoded values to YAML files
2. Implement ConfigLoader to read YAML configurations
3. Modify GameLoop to use ConfigLoader instead of hardcoded values
4. Add validation for configuration schemas

## Detailed Implementation Plan

### Phase 1: Directory Restructuring (Low Risk)
**Files to Move/Create:**
1. Create new directory structure:
   ```bash
   mkdir -p backend/{domain/{entities,services,events,repositories},application/{services,config,handlers},infrastructure/{persistence,agents,events},interfaces/http}
   ```
2. Move existing files:
   - `backend/main.py` → `backend/interfaces/http/main.py`
   - `backend/agent/agent_strategies.py` → `backend/infrastructure/agents/kani_agent.py`
   - Extract domain entities from `backend/game_loop.py`

### Phase 2: Extract Domain Logic (Medium Risk)
**Target: GameLoop.py (433 lines)**
1. Extract domain entities:
   - `Agent`, `Turn`, `GameState` → `backend/domain/entities/`
   - Remove from GameLoop lines 36-60 (initialization)

2. Create domain services:
   - `SimulationEngine` → `backend/domain/services/simulation_engine.py`
   - `TurnScheduler` → `backend/domain/services/turn_scheduler.py`
   - Extract from GameLoop lines 84-121 (run_game_loop logic)

3. Create application coordinator:
   - `GameOrchestrator` → `backend/application/services/game_orchestrator.py`
   - Replace GameLoop as main coordinator

### Phase 3: Event Bus Implementation (Medium Risk)
**Current System Replacement:**
1. Replace `GameLoop.event_queue: List[AgentActionOutput]` (line 52)
2. Replace `GameLoop._add_action_event()` method (line 290)
3. Update API endpoints:
   - `/agent_act/next` → use event bus instead of direct list access
   - `/game/events` → use event bus `get_events_since()`

**Implementation Steps:**
1. Create `EventBus` interface in `backend/domain/events/`
2. Implement `AsyncEventBus` in `backend/infrastructure/events/`
3. Update `GameOrchestrator` to use event bus
4. Migrate existing event consumers

### Phase 4: Plugin System (High Value, Kani-Compatible)
**Target: Agent Strategy Hardcoding (Kani-Compatible)**
1. Move and restructure Kani agents:
   - `KaniAgent` → `backend/infrastructure/agents/plugins/kani/openai_agent.py`
   - `ManualAgent` → `backend/infrastructure/agents/plugins/manual/manual_agent.py`
   - Maintain Kani class inheritance and function calling patterns

2. Create Kani-compatible plugin loader:
   - `AgentStrategyLoader` → `backend/application/config/agent_strategy_loader.py`
   - Support multiple Kani engines (OpenAI, Anthropic, etc.)
   - Handle Kani-specific initialization (engine, chat state, function calling)
   - Replace hardcoded creation in GameLoop lines 179-202

3. Remove hardcoded agent setup (preserve Kani patterns):
   - Replace `GameLoop._setup_agents()` (lines 145-178)
   - Maintain `@ai_function` decorator pattern for action selection
   - Preserve async function calling workflow (`full_round()` usage)
   - Use configuration-driven Kani agent creation with proper engines

### Phase 5: External Configuration (High Value)
**Target: Hardcoded Configuration Removal**
1. Extract hardcoded values:
   - Agent personas from GameLoop lines 148-152 → `agents.yaml`
   - World building logic → `worlds/house.yaml`

2. Implement configuration loader:
   - `ConfigLoader` → `backend/application/config/config_loader.py`
   - Replace `GameLoop._build_house_environment()` and `_setup_agents()`

3. Add configuration validation:
   - Pydantic models for configuration schemas
   - Validation during startup

### Phase 6: Testing and Migration (Critical)
**Ensure Zero Functionality Loss:**
1. Create comprehensive test suite:
   - Test current API endpoints work identically
   - Test agent behavior remains the same
   - Test event delivery matches current system

2. Create migration scripts:
   - Database migration for event persistence
   - Configuration migration from hardcoded values
   - Backward compatibility layers

3. Performance validation:
   - Benchmark current vs. refactored system
   - Ensure no performance regression
   - Load testing with multiple agents

**Success Criteria:**
- All existing API endpoints return identical responses
- Agent behavior remains consistent
- Frontend integration unaffected
- Configuration allows new scenarios without code changes
- Plugin system enables third-party agent strategies
- **Kani-Specific Success Criteria:**
  - Kani agents maintain proper function calling via `@ai_function` decorators
  - Async patterns preserved (`full_round()`, `select_action()` etc.)
  - Engine abstraction allows OpenAI, Anthropic, and other Kani engines
  - Chat history and state management handled by Kani framework
  - Function calling workflow (`submit_command()`) continues to work correctly
  - Agent personas and system prompts configurable via YAML
  - SSL certificate handling and API key management preserved

## Risks and Mitigations
- **Complexity Increase:** Modularization may initially complicate navigation.
  - *Mitigation:* Provide clear documentation and examples for each layer.
- **Plugin Security:** Loading external strategies could execute untrusted code.
  - *Mitigation:* Validate plugin sources and restrict execution environments.
- **Event Bus Reliability:** Using external brokers introduces new failure modes.
  - *Mitigation:* Start with in-process queue and add broker support with retry and monitoring.

## Future Work
- Implement persistence for event logs to allow replay and auditing.
- Explore distributed agent execution across multiple processes or hosts.
- Integrate metrics and tracing to observe simulation behavior in production.