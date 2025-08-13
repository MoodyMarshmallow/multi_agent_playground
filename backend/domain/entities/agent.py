"""
Agent Domain Entity
==================
Pure domain representation of an agent in the multi-agent simulation.
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class Agent:
    """
    Domain entity representing an agent in the simulation.
    
    This is a pure domain object with no infrastructure dependencies.
    """
    agent_id: str
    character_name: str
    persona: str
    current_location: Optional[str] = None
    is_active: bool = True
    
    def __post_init__(self):
        if not self.agent_id:
            raise ValueError("Agent ID cannot be empty")
        if not self.character_name:
            raise ValueError("Character name cannot be empty")
    
    def activate(self) -> None:
        """Activate the agent for participation in turns."""
        self.is_active = True
    
    def deactivate(self) -> None:
        """Deactivate the agent from participation in turns."""
        self.is_active = False
    
    def update_location(self, location: str) -> None:
        """Update the agent's current location."""
        self.current_location = location