#!/usr/bin/env python3

"""Debug script to test action discovery"""

import sys
sys.path.insert(0, 'backend')

from backend.text_adventure_games.house import build_house_game
from backend.text_adventure_games.actions.generic import MoveAction, GenericTakeAction, GenericDropAction
# Note: OpenContainer action was removed during refactoring - container interactions now use generic actions

# Build the game
game = build_house_game()

# Get the parser
parser = game.parser

# Test action discovery
print("=== Testing Action Discovery ===")
action_classes = parser.discover_action_classes()
print(f"Discovered {len(action_classes)} action classes:")
for action_class in action_classes:
    print(f"  - {action_class.__name__}: {getattr(action_class, 'COMMAND_PATTERNS', 'NO PATTERNS')}")

print("\n=== Testing GenericTakeAction Specifically ===")
print(f"GenericTakeAction class has COMMAND_PATTERNS: {hasattr(GenericTakeAction, 'COMMAND_PATTERNS')}")
print(f"GenericTakeAction COMMAND_PATTERNS: {getattr(GenericTakeAction, 'COMMAND_PATTERNS', 'NONE')}")

print("\n=== Testing Kitchen Items (Default House) ===")
kitchen = None
for location in [game.player.location] + list(game.locations.values()):
    if location.name == "Kitchen":
        kitchen = location
        break

if kitchen:
    print(f"Kitchen items: {list(kitchen.items.keys())}")
    for item_name, item in kitchen.items.items():
        print(f"  - {item_name}: gettable={item.get_property('gettable', False)}")
        print(f"    Item id: {id(item)}")
else:
    print("Kitchen not found!")

print("\n=== Testing What Happens When We Add Another Apple ===")
if kitchen:
    from backend.domain.entities.item import Item
    # Simulate what the test does
    test_apple = Item(name="apple", description="A red apple from test")
    test_apple.set_property("gettable", True)
    
    print(f"Before adding test apple: {list(kitchen.items.keys())}")
    kitchen.add_item(test_apple)  # This overwrites the existing apple!
    print(f"After adding test apple: {list(kitchen.items.keys())}")
    
    for item_name, item in kitchen.items.items():
        print(f"  - {item_name}: {item.description} (id: {id(item)})")
        print(f"    gettable: {item.get_property('gettable', False)}")

print("\n=== Testing Get Combinations ===")
# Move player to kitchen
if kitchen:
    game.player.location = kitchen
    combinations = list(GenericTakeAction.get_applicable_combinations(game.player, parser))
    print(f"Get action combinations: {combinations}")

print("\n=== Testing Available Actions ===")
if kitchen:
    available = parser.get_available_actions(game.player)
    print(f"Available actions ({len(available)}):")
    for action in available:
        print(f"  - {action['command']}: {action['description']}")

print("\n=== Testing Get Action Preconditions Manually ===")
if kitchen:
    # Test preconditions manually like the action discovery does
    try:
        get_action_instance = GenericTakeAction(game, "get apple")
        print(f"Get action instantiated successfully")
        print(f"Target found: {get_action_instance.target}")
        print(f"Target name: {get_action_instance.target.name if get_action_instance.target else 'None'}")
        
        # Test preconditions
        preconditions_result = get_action_instance.check_preconditions()
        print(f"Preconditions result: {preconditions_result}")
        
        if not preconditions_result:
            print(f"Parser error message: {parser.last_error_message}")
            
    except Exception as e:
        print(f"Get action failed: {e}")
        
    # Also test what test_action_preconditions returns
    print(f"\n=== Testing test_action_preconditions ===")
    precondition_test = parser.test_action_preconditions(GenericTakeAction, "get apple", game.player)
    print(f"test_action_preconditions result: {precondition_test}")

print("\n=== Simulating Exact Test Scenario ===")
# Reset the game to replicate the test
game2 = build_house_game()

# Add apple like the test does
from backend.domain.entities.item import Item
test_apple = Item(name="apple", description="A red apple")
test_apple.set_property("gettable", True)
kitchen2 = game2.locations["Kitchen"]
kitchen2.add_item(test_apple)

# Create test character like the test does
test_agent = game2.characters["Player"]  # Use existing player
test_agent.location = kitchen2

print(f"Test agent location: {test_agent.location.name}")
print(f"Kitchen items: {list(kitchen2.items.keys())}")

# Call get_available_actions like the test does
print(f"\n=== First call to get_available_actions ===")
available1 = game2.parser.get_available_actions(test_agent)
get_apple_commands1 = [a['command'] for a in available1 if 'get apple' in a['command']]
print(f"Get apple commands found: {get_apple_commands1}")

print(f"\n=== Second call to get_available_actions (simulating validation) ===")
available2 = game2.parser.get_available_actions(test_agent)
get_apple_commands2 = [a['command'] for a in available2 if 'get apple' in a['command']]
print(f"Get apple commands found: {get_apple_commands2}")

print(f"\n=== Comparing results ===")
print(f"First call found get apple: {'get apple' in get_apple_commands1}")
print(f"Second call found get apple: {'get apple' in get_apple_commands2}")

if get_apple_commands1 != get_apple_commands2:
    print("INCONSISTENCY DETECTED!")
else:
    print("Results are consistent")

print("\n=== Testing Multiple Characters ===")
# Test what happens with multiple characters like in the actual test
if kitchen2:
    # Add Alan character to kitchen (like in the test)
    from backend.domain.entities import Character
    alan = Character(name="alan_test", description="Alan test character", persona="test")
    kitchen2.add_character(alan)
    
    print(f"Characters in kitchen: {list(kitchen2.characters.keys())}")
    print(f"Items before multi-character test: {list(kitchen2.items.keys())}")
    
    # Test if having multiple characters affects action discovery
    available_with_alan = game2.parser.get_available_actions(test_agent)
    get_apple_with_alan = [a['command'] for a in available_with_alan if 'get apple' in a['command']]
    print(f"Get apple commands with Alan present: {get_apple_with_alan}")
    
    # Test if the apple is still there
    print(f"Items after multi-character test: {list(kitchen2.items.keys())}")
    if 'apple' in kitchen2.items:
        apple = kitchen2.items['apple']
        print(f"Apple still gettable: {apple.get_property('gettable')}")
        print(f"Apple location: {apple.location.name if apple.location else 'None'}")