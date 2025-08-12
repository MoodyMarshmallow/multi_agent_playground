# Config Module - CLAUDE.md

This module contains configuration and schema definitions for the multi-agent simulation framework.

## Overview

The config module provides centralized configuration management and Pydantic schema definitions for API responses, data validation, and system settings.

## Key Components

### Schema Definitions (`schema.py`)
Pydantic models for data validation and API responses.

**Core Schema Types:**

**Base Classes:**
- `Direction` - Enum for movement directions (north, south, east, west)
- `SingleTargetedAction` - Base for actions targeting a single object
- `ItemAction` - Base for actions involving items

**Action Schemas:**
- `MoveAction` - Movement commands with direction
- `GetAction` - Item pickup commands with item name
- `DropAction` - Item drop commands 
- `LookAction` - Environment observation commands
- `ExamineAction` - Detailed object examination
- `NoOpAction` - Failed/invalid action responses
- `HouseAction` - Union type for all game actions

**Response Schemas:**
- `AgentActionOutput` - Primary API response format containing:
  - `description`: Human-readable action description
  - `action`: Structured action object with discriminated union
  - `timestamp`: Action execution time
  - `agent_id`: Acting agent identifier

**Usage Patterns:**
```python
# Action validation
action_schema = AgentActionOutput(
    description="You moved to the kitchen",
    action=MoveAction(action_type="move", direction="north"),
    agent_id="agent_1"
)

# API response serialization
return action_schema.model_dump()
```

### LLM Configuration (`llm_config.py`)
Centralized configuration for LLM integration and API settings.

**LLMConfig Class:**
```python
class LLMConfig:
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: Optional[int] = None
    
    # Kani Configuration  
    KANI_RETRY_ATTEMPTS: int = 3
    KANI_TIMEOUT: int = 30
```

**Features:**
- Automatic .env file loading from project root
- Environment variable fallbacks
- Default model and parameter settings
- Kani framework integration settings

## Integration Points

### With FastAPI (`../main.py`)
- Schema models used for API response validation
- `AgentActionOutput` is the primary response format
- Automatic JSON serialization through Pydantic

### With Agent System (`../agent/`)
- LLM configuration used by KaniAgent
- OpenAI API key required for agent functionality
- Model parameters control agent behavior

### With Game Framework (`../text_adventure_games/`)
- Action schemas validate game commands
- Schema export system converts game actions to API format
- Discriminated unions enable type-safe action handling

## Development Guidelines

### Adding New Action Types
1. Define action schema class inheriting from appropriate base
2. Add discriminator field: `action_type: Literal["action_name"]`
3. Add to `HouseAction` union type
4. Implement action logic in text adventure framework
5. Update schema exporter to handle new type

### Schema Design Patterns
- Use discriminated unions for action types
- Include `action_type` literal for type discrimination
- Inherit from base classes for common fields
- Add validation using Pydantic validators
- Document schema fields with descriptions

### Configuration Management
- Use environment variables for sensitive data
- Provide sensible defaults for development
- Load .env files automatically
- Keep configuration centralized in LLMConfig

## Environment Variables

**Required:**
- `OPENAI_API_KEY` - OpenAI API key for LLM functionality

**Optional:**
- `OPENAI_MODEL` - Override default model (gpt-4o)
- `OPENAI_TEMPERATURE` - Override temperature (0.7)
- Additional LLM parameters as needed

## Common Patterns

### Action Schema Creation
```python
from backend.config.schema import AgentActionOutput, MoveAction

# Create structured action response
response = AgentActionOutput(
    description="Agent moved north to the kitchen",
    action=MoveAction(action_type="move", direction="north"),
    agent_id="bob"
)
```

### Configuration Access
```python
from backend.config.llm_config import LLMConfig

# Access configuration
api_key = LLMConfig.OPENAI_API_KEY
model = LLMConfig.OPENAI_MODEL
```

### API Response Handling
```python
# In FastAPI endpoints
@app.get("/agent_act/next", response_model=AgentActionOutput)
async def get_next_action():
    # Get action from game
    schema = game.schema_exporter.get_schema()
    return schema  # Automatic Pydantic validation
```

## Dependencies

- `pydantic` - Data validation and schema definitions
- `python-dotenv` - Environment variable loading (optional)
- `typing` - Type hints and annotations

## Testing

Schema validation can be tested using Pydantic's built-in validation:
```python
# Test schema creation and validation
action = MoveAction(action_type="move", direction="north") 
response = AgentActionOutput(description="test", action=action)
assert response.action.direction == "north"
```