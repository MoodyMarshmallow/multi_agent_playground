# LLM Agent Implementation

This directory contains the LLM-powered agent implementation using the Kani library with OpenAI's GPT-4o.

## Files

- **`llm_agent.py`** - Main LLM agent implementation using Kani and OpenAI GPT-4o
- **`actions.py`** - Action functions (move, interact, perceive) that the LLM can call
- **`agent.py`** - Core agent class for state management
- **`../config/llm_config.py`** - Configuration settings for LLM integration

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. **Ensure agent data exists in the correct location:**
   ```
   data/agents/{agent_id}/
   ├── agent.json
   └── memory.json
   ```

## Usage

### Basic Usage (Synchronous)

The `call_llm_or_ReAct` function is the main entry point, replacing the previous placeholder function:

```python
from character_agents.llm_agent import call_llm_or_ReAct

# Agent state from your agent system
agent_state = {
    "agent_id": "alex",
    "name": "Alex",
    "curr_tile": [5, 5],
    "daily_req": ["work", "eat", "socialize"],
    "memory": [],
    "visible_objects": {},
    "visible_agents": [],
    "currently": "idle"
}

# Perception data from the environment
perception_data = {
    "visible_objects": {
        "computer": {"state": "off", "location": [5, 6]}
    },
    "visible_agents": ["bob"],
    "current_time": "2024-01-15T09:00:00Z"
}

# Get LLM-planned action
action_json = call_llm_or_ReAct(agent_state, perception_data)
```

### Advanced Usage (Asynchronous)

For better performance in async applications:

```python
from character_agents.llm_agent import call_llm_for_action

async def plan_action():
    action_json = await call_llm_for_action(agent_state, perception_data)
    return action_json
```

### Direct Agent Class Usage

For more control over the LLM agent:

```python
from character_agents.llm_agent import LLMAgent
from character_agents.agent import Agent

# Load agent from disk
agent = Agent("data/agents/alex")

# Create LLM agent
llm_agent = LLMAgent(agent)

# Plan action
action_json = await llm_agent.plan_next_action(perception_data)
```

## Action Types

The LLM can call three main action functions:

### 1. Move Action
```python
move(destination_coordinates: tuple[int, int], action_emoji: str)
```
- Moves the agent to specified coordinates
- Returns JSON with action type "move"

### 2. Interact Action
```python
interact(object: str, new_state: str, action_emoji: str)
```
- Interacts with objects to change their state
- Returns JSON with action type "interact"

### 3. Perceive Action
```python
perceive(action_emoji: str)
```
- Perceives objects and agents in visible area
- Returns JSON with action type "perceive"

## Output Format

All actions return JSON in this format:

```json
{
    "agent_id": "alex",
    "action_type": "move",
    "content": {
        "destination_coordinates": [6, 5]
    },
    "emoji": "🚶"
}
```

## Configuration

Modify settings in `../config/llm_config.py`:

```python
class LLMConfig:
    OPENAI_MODEL = "gpt-4o"           # Model to use
    OPENAI_TEMPERATURE = 0.7         # Creativity level (0-1)
    OPENAI_MAX_TOKENS = None         # Max response length
    KANI_RETRY_ATTEMPTS = 3          # Retry failed calls
    KANI_TIMEOUT = 30                # Timeout in seconds
```

## Testing

Run the example script to test the implementation:

```bash
cd backend
python example_llm_usage.py
```

## Integration

The LLM agent is already integrated into the controller system. The `server/controller.py` file imports and uses `call_llm_or_ReAct` to replace the previous placeholder function.

## Troubleshooting

### Common Issues

1. **API Key Error**: Make sure `OPENAI_API_KEY` environment variable is set
2. **Agent Not Found**: Ensure agent data exists in `data/agents/{agent_id}/`
3. **Import Errors**: Check that all dependencies are installed with `pip install -r requirements.txt`
4. **Path Issues**: Make sure you're running from the correct directory (project root)

### Error Messages

- `"OpenAI API key not found"` - Set the OPENAI_API_KEY environment variable
- `"Agent data not found"` - Check that agent.json and memory.json exist
- `"Function call failed"` - Check network connection and API key validity

## Architecture

```
LLMAgent (Kani + ActionsMixin)
├── Kani Framework
│   ├── OpenAI GPT-4o Engine
│   ├── Function Calling
│   └── Chat Management
├── ActionsMixin
│   ├── move()
│   ├── interact()
│   └── perceive()
└── Agent State Management
    ├── Personality & Traits
    ├── Memory System
    └── Perception Handling
```

The LLM agent combines Kani's powerful LLM interaction capabilities with custom action functions, creating an intelligent agent that can reason about its environment and take appropriate actions based on its personality and current situation. 