#!/usr/bin/env python3

"""Debug AgentManager world state generation vs debug script"""

import sys
sys.path.insert(0, 'backend')

from backend.text_adventure_games.world import build_house_game
from backend.text_adventure_games.things import Character, Item
from backend.agent.manager import AgentManager


def debug_agent_manager_flow():
    """Test the exact flow that AgentManager uses vs direct parser access"""
    
    print("=== Setting Up Test Environment (Mimicking AgentTestRunner) ===")
    
    # Build game exactly like test runner
    game = build_house_game()
    
    # Add apple like test runner does
    test_apple = Item(name="apple", description="A red apple")
    test_apple.set_property("gettable", True)
    kitchen = game.locations["Kitchen"]
    kitchen.add_item(test_apple)
    
    # Create test agent exactly like test runner
    agent_char = Character(
        name="collector_agent",
        description="Test agent: Agent should find and collect an apple",
        persona="You want should find and collect an apple."
    )
    
    # Set location like test runner
    kitchen.add_character(agent_char)
    agent_char.location = kitchen
    game.add_character(agent_char)
    
    print(f"Agent location: {agent_char.location.name}")
    print(f"Kitchen items: {list(kitchen.items.keys())}")
    
    # Create AgentManager like test runner
    agent_manager = AgentManager(game)
    
    print("\n=== Direct Parser Call (like debug_actions.py) ===")
    direct_actions = game.parser.get_available_actions(agent_char)
    direct_get_commands = [a['command'] for a in direct_actions if 'get apple' in a['command']]
    print(f"Direct parser get_available_actions: {len(direct_actions)} actions")
    print(f"Direct 'get apple' commands: {direct_get_commands}")
    
    print("\n=== AgentManager World State Call ===")
    world_state = agent_manager.get_world_state_for_agent(agent_char)
    agent_manager_actions = world_state.get('available_actions', [])
    agent_manager_get_commands = [a['command'] for a in agent_manager_actions if 'get apple' in a['command']]
    print(f"AgentManager get_world_state_for_agent: {len(agent_manager_actions)} actions")
    print(f"AgentManager 'get apple' commands: {agent_manager_get_commands}")
    
    print("\n=== Detailed Action Comparison ===")
    print("Direct parser actions:")
    for action in direct_actions:
        if 'apple' in action['command']:
            print(f"  - {action['command']}: {action['description']}")
    
    print("AgentManager actions:")
    for action in agent_manager_actions:
        if 'apple' in action['command']:
            print(f"  - {action['command']}: {action['description']}")
    
    print("\n=== Full Action Lists (first 10 of each) ===")
    print("Direct parser (first 10):")
    for i, action in enumerate(direct_actions[:10]):
        print(f"  {i+1}. {action['command']}")
    
    print("AgentManager (first 10):")
    for i, action in enumerate(agent_manager_actions[:10]):
        print(f"  {i+1}. {action['command']}")
    
    print("\n=== Identity Check ===")
    print(f"Same parser instance? {agent_manager.game.parser is game.parser}")
    print(f"Same agent character? {agent_manager.game.characters.get(agent_char.name) is agent_char}")
    
    # Test multiple calls to check consistency
    print("\n=== Consistency Check (Multiple Calls) ===")
    for i in range(3):
        actions = agent_manager.get_world_state_for_agent(agent_char)['available_actions']
        get_commands = [a['command'] for a in actions if 'get apple' in a['command']]
        print(f"Call {i+1}: {len(actions)} actions, get apple: {get_commands}")
    
    return {
        'direct_actions': direct_actions,
        'agent_manager_actions': agent_manager_actions,
        'direct_get_commands': direct_get_commands,
        'agent_manager_get_commands': agent_manager_get_commands
    }


if __name__ == "__main__":
    result = debug_agent_manager_flow()
    
    print("\n=== SUMMARY ===")
    print(f"Direct parser found 'get apple': {'get apple' in result['direct_get_commands']}")
    print(f"AgentManager found 'get apple': {'get apple' in result['agent_manager_get_commands']}")
    
    if result['direct_get_commands'] != result['agent_manager_get_commands']:
        print("INCONSISTENCY DETECTED between direct parser and AgentManager!")
    else:
        print("Direct parser and AgentManager results are consistent")