"""
Driver script for grassroots demo testing of the text module, similar to canonical_demo.py.
"""

from backend.text.canonical_world import demo

HELP_TEXT = """
Available commands:
  - look: Describe the current room
  - get/take <item>: Pick up an item
  - open/close/unlock/lock <object>: Interact with doors, drawers, etc.
  - use <object>: Use an object (if possible)
  - help/controls: Show this help message
  - quit/exit: Leave the game
"""

def get_item_hints(game_obj):
    """
    Gather item-specific command hints for all items in the current location.
    """
    hints = []
    location = game_obj.player.location
    for item in getattr(location, 'items', {}).values():
        # Bed legend (special case)
        if getattr(item, 'name', '').lower() == 'bed':
            try:
                from backend.text.house_actions.bed import get_bed_legend
                hints.append(get_bed_legend())
            except Exception:
                pass
        # General command hints
        for cmd in getattr(item, 'get_command_hints', lambda: [])():
            hints.append(f"  {cmd}")
    return hints

def main():
    print("Welcome to the Grassroots House Adventure Demo!")
    try:
        game_obj = demo()  # Get the grassroots game object
        while True:
            command = input("\n> ")
            if not command:
                print("Please enter a command. Type 'help' for options.")
                continue
            if command.lower() in {"help", "controls"}:
                print(HELP_TEXT)
                continue
            if command.lower() in {"quit", "exit"}:
                print("Thanks for playing!")
                break
            # Defensive: catch unknown commands before passing to parser
            result = game_obj.parser.parse_command(command)
            if result is None:
                print("I'm not sure what you want to do.")
    except (KeyboardInterrupt, EOFError):
        print("\nExiting game. Goodbye!")
    except Exception as e:
        print(f"Critical error: {e}")

if __name__ == "__main__":
    main() 