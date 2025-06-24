"""
Integration Package - Controller Compatibility
==============================================
Provides drop-in replacements for existing controller functions.
"""

from .controller import (
    call_llm_agent,
    create_llm_agent,
    get_llm_agent, 
    remove_llm_agent,
    clear_all_llm_agents,
    get_active_agent_count
)
from .objects import ObjectManager

__all__ = [
    "call_llm_agent",
    "create_llm_agent",
    "get_llm_agent",
    "remove_llm_agent", 
    "clear_all_llm_agents",
    "get_active_agent_count",
    "ObjectManager"
] 