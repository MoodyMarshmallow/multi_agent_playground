"""
TurnScheduler Domain Service
============================
Pure business logic for managing turn progression and agent rotation in the
multi-agent simulation.

This domain service contains no infrastructure dependencies and works with
domain entities only.
"""

from typing import List, Optional, Dict, Any
import logging

from ..entities.agent import Agent
from ..entities.game_state import GameState


class TurnScheduler:
    """
    Domain service for managing turn progression and agent scheduling.
    
    This service handles the logic of which agent should act next,
    when to advance turns, and turn limit enforcement.
    """
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
    
    def should_continue_simulation(self, game_state: GameState) -> bool:
        """
        Determine if the simulation should continue running.
        
        Args:
            game_state: Current game state
            
        Returns:
            True if simulation should continue, False if it should stop
        """
        if not game_state.is_running:
            return False
        
        if game_state.has_reached_max_turns():
            self._logger.warning(f"Max turns ({game_state.max_turns_per_session}) reached, stopping simulation.")
            return False
        
        if not game_state.active_agents:
            self._logger.error("No active agents available, stopping simulation.")
            return False
        
        return True
    
    def get_current_agent_id(self, game_state: GameState) -> Optional[str]:
        """
        Get the ID of the agent whose turn it currently is.
        
        Args:
            game_state: Current game state
            
        Returns:
            Agent ID if available, None if no agents or invalid state
        """
        if not game_state.active_agents:
            return None
        
        if game_state.current_agent_index >= len(game_state.active_agents):
            # Reset index if it's out of bounds
            game_state.current_agent_index = 0
        
        return game_state.active_agents[game_state.current_agent_index]
    
    def advance_to_next_agent(self, game_state: GameState) -> None:
        """
        Advance the turn to the next agent in the rotation.
        
        Args:
            game_state: Current game state to update
        """
        if not game_state.active_agents:
            return
        
        # Move to next agent in round-robin fashion
        game_state.current_agent_index = (game_state.current_agent_index + 1) % len(game_state.active_agents)
        
        # Increment turn counter when we complete a full round or when explicitly advancing
        game_state.increment_turn()
    
    def should_advance_turn(self, action_ended_turn: bool, game_state: GameState) -> bool:
        """
        Determine if we should advance to the next agent.
        
        Args:
            action_ended_turn: Whether the current action ended the agent's turn
            game_state: Current game state
            
        Returns:
            True if we should advance to next agent, False if current agent continues
        """
        # Only advance if the action explicitly ended the turn
        return action_ended_turn
    
    def add_agent_to_rotation(self, game_state: GameState, agent_id: str) -> None:
        """
        Add an agent to the turn rotation.
        
        Args:
            game_state: Current game state to update
            agent_id: ID of agent to add
        """
        game_state.add_agent(agent_id)
        self._logger.info(f"Added agent {agent_id} to turn rotation")
    
    def remove_agent_from_rotation(self, game_state: GameState, agent_id: str) -> None:
        """
        Remove an agent from the turn rotation.
        
        Args:
            game_state: Current game state to update
            agent_id: ID of agent to remove
        """
        game_state.remove_agent(agent_id)
        self._logger.info(f"Removed agent {agent_id} from turn rotation")
    
    def reset_turn_state(self, game_state: GameState) -> None:
        """
        Reset the turn state to the beginning.
        
        Args:
            game_state: Current game state to reset
        """
        game_state.turn_counter = 0
        game_state.current_agent_index = 0
        game_state.last_updated = game_state.created_at
        self._logger.info("Turn state reset to beginning")
    
    def get_turn_statistics(self, game_state: GameState) -> Dict[str, Any]:
        """
        Get statistics about the current turn state.
        
        Args:
            game_state: Current game state
            
        Returns:
            Dictionary with turn statistics
        """
        if not game_state.active_agents:
            return {
                'current_turn': game_state.turn_counter,
                'active_agents': 0,
                'current_agent': None,
                'turns_remaining': game_state.max_turns_per_session - game_state.turn_counter,
                'progress_percentage': (game_state.turn_counter / game_state.max_turns_per_session) * 100
            }
        
        return {
            'current_turn': game_state.turn_counter,
            'active_agents': len(game_state.active_agents),
            'current_agent': self.get_current_agent_id(game_state),
            'current_agent_index': game_state.current_agent_index,
            'turns_remaining': max(0, game_state.max_turns_per_session - game_state.turn_counter),
            'progress_percentage': min(100.0, (game_state.turn_counter / game_state.max_turns_per_session) * 100),
            'game_duration_seconds': game_state.get_game_duration()
        }