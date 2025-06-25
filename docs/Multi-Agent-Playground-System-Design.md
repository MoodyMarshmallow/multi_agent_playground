# Multi-Agent Playground - System Design Document

## 🧠 Overview

The Multi-Agent Playground is a sophisticated multi-agent simulation framework that combines LLM-powered autonomous agents with real-time 2D visualization. Inspired by the [Generative Agents research](https://github.com/joonspk-research/generative_agents), this system enables AI agents to interact naturally in a shared virtual environment, demonstrating emergent social behaviors, memory formation, and goal-directed decision making.

## 🏗️ System Architecture

### High-Level Architecture
```
┌─────────────────┐    HTTP REST API     ┌─────────────────┐
│  Godot Frontend │ ◄─────────────────► │ FastAPI Backend │
│                 │                     │                 │
│ • Game Engine   │                     │ • LLM Agents    │
│ • Visualization │                     │ • Memory System │
│ • User Input    │                     │ • Action Planning│
│ • State Machine │                     │ • Persistence   │
└─────────────────┘                     └─────────────────┘
        │                                       │
        ▼                                       ▼
┌─────────────────┐                     ┌─────────────────┐
│   Agent State   │                     │   World State   │
│   (JSON Files)  │                     │   (JSON Files)  │
└─────────────────┘                     └─────────────────┘
```

### Technology Stack
- **Backend**: Python 3.x, FastAPI, Uvicorn, Kani (LLM framework)
- **LLM**: OpenAI GPT-4o integration via Kani library
- **Frontend**: Godot Engine 4.4, GDScript
- **Communication**: HTTP REST API with JSON payloads
- **Storage**: File-based JSON for agent state and world data
- **Dependencies**: See `requirements.txt` for complete list

## 📁 Project Structure

```
multi_agent_playground/
├── backend/                    # Python backend system
│   ├── character_agent/        # Core agent implementation
│   │   ├── agent.py           # Agent class with state management
│   │   ├── actions.py         # Available agent actions (Kani AI functions)
│   │   ├── kani_implementation.py  # LLM integration layer
│   │   └── clin.py            # CLI interface utilities
│   ├── config/                 # Configuration and type definitions
│   │   ├── schema.py          # Pydantic models for API
│   │   └── llm_config.py      # LLM configuration settings
│   ├── memory/                 # Memory and spatial systems
│   │   ├── spatial.py         # Graph-based spatial memory
│   │   └── data/              # Environment definitions
│   ├── server/                 # FastAPI web server
│   │   └── controller.py      # API endpoint handlers
│   └── tests/                  # Unit and integration tests
├── frontend/                   # Godot game engine frontend
│   └── Godot-Multi-Agent-Playground/
│       ├── scenes/             # Game scenes and entities
│       │   ├── characters/     # Agent and player implementations
│       │   ├── components/     # Reusable UI/game components
│       │   ├── houses/         # Environment scenes
│       │   └── test/           # Development test scenes
│       ├── scripts/            # Core GDScript systems
│       │   ├── agent_state_machine/  # State machine framework
│       │   └── globals/        # Global data types and utilities
│       ├── assets/             # Art, sprites, and audio assets
│       ├── autoload/           # Global systems (HouseLayout, TimeManager)
│       └── project.godot       # Godot project configuration
├── data/                       # Persistent data storage
│   ├── agents/                 # Individual agent data directories
│   │   ├── alan_002/          # Example agent
│   │   │   ├── agent.json     # Core agent state
│   │   │   └── memory.json    # Agent's memory events
│   │   └── [other agents]/
│   └── world/                  # Global world state
│       └── messages.json      # Inter-agent message queue
└── requirements.txt            # Python dependencies
```

## 🤖 Backend System Design

### Core Components

#### 1. FastAPI Application (`main.py`, `__main__.py`)

**Two-Step Action Protocol:**
The backend implements a sophisticated two-phase action system:

1. **Planning Phase** (`POST /agent_act/plan`):
   - Receives agent perception data from frontend
   - Uses LLM to generate next action based on agent personality and context
   - Returns action plan without committing state changes

2. **Confirmation Phase** (`POST /agent_act/confirm`):
   - Receives action execution results from frontend
   - Updates agent memory and internal state
   - Commits changes to persistent storage

**Key Features:**
- CORS middleware for cross-origin requests
- Batch processing for multiple agents
- Error handling with graceful degradation
- Structured logging for debugging

#### 2. Agent System (`character_agent/`)

##### Agent Class (`agent.py`)
The core `Agent` class encapsulates all agent state and provides persistence:

**Identity & Personality:**
```python
agent_id: str           # Unique identifier
name: str              # Display name  
age: int               # Agent age
innate: List[str]      # Core personality traits ["curious", "friendly"]
learned: List[str]     # Acquired skills ["cooking", "gardening"]
currently: str         # Current emotional/situational state
lifestyle: str         # General lifestyle description
living_area: str       # Where the agent lives
```

**Planning & Scheduling:**
```python
daily_plan_req: str                    # Daily planning requirements
daily_req: List[str]                   # Daily needs ["exercise", "food"]
f_daily_schedule: List[Tuple[str, int]] # [(activity, duration_minutes)]
f_daily_schedule_hourly_org: List[Tuple] # Organized hourly schedule
```

**Spatial & Temporal State:**
```python
curr_time: str         # Current simulation time "01T04:35:20"
curr_tile: List[int]   # Current position [x, y]
vision_r: int          # Vision radius in tiles
retention: int         # Memory retention capacity
```

**Memory System:**
```python
memory: List[Dict]     # Event memories with salience scores
```

**Runtime Perception:**
```python
visible_objects: Dict   # Objects currently visible
visible_agents: List   # Other agents in view
chatable_agents: List  # Agents within communication range
heard_messages: List   # Messages received this cycle
```

##### Actions System (`actions.py`)
Implements Kani AI functions for agent capabilities:

**Movement Actions:**
```python
@ai_function()
def move(destination_coordinates: List[int], action_emoji: str) -> Dict
```
- Detailed movement manner descriptions with emoji semantics
- Personality-driven movement styles (nervous shuffle, confident stride, etc.)
- Coordinate-based navigation in 2D grid space

**Communication Actions:**
```python
@ai_function()  
def chat(receiver: str, message: str, action_emoji: str) -> Dict
```
- Agent-to-agent messaging with delivery confirmation
- Conversation threading and context awareness
- Emotional expression through emoji and tone

**Environment Interaction:**
```python
@ai_function()
def interact(object: str, new_state: str, action_emoji: str) -> Dict
```
- Object state manipulation (open/close doors, use furniture)
- Contextual interaction styles (gentle, forceful, skilled, etc.)
- Environmental feedback and state confirmation

**Perception and Observation:**
```python
@ai_function()
def perceive(content: str, action_emoji: str) -> Dict
```
- Active environmental scanning
- Social awareness and observation
- Memory formation triggers

**Memory Evaluation:**
```python
@ai_function()
def evaluate_event_salience(event_description: str, salience_score: int) -> Dict
```
- Importance rating system (1-10 scale)
- Personality-based event significance assessment
- Memory storage decision making

##### LLM Integration (`kani_implementation.py`)

**LLMAgent Class Features:**
- Inherits from both `Kani` and `ActionsMixin`
- Dynamic system prompt generation based on agent personality
- Environment data integration for spatial awareness
- SSL/HTTPS handling for secure OpenAI API communication
- Async action planning and execution

**System Prompt Construction:**
```python
def _build_system_prompt(self) -> str:
    # Combines agent personality, spatial memory, daily requirements,
    # and behavioral guidelines into comprehensive LLM context
```

#### 3. Server Controller (`server/controller.py`)

**Core Functions:**

`plan_next_action(agent_id: str, perception: AgentPerception) -> AgentActionOutput`
- Loads agent from persistent storage
- Updates agent perception with current world state
- Invokes LLM for action planning
- Returns structured action plan

`confirm_action_and_update(agent_msg: AgentActionInput) -> None`
- Processes completed action results
- Updates agent memory with new experiences
- Evaluates event salience for memory storage
- Saves updated agent state to disk

**Message Queue Management:**
- Persistent inter-agent communication via `messages.json`
- Conversation threading with deterministic IDs
- Message delivery status tracking
- Timeout-based conversation cleanup

### Memory & Spatial Systems (`memory/`)

#### Spatial Memory (`spatial.py`)
Graph-based spatial relationship management:

```python
class SpatialMemory:
    def __init__(self, data: Dict[str, List] = None)
    def add(self, data: Dict[str, List]) -> None
    def convert_to_JSON(self) -> Dict
```

**Features:**
- Directed graph representation of spatial connections
- Hierarchical organization (house → rooms → objects)  
- JSON serialization for environment data
- Integration with agent spatial awareness

**Environment Structure:**
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
      }
    }
  }
}
```

### Configuration System (`config/`)

#### Schema Definitions (`schema.py`)
Comprehensive Pydantic models ensuring type safety:

**Message Format:**
```python
class Message(BaseModel):
    sender: str
    receiver: str  
    message: str
    timestamp: Optional[str] = None
    conversation_id: Optional[str] = None
