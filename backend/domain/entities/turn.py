"""
Turn Domain Entity
=================
Pure domain representation of a game turn in the multi-agent simulation.
"""

from typing import Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Turn:
    """
    Domain entity representing a single game turn.
    
    This is a pure domain object with no infrastructure dependencies.
    """
    turn_id: int
    agent_id: str
    action_command: str
    action_result: str
    timestamp: datetime
    turn_ended: bool = True
    metadata: Optional[dict[str, Any]] = None
    
    def __post_init__(self):
        if self.turn_id < 0:
            raise ValueError("Turn ID must be non-negative")
        if not self.agent_id:
            raise ValueError("Agent ID cannot be empty")
        if not self.action_command:
            raise ValueError("Action command cannot be empty")
    
    @classmethod
    def create(
        cls,
        turn_id: int,
        agent_id: str,
        action_command: str,
        action_result: str,
        turn_ended: bool = True,
        metadata: Optional[dict[str, Any]] = None
    ) -> "Turn":
        """Factory method to create a new turn with current timestamp."""
        return cls(
            turn_id=turn_id,
            agent_id=agent_id,
            action_command=action_command,
            action_result=action_result,
            timestamp=datetime.now(),
            turn_ended=turn_ended,
            metadata=metadata
        )