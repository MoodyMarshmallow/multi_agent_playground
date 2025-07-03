import sys
import os

# Ensure the project root is in sys.path for direct script execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.game_loop import game_loop

def main():
    print("Starting the background game loop using the canonical house environment...")
    game_loop.start_background_loop()
    input("Game loop is running in the background. Press Enter to exit.\n")

if __name__ == "__main__":
    main() 