```

**Action Types:**
- `MoveFrontendAction` / `MoveBackendAction`
- `ChatFrontendAction` / `ChatBackendAction`  
- `InteractFrontendAction` / `InteractBackendAction`
- `PerceiveFrontendAction` / `PerceiveBackendAction`

**Perception Data:**
```python
class AgentPerception(BaseModel):
    timestamp: Optional[str] = None
    current_tile: Optional[Tuple[int, int]] = None
    visible_objects: Optional[Dict[str, Dict[str, Any]]] = None
    visible_agents: Optional[List[str]] = None
    chatable_agents: Optional[List[str]] = None
    heard_messages: Optional[List[Message]] = None
```

**API Protocol:**
```python
class AgentPlanRequest(BaseModel):
    agent_id: str
    perception: AgentPerception

class AgentActionOutput(BaseModel):
    agent_id: str
    action: BackendAction
    emoji: str
    timestamp: Optional[str] = None
    current_tile: Optional[Tuple[int, int]] = None
```

## 🎮 Frontend System Design

### Godot Engine Architecture

#### Scene Hierarchy
```
Main Scene
├── AgentManager (manages all AI agents)
│   ├── Agent (instantiated per AI agent)
│   │   ├── AnimatedSprite2D (visual representation)
│   │   ├── NavigationAgent2D (pathfinding)
│   │   ├── StateMachine (behavior states)
│   │   │   ├── Idle State
│   │   │   ├── Walk State  
│   │   │   ├── Chat State
│   │   │   └── Interact State
│   │   ├── CollisionShape2D (physics)
│   │   └── EmojiLabel (action feedback)
│   └── [Additional Agents...]
├── NavigationPlayer (human-controlled test agent)
├── Environment (house, furniture, objects)
├── UI (menus, debug info)
└── Camera2D (viewport control)
```

#### State Machine System (`scripts/agent_state_machine/`)

**Base Classes:**
```gdscript
class_name StateMachine extends Node
- Manages state transitions and updates
- Handles state initialization and cleanup
- Processes per-frame state updates

