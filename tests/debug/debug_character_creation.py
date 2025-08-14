#!/usr/bin/env python3

"""Debug character creation differences"""

import sys
sys.path.insert(0, 'backend')

from backend.text_adventure_games.world import build_house_game
from backend.text_adventure_games.things import Character, Item


def debug_character_differences():
    """Compare default player vs test-created character"""
    
    print("=== Setting Up Game ===")
    game = build_house_game()
    kitchen = game.locations["Kitchen"]
    
    # Add apple like test does
    test_apple = Item(name="apple", description="A red apple")
    test_apple.set_property("gettable", True)
    kitchen.add_item(test_apple)
    
    print(f"Kitchen items: {list(kitchen.items.keys())}")
    
    print("\n=== Testing with Default Player ===")
    # Move default player to kitchen
    game.player.location.remove_character(game.player)
    kitchen.add_character(game.player)
    game.player.location = kitchen
    
    print(f"Default player name: {game.player.name}")
    print(f"Default player location: {game.player.location.name}")
    print(f"Default player in game.characters: {game.player.name in game.characters}")
    
    default_actions = game.parser.get_available_actions(game.player)
    default_get_apple = [a['command'] for a in default_actions if 'get apple' in a['command']]
    
    print(f"Default player actions: {len(default_actions)}")
    print(f"Default player get apple: {default_get_apple}")
    
    print("\n=== Testing with Test-Created Character ===")
    # Create character like test runner does
    test_char = Character(
        name="collector_agent",
        description="Test agent: Agent should find and collect an apple",
        persona="You want should find and collect an apple."
    )
    
    # Add to kitchen and game like test runner does
    kitchen.add_character(test_char)
    test_char.location = kitchen
    game.add_character(test_char)
    
    print(f"Test character name: {test_char.name}")
    print(f"Test character location: {test_char.location.name}")
    print(f"Test character in game.characters: {test_char.name in game.characters}")
    
    test_actions = game.parser.get_available_actions(test_char)
    test_get_apple = [a['command'] for a in test_actions if 'get apple' in a['command']]
    
    print(f"Test character actions: {len(test_actions)}")
    print(f"Test character get apple: {test_get_apple}")
    
    print("\n=== Detailed Comparison ===")
    print("Default player actions:")
    for action in default_actions:
        if 'apple' in action['command']:
            print(f"  - {action['command']}: {action['description']}")
    
    print("Test character actions:")
    for action in test_actions:
        if 'apple' in action['command']:
            print(f"  - {action['command']}: {action['description']}")
    
    print("\n=== Character Properties Comparison ===")
    print(f"Default player type: {type(game.player)}")
    print(f"Test character type: {type(test_char)}")
    print(f"Same location object: {game.player.location is test_char.location}")
    
    # Check if characters have different properties that affect actions
    print(f"Default player properties: {game.player.properties}")
    print(f"Test character properties: {test_char.properties}")
    
    return {
        'default_get_apple': default_get_apple,
        'test_get_apple': test_get_apple
    }


if __name__ == "__main__":
    result = debug_character_differences()
    
    print("\n=== FINAL COMPARISON ===")
    print(f"Default player can get apple: {'get apple' in result['default_get_apple']}")
    print(f"Test character can get apple: {'get apple' in result['test_get_apple']}")
    
    if result['default_get_apple'] != result['test_get_apple']:
        print("FOUND THE ISSUE: Different characters get different actions!")
    else:
        print("Characters get same actions - issue is elsewhere")