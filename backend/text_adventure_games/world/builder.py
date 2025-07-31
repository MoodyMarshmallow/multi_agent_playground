"""
World building orchestration for the house world.
"""

from backend.text_adventure_games import games
from .layout import create_house_locations, connect_house_locations
from .items import place_items_in_locations
from .characters import create_player_character, create_npc_characters, place_characters_in_locations


def build_house_game() -> games.Game:
    """
    Build and return the canonical house adventure GameController object.
    Includes all rooms, items, containers, and hooks for custom actions.
    
    Returns:
        games.Game: Fully configured game instance
    """
    # Create world layout
    locations = create_house_locations()
    connect_house_locations(locations)
    
    # Add items to locations
    place_items_in_locations(locations)
    
    # Create characters
    player = create_player_character()
    npcs = create_npc_characters()
    
    # Place characters in locations
    place_characters_in_locations(locations, npcs)
    
    # Build and return the game object
    # Note: No custom actions needed - smart objects handle their own behavior through capabilities
    game_obj = games.Game(locations["entry"], player, characters=npcs)
    return game_obj