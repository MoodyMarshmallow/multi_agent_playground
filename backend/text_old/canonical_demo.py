"""
Canonical text adventure demo for the house environment.
This module sets up a detailed house world and runs the text game loop.
"""

import os
from backend.text_old.canonical_world import build_canonical_house_environment

HELP_TEXT = """
Available commands:
  - look: Describe the current room
  - get/take <item>: Pick up an item
  - open/close/unlock/lock <object>: Interact with doors, drawers, etc.
  - use <object>: Use an object (if possible)
  - help/controls: Show this help message
  - quit/exit: Leave the game
"""

def main() -> None:
    """
    Main entry point for the canonical text adventure demo.
    Sets up the world and runs the game loop with robust error handling.
    """
    print("Welcome to the House Adventure!")
    try:
        # Use the canonical world setup
        game_obj = build_canonical_house_environment()
        # --- Game loop ---
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