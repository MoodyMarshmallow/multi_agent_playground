"""
Agent Package
=============
Contains the AgentManager class and agent strategy implementations for managing
AI-powered and manual agents in the text adventure game framework.
"""

from .manager import AgentManager
from ..infrastructure.agents.kani_agent import KaniAgent, ManualAgent, AgentStrategy

__all__ = ['AgentManager', 'KaniAgent', 'ManualAgent', 'AgentStrategy']