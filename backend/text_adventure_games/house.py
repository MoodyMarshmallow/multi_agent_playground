"""
Canonical house world setup for the text adventure game.
Builds and returns a fully populated Game object with all rooms, items, and actions.
"""

from backend.text_adventure_games import games, things
from backend.text_adventure_games.actions.bed import Sleep, MakeBed, CleanBed, ChangeQuilt, ExamineBed
# from backend.text_adventure_games.actions import ... (add custom actions as needed)

def build_house_game() -> games.Game:
    """
    Build and return the canonical house adventure Game object.
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
    bed = things.Item("bed", "a comfortable bed", "A soft bed for sleeping.")
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
    # ... (continue porting all items, containers, and their properties as in canonical_world.py) ...
    # --- Player character ---
    player = things.Character(
        name="Player",
        description="An explorer in a large, modern house.",
        persona="I am curious and love to explore new places."
    )
    # --- Custom actions (add as needed) ---
    custom_actions = [
        Sleep, MakeBed, CleanBed, ChangeQuilt, ExamineBed
    ]
    # --- Build and return the game object ---
    game_obj = games.Game(entry, player, custom_actions=custom_actions)
    return game_obj