class_name State extends Node  
- Base class for individual behavior states
- Provides enter(), exit(), update(), physics_update() methods
- Emits transition signals for state changes
```

**State Implementations:**
- **Idle State**: Default resting state, plays idle animations
- **Walk State**: Movement with pathfinding and obstacle avoidance
- **Chat State**: Communication interface and message display
- **Interact State**: Object manipulation and environmental changes

#### Agent Implementation (`scenes/characters/agents/agent.gd`)

**Core Features:**
```gdscript
class_name Agent extends CharacterBody2D

# Agent Identity
@export var agent_id: String = "alex_001"
var current_tile: Vector2i = Vector2i(0, 0)

# Perception Data  
var visible_objects: Dictionary = {}
var visible_agents: Array[String] = []
var chattable_agents: Array[String] = []
var heard_messages: Array = []

# Navigation
@onready var navigation_agent_2d: NavigationAgent2D
var speed = 50.0
var destination_tile: Vector2i

# Animation
@onready var animated_sprite_2d: AnimatedSprite2D
var last_direction := "down"

# State Management
@onready var state_machine: StateMachine
```

**Key Methods:**
- `position_to_tile()` / `tile_to_position()`: Coordinate conversion
- `on_move_action_received()`: Handles movement commands from backend
- `on_chat_action_received()`: Processes communication actions
- `on_emoji_received()`: Updates visual emoji feedback

#### HTTP Communication (`http_controller.gd`)

**Request/Response Cycle:**
```gdscript
func request_next_action() -> void:
    # 1. Collect current perception data
    var perception_data = {
        "timestamp": Time.get_datetime_string_from_system(),
        "current_tile": _get_current_tile(),
        "visible_objects": _get_visible_objects(),
        "visible_agents": _get_visible_agents(),
        "chatable_agents": _get_chatable_agents(),
        "heard_messages": _get_heard_messages()
    }
    
    # 2. Send planning request to backend
    var url = base_url + "/agent_act/plan"  
    http_request.request(url, headers, HTTPClient.METHOD_POST, JSON.stringify(perception_data))

