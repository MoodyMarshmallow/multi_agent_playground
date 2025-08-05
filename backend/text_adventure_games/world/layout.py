"""
Room definitions and connections for the house world.
"""

from backend.text_adventure_games import things


def create_house_locations():
    """
    Create all the locations (rooms) for the house world.
    
    Returns:
        dict: Dictionary mapping location names to Location objects
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
    
    locations = {
        "bedroom": bedroom,
        "kitchen": kitchen, 
        "entry": entry,
        "dining": dining,
        "bathroom": bathroom,
        "laundry": laundry,
        "living": living,
        "game": game
    }
    
    return locations


def connect_house_locations(locations):
    """
    Connect all the house locations based on the house layout.
    
    Args:
        locations: Dictionary of location objects
    """
    entry = locations["entry"]
    kitchen = locations["kitchen"]
    bedroom = locations["bedroom"]
    dining = locations["dining"]
    bathroom = locations["bathroom"]
    laundry = locations["laundry"]
    living = locations["living"]
    game = locations["game"]
    
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