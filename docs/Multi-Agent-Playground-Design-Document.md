# Multi-Agent Playground - Design Document

## 🧠 Overview

The Multi-Agent Playground is a simplified multi-agent simulation framework inspired by [joonspk-research/generative_agents](https://github.com/joonspk-research/generative_agents), featuring an added **Godot frontend** for real-time simulation and interaction. This system enables LLM-powered agents to interact in a shared 2D environment, demonstrating emergent social behaviors and autonomous decision-making.

## 📋 Table of Contents

1. [Project Architecture](#project-architecture)
2. [Backend System](#backend-system)
3. [Frontend System](#frontend-system)
4. [Data Management](#data-management)
5. [Communication Protocol](#communication-protocol)
6. [Agent Behavior System](#agent-behavior-system)
7. [Memory and Spatial Systems](#memory-and-spatial-systems)
8. [API Design](#api-design)
9. [Development Setup](#development-setup)
10. [Future Considerations](#future-considerations)

## 🏗️ Project Architecture

### High-Level System Overview

```
┌─────────────────┐    HTTP/JSON API    ┌─────────────────┐
│  Godot Frontend │ ◄─────────────────► │ FastAPI Backend │
│                 │                     │                 │
│ • Game Engine   │                     │ • LLM Agents    │
│ • Visualization │                     │ • Memory Mgmt   │
│ • User Input    │                     │ • Decision Sys  │
│ • State Machine │                     │ • Persistence   │
└─────────────────┘                     └─────────────────┘
        │                                       │
        │                                       │
        ▼                                       ▼
┌─────────────────┐                     ┌─────────────────┐
│   Agent Data    │                     │   World Data    │
│   (JSON Files)  │                     │   (JSON Files)  │
└─────────────────┘                     └─────────────────┘
```

### Core Technologies

- **Backend**: Python 3.x, FastAPI, Uvicorn, Kani (LLM framework), OpenAI GPT-4o
- **Frontend**: Godot Engine 4.4, GDScript
- **Communication**: HTTP REST API with JSON payloads
- **Storage**: File-based JSON storage for agent and world state
- **LLM Integration**: OpenAI API via Kani library

### Directory Structure

```
multi_agent_playground/
├── backend/                    # Python backend system
│   ├── character_agent/        # Agent implementation
│   ├── config/                 # Configuration and schemas
│   ├── memory/                 # Memory and spatial systems
│   ├── server/                 # FastAPI controllers
│   └── tests/                  # Unit tests
├── frontend/                   # Godot frontend
│   └── Godot-Multi-Agent-Playground/
│       ├── scenes/             # Game scenes and entities
│       ├── scripts/            # GDScript behavior
│       └── assets/             # Art and audio assets
├── data/                       # Persistent data storage
│   ├── agents/                 # Agent configurations
│   └── world/                  # World state data
└── docs/                       # Documentation
```

## 🔧 Backend System

### Core Components

#### 1. FastAPI Application (`main.py`, `__main__.py`)

The backend provides a RESTful API with two primary endpoints following a **two-step action protocol**:

1. **Planning Phase** (`/agent_act/plan`): Receives perception data, uses LLM to plan next action
2. **Confirmation Phase** (`/agent_act/confirm`): Confirms action execution and updates agent memory

**Key Features:**
- CORS middleware for cross-origin requests
- Batch processing support for multiple agents
- Error handling and graceful degradation

#### 2. Agent System (`character_agent/`)

##### Agent Class (`agent.py`)
- **Purpose**: Core agent representation with persistent state
- **Features**:
  - Identity and personality traits (innate, learned, current state)
  - Daily planning system with schedules and requirements
  - Memory management with event storage
  - Perception handling for visible objects and agents
  - JSON-based state persistence

**Key Attributes:**
```python
# Identity
agent_id, name, age, innate_traits, learned_behaviors

# Planning
daily_plan_req, f_daily_schedule, act_description

# State
curr_time, curr_tile, currently, visible_objects

# Memory
memory (list of events with timestamp, location, salience)
```

##### Actions System (`actions.py`)
- **Purpose**: Defines available agent actions via Kani AI functions
- **Actions**:
  - `move(destination_coordinates, action_emoji)`: Spatial navigation
  - `chat(receiver, message, action_emoji)`: Inter-agent communication
  - `interact(object, new_state, action_emoji)`: Environment manipulation
  - `perceive(content, action_emoji)`: Environmental observation
  - `evaluate_event_salience(event, score)`: Memory importance scoring

**Design Philosophy:**
- Rich emoji-based action representation for visual feedback
- Detailed context and manner descriptions for realistic behavior
- Personality-driven action selection

##### LLM Integration (`kani_implementation.py`)
- **Purpose**: Bridges agent state with OpenAI GPT-4o via Kani library
- **Features**:
  - Dynamic system prompt generation based on agent personality
  - SSL/HTTPS handling for secure API communication
  - Environment data integration for spatial awareness
  - Asynchronous action planning and execution

#### 3. Server Controller (`server/controller.py`)

**Core Functions:**
- `plan_next_action()`: Orchestrates LLM-based action planning
- `confirm_action_and_update()`: Processes action results and updates state
- Message queue management for agent communication
- Event salience evaluation for memory storage

### Memory System (`memory/`)

#### Spatial Memory (`spatial.py`)
- **Purpose**: Graph-based spatial relationship management
- **Features**:
  - Node and edge representation of spatial connections
  - JSON conversion for environment data integration
  - Hierarchical spatial organization (house → rooms → objects)

**Example Structure:**
```json
{
  "house": {
    "bedroom": {
      "bed": {"shape": [[x,y]...], "interact": [[x,y]...]},
      "wardrobe": {"shape": [[x,y]...], "interact": [[x,y]...]}
    }
  }
}
```

### Configuration System (`config/`)

#### Schema Definitions (`schema.py`)
Comprehensive Pydantic models for type safety:

- **Message**: Agent-to-agent communication format
- **Actions**: Frontend/Backend action type definitions
- **AgentPerception**: Environmental state representation
- **AgentActionInput/Output**: API request/response formats

**Two-Step Protocol Schema:**
```python
# Step 1: Planning
AgentPlanRequest -> plan_next_action() -> AgentActionOutput

# Step 2: Confirmation  
AgentActionInput -> confirm_action_and_update() -> StatusMsg
```

## 🎮 Frontend System

### Godot Engine Architecture

#### Scene Organization
```
scenes/
├── characters/
│   ├── agents/                 # AI-controlled agents
│   ├── navigation_player/      # Human-controlled test agent
│   └── player/                 # Traditional player character
├── components/                 # Reusable UI/game components
├── houses/                     # Environment scenes
├── test/                       # Development/testing scenes
└── ui/                         # User interface elements
```

#### State Machine System (`scripts/agent_state_machine/`)

**Base Classes:**
- `StateMachine`: Manages state transitions and updates
- `State`: Base class for individual behavior states
- Concrete states: `Idle`, `Walk`, `Interact`, `Chat`

**Agent State Machine:**
```
Idle ←→ Walk
  ↓     ↓
  Chat ←→ Interact
```

#### Agent Implementation (`scenes/characters/agents/`)

**Agent.gd Features:**
- Navigation system integration with pathfinding
- Sprite animation management with directional animations
- HTTP communication for backend integration
- Visual feedback with emoji displays
- Collision detection and spatial awareness

**Key Variables:**
```gdscript
agent_id: String              # Unique identifier
current_tile: Vector2i        # Grid position
visible_objects: Dictionary   # Environmental awareness
visible_agents: Array[String] # Other agents in range
destination_tile: Vector2i    # Movement target
```

#### Communication System (`http_controller.gd`)

**HTTP Controller Features:**
- Async HTTP requests to backend API
- Request/response cycle management
- Error handling and fallback behaviors
- Perception data collection and transmission
- Action confirmation workflow

**Communication Flow:**
1. Collect perception data (visible objects, agents, position)
2. Send planning request to backend
3. Receive action plan from LLM
4. Execute action in game world
5. Send confirmation with results to backend

### Input and Controls

**Player Controls:**
- WASD/Arrow Keys: Direct movement
- Right-click: Navigate to position
- R key: Request next AI action
- E key: Pause/resume agent polling
- F key: Toggle emoji visibility
- N key: Toggle navigation path display

## 📊 Data Management

### Agent Data Structure

Each agent maintains two JSON files:

#### `agent.json` - Core State
```json
{
  "agent_id": "alan_002",
  "name": "Alan",
  "age": 28,
  "innate": ["curious", "friendly"],
  "learned": ["cooking", "gardening"],
  "currently": "I saw these people: alex_001",
  "daily_req": ["exercise", "read", "cook"],
  "curr_time": "01T01:18:03",
  "curr_tile": [31, 12],
  "f_daily_schedule": [
    ["sleeping", 360],
    ["morning routine", 20],
    ["painting", 240]
  ]
}
```

#### `memory.json` - Event History
```json
[
  {
    "timestamp": "01T04:35:20",
    "location": "bedroom",
    "event": "Received message from alex_001: 'Good morning!'",
    "salience": 6
  }
]
```

### World Data (`data/world/`)

#### Message Queue (`messages.json`)
- Persistent inter-agent communication log
- Conversation threading with deterministic IDs
- Delivery status tracking
- Timeout-based conversation management

## 🔄 Communication Protocol

### Two-Step Action Protocol

This design separates **planning** from **execution**, allowing the LLM to generate actions without immediately committing to state changes.

#### Step 1: Action Planning
```http
POST /agent_act/plan
Content-Type: application/json

{
  "agent_id": "alex_001",
  "perception": {
    "timestamp": "01T04:35:20",
    "current_tile": [20, 8],
    "visible_objects": {...},
    "visible_agents": ["alan_002"],
    "heard_messages": [...]
  }
}
```

**Response:**
```json
{
  "agent_id": "alex_001",
  "action": {
    "action_type": "move",
    "destination_tile": [21, 9]
  },
  "emoji": "🚶",
  "timestamp": "01T04:35:20"
}
```

#### Step 2: Action Confirmation
```http
POST /agent_act/confirm
Content-Type: application/json

{
  "agent_id": "alex_001",
  "action": {
    "action_type": "move",
    "destination_tile": [21, 9]
  },
  "in_progress": false,
  "perception": {
    "timestamp": "01T04:35:25",
    "current_tile": [21, 9],
    "visible_objects": {...}
  }
}
```

### Action Types

#### 1. Movement Actions
- **Backend→Frontend**: `MoveBackendAction` with destination coordinates
- **Frontend→Backend**: `MoveFrontendAction` with completion status
- **Execution**: Pathfinding navigation with collision avoidance

#### 2. Communication Actions
- **Backend→Frontend**: `ChatBackendAction` with message content
- **Frontend→Backend**: `ChatFrontendAction` with delivery confirmation
- **Features**: Message queuing, conversation threading, spatial proximity requirements

#### 3. Interaction Actions
- **Backend→Frontend**: `InteractBackendAction` with object and state change
- **Frontend→Backend**: `InteractFrontendAction` with result confirmation
- **Examples**: Opening doors, using furniture, manipulating objects

#### 4. Perception Actions
- **Purpose**: Environmental observation and awareness updates
- **Data**: Object states, agent positions, overheard conversations
- **Frequency**: Continuous updates during gameplay

## 🤖 Agent Behavior System

### Personality-Driven Decision Making

#### Personality Framework
Each agent has three personality layers:

1. **Innate Traits**: Core personality characteristics
   - Examples: "curious", "friendly", "introverted", "ambitious"
   - Influence: Base behavioral tendencies and social interactions

2. **Learned Behaviors**: Acquired skills and habits
   - Examples: "cooking", "gardening", "painting", "programming"
   - Influence: Available actions and daily activity preferences

3. **Current State**: Dynamic emotional/situational status
   - Examples: "excited about meeting someone new", "tired from work"
   - Influence: Immediate decision making and interaction tone

#### Daily Planning System

**Requirements-Based Planning:**
- Each agent has daily requirements (exercise, food, social interaction)
- LLM generates schedules based on personality and requirements
- Dynamic adaptation based on environmental opportunities

**Schedule Structure:**
```python
f_daily_schedule = [
    ["sleeping", 360],      # Activity, duration in minutes
    ["morning routine", 20],
    ["work/painting", 240],
    ["lunch break", 60],
    ["social time", 120]
]
```

### Memory and Learning

#### Salience-Based Memory Storage
- **Salience Scale**: 1-10 importance rating
  - 1-3: Routine activities, trivial observations
  - 4-6: Notable interactions, minor events
  - 7-9: Significant experiences, emotional moments
  - 10: Life-changing events, major decisions

#### Memory Formation Process
1. Event occurs in environment
2. Agent LLM evaluates personal significance
3. Event stored with timestamp, location, description, salience
4. High-salience events influence future behavior patterns

#### Contextual Recall
- Recent high-salience memories influence current decisions
- Spatial memory associations (events tied to locations)
- Social memory patterns (relationship histories with other agents)

### Social Interaction Model

#### Communication System
- **Proximity-Based**: Agents must be within "chatting range"
- **Turn-Based**: Conversation threading with timeouts
- **Context-Aware**: Previous conversation history influences responses
- **Personality-Filtered**: Response style based on agent personality

#### Relationship Dynamics
- **First Impressions**: Initial interactions shape ongoing relationships
- **Memory Persistence**: Past conversations stored and referenced
- **Group Dynamics**: Multi-agent conversations with social awareness

## 🗺️ Memory and Spatial Systems

### Spatial Memory Architecture

#### Graph-Based Representation
The spatial memory system uses a directed graph structure to represent:
- **Nodes**: Locations (rooms, areas, specific positions)
- **Edges**: Navigable connections between locations
- **Attributes**: Shape data, interaction points, accessibility

#### Environment Integration
```json
{
  "house": {
    "first_floor": {
      "bedroom": {
        "bed": {
          "shape": [[x1,y1], [x2,y2], ...],
          "interact": [[x,y]]
        },
        "wardrobe": {
          "shape": [[x1,y1], [x2,y2], ...],
          "interact": [[x,y]]
        }
      },
      "kitchen": {...}
    }
  }
}
```

#### Spatial Awareness
- Agents build mental maps through exploration
- Object permanence and state tracking
- Route planning and optimization
- Territorial behavior and personal spaces

### Memory Retrieval and Context

#### Context-Sensitive Recall
- **Location-Based**: "What happened in the kitchen yesterday?"
- **Agent-Based**: "What do I know about Alex?"
- **Activity-Based**: "When did I last cook?"
- **Temporal-Based**: "What happened this morning?"

#### Memory Influence on Behavior
- **Decision Making**: Past experiences shape current choices
- **Social Interactions**: Relationship history affects communication style
- **Spatial Navigation**: Learned routes and preferences
- **Goal Formation**: Success/failure patterns influence aspiration levels

## 🌐 API Design

### RESTful Endpoints

#### Core Agent Actions
```
POST /agent_act/plan
POST /agent_act/confirm
```

#### Batch Processing Support
- Multiple agents can be processed in single requests
- Efficient for synchronized multi-agent scenarios
- Maintains individual agent context and state

#### Error Handling
- Graceful degradation with default actions
- Retry mechanisms for network failures
- Comprehensive logging for debugging

### Request/Response Patterns

#### Consistent JSON Schema
- Strongly typed with Pydantic models
- Validation and error reporting
- Backward compatibility considerations

#### Async Processing
- Non-blocking LLM requests
- Timeout handling for long-running operations
- Queue management for high-frequency updates

## 🚀 Development Setup

### Prerequisites
- Python 3.8+
- Godot Engine 4.4+
- OpenAI API key
- Git for version control

### Backend Setup
```bash
# Clone repository
git clone [repository-url]
cd multi-agent-playground

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-api-key-here"

# Start FastAPI server
python -m uvicorn backend.main:app --reload
```

### Frontend Setup
1. Install Godot Engine 4.4+
2. Open project file: `frontend/Godot-Multi-Agent-Playground/project.godot`
3. Run test scene: `scenes/test/test_scene_navigation.tscn`
4. Use controls: WASD for movement, R for AI action requests

### Configuration
- Backend URL: Configure in Godot scene's HTTP controller
- Agent personalities: Edit JSON files in `data/agents/`
- Environment layout: Modify `backend/memory/data/environment.json`

## 🔮 Future Considerations

### Scalability Enhancements
- **Database Integration**: Replace JSON files with PostgreSQL/MongoDB
- **Caching Layer**: Redis for frequent agent state queries
- **Load Balancing**: Horizontal scaling for multiple LLM instances
- **Real-time Updates**: WebSocket integration for live agent status

### Advanced Features
- **Voice Integration**: Text-to-speech for agent communications
- **Mobile Support**: Godot mobile deployment capabilities
- **VR/AR Integration**: Immersive agent interaction modes
- **Multi-World Support**: Parallel simulation environments

### AI/ML Improvements
- **Fine-tuned Models**: Custom agent personality models
- **Learning Systems**: Reinforcement learning for behavior optimization
- **Emotional Modeling**: Advanced emotional state systems
- **Collective Intelligence**: Swarm behavior and group decision making

### Developer Experience
- **Visual Debugging**: Agent state visualization tools
- **Performance Monitoring**: Metrics and analytics dashboard
- **Automated Testing**: Integration test suites for agent behaviors
- **Documentation**: Interactive API documentation and tutorials

### Research Applications
- **Social Psychology**: Agent interaction pattern analysis
- **Behavioral Economics**: Decision-making studies
- **AI Safety**: Multi-agent alignment research
- **Human-Computer Interaction**: Natural language interface studies

---

## 📚 References

- [Generative Agents Paper](https://arxiv.org/abs/2304.03442) - Original research inspiration
- [Kani LLM Framework](https://github.com/zhudotexe/kani) - LLM integration library
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Backend framework
- [Godot Engine Documentation](https://docs.godotengine.org/) - Frontend framework

## 🤝 Contributing

This project is under active development. Key areas for contribution:
- Agent personality modeling
- Environmental interaction systems
- Performance optimization
- Documentation and tutorials
- Bug fixes and testing

For detailed contribution guidelines, see the project repository's contributing documentation.

---

*Last Updated: January 2025*
*Version: 1.0.0* 