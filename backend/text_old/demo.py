from backend.text_adventure_games import games, things
from backend.text_old.house_actions.containers import (
    OpenCloseItem, CloseItem, TakeFromContainer
)
from backend.text_old.house_actions.door import (
    UnlockDoor, LockDoor
)
from backend.text_old.house_actions.appliance import (
    TurnOnSink, TurnOffSink, FillCup, FillBathtub, UseWashingMachine
)
from backend.text_old.house_actions.entertainment import (
    WatchTV, PlayPool, TakeBath, UseComputer
)
from backend.text_old.house_actions.house_action_protocol import HouseActionProtocol

# --- Define Locations (Rooms) ---
bedroom = things.Location(
    "Bedroom",
    "A cozy bedroom with a bed, desk, and various decorations."
)
kitchen = things.Location(
    "Kitchen",
    "A modern kitchen with appliances, cabinets, and a large table."
)
entry = things.Location(
    "Entry Room",
    "The main entryway to the house, with a door leading outside."
)
dining = things.Location(
    "Dining Room",
    "A formal dining room with a long table and chairs."
)
bathroom = things.Location(
    "Bathroom",
    "A clean bathroom with a bathtub, sink, and toilet."
)
laundry = things.Location(
    "Laundry Room",
    "A small laundry room with a washer, dryer, and supplies."
)
living = things.Location(
    "Living Room",
    "A spacious living room with sofas, a TV, and bookshelves."
)
game = things.Location(
    "Game Room",
    "A fun game room with a pool table and entertainment area."
)

# --- Connect Locations (based on grid and adjacency) ---
entry.add_connection("north", kitchen)
entry.add_connection("east", dining)
kitchen.add_connection("south", entry)
kitchen.add_connection("east", dining)
kitchen.add_connection("north", bedroom)
bedroom.add_connection("south", kitchen)
bedroom.add_connection("east", bathroom)
bathroom.add_connection("west", bedroom)
bathroom.add_connection("south", laundry)
bathroom.add_connection("east", game)
laundry.add_connection("north", bathroom)
laundry.add_connection("south", living)
living.add_connection("north", laundry)
living.add_connection("west", dining)
living.add_connection("east", game)
game.add_connection("west", living)
game.add_connection("north", bathroom)
dining.add_connection("west", kitchen)
dining.add_connection("south", entry)
dining.add_connection("east", living)
dining.add_connection("north", bedroom)  # Optional: shortcut for exploration

# --- Interactable Things (Purple objects + new detailed objects) ---
# Bedroom Drawer (rightmost, 3 drawers)
drawer = things.Item(
    "drawer", "a set of three drawers", "A set of three drawers, the rightmost one can be opened."
)
drawer.set_property("gettable", False)
drawer.set_property("is_open", False)
drawer.set_property("has_inventory", True)
drawer.add_command_hint("open drawer")
drawer.add_command_hint("close drawer")
bedroom.add_item(drawer)
# Drawer IIOs
hidden_note = things.Item("note", "a folded note", "A secret note hidden in the drawer.")
hidden_note.set_property("gettable", True)
drawer.inventory = {"note": hidden_note}

# Bathroom Sink
sink = things.Item(
    "sink", "a bathroom sink", "A clean sink with running water."
)
sink.set_property("gettable", False)
sink.set_property("is_on", False)
sink.add_command_hint("turn on sink")
sink.add_command_hint("turn off sink")
sink.add_command_hint("fill cup")
bathroom.add_item(sink)
# Sink IIO: cup (not visible until filled)
cup = things.Item("cup", "a plastic cup", "A small cup for water.")
cup.set_property("gettable", True)
sink.inventory = {"cup": cup}

# Bathroom Cabinet (next to plunger)
cabinet = things.Item(
    "cabinet", "a bathroom cabinet", "A cabinet for storing toiletries."
)
cabinet.set_property("gettable", False)
cabinet.set_property("is_open", False)
cabinet.set_property("has_inventory", True)
cabinet.add_command_hint("open cabinet")
cabinet.add_command_hint("close cabinet")
bathroom.add_item(cabinet)
# Cabinet IIOs
bandage = things.Item("bandage", "a bandage", "A clean bandage for first aid.")
bandage.set_property("gettable", True)
cabinet.inventory = {"bandage": bandage}

