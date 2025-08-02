"""
Utilities for the text adventure game framework.

This package contains modules for:
- discovery: Capability discovery logic
- Helper functions for common operations
"""

# Re-export capability protocols from the main capabilities module
from ..capabilities import (
    ActionResult,
    Activatable,
    Openable, 
    Lockable,
    Usable,
    Container,
    Recipient,
    Giver,
    Conversational,
    Consumable,
    Examinable
)

# Helper functions
def remove_item_safely(location, item, character):
    """
    Safely remove item from location, handling both Location and Container types.
    
    This function abstracts away the differences between Location and Container
    remove_item method signatures:
    - Location.remove_item(item) - takes item object
    - Container.remove_item(item_name: str, character) - takes item name and character
    
    Args:
        location: Location or Container object to remove item from
        item: Item object to remove
        character: Character performing the action
    
    Returns:
        ActionResult or None depending on location type
    """
    if hasattr(location, 'inventory'):  # It's a Container
        return location.remove_item(item.name, character)
    else:  # It's a Location
        return location.remove_item(item)