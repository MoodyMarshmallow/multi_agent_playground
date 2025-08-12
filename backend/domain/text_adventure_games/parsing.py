"""The Parser

DEPRECATED: This module now delegates to the new command processing system.
Use backend.text_adventure_games.command.parser.CommandParser instead.

The parser is the module that handles the natural language understanding in
the game. The players enter commands in text, and the parser interprets them
and performs the actions that the player intends.  This is the module with
the most potential for improvement using modern natural language processing.
The implementation that I have given below only uses simple keyword matching.
"""

from typing import Optional, Dict, List
from .command.parser import CommandParser
from .command.matcher import (
    match_item, get_items_in_scope, get_character_from_command, 
    get_direction_from_command, split_command
)
from .actions.discovery import get_available_actions
from .actions.preconditions import test_action_preconditions
from .actions.descriptions import generate_action_description
from .things import Character, Item, Location
from . import actions


class Parser:
    """
    DEPRECATED: Parser class that delegates to the new modular command processing system.
    
    The Parser is the class that handles the player's input.  The player
    writes commands, and the parser performs natural language understanding
    in order to interpret what the player intended, and how that intent
    is reflected in the simulated world.
    """

    def __init__(self, game):
        # Create the new command parser and delegate to it
        self._command_parser = CommandParser(game)
        
        # Maintain backward compatibility with old interface
        self.blocks = self._command_parser.blocks
        self.game = self._command_parser.game
        self.last_error_message = self._command_parser.last_error_message

    def ok(self, description: str):
        """Success message handler."""
        return self._command_parser.ok(description)

    def fail(self, description: str):
        """Failure message handler."""
        return self._command_parser.fail(description)

    def add_block(self, block):
        """Adds a block class to the list of blocks a parser can use."""
        return self._command_parser.add_block(block)

    def determine_intent(self, command: str):
        """Determine what command the player wants to do."""
        return self._command_parser.determine_intent(command)

    def parse_action(self, command: str) -> actions.Action:
        """Routes an action described in a command to the right action class."""
        return self._command_parser.parse_action(command)

    def parse_command(self, command: str, character: Optional[Character] = None):
        """Parse and execute a command, optionally for a specific character."""
        return self._command_parser.parse_command(command, character)

    @staticmethod
    def split_command(command: str, keyword: str) -> tuple[str, str]:
        """Splits the command string into two parts based on the keyword."""
        return split_command(command, keyword)

    def get_character(self, command: str) -> Character:
        """This method tries to match a character's name in the command."""
        return get_character_from_command(command, self.game)

    def get_character_location(self, character: Character) -> Location:
        assert character.location is not None, f"Character {character.name} has no location"
        return character.location

    def match_item(self, command: str, item_dict: Dict[str, Item]) -> Item:
        """Check whether the name any of the items match the command."""
        return match_item(command, item_dict)

    def get_items_in_scope(self, character=None) -> Dict[str, Item]:
        """Returns items in character's location, inventory, and open containers."""
        return get_items_in_scope(character, self.game)

    def get_direction(self, command: str, location: Location) -> Optional[str]:
        """Converts aliases for directions into its primary direction name."""
        return get_direction_from_command(command, location)

    def test_action_preconditions(self, action_class, command: str, character: Character) -> bool:
        """Test if an action's preconditions would be satisfied without executing."""
        return test_action_preconditions(action_class, command, character, self)

    def discover_action_classes(self):
        """Discover all available generic action classes."""
        return self._command_parser.discover_action_classes()

    def get_available_actions(self, character: Character) -> List[Dict]:
        """Return all actions currently available to a character using auto-discovery."""
        return get_available_actions(character, self)

    def generate_action_description(self, action_class, combination):
        """Generate a human-readable description for an action with given item combination."""
        return generate_action_description(action_class, combination)