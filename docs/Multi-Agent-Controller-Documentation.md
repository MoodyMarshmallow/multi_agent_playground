# Multi-Agent Controller System Documentation

## Overview

The `backend/server/controller.py` module serves as the central orchestrator for a multi-agent simulation system. It manages agent behaviors, inter-agent communication, memory processing, and decision-making through integration with Large Language Models (LLMs).

## Core Architecture

### Key Components

1. **Agent Management**: Handles individual agent state, actions, and perceptions
2. **Message Queue System**: Manages conversations between agents with timeout-based session handling
3. **Memory System**: Processes and stores agent experiences with salience-based importance scoring
4. **LLM Integration**: Uses AI models for intelligent action planning and event evaluation

## Main Functions

### 1. Agent Action Planning (`plan_next_action`)

**Purpose**: Determines the next action an agent should take based on their current perception of the environment.

**Process**:
- Loads agent data from persistent storage
- Updates agent's perception with current environment state
- Calls LLM agent to generate intelligent next action
- Converts LLM response into structured backend action
- Returns action output with metadata (emoji, timestamp, location)

**Supported Action Types**:
- **Move**: Agent moves to new coordinates
- **Chat**: Agent sends message to another agent
- **Interact**: Agent interacts with objects in environment
- **Perceive**: Agent observes surroundings (default action)

### 2. Action Confirmation (`confirm_action_and_update`)

**Purpose**: Processes completed actions and updates agent state and memory.

**Process**:
- Updates agent's current state (position, timestamp)
- Builds descriptive event string from action and perception
- Evaluates event salience (importance) using LLM
- Stores event in agent's memory with salience score
- Handles special chat message processing
- Saves updated agent state and memory

### 3. Message Management

#### Conversation Tracking (`get_or_create_conversation_id`)
- **Smart Conversation Grouping**: Groups related messages between agents
- **Timeout-Based Sessions**: Conversations expire after 30 minutes of inactivity
- **Deterministic IDs**: Creates consistent conversation IDs based on agent pairs and time

#### Message Queue (`append_message_to_queue`)
- **Persistent Storage**: Messages stored in JSON format
- **Delivery Tracking**: Tracks whether messages have been delivered
- **Location Context**: Associates messages with physical locations

### 4. Event Salience Evaluation (`evaluate_event_salience`)

**Purpose**: Uses LLM to determine how important an event is to an agent (1-10 scale).

**Benefits**:
- **Memory Prioritization**: Important events are weighted higher in memory
- **Realistic Forgetting**: Less important events may fade over time
- **Contextual Relevance**: Importance varies based on agent's personality and goals

## System Workflow

### Typical Agent Cycle

1. **Perception Phase**:
   - Agent receives current environment state
   - Includes visible objects, other agents, heard messages
   - Location and timestamp information

2. **Planning Phase**:
   - LLM analyzes agent state and perception
   - Generates contextually appropriate next action
   - Considers agent personality, goals, and memory

3. **Execution Phase**:
   - Action is performed in the environment
   - Results are captured in updated perception

4. **Memory Update Phase**:
   - Event description is generated
   - Salience is evaluated by LLM
   - Memory is updated with weighted importance
   - Agent state is persisted

### Message Handling Workflow

1. **Message Creation**:
   - Agent decides to send message via chat action
   - Message includes sender, receiver, content, timestamp

2. **Conversation Management**:
   - System determines if message belongs to existing conversation
   - Creates new conversation ID if needed
   - Groups related messages together

3. **Memory Integration**:
   - Both sender and receiver get memory events
   - Sender remembers sending the message
   - Receiver remembers receiving the message
   - Both events are evaluated for salience

## Data Structures

### Core Schemas
- **AgentPerception**: Environment state visible to agent
- **BackendAction**: Structured action commands (Move, Chat, Interact, Perceive)
- **Message**: Inter-agent communication with metadata
- **AgentActionInput/Output**: Request/response wrappers

### File Storage
- **Agent Data**: `data/agents/{agent_id}/agent.json` - Current agent state
- **Agent Memory**: `data/agents/{agent_id}/memory.json` - Event history with salience
- **Message Queue**: `data/world/messages.json` - Global message queue

## Advanced Features

### 1. Temporal Intelligence
- **Timestamp Parsing**: Handles multiple timestamp formats
- **Time-Based Decisions**: Conversations timeout, events are chronologically ordered
- **Temporal Context**: Agents understand sequence of events

### 2. Spatial Awareness
- **Location Extraction**: Determines agent location from visible objects
- **Room-Based Context**: Actions are associated with specific rooms/areas
- **Movement Tracking**: Agent positions are continuously updated

### 3. Conversation Continuity
- **Session Management**: Related messages are grouped into conversations
- **Context Preservation**: Agents can refer to earlier parts of conversations
- **Natural Timeouts**: Conversations end naturally after periods of inactivity

### 4. Memory Salience System
- **Intelligent Weighting**: Important events are remembered more strongly
- **Personalized Importance**: Same event may have different importance to different agents
- **Forgetting Simulation**: Less important events may fade over time

## Error Handling & Resilience

- **Graceful Degradation**: System continues operating if individual components fail
- **Default Fallbacks**: Safe defaults for missing data or failed LLM calls
- **File I/O Safety**: Robust JSON loading/saving with error recovery
- **Debug Logging**: Comprehensive logging for troubleshooting

## Configuration

### Constants
- `CONVERSATION_TIMEOUT_MINUTES = 30`: How long conversations stay active
- Default salience value: 5 (when LLM evaluation fails)

### File Paths
- Project root auto-detection
- Configurable agent and world data directories
- Cross-platform path handling

## Integration Points

### LLM Integration
- **Kani Framework**: Uses kani_implementation for LLM interactions
- **Async Support**: Handles asynchronous LLM calls efficiently
- **Error Recovery**: Fallback behavior when LLM services are unavailable

### External Systems
- **Frontend Integration**: Provides API endpoints for game client
- **Persistence Layer**: File-based storage for scalability
- **Modular Design**: Easy integration with different AI models or storage backends

## Performance Considerations

- **Lazy Loading**: Agents loaded only when needed
- **Efficient JSON I/O**: Minimal file operations
- **Memory Management**: Old conversations and events can be archived
- **Scalable Architecture**: Supports multiple concurrent agents

This system enables sophisticated multi-agent simulations where AI-powered agents can interact naturally, remember important events, and maintain coherent conversations over time. 