func notify_action_completed() -> void:
    # 3. Send confirmation with action results
    _confirm_action(current_action.action_type, current_action.content)
```

**Error Handling:**
- Fallback to default actions on network failure
- Retry mechanisms with exponential backoff
- Graceful degradation for offline operation

### Input System

**Control Scheme:**
- **WASD/Arrow Keys**: Direct player movement
- **Right-click**: Point-and-click navigation
- **R**: Request next AI action manually
- **E**: Pause/resume agent polling
- **F**: Toggle emoji visibility
- **N**: Toggle navigation path display
- **A**: Iterate through selected agents

## 📊 Data Management

### Agent Data Persistence

Each agent maintains persistent state across two JSON files:

#### `agent.json` - Core State
```json
{
  "agent_id": "alan_002",
  "name": "Alan", 
  "first_name": "Alan",
  "last_name": "Smith", 
  "age": 28,
  "innate": ["curious", "friendly"],
  "learned": ["cooking", "gardening"],
  "currently": "I saw these people: alex_001",
  "lifestyle": "active",
  "living_area": "apartment",
  "daily_req": ["exercise", "read", "cook"],
  "curr_time": "01T01:18:03",
  "curr_tile": [31, 12],
  "f_daily_schedule": [
    ["sleeping", 360],
    ["wakes up and stretches", 5],
    ["starts her morning routine", 15],
    ["has breakfast", 20],
    ["working on her painting", 180],
    ["lunch break", 60]
  ],
  "act_description": "Alan is planning his next activity.",
  "planned_path": [[12, 8], [12, 9], [13, 9]]
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
  },
  {
    "timestamp": "01T04:40:15",
    "location": "kitchen",
    "event": "I made coffee and thought about today's painting session",
    "salience": 4
  }
]
```

### World Data (`data/world/`)

#### Message Queue (`messages.json`)
```json
[
  {
    "sender": "alex_001",
    "receiver": "alan_002", 
    "message": "Hey, how's the painting going?",
    "timestamp": "01T04:35:20",
    "conversation_id": "conv_12345678-abcd-ef90-1234-567890abcdef",
    "location": "living_room",
    "delivered": false
  }
]
```

**Features:**
- Deterministic conversation ID generation
- Message delivery status tracking
- Location-based message context
- Timeout-based conversation management (30 minute default)

## 🔄 Communication Protocol

### Two-Step Action Protocol

This architecture separates **planning** from **execution**, enabling sophisticated LLM-based decision making without premature state commitment.

#### Step 1: Action Planning
```http
POST /agent_act/plan
Content-Type: application/json