# Bathtub (volume property, inventory, rubber ducky IIO)
bathtub = things.Item(
    "bathtub", "a bathtub", "A clean bathtub, perfect for a relaxing soak."
)
bathtub.set_property("gettable", False)
bathtub.set_property("volume", 0)
bathtub.set_property("has_inventory", True)
bathtub.add_command_hint("take bath")
bathtub.add_command_hint("fill bathtub")
bathroom.add_item(bathtub)
rubber_ducky = things.Item(
    "rubber ducky", "a rubber ducky", "A yellow rubber ducky floats in the tub."
)
rubber_ducky.set_property("gettable", True)
bathtub.inventory = {"rubber ducky": rubber_ducky}

# Entry Door (open/closed, locked/unlocked, block)
entry_door = things.Item(
    "entry door", "the front door", "A sturdy front door leading outside."
)
entry_door.set_property("gettable", False)
entry_door.set_property("is_open", False)
entry_door.set_property("is_locked", True)
entry_door.add_command_hint("open door")
entry_door.add_command_hint("close door")
entry_door.add_command_hint("unlock door")
entry_door.add_command_hint("lock door")
entry.add_item(entry_door)
# Key for the door
key = things.Item("key", "a small key", "A small key for the front door.")
key.set_property("gettable", True)
entry.add_item(key)

# Fridge (open/closed, fullness, inventory, food IIOs)
fridge = things.Item(
    "fridge", "a large fridge", "A modern fridge, maybe there's something inside."
)
fridge.set_property("gettable", False)
fridge.set_property("is_open", False)
fridge.set_property("fullness", 3)
fridge.set_property("has_inventory", True)
fridge.add_command_hint("open fridge")
fridge.add_command_hint("close fridge")
fridge.add_command_hint("take food")
kitchen.add_item(fridge)
# Fridge IIOs
apple = things.Item("apple", "a red apple", "A fresh red apple.")
apple.set_property("gettable", True)
sandwich = things.Item("sandwich", "a sandwich", "A tasty sandwich.")
sandwich.set_property("gettable", True)
water_bottle = things.Item("water bottle", "a bottle of water", "A cold bottle of water.")
water_bottle.set_property("gettable", True)
fridge.inventory = {
    "apple": apple,
    "sandwich": sandwich,
    "water bottle": water_bottle
}

# --- Other Interactables (from previous step) ---
washing_machine = things.Item(
    "washing machine", "a washing machine", "A front-loading washing machine."
)
washing_machine.set_property("gettable", False)
washing_machine.add_command_hint("use washing machine")
laundry.add_item(washing_machine)

tv = things.Item(
    "tv", "a flat-screen TV", "A big TV with a remote nearby."
)
tv.set_property("gettable", False)
tv.add_command_hint("watch tv")
living.add_item(tv)

pool_table = things.Item(
    "pool table", "a pool table", "A pool table with balls and cues."
)
pool_table.set_property("gettable", False)
pool_table.add_command_hint("play pool")
game.add_item(pool_table)

computer = things.Item(
    "computer", "a computer", "A desktop computer with a glowing screen."
)
computer.set_property("gettable", False)
computer.add_command_hint("use computer")
bedroom.add_item(computer)

# --- Register containers for use by actions ---
containers = {
    "drawer": drawer,
    "cabinet": cabinet,
    "fridge": fridge,
    "bathtub": bathtub,
    "sink": sink
}

# --- Create Player ---
player = things.Character(
    name="Player",
    description="An explorer in a large, modern house.",
    persona="I am curious and love to explore new places."
)

# --- Register all custom actions ---
custom_actions: list[type[HouseActionProtocol]] = [
    OpenCloseItem, CloseItem, UnlockDoor, LockDoor, TurnOnSink, TurnOffSink, FillCup, FillBathtub, TakeFromContainer,
    UseWashingMachine, WatchTV, PlayPool, TakeBath, UseComputer
]
game = games.Game(entry, player, custom_actions=custom_actions)
game.containers = containers

def main():
    print("Welcome to the House Adventure!")
    game.game_loop()

if __name__ == "__main__":
    main()
