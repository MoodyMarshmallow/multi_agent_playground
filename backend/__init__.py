"""
Multi-Agent Playground - Backend Package
========================================
Main backend package for the multi-agent simulation system.

This package provides:
- FastAPI server endpoints for agent communication
- LLM-powered character agents with personality and memory
- Action system for agent interactions (move, interact, perceive)
- Configuration management for LLM integration
- Memory and spatial reasoning capabilities

Entry Points:
- Run server: python3 -m backend
- Agent system: backend.character_agent
- Memory system: backend.memory
- Configuration: backend.config

Author: Multi-Agent Playground Team
Version: 1.0.0
"""

# Server components
from .server.controller import plan_next_action

# Character agent system - using arush_llm
from .arush_llm.integration.character_agent_adapter import CharacterAgentAdapter as Agent
from .character_agent.actions import ActionsMixin  # Keep for action interfaces
from .character_agent.kani_agent import LLMAgent    # Keep for LLM interfaces

# Configuration
from .config.llm_config import LLMConfig
from .config.schema import (
    AgentActionInput, 
    AgentActionOutput, 
    AgentPerception, 
    StatusMsg
)

# Memory system
from .memory import SpatialMemory

__version__ = "1.0.0"

__all__ = [
    # Server functions
    "plan_next_action",
    
    # Agent classes
    "Agent", 
    "ActionsMixin",
    "LLMAgent",
    
    # Configuration
    "LLMConfig",
    
    # Data models
    "AgentActionInput",
    "AgentActionOutput", 
    "AgentPerception",
    "StatusMsg",
    
    # Memory
    "SpatialMemory",
]
