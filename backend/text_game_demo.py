import sys
import os
import json
import argparse

# Ensure the project root is in sys.path for module resolution
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

"""
Unified driver script for the canonical house text adventure game.
"""

from backend.text_adventure_games.house import build_house_game
from backend.log_config import setup_logging
import logging

# Module-level logger
logger = logging.getLogger(__name__)

HELP_TEXT = (
    "Available commands:\n"
    "  - look: Describe the current room\n"
    "  - get/take <item>: Pick up an item\n"
    "  - open/close/unlock/lock <object>: Interact with doors, drawers, etc.\n"
    "  - use <object>: Use an object (if possible)\n"
    "  - look in/view <container>: View the contents of a container\n"
    "  - help/controls: Show this help message\n"
    "  - quit/exit: Leave the game\n"
)

def main():
    print("Welcome to the House Adventure Demo!" + "\n" * 5)
    try:
        game_obj = build_house_game()
        # Canonical parse and render for initial look
        narration, schema = game_obj.parser.parse_command("look")
        print(narration)
        logger.debug(f"Action schema: {getattr(schema, 'description', schema)}")
        if hasattr(schema, '__dict__'):
            logger.debug(f"ActionResult fields: {vars(schema)}")
        try:
            schema_result = game_obj.schema_exporter.get_schema()
            logger.debug("get_schema() DEBUG OUTPUT:")
            logger.debug(json.dumps(schema_result.model_dump(), indent=2))
        except Exception as e:
            logger.error(f"get_schema() ERROR: {e}")
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
            # Canonical parse and render for user command
            narration, schema = game_obj.parser.parse_command(command)
            print(narration)
            logger.debug(f"Action schema: {getattr(schema, 'description', schema)}")
            if hasattr(schema, '__dict__'):
                logger.debug(f"ActionResult fields: {vars(schema)}")
            # Debug the get_schema() output
            try:
                schema_result = game_obj.schema_exporter.get_schema()
                logger.debug("get_schema() DEBUG OUTPUT:")
                logger.debug(json.dumps(schema_result.model_dump(), indent=2))
            except Exception as e:
                logger.error(f"get_schema() ERROR: {e}")
    except (KeyboardInterrupt, EOFError):
        print("\nExiting game. Goodbye!")
    except Exception as e:
        logger.error(f"Critical error: {e}")
        print(f"Critical error: {e}")  # Also print to console for immediate visibility

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Text Adventure Game Demo")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose logging (show INFO+ messages)")
    args = parser.parse_args()
    
    # Setup logging based on verbose flag
    setup_logging(verbose=args.verbose)
    
    main() 