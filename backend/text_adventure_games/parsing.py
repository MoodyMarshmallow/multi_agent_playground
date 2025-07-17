"""The Parser

The parser is the module that handles the natural language understanding in
the game. The players enter commands in text, and the parser interprets them
and performs the actions that the player intends.  This is the module with
the most potential for improvement using modern natural language processing.
The implementation that I have given below only uses simple keyword matching.
"""

import inspect
import textwrap
import re

from .things import Character, Item, Location
from . import actions, blocks


class Parser:
    """
    The Parser is the class that handles the player's input.  The player
    writes commands, and the parser performs natural language understanding
    in order to interpret what the player intended, and how that intent
    is reflected in the simulated world.
    """

    def __init__(self, game):
        # A list of the commands that the player has issued,
        # and the respones given to the player.
        self.command_history = []

        # Build default scope of actions
        self.actions = game.default_actions()

        # Build default scope of blocks
        self.blocks = game.default_blocks()

        # A pointer to the game.
        self.game = game
        self.game.parser = self
        self.last_error_message = None

    def ok(self, description: str):
        """
        In the next homework, we'll replace this with a call to the OpenAI API
        in order to create more evocative descriptions.
        """
        self.add_description_to_history(description)
        self.last_error_message = None
        return description

    def fail(self, description: str):
        """
        In the next homework, we'll replace this with a call to the OpenAI API
        in order to create more evocative descriptions.
        """
        self.last_error_message = description
        return description

    @staticmethod
    def wrap_text(text: str, width: int = 80) -> str:
        """
        Keeps text output narrow enough to easily be read
        """
        lines = text.split("\n")
        wrapped_lines = [textwrap.fill(line, width) for line in lines]
        return "\n".join(wrapped_lines)

    def add_command_to_history(self, command: str):
        message = {"role": "user", "content": command}
        self.command_history.append(message)
        # CCB - todo - manage command_history size

    def add_description_to_history(self, description: str):
        message = {"role": "assistant", "content": description}
        self.command_history.append(message)
        # CCB - todo - manage command_history size

    def add_action(self, action: actions.Action):
        """
        Add an Action class to the list of actions a parser can use
        """
        self.actions[action.action_name()] = action

    def add_block(self, block):
        """
        Adds a block class to the list of blocks a parser can use. This is
        primarily useful for loading game states from a save.
        """
        self.blocks[block.__class__.__name__] = block

    def init_actions(self):
        self.actions = {}
        for member in dir(actions):
            attr = getattr(actions, member)
            if inspect.isclass(attr) and issubclass(attr, actions.Action):
                # dont include base class
                if not attr == actions.Action:
                    self.add_action(attr)

    def determine_intent(self, command: str):
        """
        This function determines what command the player wants to do.
        Here we have implemented it with a simple keyword match. Later
        we will use AI to do more flexible matching.
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
        elif command == "look" or command == "l":
            # when the user issues a "look" command, re-describe what they see
            return "describe"
        elif "examine " in command or command.startswith("x "):
            return "examine"
        elif "take " in command or "get " in command:
            return "take"
        elif "light" in command:
            return "light"
        elif "drop " in command:
            return "drop"
        elif (
            "eat " in command
            or "eats " in command
            or "ate " in command
            or "eating " in command
        ):
            return "eat"
        elif "drink" in command:
            return "drink"
        elif "give" in command:
            return "give"
        elif "attack" in command or "hit " in command or "hits " in command:
            return "attack"
        elif "inventory" in command or command == "i":
            return "inventory"
        elif "quit" in command:
            return "quit"
        else:
            for _, action in self.actions.items():
                aliases = [action.action_name()]
                if getattr(action, "ACTION_ALIASES", None):
                    aliases += action.ACTION_ALIASES
                for alias in aliases:
                    # Match if command is exactly alias or starts with alias + space
                    if command == alias or command.startswith(alias + " "):
                        return action.action_name()
        return None

    def parse_action(self, command: str) -> actions.Action:
        """
        Routes an action described in a command to the right action class for
        performing the action.
        """
        command = command.lower().strip()
        if command == "":
            return None
        intent = self.determine_intent(command)
        if intent in self.actions:
            action = self.actions[intent]
            return action(self.game, command)
        elif intent == "direction":
            return actions.Go(self.game, command)
        elif intent == "take":
            return actions.Get(self.game, command)
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
        # add this command to the history
        self.add_command_to_history(command)
        
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

    def get_available_actions(self, character: Character) -> list[dict]:
        """
        Return all actions currently available to a character.
        
        Returns:
            List of dicts with 'command' and 'description' keys
        """
        available = []
        location = character.location
        
        if not location:
            return available
        
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
                    if other_name != character.name and not other_char.get_property("is_dead", False):
                        available.append({
                            'command': f"attack {other_name} with {item_name}",
                            'description': f"Attack {other_char.description} with {item.description}"
                        })
        
        # Inventory actions
        for item_name, item in character.inventory.items():
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
                    if other_name != character.name and not other_char.get_property("is_dead", False):
                        available.append({
                            'command': f"attack {other_name} with {item_name}",
                            'description': f"Attack {other_char.description} with {item.description}"
                        })
        
        # Character interaction actions
        for other_name, other_char in location.characters.items():
            if other_name != character.name:
                # Give actions
                for item_name in character.inventory:
                    available.append({
                        'command': f"give {item_name} to {other_name}",
                        'description': f"Give {item_name} to {other_char.description}"
                    })
        
        # Fishing actions if at pond location
        if hasattr(location, 'get_property') and location.get_property("has_fish", False):
            # Check if character has a pole
            if "pole" in character.inventory:
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
        if "key" in character.inventory:
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

    def print_narration(self, narration):
        # Always print a blank line before narration for consistent output
        print("")
        if narration and narration.lower() != "none":
            print(narration)
            if narration == self.last_error_message:
                print("I'm not sure what you want to do.\n")
        else:
            print("I'm not sure what you want to do.\n")
        print("")
