"""
Character and agent management utilities for the game state.
"""

from typing import Set, List
from backend.text_adventure_games.things import Character


class CharacterManager:
    """
    Manages active game characters/agents and turn order for the game.
    """
    
    def __init__(self, game):
        self.game = game
        self.active_agents: Set[str] = set()
        self.turn_order: List[str] = []
        self.current_agent_index = 0
        
        # Add player as active agent by default
        if game.player:
            self.active_agents.add(game.player.name)
            self.turn_order.append(game.player.name)
    
    def register_agent(self, character: Character):
        """
        Mark a character as an active agent who can take turns.
        
        Args:
            character: The Character to make an active agent
        """
        if character.name not in self.game.characters:
            raise ValueError(f"Character {character.name} not in game")
        
        self.active_agents.add(character.name)
        if character.name not in self.turn_order:
            self.turn_order.append(character.name)
    
    def get_current_agent(self) -> Character:
        """
        Get the character whose turn it currently is.
        
        Returns:
            Character: The current agent
        """
        if not self.turn_order:
            return self.game.player
        
        current_name = self.turn_order[self.current_agent_index % len(self.turn_order)]
        return self.game.characters.get(current_name, self.game.player)
    
    def advance_turn(self):
        """Advance to the next agent's turn."""
        if self.turn_order:
            self.current_agent_index = (self.current_agent_index + 1) % len(self.turn_order)
    
    def is_active_agent(self, character: Character) -> bool:
        """Check if a character is an active agent."""
        return character.name in self.active_agents