# Agent Module - CLAUDE.md

This module contains the AI agent coordination system for the multi-agent simulation framework.

## Overview

The agent module bridges LLM-powered agents with the text adventure game framework using the Kani library. It provides agent strategy protocols and coordination management.

## Key Components

### AgentManager (`manager.py`)
Central coordinator for AI agents interacting with the game world.

**Key Methods:**
- `execute_agent_turn(agent, action_result)`: Execute a single agent turn with feedback from previous action
- `get_world_state_for_agent(agent)`: Get observable world state for an agent
- `get_next_agent()`: Get next agent in turn order
- `store_action_result(agent_id, result)`: Store action results for next turn feedback

**Architecture:**
- Manages turn-based execution of AI agents
- Provides action result feedback to agents (not full world state)
- Interfaces with game loop for sequential agent execution
- Handles both successful actions and error feedback

### Agent Strategies (`agent_strategies.py`)
LLM-powered agent implementations using the Kani framework.

**AgentStrategy Protocol:**
- `select_action(action_result)`: Choose next action based on previous result
- Interface for implementing custom agent decision-making

**KaniAgent Class:**
- OpenAI-powered agent using Kani framework
- Function calling for structured action selection
- Persona-based behavior configuration
- Recent actions context to prevent loops

**Key Features:**
- Uses `@ai_function submit_command(command: str)` for action selection
- Receives action results from previous turn as feedback
- System prompts include persona and world interaction instructions
- Integrates with OpenAI API through Kani engine

## Integration Points

### With Game Loop (`../game_loop.py`)
- `AgentManager` is used by game loop for turn execution
- Agents are registered and executed in sequence
- Action results flow from game loop back to agents

### With Text Adventure Framework (`../text_adventure_games/`)
- Agents interact with game world through character objects
- Actions are parsed and executed through game framework
- World state queries go through game managers

### With Configuration (`../config/`)
- Uses schema definitions for action validation
- LLM configuration for OpenAI API keys
- Pydantic models for structured data

## Development Guidelines

### Adding New Agent Types
1. Implement the `AgentStrategy` protocol
2. Register with `AgentManager` in game loop
3. Configure persona and behavior parameters
4. Test with agent goal testing framework

### Agent Feedback System
- Agents receive **action results** from previous turn, not full world state
- Use look actions for agents to observe environment actively
- Error messages are passed as action results for failed actions
- Success descriptions provide narrative feedback

### LLM Integration
- **Required**: `OPENAI_API_KEY` environment variable
- Uses Kani framework for LLM orchestration: https://kani.readthedocs.io/en/latest/index.html
- Function calling enables structured action selection
- Persona definitions control agent behavior

## Common Patterns

### Agent Turn Execution
```python
# In game loop
action_result = agent_manager.get_previous_action_result(agent_id)
agent_manager.execute_agent_turn(agent, action_result)
schema = game.schema_exporter.get_schema()
agent_manager.store_action_result(agent_id, schema.description)
```

### Agent Registration
```python
# Create KaniAgent with persona
agent = KaniAgent(character_name="Bob", persona="I am helpful...")
agent_manager.register_agent_strategy(character, agent)
```

### World State Access
```python
# Agents must actively look to see environment
world_state = game.world_state_manager.get_world_state_for_agent(agent)
# Or use look action within game
```

## Dependencies

- `kani[openai]` - LLM agent framework (REQUIRED)
- `openai` - OpenAI API client
- Environment: `OPENAI_API_KEY` must be set

## Testing

Use the agent goal-based testing framework in `../testing/` to test agent behaviors and decision-making capabilities.