"""
World building components for the text adventure game.

This package contains modules for creating and managing the game world:
- layout: Room definitions and connections
- items: Item creation and placement
- characters: Character definitions and setup
- builder: World building orchestration
"""

from .builder import build_house_game

__all__ = ["build_house_game"]