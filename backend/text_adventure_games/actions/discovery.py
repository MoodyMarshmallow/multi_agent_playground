"""
Action discovery and availability system.
"""

import logging
from typing import List, Dict, Any
from backend.text_adventure_games.things import Character
from .preconditions import test_action_preconditions


def discover_action_classes():
    """
    Discover all available generic action classes.
    
    Returns:
        list: Generic action classes that delegate to object capabilities
    """
    # Import and use ALL 10 generic action classes
    from backend.text_adventure_games.actions.generic import (
        EnhancedLookAction, GenericSetToStateAction, GenericStartUsingAction, GenericStopUsingAction,
        GenericTakeAction, GenericDropAction, GenericPlaceAction, GenericConsumeAction, 
        GenericExamineAction, MoveAction
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
        MoveAction
    ]
    
    return generic_actions


def get_available_actions(character: Character, parser) -> List[Dict[str, Any]]:
    """
    Return all actions currently available to a character using auto-discovery.
    
    Args:
        character: The character to get available actions for
        parser: The parser instance for precondition testing
        
    Returns:
        List of dicts with 'command' and 'description' keys
    """
    available = []
    location = character.location
    
    # Auto-discover actions using the pattern system
    action_classes = discover_action_classes()
    
    for action_class in action_classes:
        # Get all possible command patterns for this action
        patterns = action_class.get_command_patterns()
        
        # Get all applicable combinations for this action 
        try:
            combinations = list(action_class.get_applicable_combinations(character, parser))
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
                    precondition_result = test_action_preconditions(action_class, command, character, parser)
                    if precondition_result:
                        # Generate a description based on the action and items
                        from .descriptions import generate_action_description
                        description = generate_action_description(action_class, combination)
                        
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
    
    return available