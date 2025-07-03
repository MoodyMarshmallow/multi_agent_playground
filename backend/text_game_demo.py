import sys
import os

# Ensure the project root is in sys.path for module resolution
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

"""
Unified driver script for the canonical house text adventure game.
"""

from backend.text_adventure_games.house import build_house_game

HELP_TEXT = """
Available commands:
  - look: Describe the current room
  - get/take <item>: Pick up an item
  - open/close/unlock/lock <object>: Interact with doors, drawers, etc.
  - use <object>: Use an object (if possible)
  - help/controls: Show this help message
  - quit/exit: Leave the game
"""

def main():
    print("Welcome to the House Adventure Demo!")
    try:
        game_obj = build_house_game()
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
            result = game_obj.parser.parse_command(command)
            if result is None:
                print("I'm not sure what you want to do.")
    except (KeyboardInterrupt, EOFError):
        print("\nExiting game. Goodbye!")
    except Exception as e:
        print(f"Critical error: {e}")

if __name__ == "__main__":
    main() 