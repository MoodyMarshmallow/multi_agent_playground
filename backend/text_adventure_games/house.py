"""
Canonical house world setup for the text adventure game.
Builds and returns a fully populated Game object with all rooms, items, and actions.
"""

from backend.text_adventure_games import games, things
from backend.text_adventure_games.actions.bed import Sleep, MakeBed, CleanBed, ChangeQuilt, ExamineBed
from backend.text_adventure_games.things.containers import Container
from backend.text_adventure_games.things.items import Item
from backend.text_adventure_games.actions.containers import (
    OpenContainer, CloseContainer, TakeFromContainer, ViewContainer, PutInContainer
)
# from backend.text_adventure_games.actions import ... (add custom actions as needed)

def build_house_game() -> games.Game:
    """
    Build and return the canonical house adventure GameController object.
    Includes all rooms, items, containers, and hooks for custom actions.
    """
    # --- Define Locations (Rooms) ---
    bedroom = things.Location("Bedroom", "A cozy bedroom with a bed, closet, and dresser.")
    kitchen = things.Location("Kitchen", "A modern kitchen with appliances, cabinets, and a large table.")
    entry = things.Location("Entry Room", "The main entryway to the house, with a door leading outside.")
    dining = things.Location("Dining Room", "A formal dining room with a long table and chairs.")
    bathroom = things.Location("Bathroom", "A clean bathroom with a bathtub, sink, and toilet.")
    laundry = things.Location("Laundry Room", "A small laundry room with a washer, dryer, and supplies.")
    living = things.Location("Living Room", "A spacious living room with sofas, a TV, and bookshelves.")
    game = things.Location("Game Room", "A fun game room with a pool table and entertainment area.")
    # --- Connect Locations (based on grid and adjacency) ---
    entry.add_connection("north", kitchen)
    entry.add_connection("east", dining)
    kitchen.add_connection("south", entry)
    kitchen.add_connection("east", dining)
    kitchen.add_connection("north", bedroom)
    bedroom.add_connection("south", kitchen)
    bedroom.add_connection("east", laundry)
    bathroom.add_connection("south", game)
    laundry.add_connection("west", bedroom)
    laundry.add_connection("east", game)
    living.add_connection("west", dining)
    living.add_connection("east", game)
    game.add_connection("north", bathroom)
    game.add_connection("west", laundry)
    game.add_connection("south", living)
    dining.add_connection("west", kitchen)
    dining.add_connection("east", living)
    dining.add_connection("north", bedroom)
    # --- Add Items, Characters, etc. (verbatim from canonical_world.py) ---
    bed: Item = things.Item("bed", "a comfortable bed", "A soft bed for sleeping.")
    bed.set_property("is_interactable", True)
    bed.set_property("is_sleepable", True)
    bed.set_property("is_made", True)
    bed.set_property("cleanliness", 90)  # numeric 0-100
    bed.set_property("color", "blue")
    bed.set_property("quilt_color", "blue")
    bed.set_property("gettable", False)
    bed.add_command_hint("sleep")
    bed.add_command_hint("make bed")
    bed.add_command_hint("clean bed")
    bed.add_command_hint("change quilt to <color>")
    bedroom.add_item(bed)

    # Add a closet container to the bedroom (canonical Container class)
    closet: Container = Container("closet", "A large wooden closet.", is_openable=True, is_open=False)
    closet.set_property("is_interactable", True)
    closet.set_property("fullness", 50)  # numeric 0-100
    closet.set_property("material", "wood")
    closet.add_command_hint("open")
    closet.add_command_hint("close")
    closet.add_command_hint("take")
    closet.add_command_hint("view")
    # Add multiple objects to the closet
    jacket: Item = Item("jacket", "a warm jacket", "A warm, cozy jacket.")
    jacket.add_command_hint("wear")
    jacket.add_command_hint("examine")
    boots: Item = Item("boots", "a pair of boots", "Sturdy leather boots.")
    boots.add_command_hint("wear")
    boots.add_command_hint("examine")
    hat: Item = Item("hat", "a sun hat", "A wide-brimmed sun hat.")
    hat.add_command_hint("wear")
    hat.add_command_hint("examine")
    scarf: Item = Item("scarf", "a wool scarf", "A long, woolen scarf.")
    scarf.add_command_hint("wear")
    scarf.add_command_hint("examine")
    closet.add_item(jacket)
    closet.add_item(boots)
    closet.add_item(hat)
    closet.add_item(scarf)
    # Add quilt items to the closet
    for color in ["red", "blue", "green", "yellow", "white", "black"]:
        quilt = Item(f"{color} quilt", f"a {color} quilt", f"A soft, {color} quilt for the bed.")
        quilt.set_property("quilt_color", color)
        quilt.add_command_hint("take")
        quilt.add_command_hint("examine")
        closet.add_item(quilt)
    closet.add_command_hint("view")
    bedroom.add_item(closet)

    # ... (continue porting all items, containers, and their properties as in canonical_world.py) ...
    # --- Player character ---
    player: things.Character = things.Character(
        name="Player",
        description="An explorer in a large, modern house.",
        persona="I am curious and love to explore new places."
    )
    
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

    # Place characters in different rooms
    bedroom.add_character(alex)
    kitchen.add_character(alan)
    
    # --- Custom actions (add as needed) ---
    custom_actions = [
        Sleep, MakeBed, CleanBed, ChangeQuilt, ExamineBed,
        OpenContainer, CloseContainer, TakeFromContainer, ViewContainer, PutInContainer
    ]
    # --- Build and return the game object ---
    # Pass the NPCs to the Game constructor so they get registered
    npcs = [alex, alan]
    game_obj: games.Game = games.Game(entry, player, characters=npcs, custom_actions=custom_actions)
    return game_obj