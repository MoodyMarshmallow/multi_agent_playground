"""
AgentStrategy Protocol - Domain Interface
==========================================
Defines the interface for agent decision-making strategies in the domain layer.
This is a Protocol (structural typing) to support Kani-based agents that must
extend the Kani class directly.
"""

from typing import Protocol


class AgentStrategy(Protocol):
    """
    Protocol for agent decision-making strategies.
    
    Note: Kani-based agents must extend the Kani class directly,
    so this is a Protocol (structural typing) not an ABC.
    """
    async def select_action(self, action_result: str) -> str:
        """Select next action based on previous action result."""
        ...
    
    @property
    def character_name(self) -> str:
        """Agent's character name."""
        ...