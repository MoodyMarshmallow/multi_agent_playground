"""
World state queries and utilities.
"""

from typing import Dict, List, Any
from backend.text_adventure_games.things import Character, Location


class WorldStateManager:
    """
    Manages world state queries and provides centralized access to world information.
    """
    
    def __init__(self, game):
        self.game = game
    
    def _get_agent_inventory_names(self, agent: Character) -> List[str]:
        """Get agent inventory as list of item names."""
        return list(agent.inventory.keys())
    
    def _get_visible_items(self, location: Location) -> List[Dict[str, str]]:
        """Get visible items in location with name and description."""
        return [
            {'name': item.name, 'description': item.description}
            for item in location.items.values()
        ]
    
    def _get_visible_characters(self, location: Location, exclude_agent: Character) -> List[Dict[str, str]]:
        """Get visible characters in location excluding the specified agent."""
        return [
            {'name': char.name, 'description': char.description}
            for char in location.characters.values()
            if char.name != exclude_agent.name
        ]
    
    def _get_formatted_exits(self, location: Location) -> List[str]:
        """Get exits formatted with destination names."""
        return [f"{direction} to {destination.name}" 
                for direction, destination in location.connections.items()]
    
    def _get_empty_world_state(self, agent_name: str) -> Dict[str, Any]:
        """Return empty world state for agents with no location."""
        return {
            'agent_name': agent_name,
            'location': {'name': 'Nowhere', 'description': 'You are in a void.'},
            'inventory': [],
            'visible_items': [],
            'visible_characters': [],
            'available_exits': [],
            'available_actions': []
        }

    def get_world_state_for_agent(self, agent: Character) -> Dict[str, Any]:
        """
        CENTRALIZED METHOD: Get the observable world state for an agent.
        This is the single source of truth for world state building.
        
        Args:
            agent: The character to get world state for
            
        Returns:
            Dict containing location info, inventory, and available actions
        """
        if agent.location is None:
            return self._get_empty_world_state(agent.name)
            
        location = agent.location
        
        # Get available actions using the parser's action discovery
        available_actions = []
        if hasattr(self.game, 'parser'):
            from backend.text_adventure_games.actions.discovery import get_available_actions
            available_actions = get_available_actions(agent, self.game.parser)
        
        return {
            'agent_name': agent.name,
            'location': {
                'name': location.name,
                'description': location.description
            },
            'inventory': self._get_agent_inventory_names(agent),
            'visible_items': self._get_visible_items(location),
            'visible_characters': self._get_visible_characters(location, agent),
            'available_exits': self._get_formatted_exits(location),
            'available_actions': available_actions
        }