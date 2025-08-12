"""
Action description generation utilities.
"""

from typing import Dict, Any, Type
from backend.text_adventure_games import actions


def generate_action_description(action_class: Type[actions.Action], combination: Dict[str, Any]) -> str:
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
    action_name = action_class.__name__
    
    if action_name == 'GenericTakeAction':
        item_name = combination.get('item', 'item')
        return f"Pick up the {item_name}"
    elif action_name == 'GenericDropAction':
        item_name = combination.get('item', 'item')
        return f"Drop the {item_name}"
    elif action_name == 'GenericSetToStateAction':
        target_name = combination.get('target', 'object')
        return f"Change the state of the {target_name}"
    elif action_name == 'GenericPlaceAction':
        item_name = combination.get('item', 'item')
        container_name = combination.get('container', 'container')
        return f"Put {item_name} in {container_name}"
    elif action_name == 'GenericConsumeAction':
        item_name = combination.get('item', 'item')
        return f"Consume the {item_name}"
    elif action_name == 'GenericExamineAction':
        item_name = combination.get('item', 'item')
        return f"Examine the {item_name}"
    elif action_name == 'GenericStartUsingAction':
        item_name = combination.get('item', 'item')
        return f"Start using the {item_name}"
    elif action_name == 'GenericStopUsingAction':
        item_name = combination.get('item', 'item')
        return f"Stop using the {item_name}"
    elif action_name == 'EnhancedLookAction':
        return "Look around the current location"
    elif action_name == 'MoveAction':
        direction = combination.get('direction', 'somewhere')
        return f"Move {direction}"
    else:
        # Generic fallback
        return action_desc