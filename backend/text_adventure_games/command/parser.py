"""
Core command parsing and intent detection.
"""

from typing import Optional
from backend.text_adventure_games.things import Character
from backend.text_adventure_games import actions
from backend.text_adventure_games.actions.generic import MoveAction
from .matcher import get_character_from_command, get_direction_from_command


class CommandParser:
    """
    The CommandParser handles the player's input and performs natural language understanding
    to interpret what the player intended.
    """

    def __init__(self, game):
        # Build default scope of blocks (empty since blocks are not used)
        self.blocks = {}

        # A pointer to the game.
        self.game = game
        self.last_error_message = None


    def add_block(self, block):
        """
        Adds a block class to the list of blocks a parser can use. This is
        primarily useful for loading game states from a save.
        """
        self.blocks[block.__class__.__name__] = block

    def determine_intent(self, command: str):
        """
        This function determines what command the player wants to do.
        Only handles sequences and directions - all other actions use pattern-based discovery.
        
        Args:
            command: The command string to analyze
            
        Returns:
            str: The intent ("sequence", "direction", or None)
        """
        # check which character is acting (defaults to the player)
        character = get_character_from_command(command, self.game)
        command = command.lower()
        if "," in command:
            # Let the player type in a comma separted sequence of commands
            return "sequence"
        elif character.location is not None and get_direction_from_command(command, character.location):
            # Check for the direction intent
            return "direction"
        return None

    def parse_action(self, command: str) -> actions.Action:
        """
        Routes an action described in a command to the right action class for
        performing the action. Uses only pattern-based discovery.
        
        Args:
            command: The command string to parse
            
        Returns:
            actions.Action: The parsed action instance
            
        Raises:
            ValueError: If no action can be found for the command
        """
        command = command.lower().strip()
        if command == "":
            raise ValueError("Empty command provided")
            
        intent = self.determine_intent(command)
        if intent == "sequence":
            return actions.ActionSequence(self.game, command)
        elif intent == "direction":
            return MoveAction(self.game, command)
        else:
            # Use pattern-based discovery for all other actions
            action_classes = self.discover_action_classes()
            for action_class in action_classes:
                patterns = action_class.get_command_patterns()
                for pattern in patterns:
                    # Check if command matches pattern (basic word matching)
                    pattern_words = pattern.lower().split()
                    command_words = command.split()
                    if len(command_words) >= len(pattern_words):
                        # Check if non-placeholder words match
                        matches = True
                        for i, pattern_word in enumerate(pattern_words):
                            if not pattern_word.startswith('{') and not pattern_word.endswith('}'):
                                if i >= len(command_words) or command_words[i] != pattern_word:
                                    matches = False
                                    break
                        if matches:
                            return action_class(self.game, command)
            
        self.last_error_message = f"No action found for {command}"
        raise ValueError(f"No action found for {command}")

    def parse_command(self, command: str, character: Optional[Character] = None):
        """
        Parse and execute a command, optionally for a specific character.
        
        Args:
            command: The command string to parse
            character: Optional character to execute the command (defaults to player)
            
        Returns:
            ActionResult: The result of executing the action
        """
        # Set the acting character for this command
        original_player = self.game.player
        if character:
            self.game.player = character
        
        try:
            action = self.parse_action(command)
            if not action:
                self.last_error_message = "I'm not sure what you want to do."
                from backend.text_adventure_games.actions.base import ActionResult
                result = ActionResult(description=self.last_error_message or "I'm not sure what you want to do.")
                return result
            else:
                # Store the action instance for turn management
                self.game._last_executed_action = action
                result = action()
                # All actions now return ActionResult directly
                if not hasattr(result, 'description'):
                    # Fallback - create ActionResult from string
                    from backend.text_adventure_games.actions.base import ActionResult
                    result = ActionResult(description=str(result))
                
                # Record the last acting agent's id for schema export
                if hasattr(self.game, '_last_action_agent_id'):
                    self.game._last_action_agent_id = self.game.player.name
                    
                return result
        finally:
            self.game.player = original_player

    def discover_action_classes(self):
        """
        Discover all available generic action classes.
        
        Returns:
            list: Generic action classes that delegate to object capabilities
        """
        from backend.text_adventure_games.actions.discovery import discover_action_classes
        return discover_action_classes()