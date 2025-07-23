"""
Canonical house world setup for the text adventure game.
Builds and returns a fully populated Game object with all rooms, items, and actions.
"""

from backend.text_adventure_games import games, things
from backend.text_adventure_games.things import (
    Item, EdibleItem, DrinkableItem, Container, Bed, Television, Sink,
    ClothingItem, UtilityItem, BookItem, BeddingItem, Chair, Table, Cabinet, Bookshelf, Toilet
)
# Note: Smart objects replace the need for custom action classes

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
    # --- Add Smart Objects with Capabilities ---
    bed = Bed("bed", "A comfortable bed with soft pillows and a blue quilt")
    bed.set_property("color", "blue")
    bed.set_property("quilt_color", "blue")
    bed.is_made = True
    bedroom.add_item(bed)

    # Add a closet container to the bedroom (smart Container class)
    closet = Container("closet", "A large wooden closet", is_openable=True, is_open=False)
    closet.set_property("material", "wood")
    # Add multiple items to the closet
    jacket = ClothingItem("jacket", "a warm jacket", "A warm, cozy jacket.", clothing_type="jacket", material="wool")
    boots = ClothingItem("boots", "a pair of boots", "Sturdy leather boots.", clothing_type="boots", material="leather")
    hat = ClothingItem("hat", "a sun hat", "A wide-brimmed sun hat.", clothing_type="hat", material="straw")
    scarf = ClothingItem("scarf", "a wool scarf", "A long, woolen scarf.", clothing_type="scarf", material="wool")
    closet.add_item(jacket)
    closet.add_item(boots)
    closet.add_item(hat)
    closet.add_item(scarf)
    # Add quilt items to the closet
    for color in ["red", "blue", "green", "yellow", "white", "black"]:
        quilt = BeddingItem(f"{color} quilt", f"a {color} quilt", f"A soft, {color} quilt for the bed.", 
                           bedding_type="quilt", material="cotton", color=color)
        closet.add_item(quilt)
    bedroom.add_item(closet)

    # Add apple to the kitchen (smart consumable item)
    apple = EdibleItem("apple", "A red apple", "A juicy red apple that looks delicious.")
    kitchen.add_item(apple)
    
    # Add more smart objects to other rooms
    # Kitchen sink
    sink = Sink("sink", "A stainless steel kitchen sink with modern fixtures")
    kitchen.add_item(sink)
    
    # Living room TV and furniture
    tv = Television("tv", "A large flat-screen television mounted on the wall")
    living.add_item(tv)
    
    # Living room furniture
    couch = Chair("couch", "A comfortable leather couch perfect for watching TV")
    couch.material = "leather"
    couch.comfort_level = "very comfortable"
    living.add_item(couch)
    
    coffee_table = Table("coffee table", "A glass coffee table in front of the couch")
    coffee_table.material = "glass"
    coffee_table.shape = "rectangular"
    living.add_item(coffee_table)
    
    bookshelf = Bookshelf("bookshelf", "A tall wooden bookshelf filled with interesting books")
    living.add_item(bookshelf)
    
    # Add some books to the bookshelf
    novel = BookItem("novel", "A mystery novel", title="The Case of the Missing Code", author="Jane Developer")
    cookbook = BookItem("cookbook", "A cookbook", title="Cooking for Coders", author="Chef Algorithm")
    bookshelf.place_item(novel, None)
    bookshelf.place_item(cookbook, None)
    
    # Dining room furniture
    dining_table = Table("dining table", "A large wooden dining table")
    dining_table.material = "oak"
    dining_table.shape = "oval"
    dining.add_item(dining_table)
    
    dining_chair = Chair("dining chair", "A wooden dining chair")
    dining_chair.material = "oak"
    dining.add_item(dining_chair)
    
    # Kitchen cabinet
    kitchen_cabinet = Cabinet("kitchen cabinet", "A wooden cabinet for storing dishes and food")
    kitchen.add_item(kitchen_cabinet)
    
    # Add some utensils to the kitchen cabinet
    fork = UtilityItem("fork", "A metal dinner fork", utility_type="utensil")
    knife = UtilityItem("knife", "A sharp kitchen knife", utility_type="utensil")
    plate = UtilityItem("plate", "A ceramic dinner plate", utility_type="utensil")
    kitchen_cabinet.place_item(fork, None)
    kitchen_cabinet.place_item(knife, None)
    kitchen_cabinet.place_item(plate, None)
    
    # Bathroom toilet
    toilet = Toilet("toilet", "A standard white porcelain toilet")
    bathroom.add_item(toilet)
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
    
    # --- Build and return the game object ---
    # Note: No custom actions needed - smart objects handle their own behavior through capabilities
    npcs = [alex, alan]
    game_obj: games.Game = games.Game(entry, player, characters=npcs, custom_actions=[])
    return game_obj