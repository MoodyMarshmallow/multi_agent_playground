#!/usr/bin/env python3

"""Debug house setup differences"""

import sys
sys.path.insert(0, 'backend')

from backend.text_adventure_games.world import build_house_game


def debug_house_setup():
    """Check default house setup vs test modifications"""
    
    print("=== Default House Setup ===")
    game = build_house_game()
    kitchen = game.locations["Kitchen"]
    
    print(f"Kitchen items by default: {list(kitchen.items.keys())}")
    for item_name, item in kitchen.items.items():
        print(f"  - {item_name}: {item.description}")
        print(f"    gettable: {item.get_property('gettable', False)}")
        print(f"    id: {id(item)}")
    
    print(f"\nPlayer location: {game.player.location.name}")
    print(f"Player id: {id(game.player)}")
    
    # Test with player in kitchen
    print("\n=== Moving Player to Kitchen ===")
    game.player.location.remove_character(game.player) 
    kitchen.add_character(game.player)
    game.player.location = kitchen
    
    available_actions = game.parser.get_available_actions(game.player)
    get_apple_actions = [a['command'] for a in available_actions if 'get apple' in a['command']]
    
    print(f"Available actions with default player: {len(available_actions)}")
    print(f"Get apple actions: {get_apple_actions}")
    
    print("\n=== Test Environment Setup (Adding Apple Like Test) ===")
    from backend.text_adventure_games.things import Item
    
    # This is what the test does - it adds an apple
    test_apple = Item(name="apple", description="A red apple")
    test_apple.set_property("gettable", True)
    
    print(f"Before adding test apple: {list(kitchen.items.keys())}")
    kitchen.add_item(test_apple)  # This might overwrite!
    print(f"After adding test apple: {list(kitchen.items.keys())}")
    
    for item_name, item in kitchen.items.items():
        print(f"  - {item_name}: {item.description}")
        print(f"    gettable: {item.get_property('gettable', False)}")
        print(f"    id: {id(item)}")
    
    # Test again with overwritten apple
    available_actions_after = game.parser.get_available_actions(game.player)
    get_apple_actions_after = [a['command'] for a in available_actions_after if 'get apple' in a['command']]
    
    print(f"\nAvailable actions after test setup: {len(available_actions_after)}")
    print(f"Get apple actions after test setup: {get_apple_actions_after}")
    
    return {
        'before': get_apple_actions,
        'after': get_apple_actions_after
    }


if __name__ == "__main__":
    result = debug_house_setup()
    
    print("\n=== COMPARISON ===")
    print(f"Before test setup: {result['before']}")
    print(f"After test setup: {result['after']}")