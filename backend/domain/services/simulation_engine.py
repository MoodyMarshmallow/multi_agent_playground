"""
SimulationEngine Domain Service
===============================
Pure business logic for executing agent turns in the multi-agent simulation.

This domain service contains no infrastructure dependencies and works with
domain entities and protocols only.
"""

from typing import Protocol, Tuple, Optional, Dict, Any
from abc import abstractmethod

from ..entities.agent import Agent
from ..entities.turn import Turn
from ..entities.game_state import GameState


class AgentExecutor(Protocol):
    """Protocol for executing agent actions (implemented by infrastructure layer)."""
    
    @abstractmethod
    async def execute_agent_turn(self, agent: Agent, action_result: str) -> Tuple[Dict[str, Any], bool]:
        """Execute a single agent turn and return (action_schema, turn_ended)."""
        ...


class ActionEventPublisher(Protocol):
    """Protocol for publishing action events (implemented by infrastructure layer)."""
    
    @abstractmethod
    def publish_action_event(self, action_schema: Dict[str, Any]) -> None:
        """Publish an action event to the event system."""
        ...


class SimulationEngine:
    """
    Domain service for managing the core simulation logic.
    
    This service orchestrates agent turns, tracks simulation state,
    and coordinates turn progression without depending on infrastructure.
    """
    
    def __init__(self, agent_executor: AgentExecutor, event_publisher: ActionEventPublisher):
        self._agent_executor = agent_executor
        self._event_publisher = event_publisher
        self._turn_history: Dict[str, Turn] = {}
    
    async def execute_simulation_turn(
        self, 
        game_state: GameState, 
        agent: Agent, 
        previous_action_result: Optional[str] = None
    ) -> Tuple[Optional[Dict[str, Any]], bool]:
        """
        Execute a single simulation turn for the given agent.
        
        Args:
            game_state: Current game state
            agent: Agent taking the turn
            previous_action_result: Result from agent's previous action
        
        Returns:
            Tuple of (action_schema, turn_ended) or (None, False) if no action taken
        """
        if not agent.is_active:
            return None, False
        
        # Execute the agent's turn through the infrastructure layer
        try:
            action_schema, action_ended_turn = await self._agent_executor.execute_agent_turn(
                agent, previous_action_result or ""
            )
            
            if action_schema:
                # Create turn record for history
                turn = Turn.create(
                    turn_id=game_state.turn_counter,
                    agent_id=agent.agent_id,
                    action_command=action_schema.get('action', {}).get('action_type', 'unknown'),
                    action_result=action_schema.get('description', ''),
                    turn_ended=action_ended_turn,
                    metadata={'schema': action_schema}
                )
                
                # Store turn in history
                self._turn_history[f"{agent.agent_id}_{game_state.turn_counter}"] = turn
                
                # Publish the action event
                self._event_publisher.publish_action_event(action_schema)
                
                return action_schema, action_ended_turn
            
            return None, False
            
        except Exception as e:
            # Log simulation error and continue
            error_turn = Turn.create(
                turn_id=game_state.turn_counter,
                agent_id=agent.agent_id,
                action_command="error",
                action_result=f"Simulation error: {e}",
                turn_ended=True,
                metadata={'error': str(e)}
            )
            self._turn_history[f"{agent.agent_id}_{game_state.turn_counter}_error"] = error_turn
            return None, True  # End turn on error
    
    def get_agent_turn_history(self, agent_id: str, limit: int = 10) -> list[Turn]:
        """Get recent turn history for an agent."""
        agent_turns = [
            turn for turn in self._turn_history.values() 
            if turn.agent_id == agent_id
        ]
        return sorted(agent_turns, key=lambda t: t.timestamp, reverse=True)[:limit]
    
    def get_simulation_statistics(self) -> Dict[str, Any]:
        """Get statistics about the simulation."""
        total_turns = len(self._turn_history)
        agents_active = len(set(turn.agent_id for turn in self._turn_history.values()))
        
        error_turns = len([
            turn for turn in self._turn_history.values() 
            if turn.metadata and 'error' in turn.metadata
        ])
        
        return {
            'total_turns': total_turns,
            'active_agents': agents_active,
            'error_turns': error_turns,
            'success_rate': (total_turns - error_turns) / max(total_turns, 1)
        }
    
    def clear_history(self) -> None:
        """Clear the turn history (used for reset)."""
        self._turn_history.clear()