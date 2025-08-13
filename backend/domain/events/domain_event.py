"""
Domain Events - Core Event Structures
====================================
Defines the domain event structures for the event bus system.
These events represent things that happen in the simulation domain.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


@dataclass
class DomainEvent:
    """
    Base domain event structure.
    
    All events in the system inherit from this base structure to ensure
    consistent event handling and metadata tracking.
    """
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    agent_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Ensure event_type is set."""
        if not self.event_type:
            self.event_type = self.__class__.__name__.lower().replace('event', '')


@dataclass
class AgentActionEvent(DomainEvent):
    """
    Event representing an agent action in the simulation.
    
    This event type specifically handles agent actions and maintains
    compatibility with the existing AgentActionOutput format.
    """
    event_type: str = "agent_action"
    
    @classmethod
    def from_agent_action_output(cls, agent_action_output: Dict[str, Any]) -> 'AgentActionEvent':
        """Create an AgentActionEvent from AgentActionOutput data."""
        return cls(
            agent_id=agent_action_output.get('agent_id'),
            data=agent_action_output,
            metadata={
                'source': 'agent_action_output',
                'current_room': agent_action_output.get('current_room'),
                'description': agent_action_output.get('description')
            }
        )
    
    def to_agent_action_output(self) -> Dict[str, Any]:
        """Convert back to AgentActionOutput format for API compatibility."""
        return self.data.copy()


@dataclass 
class GameStateEvent(DomainEvent):
    """
    Event representing changes to the game state.
    
    Used for tracking game lifecycle events like start, pause, reset, etc.
    """
    event_type: str = "game_state"


@dataclass
class SimulationEvent(DomainEvent):
    """
    Event representing simulation-level events.
    
    Used for tracking turn progression, simulation statistics, etc.
    """
    event_type: str = "simulation"


# Event Type Constants
class EventTypes:
    """Constants for event types to ensure consistency."""
    AGENT_ACTION = "agent_action"
    GAME_STATE = "game_state" 
    SIMULATION = "simulation"