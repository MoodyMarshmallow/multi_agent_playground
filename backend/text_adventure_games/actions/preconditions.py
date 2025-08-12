"""
Precondition testing logic for actions.
"""

import logging
import inspect
from typing import Type
from backend.text_adventure_games.things import Character
from backend.text_adventure_games import actions


def test_action_preconditions(action_class: Type[actions.Action], command: str, character: Character, parser) -> bool:
    """
    Test if an action's preconditions would be satisfied without executing the action.
    
    Args:
        action_class: The action class to test
        command: The command string that would trigger this action
        character: The character attempting the action
        parser: The parser instance for error reporting
        
    Returns:
        bool: True if the action's preconditions would be satisfied
    """
    
    try:
        # Temporarily set the game player to the specified character for action instantiation
        original_player = parser.game.player
        parser.game.player = character
        
        try:
            # Create a temporary instance of the action
            # Most actions now take (game, command) as parameters
            try:
                action_instance = action_class(parser.game, command)  # type: ignore
            except TypeError:
                # Fall back to single argument constructor for legacy actions
                action_instance = action_class(parser.game)  # type: ignore
            
            # Test its preconditions
            result = action_instance.check_preconditions()
        finally:
            # Always restore the original player
            parser.game.player = original_player
        
        # Debug logging for Get action failures
        logger = logging.getLogger(__name__)
        
        if action_class.__name__ == 'Get' and not result:
            logger.debug(f"Get action precondition FAILED for command '{command}'")
            if character.location is not None:
                logger.debug(f"Character: {character.name} at {character.location.name}")
            else:
                logger.debug(f"Character: {character.name} at unknown location")
            logger.debug(f"Parser last error: {parser.last_error_message}")
            
            # Try to understand what failed by checking each condition manually
            if hasattr(action_instance, 'item'):
                item = getattr(action_instance, 'item')
                if item is None:
                    logger.debug("- Item not matched/found")
                else:
                    logger.debug(f"- Item found: {item.name}")
                    logger.debug(f"- Item location: {getattr(item, 'location', 'No location')}")
                    logger.debug(f"- Item gettable: {item.get_property('gettable', 'No gettable property')}")
                    
                    # Check if item is in location
                    if character.location is not None:
                        if item.name in character.location.items:
                            logger.debug("- Item IS in character location")
                        else:
                            logger.debug("- Item NOT in character location")
                            logger.debug(f"- Location items: {list(character.location.items.keys())}")
                    else:
                        logger.debug("- Character has no location")
        
        return result
    except Exception as e:
        # If instantiation or precondition check fails, action is not available
        logger = logging.getLogger(__name__)
        if action_class.__name__ == 'Get':
            logger.debug(f"Get action instantiation FAILED for command '{command}': {e}")
        return False