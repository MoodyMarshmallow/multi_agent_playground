"""The Parser

The parser is the module that handles the natural language understanding in
the game. The players enter commands in text, and the parser interprets them
and performs the actions that the player intends.  This is the module with
the most potential for improvement using modern natural language processing.
The implementation that I have given below only uses simple keyword matching.
"""

import inspect
import re
import logging

from .things import Character, Item, Location
from . import actions, blocks
from .actions.generic import (
    GenericSetToStateAction, GenericStartUsingAction, GenericStopUsingAction,
    GenericTakeAction, GenericDropAction, GenericPlaceAction, 
    GenericConsumeAction, GenericExamineAction, GenericGoToAction, EnhancedLookAction
)


class Parser:
    """
    The Parser is the class that handles the player's input.  The player
    writes commands, and the parser performs natural language understanding
    in order to interpret what the player intended, and how that intent
    is reflected in the simulated world.
    """

    def __init__(self, game):
        # Build default scope of blocks (empty since blocks are not used)
        self.blocks = {}

        # A pointer to the game.
        self.game = game
        self.game.parser = self
        self.last_error_message = None

    def ok(self, description: str):
        """
        In the next homework, we'll replace this with a call to the OpenAI API
        in order to create more evocative descriptions.
        """
        self.last_error_message = None
        return description

    def fail(self, description: str):
        """
        In the next homework, we'll replace this with a call to the OpenAI API
        in order to create more evocative descriptions.
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
        """
        # check which character is acting (defaults to the player)
        character = self.get_character(command)
        command = command.lower()
        if "," in command:
            # Let the player type in a comma separted sequence of commands
            return "sequence"
        elif self.get_direction(command, character.location):
            # Check for the direction intent
            return "direction"
        return None

    def parse_action(self, command: str) -> actions.Action:
        """
        Routes an action described in a command to the right action class for
        performing the action. Uses only pattern-based discovery.
        """
        command = command.lower().strip()
        if command == "":
            return None
        intent = self.determine_intent(command)
        if intent == "sequence":
            return actions.ActionSequence(self.game, command)
        elif intent == "direction":
            return actions.Go(self.game, command)
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
        return None

    def parse_command(self, command: str, character: Character = None):
        """
        Parse and execute a command, optionally for a specific character.
        
        Args:
            command: The command string to parse
            character: Optional character to execute the command (defaults to player)
            
        Returns:
            (narration, schema) tuple: narration is user-facing, schema is ActionResult
        """
        # print("\n>", command, "\n", flush=True)
        
        # Set the acting character for this command
        original_player = self.game.player
        if character:
            self.game.player = character
        
        try:
            action = self.parse_action(command)
            if not action:
                narration = self.fail("I'm not sure what you want to do.")
                from backend.text_adventure_games.actions.base import ActionResult
                schema = ActionResult(description=str(narration))
                return narration, schema
            else:
                result = action()
                # result should be (narration, schema)
                if not (isinstance(result, tuple) and len(result) == 2):
                    narration = str(result)
                    from backend.text_adventure_games.actions.base import ActionResult
                    schema = ActionResult(description=narration)
                else:
                    narration, schema = result
                # If narration is None, use last error message
                if narration is None:
                    narration = self.last_error_message or "An unknown error occurred."
                # Record the last acting agent's id for schema export
                if hasattr(self.game, '_last_action_agent_id'):
                    self.game._last_action_agent_id = self.game.player.name
                # Get the narration from the ActionResult (if available)
            # Always return (narration, schema)
            return narration, schema
        finally:
            # Restore original player
            self.game.player = original_player

    @staticmethod
    def split_command(command: str, keyword: str) -> tuple[str, str]:
        """
        Splits the command string into two parts based on the keyword.

        Args:
        command (str): The command string to be split.
        keyword (str): The keyword to split the command string around.

        Returns:
        tuple: A tuple containing the part of the command before the keyword and the part after.
        """
        command = command.lower()
        keyword = keyword.lower()
        # Find the position of the keyword in the command
        keyword_pos = command.find(keyword)

        # If the keyword is not found, return the entire command and an empty string
        if keyword_pos == -1:
            return (command, "")

        # Split the command into two parts
        before_keyword = command[:keyword_pos]
        after_keyword = command[keyword_pos + len(keyword) :]

        return (before_keyword, after_keyword)

    def get_character(self, command: str) -> Character:
        """
        This method tries to match a character's name in the command.
        If no names are matched, it returns the default value.
        """
        command = command.lower()
        # matched_character_name = ""  # JD logical change
        for name in self.game.characters.keys():
            if name.lower() in command:
                return self.game.characters[name]
        return self.game.player

    def get_character_location(self, character: Character) -> Location:
        return character.location

    def match_item(self, command: str, item_dict: dict[str, Item]) -> Item:
        """
        Check whether the name any of the items in this dictionary match the
        command. If so, return Item, else return None.
        """
        for item_name in item_dict:
            if item_name in command:
                item = item_dict[item_name]
                return item
        return None

    def get_items_in_scope(self, character=None) -> dict[str, Item]:
        """
        Returns a list of items in character's location, their inventory, and in open containers in the location (recursively).
        """
        if character is None:
            character = self.game.player
        items_in_scope = {}
        # Items in the location
        for item_name, item in character.location.items.items():
            items_in_scope[item_name] = item
            # If the item is a container and open, add its contents
            if hasattr(item, 'get_property') and item.get_property('is_container', False):
                if item.get_property('is_open', False):
                    # Recursively add items in the open container
                    def add_container_items(container):
                        for subitem_name, subitem in getattr(container, 'items', {}).items():
                            items_in_scope[subitem_name] = subitem
                            if hasattr(subitem, 'get_property') and subitem.get_property('is_container', False):
                                if subitem.get_property('is_open', False):
                                    add_container_items(subitem)
                    add_container_items(item)
        # Items in inventory
        for item_name, item in character.inventory.items():
            items_in_scope[item_name] = item
        return items_in_scope

    def get_direction(self, command: str, location: Location = None) -> str:
        """
        Converts aliases for directions into its primary direction name.
        """
        command = command.lower()
        if command == "n" or "north" in command:
            return "north"
        if command == "s" or "south" in command:
            return "south"
        if command == "e" or "east" in command:
            return "east"
        if command == "w" or "west" in command:
            return "west"
        if command.endswith("go up"):
            return "up"
        if command.endswith("go down"):
            return "down"
        if command.endswith("go out"):
            return "out"
        if command.endswith("go in"):
            return "in"
        if location:
            for exit in location.connections.keys():
                if exit.lower() in command:
                    return exit
        return None

    def test_action_preconditions(self, action_class, command: str, character: Character = None) -> bool:
        """
        Test if an action's preconditions would be satisfied without executing the action.
        
        Args:
            action_class: The action class to test
            command: The command string that would trigger this action
            character: The character attempting the action (defaults to game player)
            
        Returns:
            bool: True if the action's preconditions would be satisfied
        """
        if character is None:
            character = self.game.player
        
        try:
            # Temporarily set the game player to the specified character for action instantiation
            original_player = self.game.player
            self.game.player = character
            
            try:
                # Create a temporary instance of the action
                action_instance = action_class(self.game, command)
                # Test its preconditions
                result = action_instance.check_preconditions()
            finally:
                # Always restore the original player
                self.game.player = original_player
            
            # Debug logging for Get action failures
            logger = logging.getLogger(__name__)
            
            if action_class.__name__ == 'Get' and not result:
                logger.debug(f"Get action precondition FAILED for command '{command}'")
                logger.debug(f"Character: {character.name} at {character.location.name}")
                logger.debug(f"Parser last error: {self.last_error_message}")
                
                # Try to understand what failed by checking each condition manually
                if hasattr(action_instance, 'item'):
                    if action_instance.item is None:
                        logger.debug("- Item not matched/found")
                    else:
                        logger.debug(f"- Item found: {action_instance.item.name}")
                        logger.debug(f"- Item location: {getattr(action_instance.item, 'location', 'No location')}")
                        logger.debug(f"- Item gettable: {action_instance.item.get_property('gettable', 'No gettable property')}")
                        
                        # Check if item is in location
                        if action_instance.item.name in character.location.items:
                            logger.debug("- Item IS in character location")
                        else:
                            logger.debug("- Item NOT in character location")
                            logger.debug(f"- Location items: {list(character.location.items.keys())}")
            
            return result
        except Exception as e:
            # If instantiation or precondition check fails, action is not available
            logger = logging.getLogger(__name__)
            if action_class.__name__ == 'Get':
                logger.debug(f"Get action instantiation FAILED for command '{command}': {e}")
            return False

    def discover_action_classes(self):
        """
        Discover all available generic action classes.
        
        Returns:
            list: Generic action classes that delegate to object capabilities
        """
        # Import and use ALL 10 generic action classes
        from .actions.generic import (
            EnhancedLookAction, GenericSetToStateAction, GenericStartUsingAction, GenericStopUsingAction,
            GenericTakeAction, GenericDropAction, GenericPlaceAction, GenericConsumeAction, 
            GenericExamineAction, GenericGoToAction
        )
        
        generic_actions = [
            EnhancedLookAction,
            GenericSetToStateAction,
            GenericStartUsingAction, 
            GenericStopUsingAction,
            GenericTakeAction,
            GenericDropAction,
            GenericPlaceAction,
            GenericConsumeAction,
            GenericExamineAction,
            GenericGoToAction
        ]
        
        return generic_actions

    def get_available_actions(self, character: Character) -> list[dict]:
        """
        Return all actions currently available to a character using auto-discovery.
        
        Returns:
            List of dicts with 'command' and 'description' keys
        """
        available = []
        location = character.location
        
        if not location:
            return available
        
        # Movement actions (still hardcoded as they're not pattern-based actions)
        for direction, connected_loc in location.connections.items():
            # Check if the connection is blocked
            if not location.is_blocked(direction):
                available.append({
                    'command': f"go {direction}",
                    'description': f"Move {direction} to {connected_loc.name}"
                })
        
        # Auto-discover actions using the pattern system
        action_classes = self.discover_action_classes()
        
        for action_class in action_classes:
            # Get all possible command patterns for this action
            patterns = action_class.get_command_patterns()
            
            # Get all applicable combinations for this action 
            try:
                combinations = list(action_class.get_applicable_combinations(character, self))
            except Exception:
                # If get_applicable_combinations fails, skip this action
                combinations = []
            
            # Generate commands and test them
            for pattern in patterns:
                for combination in combinations:
                    try:
                        # Fill in the pattern with the combination
                        command = pattern.format(**combination)
                        
                        # Test if this command would work
                        precondition_result = self.test_action_preconditions(action_class, command, character)
                        if precondition_result:
                            # Generate a description based on the action and items
                            description = self.generate_action_description(action_class, combination)
                            
                            available.append({
                                'command': command,
                                'description': description
                            })
                        elif action_class.__name__ == 'Get':
                            # Debug: Get action was filtered out
                            logger = logging.getLogger(__name__)
                            logger.debug(f"Get command '{command}' filtered out due to failed preconditions")
                    except (KeyError, ValueError):
                        # Pattern couldn't be filled with this combination, skip
                        continue
        
        # Add basic non-pattern actions
        available.extend([
            {'command': 'look', 'description': 'Examine your surroundings'},
            {'command': 'describe', 'description': 'Describe the current location'},
            {'command': 'inventory', 'description': 'Check what you are carrying'},
            {'command': 'quit', 'description': 'Quit the game'}
        ])
        
        return available

    def generate_action_description(self, action_class, combination):
        """
        Generate a human-readable description for an action with given item combination.
        
        Args:
            action_class: The action class
            combination: Dict with item names (e.g., {"item": "apple"})
            
        Returns:
            str: Human-readable description of the action
        """
        # Get the action's description template
        action_desc = getattr(action_class, 'ACTION_DESCRIPTION', 'Perform action')
        
        # Try to create meaningful descriptions based on action type
        if action_class.__name__ == 'Get':
            item_name = combination.get('item', 'item')
            return f"Pick up the {item_name}"
        elif action_class.__name__ == 'Drop':
            item_name = combination.get('item', 'item')
            return f"Drop the {item_name}"
        elif action_class.__name__ == 'OpenContainer':
            item_name = combination.get('item', 'container')
            return f"Open the {item_name}"
        elif action_class.__name__ == 'CloseContainer':
            item_name = combination.get('item', 'container')
            return f"Close the {item_name}"
        elif action_class.__name__ == 'ViewContainer':
            item_name = combination.get('item', 'container')
            return f"View contents of the {item_name}"
        elif action_class.__name__ == 'TakeFromContainer':
            item_name = combination.get('item', 'item')
            container_name = combination.get('container', 'container')
            return f"Take {item_name} from {container_name}"
        elif action_class.__name__ == 'PutInContainer':
            item_name = combination.get('item', 'item')
            container_name = combination.get('container', 'container')
            return f"Put {item_name} in {container_name}"
        else:
            # Generic fallback
            return action_desc

