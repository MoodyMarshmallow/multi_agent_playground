"""
Character definitions and setup for the house world.
"""

from backend.text_adventure_games import things


def create_player_character():
    """
    Create and return the player character.
    
    Returns:
        Character: The player character
    """
    player = things.Character(
        name="Player",
        description="An explorer in a large, modern house.",
        persona="I am curious and love to explore new places."
    )
    return player


def create_npc_characters():
    """
    Create and return all NPC characters.
    
    Returns:
        list: List of NPC Character objects
    """
    # AI-controlled characters that the game controller expects
    alex = things.Character(
        name="alex_001",
        description="Alex is a friendly and social person who loves to chat with others.",
        persona="I am Alex, a friendly and social person who loves to chat with others. I enjoy reading books and might want to explore the house. I'm curious about what others are doing and like to help when I can."
    )
    
    alan = things.Character(
        name="alan_002", 
        description="Alan is a quiet and thoughtful person who likes to observe and think.",
        persona="I am Alan, a quiet and thoughtful person who likes to observe and think. I prefer to explore slowly and examine things carefully. I might be interested in food and practical items."
    )
    
    return [alex, alan]


def place_characters_in_locations(locations, npcs):
    """
    Place NPCs in their starting locations.
    
    Args:
        locations: Dictionary of location objects
        npcs: List of NPC characters
    """
    # Place characters in different rooms
    alex, alan = npcs
    locations["bedroom"].add_character(alex)
    locations["kitchen"].add_character(alan)