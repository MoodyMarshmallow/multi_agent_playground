"""
Multi-Agent Playground - Configuration Package
==============================================
Configuration package containing LLM settings and data schemas.

This package provides:
- LLM configuration management (API keys, model parameters)
- Pydantic data schemas for API communication
- Environment variable handling

Key Classes:
- LLMConfig: Configuration class for LLM settings
- AgentActionInput: Schema for frontend → backend action requests
- AgentActionOutput: Schema for backend → frontend action responses  
- AgentPerception: Schema for agent perception data
- StatusMsg: Simple status response schema

Author: Multi-Agent Playground Team
Version: 1.0.0
"""

from .llm_config import LLMConfig
from .schema import (
    AgentActionInput,
    AgentActionOutput,
    AgentPerception,
    StatusMsg,
    AgentActionContent
)

__version__ = "1.0.0"

__all__ = [
    "LLMConfig",
    "AgentActionInput",
    "AgentActionOutput", 
    "AgentPerception",
    "StatusMsg",
    "AgentActionContent",
]
