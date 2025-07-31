"""
Canonical house world setup for the text adventure game.
Builds and returns a fully populated Game object with all rooms, items, and actions.

DEPRECATED: This module now delegates to the new world building system.
Use backend.text_adventure_games.world.build_house_game() instead.
"""

from backend.text_adventure_games.world import build_house_game

# Maintain backward compatibility by re-exporting the main function
__all__ = ["build_house_game"]