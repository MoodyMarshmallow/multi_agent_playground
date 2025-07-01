# Multi-Agent Playground - Comprehensive System Design Document

## Table of Contents

1. [System Overview](#system-overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Core Components](#core-components)
4. [Class Interactions](#class-interactions)
5. [Data Flow Diagrams](#data-flow-diagrams)
6. [API Interfaces](#api-interfaces)
7. [Sequence Diagrams](#sequence-diagrams)
8. [Input/Output Specifications](#inputoutput-specifications)
9. [Module Interactions](#module-interactions)
10. [Performance Optimizations](#performance-optimizations)
11. [Frontend Integration](#frontend-integration)
12. [Deployment Architecture](#deployment-architecture)

---

## System Overview

The Multi-Agent Playground is a sophisticated simulation environment that enables real-time AI agent interactions within a house environment. The system combines:

- **Frontend**: Godot-based game engine for 2D visualization and user interaction
- **Backend**: FastAPI-based REST API with optimized agent processing using the Arush LLM framework
- **Agent System**: LLM-powered agents with GPT-4o integration
- **Memory Management**: Episodic memory with O(1) access patterns and salience-based importance
- **Spatial Awareness**: Location tracking and object interaction systems
- **Integration Layer**: Backward-compatible adapter pattern for seamless migration

### Key Features

- **Real-time agent interactions** with natural language processing
- **Zero-latency memory access** using optimized data structures
- **Scalable architecture** supporting multiple concurrent agents
- **Persistent state management** with JSON-based storage
- **Drop-in compatibility** with existing character_agent interfaces

---

## High-Level Architecture

```mermaid
graph TB
    subgraph "Frontend Layer - Godot Engine"
        A[Godot Game Engine]
        A1[Agent Visualization]
        A2[World Rendering]
        A3[User Interface]
        A4[HTTP Manager]
    end
    
    subgraph "API Layer - FastAPI"
        B[FastAPI Server]
        B1[/agent_act/plan Endpoint]
        B2[/agent_act/confirm Endpoint]
        B3[/agents/init Endpoint]
        B4[CORS Middleware]
    end
    
    subgraph "Control Layer"
        C[Controller.py]
        C1[plan_next_action]
        C2[confirm_action_and_update]
        C3[get_updated_perception_for_agent]
        C4[Message Queue Management]
    end
    
    subgraph "Agent Processing Layer - Arush LLM"
        D[CharacterAgentAdapter]
        D1[Agent Manager]
        D2[Integration Layer]
        D3[LLM Communication]
    end
    
    subgraph "Core Components"
        E[AgentMemory]
        F[LocationTracker]
        G[PromptTemplates]
        H[ResponseParser]
        I[Cache System]
        J[Action Validator]
    end
    
    subgraph "External Services"
        K[OpenAI GPT-4o API]
        L[JSON Data Storage]
        M[Object Registry]
    end
    
    A4 --> B1
    A4 --> B2
    A4 --> B3
    B1 --> C1
    B2 --> C2
    B3 --> C3
    C1 --> D
    C2 --> D
    D --> E
    D --> F
    D --> G
    D --> H
    D --> I
    D --> J
    D --> K
    E --> L
    F --> L
    G --> K
    M --> D
    
    style A fill:#e1f5fe
    style D fill:#f3e5f5
    style K fill:#fff3e0
    style L fill:#e8f5e8
```

---

## Core Components

### 1. Agent Memory System (`AgentMemory`)

**Purpose**: Manages episodic memory with O(1) access patterns and salience-based importance scoring.

**Key Features**:
- **O(1) Memory Operations**: Insertion, retrieval, and indexing using LRU caches
- **Salience-Based Importance**: Events rated 1-10 for memory prioritization
- **Context-Aware Retrieval**: Location, temporal, and tag-based memory access
- **Persistent Storage**: JSON serialization with full state preservation

**Class Structure**:
```python
class AgentMemory:
    def __init__(self, agent_id: str, data_dir: str = None, memory_capacity: int = 1000)
    def add_event(self, timestamp: str, location: str, event: str, salience: int, tags: List[str]) -> str
    def get_relevant_memories(self, context: str, limit: int = 5, min_salience: int = 3) -> List[Dict]
    def get_location_memories(self, location: str, limit: int = 5) -> List[Dict]
    def get_high_salience_memories(self, min_salience: int = 7, limit: int = 5) -> List[Dict]
    def save_memory(self) -> None
    def get_memory_stats(self) -> Dict[str, Any]
```

**Internal Data Structures**:
- `_memory_cache`: LRUCache for O(1) access to recent memories
- `_memories_by_salience`: Defaultdict mapping salience scores to memory IDs
- `_memories_by_context`: Defaultdict mapping contexts/tags to memory IDs
- `_memories_by_timestamp`: List of (timestamp, memory_id) tuples

### 2. Location Tracking System (`LocationTracker`)

**Purpose**: Provides spatial awareness and position tracking for agents with O(1) lookups.

**Key Features**:
- **Real-time Position Updates**: Track agent movement and current location
- **Spatial Indexing**: O(1) lookup for nearby objects and agents
- **Room Mapping**: Integration with house layout data
- **Movement History**: Track agent paths and visited locations

**Class Structure**:
```python
class LocationTracker:
    def __init__(self, agent_id: str, data_dir: str = None, cache_size: int = 200)
    def update_position(self, tile: Tuple[int, int], room: str = None) -> None
    def get_nearby_objects(self, radius: int = 2) -> List[Tuple[int, int]]
    def get_nearby_agents(self, agent_positions: Dict, radius: int = 3) -> List[str]
    def get_movement_options(self, max_distance: int = 3) -> List[Dict[str, Any]]
    def get_current_location(self) -> Dict[str, Any]
    def get_distance(self, other_tile: Tuple[int, int]) -> int
```

### 3. Prompt Generation System (`PromptTemplates`)

**Purpose**: Generates context-aware prompts for different agent actions with O(1) template access.

**Key Features**:
- **Action-Specific Templates**: Specialized prompts for perceive, chat, move, interact
- **Dynamic Context Building**: Real-time integration of agent state and environment
- **Template Caching**: LRU cache for frequently used prompt structures
- **Agent Personality Integration**: Prompts adapted to individual agent characteristics

**Template Categories**:
```python
class PromptTemplates:
    # Core action templates
    def get_system_prompt(cls, agent_data: Dict[str, Any]) -> str
    def get_perceive_prompt(cls, perception_data: Dict, memories: List[Dict]) -> str
    def get_chat_prompt(cls, perception_data: Dict, memories: List[Dict], conversation_history: List[Dict]) -> str
    def get_move_prompt(cls, perception_data: Dict, goals: List[str], memories: List[Dict]) -> str
    def get_interact_prompt(cls, perception_data: Dict, goals: List[str], memories: List[Dict]) -> str
    def get_salience_prompt(cls, agent_data: Dict, event_description: str) -> str
```

### 4. Response Parsing System (`ResponseParser`)

**Purpose**: Extracts structured data from LLM responses with O(1) parsing operations.

**Key Features**:
- **Multi-Format Support**: JSON, key-value, and natural language parsing
- **Action Recognition**: Pattern-based detection of action types
- **Error Handling**: Graceful fallback for malformed responses
- **Validation**: Ensures response format consistency

**Parsing Methods**:
```python
class ResponseParser:
    def parse_action_response(cls, response_text: str, expected_action: str = None) -> Dict[str, Any]
    def parse_salience_response(cls, response_text: str) -> int
    def _parse_perceive_response(cls, parsed: Dict[str, Any]) -> Dict[str, Any]
    def _parse_chat_response(cls, parsed: Dict[str, Any]) -> Dict[str, Any]
    def _parse_move_response(cls, parsed: Dict[str, Any]) -> Dict[str, Any]
    def _parse_interact_response(cls, parsed: Dict[str, Any]) -> Dict[str, Any]
```

### 5. Character Agent Adapter (`CharacterAgentAdapter`)

**Purpose**: Provides backward compatibility while using optimized Arush LLM components.

**Key Features**:
- **Legacy Interface Compatibility**: Maintains existing API surface
- **Internal Optimization**: Uses Arush LLM components for performance
- **State Synchronization**: Bidirectional sync between legacy and optimized systems
- **Memory Management**: Transparent integration with AgentMemory

**Interface Methods**:
```python
class CharacterAgentAdapter:
    def __init__(self, config_path: str)
    def update_perception(self, perception: Dict[str, Any])
    def update_agent_data(self, data: Dict[str, Any])
    def add_memory_event(self, timestamp: str, location: str, event: str, salience: int)
    def save(self)
    def save_memory(self)
    def get_relevant_memories(self, context: str, limit: int = 5, min_salience: int = 3)
```

---

## Class Interactions

### Agent Processing Flow

```mermaid
classDiagram
    class CharacterAgentAdapter {
        +agent_id: str
        +curr_tile: tuple
        +memory: AgentMemory
        +location_tracker: LocationTracker
        +update_perception(perception)
        +add_memory_event(timestamp, location, event, salience)
        +save()
    }
    
    class AgentMemory {
        +_memory_cache: LRUCache
        +_memories_by_salience: defaultdict
        +add_event(timestamp, location, event, salience)
        +get_relevant_memories(context, limit)
        +save_memory()
    }
    
    class LocationTracker {
        +current_tile: tuple
        +_position_cache: LRUCache
        +update_position(tile, room)
        +get_nearby_objects(radius)
        +get_movement_options(max_distance)
    }
    
    class PromptTemplates {
        +_SYSTEM_PROMPT_TEMPLATE: Template
        +_PERCEIVE_PROMPT_TEMPLATE: Template
        +get_system_prompt(agent_data)
        +get_perceive_prompt(perception_data, memories)
    }
    
    class ResponseParser {
        +_json_patterns: dict
        +_action_patterns: dict
        +parse_action_response(response_text)
        +parse_salience_response(response_text)
    }
    
    class LLMAgentManagerAdapter {
        +_agent_cache: LRUCache
        +get_agent(agent_id)
        +preload_all_agents()
        +remove_agent(agent_id)
    }
    
    CharacterAgentAdapter --> AgentMemory : uses
    CharacterAgentAdapter --> LocationTracker : uses
    LLMAgentManagerAdapter --> CharacterAgentAdapter : manages
    CharacterAgentAdapter ..> PromptTemplates : generates prompts
    CharacterAgentAdapter ..> ResponseParser : parses responses
```

### Controller Integration Flow

```mermaid
classDiagram
    class Controller {
        +plan_next_action(agent_id)
        +confirm_action_and_update(agent_msg)
        +get_updated_perception_for_agent(agent_id)
        +evaluate_event_salience(agent, event_description)
    }
    
    class FastAPIServer {
        +post_plan_action_batch(agent_requests)
        +post_confirm_action_batch(agent_msgs)
        +get_all_agents_init()
    }
    
    class AgentPerception {
        +timestamp: str
        +current_tile: tuple
        +visible_objects: dict
        +visible_agents: list
        +chatable_agents: list
        +heard_messages: list
    }
    
    class AgentActionOutput {
        +agent_id: str
        +action: BackendAction
        +emoji: str
        +timestamp: str
        +current_tile: tuple
    }
    
    class BackendAction {
        <<interface>>
        +action_type: str
    }
    
    class MoveBackendAction {
        +action_type: "move"
        +destination_tile: tuple
    }
    
    class ChatBackendAction {
        +action_type: "chat"
        +message: Message
    }
    
    class InteractBackendAction {
        +action_type: "interact"
        +object: str
        +current_state: str
        +new_state: str
    }
    
    class PerceiveBackendAction {
        +action_type: "perceive"
    }
    
    FastAPIServer --> Controller : calls
    Controller --> AgentPerception : processes
    Controller --> AgentActionOutput : returns
    BackendAction <|-- MoveBackendAction
    BackendAction <|-- ChatBackendAction
    BackendAction <|-- InteractBackendAction
    BackendAction <|-- PerceiveBackendAction
    AgentActionOutput --> BackendAction : contains
```

---

## Data Flow Diagrams

### Primary Action Flow

```mermaid
flowchart TD
    A[Godot Frontend] -->|HTTP POST /agent_act/plan| B[FastAPI Server]
    B --> C[plan_next_action]
    C --> D[get_updated_perception_for_agent]
    D --> E[CharacterAgentAdapter.get_agent]
    E --> F[AgentMemory.get_relevant_memories]
    E --> G[LocationTracker.get_current_location]
    E --> H[PromptTemplates.get_system_prompt]
    H --> I[OpenAI GPT-4o API]
    I --> J[ResponseParser.parse_action_response]
    J --> K[AgentActionOutput]
    K -->|HTTP Response| A
    A -->|Execute Action| L[Update Game State]
    L -->|HTTP POST /agent_act/confirm| B
    B --> M[confirm_action_and_update]
    M --> N[AgentMemory.add_event]
    M --> O[LocationTracker.update_position]
    O --> P[Save Agent State]
    
    style I fill:#fff3e0
    style F fill:#e8f5e8
    style G fill:#e8f5e8
    style H fill:#f3e5f5
```

### Memory System Data Flow

```mermaid
flowchart LR
    subgraph "Memory Input"
        A[Event Timestamp]
        B[Event Location]
        C[Event Description]
        D[Salience Score]
    end
    
    subgraph "Memory Processing"
        E[AgentMemory.add_event]
        F[LRU Cache Update]
        G[Salience Index Update]
        H[Context Index Update]
        I[Timestamp Index Update]
    end
    
    subgraph "Memory Storage"
        J[JSON Persistence]
        K[Cache Storage]
    end
    
    subgraph "Memory Retrieval"
        L[Context Query]
        M[Salience Filter]
        N[Time-based Filter]
        O[Relevant Memories]
    end
    
    A --> E
    B --> E
    C --> E
    D --> E
    E --> F
    E --> G
    E --> H
    E --> I
    F --> K
    G --> K
    H --> K
    I --> K
    E --> J
    L --> M
    M --> N
    N --> O
    K --> O
    
    style E fill:#e1f5fe
    style F fill:#e8f5e8
    style O fill:#fff3e0
```

---

## API Interfaces

### FastAPI Endpoints

#### 1. Plan Action Endpoint
```http
POST /agent_act/plan
Content-Type: application/json

Request Body: List[AgentPlanRequest]
[
  {
    "agent_id": "alex_001",
    "perception": {
      "timestamp": "01T04:35:20",
      "current_tile": [12, 8],
      "visible_objects": {...},
      "visible_agents": ["alan_002"],
      "chatable_agents": ["alan_002"],
      "heard_messages": []
    }
  }
]

Response: List[PlanActionResponse]
[
  {
    "action": {
      "agent_id": "alex_001",
      "action": {
        "action_type": "chat",
        "message": {
          "sender": "alex_001",
          "receiver": "alan_002",
          "message": "Good morning!"
        }
      },
      "emoji": "💬",
      "timestamp": "01T04:35:20",
      "current_tile": [12, 8]
    },
    "perception": {...}
  }
]
```

#### 2. Confirm Action Endpoint
```http
POST /agent_act/confirm
Content-Type: application/json

Request Body: List[AgentActionInput]
[
  {
    "agent_id": "alex_001",
    "action": {
      "action_type": "chat",
      "forwarded": true
    },
    "in_progress": false,
    "perception": {
      "timestamp": "01T04:35:25",
      "current_tile": [12, 8],
      "visible_objects": {...},
      "visible_agents": ["alan_002"],
      "chatable_agents": ["alan_002"],
      "heard_messages": []
    }
  }
]

Response: List[StatusMsg]
[
  {
    "status": "ok"
  }
]
```

#### 3. Agent Initialization Endpoint
```http
GET /agents/init

Response: List[AgentSummary]
[
  {
    "agent_id": "alex_001",
    "first_name": "Alex",
    "last_name": "Smith",
    "curr_tile": [12, 8],
    "age": 29,
    "occupation": "artist",
    "currently": "focused on painting"
  }
]
```

### Internal Function Interfaces

#### Controller Functions
```python
def plan_next_action(agent_id: str) -> PlanActionResponse:
    """
    Plans the next action for an agent based on current perception.
    
    Args:
        agent_id: Unique agent identifier
        
    Returns:
        PlanActionResponse containing action and updated perception
    """

def confirm_action_and_update(agent_msg: AgentActionInput) -> None:
    """
    Confirms action execution and updates agent memory/state.
    
    Args:
        agent_msg: Input containing agent action and perception data
    """

def get_updated_perception_for_agent(agent_id: str) -> AgentPerception:
    """
    Retrieves current world perception for an agent.
    
    Args:
        agent_id: Unique agent identifier
        
    Returns:
        AgentPerception with current world state
    """
```

---

## Sequence Diagrams

### Agent Action Planning Sequence

```mermaid
sequenceDiagram
    participant F as Godot Frontend
    participant API as FastAPI Server
    participant C as Controller
    participant A as CharacterAgentAdapter
    participant M as AgentMemory
    participant L as LocationTracker
    participant P as PromptTemplates
    participant OpenAI as OpenAI API
    participant RP as ResponseParser
    
    F->>API: POST /agent_act/plan [AgentPlanRequest]
    API->>C: plan_next_action(agent_id)
    C->>C: get_updated_perception_for_agent(agent_id)
    C->>A: get_agent(agent_id)
    A->>M: get_relevant_memories(context)
    A->>L: get_current_location()
    C->>P: get_system_prompt(agent_data)
    C->>P: get_perceive_prompt(perception, memories)
    C->>OpenAI: chat.completions.create()
    OpenAI-->>C: LLM Response
    C->>RP: parse_action_response(response)
    RP-->>C: Parsed Action
    C-->>API: PlanActionResponse
    API-->>F: List[PlanActionResponse]
    
    F->>F: Execute Action in Game World
    
    Note over F,RP: Action execution happens in frontend,<br/>then confirmation is sent back
```

### Agent Action Confirmation Sequence

```mermaid
sequenceDiagram
    participant F as Godot Frontend
    participant API as FastAPI Server
    participant C as Controller
    participant A as CharacterAgentAdapter
    participant M as AgentMemory
    participant L as LocationTracker
    participant Storage as JSON Storage
    
    F->>API: POST /agent_act/confirm [AgentActionInput]
    API->>C: confirm_action_and_update(agent_msg)
    C->>A: get_agent(agent_id)
    C->>C: build_event_description(action, perception)
    C->>C: evaluate_event_salience(agent, event)
    C->>A: add_memory_event(timestamp, location, event, salience)
    A->>M: add_event(timestamp, location, event, salience)
    M->>M: Update indices and cache
    alt if location changed
        C->>A: update_agent_data({"curr_tile": new_tile})
        A->>L: update_position(new_tile)
    end
    A->>Storage: save() and save_memory()
    C-->>API: Success
    API-->>F: List[StatusMsg]
    
    Note over F,Storage: Memory and state are persisted<br/>for future agent decisions
```

### Memory Retrieval Sequence

```mermaid
sequenceDiagram
    participant C as Controller/Caller
    participant A as CharacterAgentAdapter
    participant M as AgentMemory
    participant Cache as LRU Cache
    participant Indices as Memory Indices
    participant Storage as JSON Storage
    
    C->>A: get_relevant_memories(context)
    A->>M: get_relevant_memories(context, limit, min_salience)
    M->>Indices: Lookup context in _memories_by_context
    Indices-->>M: List of memory_ids
    loop for each memory_id
        M->>Cache: get(memory_id)
        alt if in cache
            Cache-->>M: Memory object
        else if not in cache
            M->>Storage: Load from JSON
            Storage-->>M: Memory data
            M->>Cache: put(memory_id, memory)
        end
    end
    M->>M: Filter by salience and sort
    M-->>A: List of relevant memories
    A-->>C: Formatted memory context
    
    Note over C,Storage: O(1) access for cached memories,<br/>automatic cache management
```

---

## Input/Output Specifications

### Agent Configuration Input (`agent.json`)

```json
{
  "agent_id": "alex_001",
  "first_name": "Alex",
  "last_name": "Smith",
  "age": 29,
  "curr_time": "2023-10-01T08:00:00Z",
  "curr_tile": [12, 8],
  "personality": "Creative and focused artist",
  "backstory": "Alex is a talented painter preparing for an upcoming gallery show",
  "occupation": "artist",
  "currently": "focused on painting",
  "lifestyle": "artist",
  "living_area": "downtown studio",
  "daily_req": [
    "Work on her paintings for her upcoming show",
    "Take a break to watch some TV",
    "Make lunch for herself"
  ],
  "f_daily_schedule": [
    ["sleeping", 360],
    ["morning routine", 20],
    ["painting", 240],
    ["lunch", 60]
  ]
}
```

### Memory Data Structure (`memory.json`)

```json
{
  "episodic_memory": [
    {
      "id": "alex_001_1",
      "timestamp": "01T04:35:20",
      "location": "bedroom",
      "event": "Woke up feeling refreshed and ready to paint",
      "salience": 6,
      "tags": ["morning", "emotion", "painting"],
      "created_at": 1699123520.123
    }
  ],
  "memory_metadata": {
    "total_memories": 1,
    "last_updated": "2023-10-01T08:00:00Z",
    "memory_capacity": 1000
  }
}
```

### Perception Input Format

```python
AgentPerception = {
    "timestamp": "01T04:35:20",          # Format: DDTHH:MM:SS
    "current_tile": [12, 8],             # [x, y] coordinates
    "visible_objects": {                 # Dict of object_name -> object_data
        "bed": {
            "room": "bedroom",
            "position": [21, 9],
            "state": "made"
        },
        "wardrobe": {
            "room": "bedroom", 
            "position": [20, 7],
            "state": "open"
        }
    },
    "visible_agents": ["alan_002"],      # List of agent_ids in sight
    "chatable_agents": ["alan_002"],     # List of agent_ids in chat range
    "heard_messages": [                  # List of Message objects
        {
            "sender": "alan_002",
            "receiver": "alex_001",
            "message": "Good morning!",
            "timestamp": "01T04:35:15",
            "conversation_id": "conv_123"
        }
    ]
}
```

### Action Output Format

```python
# Move Action
AgentActionOutput = {
    "agent_id": "alex_001",
    "action": {
        "action_type": "move",
        "destination_tile": [15, 10]
    },
    "emoji": "🚶",
    "timestamp": "01T04:35:20",
    "current_tile": [12, 8]
}

# Chat Action
AgentActionOutput = {
    "agent_id": "alex_001", 
    "action": {
        "action_type": "chat",
        "message": {
            "sender": "alex_001",
            "receiver": "alan_002",
            "message": "Good morning! How are you?",
            "timestamp": "01T04:35:20"
        }
    },
    "emoji": "💬",
    "timestamp": "01T04:35:20",
    "current_tile": [12, 8]
}

# Interact Action
AgentActionOutput = {
    "agent_id": "alex_001",
    "action": {
        "action_type": "interact",
        "object": "coffee_machine",
        "current_state": "off",
        "new_state": "brewing"
    },
    "emoji": "☕",
    "timestamp": "01T04:35:20", 
    "current_tile": [12, 8]
}

# Perceive Action
AgentActionOutput = {
    "agent_id": "alex_001",
    "action": {
        "action_type": "perceive"
    },
    "emoji": "👀",
    "timestamp": "01T04:35:20",
    "current_tile": [12, 8]
}
```

---

## Module Interactions

### Backend Module Dependencies

```mermaid
graph TD
    subgraph "Entry Points"
        A[main.py - FastAPI Server]
        B[__main__.py - Direct Backend]
    end
    
    subgraph "API Layer"
        C[server/controller.py]
    end
    
    subgraph "Configuration"
        D[config/schema.py - Pydantic Models]
        E[config/llm_config.py - LLM Settings]
    end
    
    subgraph "Arush LLM Framework"
        F[arush_llm/__init__.py]
        G[arush_llm/integration/character_agent_adapter.py]
        H[arush_llm/agent/memory.py]
        I[arush_llm/agent/location.py]
        J[arush_llm/utils/prompts.py]
        K[arush_llm/utils/parsers.py]
        L[arush_llm/utils/cache.py]
    end
    
    subgraph "Legacy Support"
        M[character_agent/ - Legacy modules]
    end
    
    subgraph "Object System"
        N[objects/object_registry.py]
        O[objects/interactive_object.py]
    end
    
    A --> C
    B --> C
    C --> D
    C --> G
    G --> H
    G --> I
    G --> J
    G --> K
    G --> L
    F --> G
    F --> H
    F --> I
    F --> J
    F --> K
    F --> L
    C --> N
    N --> O
    G --> M
    
    style G fill:#f3e5f5
    style H fill:#e8f5e8
    style I fill:#e8f5e8
    style J fill:#fff3e0
    style K fill:#fff3e0
```

### Frontend Module Structure

```mermaid
graph TD
    subgraph "Godot Project Root"
        A[project.godot]
        B[Main Scene]
    end
    
    subgraph "Scenes"
        C[scenes/components/http_manager/]
        D[scenes/components/agent_manager/]
        E[scenes/characters/agents/]
        F[scenes/houses/]
    end
    
    subgraph "Scripts"
        G[scripts/agent_state_machine/]
        H[scripts/state_machine/]
        I[scripts/globals/]
    end
    
    subgraph "Assets"
        J[assets/game/characters/]
        K[assets/game/objects/]
        L[assets/ui/]
    end
    
    subgraph "Autoload"
        M[autoload/house_layout.gd]
        N[autoload/time_manager.gd]
    end
    
    A --> B
    B --> C
    B --> D
    D --> E
    B --> F
    E --> G
    G --> H
    B --> I
    E --> J
    F --> K
    B --> L
    A --> M
    A --> N
    
    style C fill:#e1f5fe
    style D fill:#f3e5f5
    style E fill:#e8f5e8
```

### Data Flow Between Modules

```mermaid
flowchart LR
    subgraph "Frontend Modules"
        A[HTTP Manager]
        B[Agent Manager]
        C[Agent State Machine]
    end
    
    subgraph "Backend Modules"
        D[FastAPI Server]
        E[Controller]
        F[Character Agent Adapter]
    end
    
    subgraph "Core Modules"
        G[Agent Memory]
        H[Location Tracker]
        I[Prompt Templates]
        J[Response Parser]
    end
    
    subgraph "External"
        K[OpenAI API]
        L[JSON Storage]
    end
    
    A <-->|HTTP Requests| D
    D --> E
    E --> F
    F --> G
    F --> H
    F --> I
    F --> J
    I --> K
    G --> L
    H --> L
    F --> L
    
    B --> A
    C --> B
    
    style A fill:#e1f5fe
    style F fill:#f3e5f5
    style G fill:#e8f5e8
    style H fill:#e8f5e8
```

---

## Performance Optimizations

### Memory System Optimizations

1. **O(1) Access Patterns**
   - LRU Cache for frequently accessed memories
   - Hash-based indexing for salience and context lookups
   - Pre-compiled regex patterns for parsing

2. **Cache Strategy**
   ```python
   # Memory cache with TTL
   _memory_cache = LRUCache(1000, ttl_seconds=7200)  # 2 hours
   
   # Position cache for spatial queries
   _position_cache = LRUCache(200, ttl_seconds=1800)  # 30 minutes
   
   # Proximity cache for O(1) neighbor finding
   _proximity_cache = LRUCache(100, ttl_seconds=600)  # 10 minutes
   ```

3. **Index Management**
   ```python
   # Efficient multi-dimensional indexing
   _memories_by_salience = defaultdict(list)     # O(1) salience lookup
   _memories_by_context = defaultdict(list)      # O(1) context lookup
   _memories_by_timestamp = []                   # O(log n) temporal lookup
   ```

### Prompt Generation Optimizations

1. **Template Caching**
   ```python
   @lru_cache(maxsize=100)
   def _get_system_prompt_cached(cls, agent_key: tuple) -> str:
       # Cached system prompt generation
   ```

2. **Pre-compiled Templates**
   ```python
   _SYSTEM_PROMPT_TEMPLATE = string.Template("""System prompt...""")
   _PERCEIVE_PROMPT_TEMPLATE = string.Template("""Perceive prompt...""")
   ```

### Response Parsing Optimizations

1. **Pre-compiled Regex Patterns**
   ```python
   _json_patterns = {
       'basic': re.compile(r'\{[^{}]*\}'),
       'multiline': re.compile(r'\{[^{}]*\}', re.DOTALL),
       'markdown': re.compile(r'```json\s*(\{.*?\})\s*```', re.DOTALL)
   }
   ```

2. **Fast Action Detection**
   ```python
   _action_patterns = {
       'interact': re.compile(r'\b(?:interact|use|operate)\b', re.IGNORECASE),
       'move': re.compile(r'\b(?:move|go|walk)\b', re.IGNORECASE)
   }
   ```

### API Performance Optimizations

1. **Batch Processing**
   - Multiple agent requests processed in single API call
   - Concurrent agent processing where possible

2. **Connection Pooling**
   - Persistent HTTP connections
   - CORS optimization for frontend requests

---

## Frontend Integration

### Godot HTTP Manager

The frontend communicates with the backend through a dedicated HTTP manager that handles:

```gdscript
# HTTP Manager Core Functions
func _request_next_actions():
    # Builds batch request for all agents
    var request_body = []
    for agent_id in agent_ids:
        request_body.append({
            "agent_id": agent_id,
            "perception": agent_manager.get_agent_perception(agent_id)
        })

func _process_all_actions():
    # Processes backend responses and updates game state
    for action in _current_actions:
        _process_single_action(action)
    _send_pending_confirmations()

func _send_pending_confirmations():
    # Confirms action completion back to backend
    var confirm_bodies = []
    for action in _pending_confirmations:
        confirm_bodies.append({
            "agent_id": action.agent_id,
            "action": agent_manager.get_agent_frontend_action(action.agent_id),
            "in_progress": agent_manager.get_agent_in_progress(action.agent_id),
            "perception": agent_manager.get_agent_perception(action.agent_id)
        })
```

### Agent State Management

```gdscript
# Agent Manager Core Functions
func get_agent_perception(agent_id: String) -> Dictionary:
    # Builds perception data for backend
    return {
        "timestamp": TimeManager.get_formatted_time(),
        "current_tile": get_agent_tile(agent_id),
        "visible_objects": get_visible_objects(agent_id),
        "visible_agents": get_visible_agents(agent_id),
        "chatable_agents": get_chatable_agents(agent_id),
        "heard_messages": get_heard_messages(agent_id)
    }

func handle_move_action(agent_id: String, dest_tile: Vector2i):
    # Updates agent position and triggers movement animation
    
func handle_chat_action(agent_id: String, message: Dictionary):
    # Displays chat bubble and forwards message to receiver
    
func handle_interact_action(agent_id: String, object_name: String, current_state: String, new_state: String):
    # Updates object state and triggers interaction animation
```

### Real-time Polling System

```gdscript
# Polling Configuration
const POLL_INTERVAL = 5.0  # 5 seconds between backend requests
const BACKEND_URL = "http://localhost:8000"

# Polling Control
func _on_poll_timer_timeout():
    if not _is_processing_actions:
        _is_processing_actions = true
        _request_next_actions()

# Debug Controls
func _input(event):
    if event.is_action_pressed("pause_polling"):
        toggle_polling()
    if event.is_action_pressed("request_next_action"):
        forcibly_request_next_actions()
```

---

## Deployment Architecture

### Development Environment

```mermaid
graph TB
    subgraph "Developer Machine"
        A[Godot Editor]
        B[Backend Python Server]
        C[Local File System]
        D[Git Repository]
    end
    
    subgraph "External Services"
        E[OpenAI API]
        F[GitHub]
    end
    
    A -->|HTTP localhost:8000| B
    B --> C
    B --> E
    A --> C
    C --> D
    D --> F
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style E fill:#fff3e0
```

### Production Environment

```mermaid
graph TB
    subgraph "Client Devices"
        A[Godot Game Client]
    end
    
    subgraph "Cloud Infrastructure"
        B[Load Balancer]
        C[FastAPI Server Instances]
        D[Redis Cache]
        E[File Storage]
        F[Monitoring]
    end
    
    subgraph "External Services"
        G[OpenAI API]
        H[CDN for Assets]
    end
    
    A --> B
    B --> C
    C --> D
    C --> E
    C --> G
    A --> H
    C --> F
    
    style A fill:#e1f5fe
    style C fill:#f3e5f5
    style G fill:#fff3e0
```

### Configuration Management

```python
# Environment-based configuration
class Settings:
    # API Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    # Performance Settings
    MEMORY_CACHE_SIZE: int = int(os.getenv("MEMORY_CACHE_SIZE", "1000"))
    POSITION_CACHE_SIZE: int = int(os.getenv("POSITION_CACHE_SIZE", "200"))
    
    # Agent Settings
    DEFAULT_SALIENCE_THRESHOLD: int = int(os.getenv("DEFAULT_SALIENCE_THRESHOLD", "3"))
    MAX_MEMORY_LIMIT: int = int(os.getenv("MAX_MEMORY_LIMIT", "5"))
    
    # File Paths
    AGENTS_DATA_DIR: str = os.getenv("AGENTS_DATA_DIR", "data/agents")
    WORLD_DATA_DIR: str = os.getenv("WORLD_DATA_DIR", "data/world")
```

### Health Monitoring

```python
# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "Backend is running",
        "timestamp": datetime.now().isoformat(),
        "active_agents": agent_manager.get_active_agent_count(),
        "memory_usage": get_memory_stats(),
        "cache_stats": get_cache_stats()
    }
```

---

## Conclusion

The Multi-Agent Playground represents a sophisticated integration of modern AI capabilities with real-time simulation technology. The system's architecture prioritizes:

1. **Performance**: O(1) operations for critical paths
2. **Scalability**: Modular design supporting multiple agents
3. **Maintainability**: Clear separation of concerns and interfaces
4. **Compatibility**: Seamless migration from legacy systems
5. **Extensibility**: Plugin architecture for new capabilities

The design document serves as a comprehensive guide for understanding, maintaining, and extending the Multi-Agent Playground system, ensuring that future development can build upon this solid architectural foundation.