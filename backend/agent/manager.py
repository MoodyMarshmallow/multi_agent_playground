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
            
            # Format result for readable output
            if isinstance(result, tuple) and len(result) >= 1:
                description = result[0]
                print(f"Action result passed to agent:")
                print("─" * 50)
                print(description)
                print("─" * 50)
            else:
                print(f"Action result passed to agent: {result}")
            
            # Get the schema immediately after execution
            action_schema = self.game.get_schema()
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
            'available_actions': self.get_available_actions_for_agent(agent)
        }
        
        return state
    
    def get_available_actions_for_agent(self, agent: Character) -> List[dict]:
        """
        Return all actions currently available to a character.
        
        Returns:
            List of dicts with 'command' and 'description' keys
        """
        available = []
        location = agent.location
        
        # Movement actions
        for direction, connected_loc in location.connections.items():
            # Check if the connection is blocked
            if not location.is_blocked(direction):
                available.append({
                    'command': f"go {direction}",
                    'description': f"Move {direction} to {connected_loc.name}"
                })
        
        # Item actions - Get/Take items in location
        for item_name, item in location.items.items():
            if item.get_property("gettable") is True:  # Default to not gettable
                available.append({
                    'command': f"get {item_name}",
                    'description': f"Pick up the {item.description}"
                })
                available.append({
                    'command': f"take {item_name}",
                    'description': f"Take the {item.description}"
                })
            
            # Examine actions for items in location
            available.append({
                'command': f"examine {item_name}",
                'description': f"Examine the {item.description}"
            })
            available.append({
                'command': f"look at {item_name}",
                'description': f"Look at the {item.description}"
            })
            
            # Container-specific actions
            if item.get_property("is_container", False):
                if item.get_property("is_openable", False):
                    if not item.get_property("is_open", False):
                        available.append({
                            'command': f"open {item_name}",
                            'description': f"Open the {item.description}"
                        })
                    else:
                        available.append({
                            'command': f"close {item_name}",
                            'description': f"Close the {item.description}"
                        })
                        available.append({
                            'command': f"view {item_name}",
                            'description': f"View contents of the {item.description}"
                        })
                        # Show items that can be taken from container
                        if hasattr(item, 'inventory'):
                            for container_item_name in item.inventory.keys():
                                available.append({
                                    'command': f"take {container_item_name} from {item_name}",
                                    'description': f"Take {container_item_name} from {item.description}"
                                })
            
            # Bed-specific actions
            if item.get_property("is_sleepable", False):
                available.append({
                    'command': "sleep",
                    'description': f"Sleep in the {item.description}"
                })
                if not item.get_property("is_made", True):
                    available.append({
                        'command': "make bed",
                        'description': f"Make the {item.description}"
                    })
                if item.get_property("cleanliness", 100) < 100:
                    available.append({
                        'command': "clean bed",
                        'description': f"Clean the {item.description}"
                    })
                available.append({
                    'command': "examine bed",
                    'description': f"Examine the {item.description} closely"
                })
            
            # Food/drink actions for items with those properties
            if item.get_property("is_food", False):
                available.append({
                    'command': f"eat {item_name}",
                    'description': f"Eat the {item.description}"
                })
            
            if item.get_property("is_drink", False):
                available.append({
                    'command': f"drink {item_name}",
                    'description': f"Drink the {item.description}"
                })
            
            # Lightable items
            if item.get_property("is_lightable", False) and not item.get_property("is_lit", False):
                available.append({
                    'command': f"light {item_name}",
                    'description': f"Light the {item.description}"
                })
            
            # Rose-specific actions
            if item_name == "rosebush" and item.get_property("has_rose", False):
                available.append({
                    'command': "pick rose",
                    'description': "Pick a rose from the rosebush"
                })
            
            # Weapon actions if other characters present
            if item.get_property("is_weapon", False) and len(location.characters) > 1:
                for other_name, other_char in location.characters.items():
                    if other_name != agent.name and not other_char.get_property("is_dead", False):
                        available.append({
                            'command': f"attack {other_name} with {item_name}",
                            'description': f"Attack {other_char.description} with {item.description}"
                        })
        
        # Inventory actions
        for item_name, item in agent.inventory.items():
            # Drop actions
            available.append({
                'command': f"drop {item_name}",
                'description': f"Drop the {item.description}"
            })
            
            # Examine actions for inventory items
            available.append({
                'command': f"examine {item_name}",
                'description': f"Examine the {item.description}"
            })
            
            # Container actions for items in inventory
            for location_item_name, location_item in location.items.items():
                if location_item.get_property("is_container", False) and location_item.get_property("is_open", False):
                    available.append({
                        'command': f"put {item_name} in {location_item_name}",
                        'description': f"Put {item.description} in {location_item.description}"
                    })
            
            # Food/drink actions for inventory items
            if item.get_property("is_food", False):
                available.append({
                    'command': f"eat {item_name}",
                    'description': f"Eat the {item.description}"
                })
            
            if item.get_property("is_drink", False):
                available.append({
                    'command': f"drink {item_name}",
                    'description': f"Drink the {item.description}"
                })
            
            # Light actions for inventory items
            if item.get_property("is_lightable", False) and not item.get_property("is_lit", False):
                available.append({
                    'command': f"light {item_name}",
                    'description': f"Light the {item.description}"
                })
            
            # Rose smell action
            if item_name == "rose":
                available.append({
                    'command': "smell rose",
                    'description': "Smell the rose"
                })
            
            # Weapon actions against other characters
            if item.get_property("is_weapon", False):
                for other_name, other_char in location.characters.items():
                    if other_name != agent.name and not other_char.get_property("is_dead", False):
                        available.append({
                            'command': f"attack {other_name} with {item_name}",
                            'description': f"Attack {other_char.description} with {item.description}"
                        })
        
        # Character interaction actions
        for other_name, other_char in location.characters.items():
            if other_name != agent.name:
                # Give actions
                for item_name in agent.inventory:
                    available.append({
                        'command': f"give {item_name} to {other_name}",
                        'description': f"Give {item_name} to {other_char.description}"
                    })
        
        # Fishing actions if at pond location
        if hasattr(location, 'get_property') and location.get_property("has_fish", False):
            # Check if agent has a pole
            if "pole" in agent.inventory:
                available.append({
                    'command': "catch fish with pole",
                    'description': "Catch fish using the fishing pole"
                })
            else:
                available.append({
                    'command': "catch fish",
                    'description': "Try to catch fish with hands"
                })
        
        # Door unlocking if key and locked door present
        if "key" in agent.inventory:
            for item_name, item in location.items.items():
                if item_name == "door" and item.get_property("is_locked", False):
                    available.append({
                        'command': "unlock door",
                        'description': "Unlock the door with the key"
                    })
        
        # Always available actions
        available.extend([
            {'command': 'look', 'description': 'Examine your surroundings'},
            {'command': 'describe', 'description': 'Describe the current location'},
            {'command': 'inventory', 'description': 'Check what you are carrying'},
            {'command': 'quit', 'description': 'Quit the game'}
        ])
        
        return available
    
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