"""
Item creation and placement for the house world.
"""

from backend.text_adventure_games.things import (
    EdibleItem, Container, Bed, Television, Sink,
    ClothingItem, UtilityItem, BookItem, BeddingItem, Chair, Table, Cabinet, Bookshelf, Toilet
)


def create_bedroom_items():
    """Create and return items for the bedroom."""
    items = {}
    
    # Add a bed
    bed = Bed("bed", "A comfortable bed with soft pillows and a blue quilt")
    bed.set_property("color", "blue")
    bed.set_property("quilt_color", "blue")
    bed.is_made = True
    items["bed"] = bed

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
    
    items["closet"] = closet
    return items


def create_kitchen_items():
    """Create and return items for the kitchen."""
    items = {}
    
    # Add apple to the kitchen (smart consumable item)
    apple = EdibleItem("apple", "A red apple", "A juicy red apple that looks delicious.")
    items["apple"] = apple
    
    # Kitchen sink
    sink = Sink("sink", "A stainless steel kitchen sink with modern fixtures")
    items["sink"] = sink
    
    # Kitchen cabinet
    kitchen_cabinet = Cabinet("kitchen cabinet", "A wooden cabinet for storing dishes and food")
    
    # Add some utensils to the kitchen cabinet
    fork = UtilityItem("fork", "A metal dinner fork", utility_type="utensil")
    knife = UtilityItem("knife", "A sharp kitchen knife", utility_type="utensil")
    plate = UtilityItem("plate", "A ceramic dinner plate", utility_type="utensil")
    kitchen_cabinet.place_item(fork, None)
    kitchen_cabinet.place_item(knife, None)
    kitchen_cabinet.place_item(plate, None)
    
    items["kitchen cabinet"] = kitchen_cabinet
    return items


def create_living_room_items():
    """Create and return items for the living room."""
    items = {}
    
    # Living room TV and furniture
    tv = Television("tv", "A large flat-screen television mounted on the wall")
    items["tv"] = tv
    
    # Living room furniture
    couch = Chair("couch", "A comfortable leather couch perfect for watching TV")
    couch.material = "leather"
    couch.comfort_level = "very comfortable"
    items["couch"] = couch
    
    coffee_table = Table("coffee table", "A glass coffee table in front of the couch")
    coffee_table.material = "glass"
    coffee_table.shape = "rectangular"
    items["coffee table"] = coffee_table
    
    bookshelf = Bookshelf("bookshelf", "A tall wooden bookshelf filled with interesting books")
    
    # Add some books to the bookshelf
    novel = BookItem("novel", "A mystery novel", title="The Case of the Missing Code", author="Jane Developer")
    cookbook = BookItem("cookbook", "A cookbook", title="Cooking for Coders", author="Chef Algorithm")
    bookshelf.place_item(novel, None)
    bookshelf.place_item(cookbook, None)
    
    items["bookshelf"] = bookshelf
    return items


def create_dining_room_items():
    """Create and return items for the dining room."""
    items = {}
    
    # Dining room furniture
    dining_table = Table("dining table", "A large wooden dining table")
    dining_table.material = "oak"
    dining_table.shape = "oval"
    items["dining table"] = dining_table
    
    dining_chair = Chair("dining chair", "A wooden dining chair")
    dining_chair.material = "oak"
    items["dining chair"] = dining_chair
    
    return items


def create_bathroom_items():
    """Create and return items for the bathroom."""
    items = {}
    
    # Bathroom toilet
    toilet = Toilet("toilet", "A standard white porcelain toilet")
    items["toilet"] = toilet
    
    return items


def place_items_in_locations(locations):
    """
    Place all items in their respective locations.
    
    Args:
        locations: Dictionary of location objects
    """
    # Bedroom items
    bedroom_items = create_bedroom_items()
    for item in bedroom_items.values():
        locations["bedroom"].add_item(item)
    
    # Kitchen items
    kitchen_items = create_kitchen_items()
    for item in kitchen_items.values():
        locations["kitchen"].add_item(item)
    
    # Living room items
    living_items = create_living_room_items()
    for item in living_items.values():
        locations["living"].add_item(item)
    
    # Dining room items
    dining_items = create_dining_room_items()
    for item in dining_items.values():
        locations["dining"].add_item(item)
    
    # Bathroom items
    bathroom_items = create_bathroom_items()
    for item in bathroom_items.values():
        locations["bathroom"].add_item(item)