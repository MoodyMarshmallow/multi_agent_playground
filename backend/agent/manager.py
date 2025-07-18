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
from .config.schema import AgentActionOutput

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
    
    async def execute_agent_turn(self, agent: Character) -> Optional[AgentActionOutput]:
        """
        Have an agent take their turn using their strategy.
        
        Returns:
            AgentActionOutput schema if an action was executed, None if no strategy or error.
        """
        if agent.name not in self.agent_strategies:
            return None
            
        try:
            # Get world state from agent's perspective
            world_state = self.get_world_state_for_agent(agent)
            
            # Let the strategy decide
            strategy = self.agent_strategies[agent.name]
            command = await strategy.select_action(world_state)
            
            # Execute the command
            print(f"\n{agent.name}: {command}")
            result = self.game.parser.parse_command(command, character=agent)
            
            # Get the schema immediately after execution
            action_schema = self.game.get_schema()
            
            # Check if this was a noop action (non-fatal error)
            is_noop = action_schema.action.action_type == "noop"
            
            if is_noop:
                # For noop actions, provide error feedback
                print(f"[WARNING]: Command failed for {agent.name}")
                print("─" * 50)
                print(f"Error: {action_schema.description}")
                print("─" * 50)
            else:
                # For successful actions, provide normal feedback
                if isinstance(result, tuple) and len(result) >= 1:
                    description = result[0]
                    print(f"✓ Action result for {agent.name}:")
                    print("─" * 50)
                    print(description)
                    print("─" * 50)
                else:
                    print(f"✓ Action result for {agent.name}: {result}")
            
            return action_schema
            
        except Exception as e:
            print(f"Error in execute_agent_turn for {agent.name}: {e}")
            return None
    
    def get_world_state_for_agent(self, agent: Character) -> dict:
        """
        Get the observable world state for an agent.
        
        Returns:
            Dict containing location info, inventory, and available actions
        """
        location = agent.location
        
        state = {
            'agent_name': agent.name,
            'location': {
                'name': location.name,
                'description': location.description
            },
            'inventory': list(agent.inventory.keys()),
            'visible_items': [
                {'name': item.name, 'description': item.description}
                for item in location.items.values()
            ],
            'visible_characters': [
                {'name': char.name, 'description': char.description}
                for char in location.characters.values()
                if char.name != agent.name
            ],
            'available_exits': list(location.connections.keys()),
            'available_actions': self.game.parser.get_available_actions(agent)
        }
        
        return state
    
    
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