{
  "agent_id": "alex_001",
  "perception": {
    "timestamp": "01T04:35:20",
    "current_tile": [20, 8],
    "visible_objects": {
      "bed": {
        "room": "bedroom",
        "position": [21, 9], 
        "state": "made"
      }
    },
    "visible_agents": ["alan_002"],
    "chatable_agents": ["alan_002"],
    "heard_messages": []
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
  "timestamp": "01T04:35:20",
  "current_tile": [20, 8]
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
    "visible_objects": {
      "bed": {
        "room": "bedroom",
        "position": [21, 9],
        "state": "made"
      }
    }
  }
}
```

**Response:**
```json
{
  "status": "ok"
}
```

### Action Type Specifications

#### 1. Movement Actions
- **Planning**: LLM selects destination based on goals and environment
- **Execution**: Godot pathfinding with collision avoidance
- **Confirmation**: Position update and environmental observation

#### 2. Communication Actions  
- **Planning**: LLM generates message content and selects recipient
- **Execution**: Message queuing and proximity verification
- **Confirmation**: Delivery status and conversation threading

#### 3. Interaction Actions
- **Planning**: LLM chooses object and desired state change
- **Execution**: Object state modification in game world  
- **Confirmation**: State verification and environmental update

#### 4. Perception Actions
- **Planning**: LLM decides to actively observe environment
- **Execution**: Enhanced perception data collection
- **Confirmation**: Memory formation and salience evaluation

## 🧠 Agent Behavior System

### Personality-Driven Decision Making

#### Three-Layer Personality Model

**1. Innate Traits** (Core personality):
```python
innate: ["curious", "friendly", "introverted", "ambitious"]
```
- Influences base behavioral tendencies
- Affects social interaction preferences  
- Shapes risk tolerance and exploration behavior
- Determines default emotional responses

**2. Learned Behaviors** (Acquired skills):
```python
learned: ["cooking", "gardening", "painting", "programming"]
```
- Enables specific action capabilities
- Influences daily activity preferences
- Affects problem-solving approaches
- Shapes goal formation and planning

**3. Current State** (Dynamic status):
```python
currently: "excited about meeting someone new but tired from work"
```
- Modifies immediate decision making
- Influences interaction tone and energy
- Affects action selection priorities
- Evolves based on recent experiences

#### Daily Planning System

**Requirements-Based Scheduling:**
```python
daily_req: ["exercise", "food", "social_interaction", "creative_work"]

