"""
Core command parsing and intent detection.
"""

from typing import Optional
from ....domain.entities.character import Character
from ....domain.actions.base_action import Action
from ....domain.actions.interaction_actions import ActionSequence
from ....domain.actions.interaction_actions import MoveAction
from .matcher import get_character_from_command, get_direction_from_command
from ....domain.actions.base_action import ActionResult


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

    def ok(self, description: str):
        """
        Success message handler.
        """
        self.last_error_message = None
        return description

    def fail(self, description: str):
        """
        Failure message handler.
        """
        self.last_error_message = description
        return description

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

    def parse_action(self, command: str) -> Action:
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
            return ActionSequence(self.game, command)
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
            
        self.fail(f"No action found for {command}")
        raise ValueError(f"No action found for {command}")

    def parse_command(self, command: str, character: Optional[Character] = None):
        """
        Parse and execute a command, optionally for a specific character.
        
        Args:
            command: The command string to parse
            character: Optional character to execute the command (defaults to player)
            
        Returns:
            tuple: (narration, schema) tuple: narration is user-facing, schema is ActionResult
        """
        # Set the acting character for this command
        original_player = self.game.player
        if character:
            self.game.player = character
        
        try:
            action = self.parse_action(command)
            if not action:
                narration = self.fail("I'm not sure what you want to do.")
                schema = ActionResult(description=str(narration))
                return narration, schema
            else:
                # Store the action instance for turn management
                self.game._last_executed_action = action
                result = action()
                # result should be (narration, schema)
                if not (isinstance(result, tuple) and len(result) == 2):
                    narration = str(result)
                    schema = ActionResult(description=narration)
                else:
                    narration, schema = result
                # If narration is None, use last error message
                if narration is None:
                    narration = self.last_error_message or "An unknown error occurred."
                # Record the last acting agent's id for schema export
                if hasattr(self.game, '_last_action_agent_id'):
                    self.game._last_action_agent_id = self.game.player.name
            return narration, schema
        finally:
            self.game.player = original_player

    def discover_action_classes(self):
        """
        Discover all available generic action classes.
        
        Returns:
            list: Generic action classes that delegate to object capabilities
        """
        # For now, return empty list - discovery will be implemented later
        return []
        return discover_action_classes()