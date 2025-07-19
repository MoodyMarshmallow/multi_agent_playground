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
        # This is what happens in Get.__init__
        parser = game.parser
        parser.character = test_char  # Set the character for parser
        
        print(f"Parser character: {parser.character}")
        print(f"Parser character location: {parser.character.location.name}")
        
        # Create Get action (this calls match_item)
        get_action = Get(game, command)
        print(f"Get action item: {get_action.item}")
        print(f"Get action character: {get_action.character}")
        print(f"Get action location: {get_action.location}")
        
        # Test preconditions
        preconditions_pass = get_action.check_preconditions()
        print(f"Preconditions pass: {preconditions_pass}")
        
        if not preconditions_pass:
            print(f"Parser last error: {parser.last_error_message}")
        
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
        
        parser.character = game.player
        
        get_action_player = Get(game, command)
        print(f"Default player Get action item: {get_action_player.item}")
        
        preconditions_player = get_action_player.check_preconditions()
        print(f"Default player preconditions pass: {preconditions_player}")
        
    except Exception as e:
        print(f"Error with default player: {e}")


if __name__ == "__main__":
    debug_match_item()