#!/usr/bin/env python3

"""Debug match_item call specifically"""

import sys
sys.path.insert(0, 'backend')

from backend.text_adventure_games.house import build_house_game
from backend.text_adventure_games.things import Character, Item
from backend.text_adventure_games.actions.things import Get


def debug_match_item():
    """Debug the exact match_item call that's failing"""
    
    print("=== Setting Up Exact Test Environment ===")
    game = build_house_game()
    kitchen = game.locations["Kitchen"]
    
    # Add apple exactly like test does
    test_apple = Item(name="apple", description="A red apple")
    test_apple.set_property("gettable", True)
    kitchen.add_item(test_apple)
    
    # Create test character exactly like test does
    test_char = Character(
        name="collector_agent",
        description="Test agent",
        persona="Test persona"
    )
    kitchen.add_character(test_char)
    test_char.location = kitchen
    game.add_character(test_char)
    
    print(f"Kitchen items: {list(kitchen.items.keys())}")
    print(f"Character location: {test_char.location.name}")
    
    print("\n=== Direct match_item Test ===")
    command = "get apple"
    location_items = test_char.location.items
    
    print(f"Command: '{command}'")
    print(f"Location items dict: {location_items}")
    print(f"Location items keys: {list(location_items.keys())}")
    
    # Test the match_item logic manually
    matched_item = game.parser.match_item(command, location_items)
    print(f"match_item result: {matched_item}")
    
    if matched_item:
        print(f"Matched item name: {matched_item.name}")
        print(f"Matched item gettable: {matched_item.get_property('gettable')}")
    else:
        print("No item matched - debugging the loop manually:")
        for item_name in location_items:
            print(f"  Checking '{item_name}' in '{command}': {item_name in command}")
    
    print("\n=== Testing Get Action Creation ===")
    try:
        # This is what happens with the new parser interface
        parser = game.parser
        # The new parser uses character as parameter, not attribute
        print(f"Test character: {test_char}")
        print(f"Test character location: {test_char.location.name}")
        
        # Test parsing with the character parameter (new interface)
        result = parser.parse_command(command, character=test_char)
        print(f"Parse result: {result}")
        print(f"Parser last error: {parser.last_error_message}")
        
        # Check if action was executed successfully
        if hasattr(game, '_last_executed_action') and game._last_executed_action:
            last_action = game._last_executed_action
            print(f"Last executed action: {type(last_action).__name__}")
            print(f"Action character: {last_action.character}")
        else:
            print("No action was executed")
        
    except Exception as e:
        print(f"Error creating Get action: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Testing with Default Player ===")
    try:
        # Move default player to kitchen and test
        game.player.location.remove_character(game.player)
        kitchen.add_character(game.player)
        game.player.location = kitchen
        
        # Use new parser interface
        player_result = game.parser.parse_command(command, character=game.player)
        print(f"Default player parse result: {player_result}")
        
        # Check last executed action
        if hasattr(game, '_last_executed_action') and game._last_executed_action:
            last_action = game._last_executed_action
            print(f"Default player last action: {type(last_action).__name__}")
        
    except Exception as e:
        print(f"Error with default player: {e}")


if __name__ == "__main__":
    debug_match_item()