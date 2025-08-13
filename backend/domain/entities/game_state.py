"""
GameState Domain Entity
======================
Representation of the overall game state in the multi-agent simulation.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class GameState:
    """
    Entity representing the overall state of the game simulation.
    """
    session_id: str
    turn_counter: int = 0
    max_turns_per_session: int = 1000
    is_running: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Agent state tracking
    active_agents: List[str] = field(default_factory=list)
    current_agent_index: int = 0
    
    # Game world state
    world_name: Optional[str] = None
    world_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.session_id:
            raise ValueError("Session ID cannot be empty")
        if self.turn_counter < 0:
            raise ValueError("Turn counter must be non-negative")
        if self.max_turns_per_session <= 0:
            raise ValueError("Max turns per session must be positive")
    
    def start_game(self) -> None:
        """Start the game session."""
        self.is_running = True
        self.last_updated = datetime.now()
    
    def stop_game(self) -> None:
        """Stop the game session."""
        self.is_running = False
        self.last_updated = datetime.now()
    
    def increment_turn(self) -> None:
        """Increment the turn counter and update timestamp."""
        self.turn_counter += 1
        self.last_updated = datetime.now()
    
    def add_agent(self, agent_id: str) -> None:
        """Add an agent to the active agents list."""
        if agent_id not in self.active_agents:
            self.active_agents.append(agent_id)
            self.last_updated = datetime.now()
    
    def remove_agent(self, agent_id: str) -> None:
        """Remove an agent from the active agents list."""
        if agent_id in self.active_agents:
            self.active_agents.remove(agent_id)
            # Adjust current agent index if necessary
            if self.current_agent_index >= len(self.active_agents):
                self.current_agent_index = 0
            self.last_updated = datetime.now()
    
    def get_next_agent_id(self) -> Optional[str]:
        """Get the ID of the next agent to take a turn."""
        if not self.active_agents:
            return None
        
        agent_id = self.active_agents[self.current_agent_index]
        self.current_agent_index = (self.current_agent_index + 1) % len(self.active_agents)
        return agent_id
    
    def has_reached_max_turns(self) -> bool:
        """Check if the game has reached the maximum number of turns."""
        return self.turn_counter >= self.max_turns_per_session
    
    def get_game_duration(self) -> float:
        """Get the duration of the game in seconds."""
        return (self.last_updated - self.created_at).total_seconds()