"""
Multi-Agent Playground - Character Agent Package
================================================
Character agent package containing the core agent system implementation.

This package implements:
- Agent class for agent state management and persistence
- ActionsMixin for action functions (move, interact, perceive)
- LLMAgent for LLM-powered agent behavior using Kani
- Agent state management and perception processing

Key Classes:
- Agent: Core agent with personality, memory, and state persistence
- ActionsMixin: Mixin providing action functions for agents
- LLMAgent: Kani-based LLM agent implementation

Key Functions:
- call_llm_agent: Main entry point for LLM-based action planning

Author: Multi-Agent Playground Team
Version: 1.0.0
"""

from .agent import Agent
from .actions import ActionsMixin
from .kani_agent import LLMAgent

__version__ = "1.0.0"

__all__ = [
    "Agent",
    "ActionsMixin", 
    "LLMAgent",
]
