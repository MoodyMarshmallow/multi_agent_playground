"""
World state formatting service
==============================
Centralizes formatting of the observable world state for agents and actions.
"""
from typing import Dict, List


def format_world_state(state: Dict) -> str:
    """Format world state into a readable observation string.
    Expected input keys:
      - location: { name, description }
      - inventory: [str]
      - visible_items: [ { name, description } ]
      - visible_characters: [ { name, description } ]
      - available_exits: [str]
      - available_actions: [ { command, description } ]
    """
    lines: List[str] = []

    # Location
    location_info = state.get("location", {})
    lines.append(f"You are at: {location_info.get('name', 'Unknown Location')}")
    if location_info.get("description"):
        lines.append(location_info["description"])

    # Inventory
    inventory = state.get("inventory", [])
    if inventory:
        lines.append(f"\nYou are carrying: {', '.join(inventory)}")
    else:
        lines.append("\nYou are not carrying anything.")

    # Visible items
    visible_items = state.get("visible_items", [])
    if visible_items:
        lines.append("\nYou can see:")
        for item in visible_items:
            lines.append(f"  - {item.get('name', 'item')}: {item.get('description', 'an item')}")

    # Other characters
    visible_characters = state.get("visible_characters", [])
    if visible_characters:
        lines.append("\nOther characters here:")
        for char in visible_characters:
            char_line = f"  - {char.get('name', 'character')}: {char.get('description', 'a character')}"
            char_name = char.get('name')
            if char_name:
                char_line += f" (You can chat with {char_name} using: chat_request {char_name} <your message>)"
            lines.append(char_line)

    # Available exits
    available_exits = state.get("available_exits", [])
    if available_exits:
        lines.append(f"\nAvailable exits: {', '.join(available_exits)}")

    # Available actions
    available_actions = state.get("available_actions", [])
    if available_actions:
        lines.append("\nAvailable actions:")
        for action in available_actions:
            lines.append(f"  - {action['command']}: {action.get('description', 'perform action')}")

    return "\n".join(lines)
