"""
AgentManager - Game agent coordination
======================================
Contains the AgentManager class that coordinates AI agents with the
text adventure game framework.
"""

from typing import Optional, Dict, List

# Text adventure games imports
from ..text_adventure_games.things import Character
from ..text_adventure_games.games import Game

# Schema imports  
from ..config.schema import AgentActionOutput

# Local imports
from .agent_strategies import AgentStrategy


class AgentManager:
    """
    Manages the connection between Characters and their AI strategies.
    """
    def __init__(self, game: Game):
        self.game = game
        self.agent_strategies: Dict[str, AgentStrategy] = {}
        
        # Add turn management
        self.active_agents: List[str] = []
        self.current_agent_index = 0
        
        # Track the single most recent action result for each agent
        self.previous_action_results: Dict[str, str] = {}
        
    def register_agent_strategy(self, character_name: str, strategy: AgentStrategy):
        """
        Connect an AI strategy to a character.
        
        Args:
            character_name: Name of the character
            strategy: Object implementing AgentStrategy (e.g., kani agent)
        """
        if character_name not in self.game.characters:
            raise ValueError(f"Character {character_name} not found")
        
        self.agent_strategies[character_name] = strategy
        
        # Add to active agents list if not already there
        if character_name not in self.active_agents:
            self.active_agents.append(character_name)
    
    async def execute_agent_turn(self, agent: Character) -> tuple[Optional[AgentActionOutput], bool]:
        """
        Have an agent take their turn using their strategy.
        
        Returns:
            Tuple of (AgentActionOutput schema if action executed or None, action_ended_turn boolean)
        """
        if agent.name not in self.agent_strategies:
            return None, True  # Default to ending turn if no strategy
            
        try:
            # Get the previous action result for this agent (empty string for first turn)
            previous_result = self.previous_action_results.get(agent.name, "Welcome to the game! This is your first turn.")
            
            # Let the strategy decide
            strategy = self.agent_strategies[agent.name]
            command = await strategy.select_action(previous_result)
            
            # Execute the command
            print(f"\n{agent.name}: {command}")
            result = self.game.parser.parse_command(command, character=agent)
            
            # Get the schema immediately after execution
            action_schema = self.game.schema_exporter.get_schema()
            
            # Check if this was a noop action (non-fatal error)
            is_noop = action_schema.action.action_type == "noop"
            
            # Extract and store action result for next turn
            if is_noop:
                # For noop actions, store error message
                action_result = f"Action failed: {action_schema.description or 'Unknown error'}"
                print(f"[WARNING]: Command failed for {agent.name}")
                print("─" * 50)
                print(f"Error: {action_schema.description}")
                print("─" * 50)
            else:
                # For successful actions, store result description
                if isinstance(result, tuple) and len(result) >= 1:
                    action_result = result[0]
                    print(f"✓ Action result for {agent.name}:")
                    print("─" * 50)
                    print(action_result)
                    print("─" * 50)
                else:
                    action_result = str(result)
                    print(f"✓ Action result for {agent.name}: {action_result}")
            
            # Store the action result for this agent's next turn
            self.previous_action_results[agent.name] = action_result
            
            # Check if the action ended the turn
            action_ended_turn = True  # Default to ending turn
            if hasattr(self.game, '_last_executed_action') and self.game._last_executed_action:
                action_ended_turn = getattr(self.game._last_executed_action, 'ends_turn', True)
            
            return action_schema, action_ended_turn
            
        except Exception as e:
            print(f"Error in execute_agent_turn for {agent.name}: {e}")
            return None, True  # Default to ending turn on error
    
    def get_world_state_for_agent(self, agent: Character) -> dict:
        """
        DELEGATED TO GAME: Get the observable world state for an agent.
        Uses the centralized method in Game class to avoid duplication.
        
        Returns:
            Dict containing location info, inventory, and available actions
        """
        return self.game.world_state_manager.get_world_state_for_agent(agent)
    
    
    def get_next_agent(self) -> Optional[Character]:
        """Get the next agent in turn order."""
        if not self.active_agents:
            return None
            
        agent_name = self.active_agents[self.current_agent_index]
        return self.game.characters.get(agent_name)
    
    def advance_turn(self):
        """Move to the next agent's turn."""
        if self.active_agents:
            self.current_agent_index = (self.current_agent_index + 1) % len(self.active_agents)