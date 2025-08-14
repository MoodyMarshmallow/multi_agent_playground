"""
Item and object matching utilities for command processing.
"""

from typing import Dict, Optional
from ....domain.entities import Item, Character, Location


def match_item(command: str, item_dict: Dict[str, Item]) -> Item:
    """
    Check whether the name any of the items in this dictionary match the
    command. If so, return Item, else raise ValueError.
    
    Args:
        command: The command string to search for item names
        item_dict: Dictionary of item names to Item objects
        
    Returns:
        Item: The matched item
        
    Raises:
        ValueError: If no item matches the command
    """
    for item_name in item_dict:
        if item_name in command:
            item = item_dict[item_name]
            return item
    raise ValueError(f"No item found matching '{command}'")


def get_items_in_scope(character: Optional[Character] = None, game=None) -> Dict[str, Item]:
    """
    Returns a list of items in character's location, their inventory, and in open containers in the location (recursively).
    
    Args:
        character: The character to get items for (defaults to game player)
        game: The game instance
        
    Returns:
        Dict[str, Item]: Dictionary of item names to Item objects
    """
    if character is None and game:
        character = game.player
    if character is None:
        return {}
        
    items_in_scope = {}
    
    # Items in the location
    if character.location is None:
        return {}
        
    assert character.location is not None, f"Character {character.name} has no location"
    
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


def get_character_from_command(command: str, game) -> Character:
    """
    This method tries to match a character's name in the command.
    If no names are matched, it returns the player character.
    
    Args:
        command: The command string to search for character names
        game: The game instance
        
    Returns:
        Character: The matched character or player character
    """
    command = command.lower()
    for name in game.characters.keys():
        if name.lower() in command:
            return game.characters[name]
    return game.player


def get_direction_from_command(command: str, location: Location) -> Optional[str]:
    """
    Converts aliases for directions into its primary direction name.
    Returns None if no direction is found.
    
    Args:
        command: The command string to parse for directions
        location: The current location to check exits
        
    Returns:
        Optional[str]: The direction name if found, None otherwise
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
    for exit in location.connections.keys():
        if exit.lower() in command:
            return exit
    return None


def split_command(command: str, keyword: str) -> tuple[str, str]:
    """
    Splits the command string into two parts based on the keyword.

    Args:
        command: The command string to be split.
        keyword: The keyword to split the command string around.

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