f_daily_schedule: [
    ["sleeping", 360],           # 6 hours
    ["morning routine", 20],     # hygiene, coffee
    ["exercise", 60],            # requirement fulfillment  
    ["creative work", 240],      # painting/main activity
    ["lunch break", 60],         # food requirement
    ["social time", 120],        # interaction requirement  
    ["evening routine", 60]      # wind-down
]
```

**Dynamic Adaptation:**
- Schedule flexibility based on opportunities
- Social interaction prioritization when others are available
- Emergency response to unexpected events
- Long-term goal progression tracking

### Memory and Learning

#### Salience-Based Memory System

**Importance Scale (1-10):**
- **1-3**: Routine activities, environmental observations
  - "I walked to the kitchen"
  - "The weather looks nice today"
  - "I heard background music"

- **4-6**: Notable interactions, minor events  
  - "I had a pleasant conversation with Alan"
  - "I finished painting a new piece"
  - "I discovered a new recipe"

- **7-9**: Significant experiences, emotional moments
  - "I had an argument with Alex about politics"
  - "I achieved a personal breakthrough in my art"
  - "I helped someone through a difficult situation"

- **10**: Life-changing events, major decisions
  - "I decided to pursue a new career path"
  - "I fell in love"
  - "I experienced a profound loss"

#### Memory Formation Process

1. **Event Occurrence**: Action or observation in environment
2. **LLM Evaluation**: Agent assesses personal significance
3. **Salience Scoring**: 1-10 importance rating based on personality
4. **Memory Storage**: Event stored with context (time, location, description)
5. **Behavioral Influence**: High-salience memories shape future decisions

#### Contextual Memory Retrieval

**Spatial Associations:**
- "What happened in the kitchen?" → cooking memories, conversations
- Location-triggered recall during navigation
- Environmental cues activate related memories

**Social Associations:**
- "What do I know about Alan?" → interaction history, relationship status
- Agent-specific memory clusters
- Personality-based interaction patterns

**Temporal Associations:**
- "What did I do yesterday morning?" → recent schedule patterns
- Time-based memory organization
- Routine vs. exceptional event differentiation

**Activity Associations:**  
- "When did I last paint?" → creative work memories
- Skill-based memory clustering
- Progress and achievement tracking

### Social Interaction Model

#### Communication Framework

**Proximity Requirements:**
- Agents must be within `chatable_agents` range
- Physical distance affects conversation initiation
- Environmental barriers (walls, doors) impact communication

**Conversation Threading:**
```python
conversation_id = "conv_12345678-abcd-ef90-1234-567890abcdef"
timeout_minutes = 30  # Conversation session duration
```

**Context Awareness:**
- Previous conversation history influences responses
- Relationship status affects interaction tone
- Shared experiences create conversational references

#### Relationship Dynamics

**First Impressions:**
- Initial interactions set relationship baseline
- Personality compatibility assessment
- Trust and rapport establishment

**Relationship Evolution:**
- Memory accumulation shapes relationship perception
- Positive/negative interaction balance
- Shared experiences strengthen bonds

**Group Dynamics:**
- Multi-agent conversation coordination
- Social hierarchy emergence
- Collective decision making processes

## 🗺️ Spatial and Environmental Systems

### Environment Design

#### Hierarchical Spatial Organization
```
House
└── First Floor
    ├── Bedroom
    │   ├── Bed (interactable)
    │   ├── Wardrobe (interactable) 
    │   └── Window (observable)
    ├── Kitchen
    │   ├── Stove (interactable)
    │   ├── Refrigerator (interactable)
    │   └── Table (interactable)
    └── Living Room
        ├── Sofa (interactable)
        ├── TV (interactable)
        └── Bookshelf (interactable)
```

#### Object State System
```json
{
  "bed": {
    "room": "bedroom",
    "position": [21, 9],
    "state": "made",  // "made" | "messy"
    "interaction_points": [[21, 8]],
    "interactions": ["sleep", "make", "mess"]
  },
  "stove": {
    "room": "kitchen", 
    "position": [15, 12],
    "state": "off",  // "off" | "on" | "cooking"
    "interaction_points": [[15, 13]],
    "interactions": ["turn_on", "turn_off", "cook"]
  }
}
```

#### Navigation System
- **Godot NavigationAgent2D**: A* pathfinding with dynamic obstacles
- **Tile-based Grid**: 16x16 pixel tiles for consistent positioning  
- **Collision Avoidance**: Multi-agent coordination during movement
- **Path Optimization**: Smooth movement with simplified paths

### Spatial Memory Integration

#### Agent Spatial Awareness
- **Vision Radius**: Configurable sight distance (default 4 tiles)
- **Object Persistence**: Remembering object locations and states
- **Room Recognition**: Understanding spatial boundaries and contexts
- **Route Learning**: Optimizing paths through repeated navigation

#### Environmental Feedback
- **State Changes**: Objects update based on agent interactions
- **Visual Feedback**: Sprite animations reflect current states
- **Persistence**: Object states maintained across sessions
- **Shared Environment**: All agents see consistent world state

## 🔧 Development and Deployment

### Setup Requirements

**Development Environment:**
```bash
# Python Backend
Python 3.8+
pip install -r requirements.txt
export OPENAI_API_KEY="your-api-key-here"

