# Data Module - CLAUDE.md

This file provides guidance to Claude Code when working with the data module of the multi-agent simulation framework.

## Module Overview

The data module contains persistent storage for agent configurations, memory, and world state. This directory serves as the runtime data store for the simulation.

## Directory Structure

### Agent Data (`agents/`)
Contains individual agent configurations and memory persistence:
- **agent.json**: Agent configuration including persona, behavior settings, and metadata
- **memory.json**: Agent memory state and conversation history

Each agent has its own subdirectory (e.g., `alan_002/`, `alex/`, `alex_001/`, `test_agent/`)

### World Data (`world/`)
Contains global world state and events:
- **messages.json**: World events, messages, and interaction history

## Data Format

### Agent Configuration (agent.json)
Typical structure includes:
- Agent identifier and name
- Persona and behavioral instructions
- Initial world state preferences
- Configuration metadata

### Agent Memory (memory.json)
Contains:
- Conversation history with the game world
- Action results and feedback
- State information for persistence across sessions

### World Messages (messages.json)
Contains:
- Global game events
- Inter-agent communications
- World state change notifications

## Development Guidelines

### Working with Agent Data
- **Never manually edit** agent memory files during active sessions
- Agent data is automatically managed by the backend system
- Use backend APIs to modify agent configurations safely

### Adding New Agents
1. Create new directory under `agents/` with agent identifier
2. Backend will automatically generate `agent.json` and `memory.json`
3. Configure agent in `backend/game_loop.py` for registration

### Data Persistence
- Files are automatically updated during game execution
- Memory files maintain conversation context between sessions
- World messages provide event history for analysis

### Backup and Recovery
- Data directory should be backed up regularly
- Individual agent directories can be copied for agent duplication
- Clear memory.json to reset agent memory state

## Important Notes

### File Access
- Data files may be locked during active game sessions
- Always stop the backend server before manual data manipulation
- Use appropriate file locking when accessing data programmatically

### Data Integrity
- JSON files must maintain valid structure
- Corrupted agent memory can be reset by deleting memory.json
- World messages maintain chronological order

### Testing
- Use separate data directories for testing environments
- Test agents use `test_agent/` directory by convention
- Clear test data between test runs for consistency

## Common Patterns

### Agent Reset
```bash
# Reset agent memory
rm data/agents/agent_name/memory.json

# Reset world state
rm data/world/messages.json
```

### Agent Duplication
```bash
# Copy agent configuration
cp -r data/agents/source_agent data/agents/new_agent
# Edit agent.json in new directory for unique identifier
```

### Data Analysis
- Use `messages.json` for world event analysis
- Agent memory files contain conversation patterns
- Combine data for multi-agent interaction analysis