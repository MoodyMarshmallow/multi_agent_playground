"""
Kani Agent Package
==================
Contains the AgentManager class and KaniAgent implementation for managing
AI-powered agents in the text adventure game framework using the Kani library.
"""

from .manager import AgentManager
from .kani_agent import KaniAgent, AgentStrategy

__all__ = ['AgentManager', 'KaniAgent', 'AgentStrategy']