# Godot Frontend  
Godot Engine 4.4+
Open: frontend/Godot-Multi-Agent-Playground/project.godot
```

**Running the System:**
```bash
# Terminal 1: Start Backend
cd multi_agent_playground
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Frontend
# Open Godot, load project, run test_scene_navigation.tscn
```

### Configuration Options

**Backend Configuration:**
- `OPENAI_API_KEY`: OpenAI API credentials
- `OPENAI_MODEL`: Model selection (default: gpt-4o)
- `OPENAI_TEMPERATURE`: Response creativity (default: 0.7) 
- `OPENAI_MAX_TOKENS`: Response length limit

**Frontend Configuration:**
- `base_url`: Backend API endpoint (default: http://localhost:8000)
- `update_interval`: Agent action frequency (default: 5.0 seconds)
- `agent_id`: Per-agent unique identifier

**Agent Personality Configuration:**
Edit JSON files in `data/agents/[agent_id]/agent.json` to customize:
- Personality traits (`innate`, `learned`)
- Daily requirements and schedules
- Living situation and lifestyle
- Initial spatial position

### Testing and Debugging

**Debug Features:**
- **Navigation Paths**: Visual pathfinding display (N key)
- **Emoji Feedback**: Action representation toggle (F key)  
- **Agent Selection**: Cycle through agents (A key)
- **Manual Actions**: Force action requests (R key)
- **Console Logging**: Detailed backend/frontend communication logs

**Test Scenarios:**
- **Single Agent**: Basic behavior and navigation
- **Multi-Agent**: Social interaction and coordination
- **Memory Formation**: Event storage and recall
- **Environment Interaction**: Object state changes
- **Communication**: Message passing and conversation threading

## 🚀 Future Enhancements

### Scalability Improvements
- **Database Integration**: PostgreSQL/MongoDB for large-scale agent storage
- **Caching Layer**: Redis for frequent state queries and session management
- **Horizontal Scaling**: Multiple backend instances with load balancing
- **WebSocket Integration**: Real-time bidirectional communication

### Advanced AI Features
- **Custom Model Fine-tuning**: Agent-specific personality models
- **Reinforcement Learning**: Behavior optimization through experience
- **Emotional Modeling**: Complex emotional state systems
- **Collective Intelligence**: Group decision making and swarm behavior

### Extended Functionality
- **Voice Integration**: Text-to-speech for agent communication
- **Mobile Support**: Touch-based interaction for tablets/phones
- **VR/AR Integration**: Immersive agent interaction experiences
- **Multi-Environment**: Parallel simulations with agent migration

### Research Applications
- **Social Psychology**: Interaction pattern analysis and behavioral studies
- **AI Safety Research**: Multi-agent alignment and coordination studies
- **Human-Computer Interaction**: Natural language interface research
- **Behavioral Economics**: Decision-making and resource allocation studies

---

## 📚 References and Credits

- **Generative Agents Research**: [Park et al., 2023](https://arxiv.org/abs/2304.03442)
- **Kani LLM Framework**: [GitHub Repository](https://github.com/zhudotexe/kani)
- **FastAPI Documentation**: [Official Docs](https://fastapi.tiangolo.com/)
- **Godot Engine Documentation**: [Official Docs](https://docs.godotengine.org/)
- **OpenAI API**: [Platform Documentation](https://platform.openai.com/docs)

---

*Document Version: 1.0*  
*Last Updated: January 2025*  
*System Status: Active Development* 