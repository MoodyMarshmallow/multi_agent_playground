"""
Arush LLM Package
================
High-performance agent components with O(1) optimizations.

Migration Note: This package replaces the character_agent module,
providing the same interface with optimized implementations.
"""

from .utils.cache import LRUCache, AgentDataCache
from .utils.prompts import PromptTemplates
from .utils.parsers import ResponseParser, ActionValidator
from .agent.memory import AgentMemory, MemoryContextBuilder
from .agent.location import LocationTracker

# Migration compatibility - provide legacy interfaces
from .integration.character_agent_adapter import CharacterAgentAdapter

__version__ = "0.1.0"
__author__ = "Arush LLM Team"

__all__ = [
    # Cache utilities
    "LRUCache",
    "AgentDataCache",
    
    # Prompt utilities
    "PromptTemplates",
    
    # Parser utilities
    "ResponseParser", 
    "ActionValidator",
    
    # Agent components
    "AgentMemory",
    "MemoryContextBuilder",
    "LocationTracker",
    
    # Migration compatibility
    "CharacterAgentAdapter",
]
