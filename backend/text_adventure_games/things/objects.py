"""
Object classes for the object-centric architecture.

Objects are fixed in place and cannot be picked up, but can be interacted with
through various capabilities.
"""

from backend.text_adventure_games.things.base import Thing
from backend.text_adventure_games.capabilities import ActionResult, Activatable, Usable, Examinable, Openable, Container as ContainerCapability
from typing import Optional, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from backend.text_adventure_games.things.characters import Character
    from backend.text_adventure_games.things.items import Item


class Object(Thing):
    """Objects that are fixed in place but can be interacted with"""
    
    def __init__(self, name: str, description: str):
        super().__init__(name, description)
        self.set_property("gettable", False)
        self.location = None


class Sink(Object, Activatable, Examinable):
    """A kitchen sink that can be turned on/off"""
    
    def __init__(self, name: str = "sink", description: str = "A stainless steel kitchen sink"):
        super().__init__(name, description)
        self.is_on = False
        self.water_level = "empty"
    
    def activate(self) -> ActionResult:
        if self.is_on:
            return ActionResult("The sink is already running", success=False)
        self.is_on = True
        self.set_property("is_on", True)
        return ActionResult("Water flows from the sink", state_changed={"is_on": True})
    
    def deactivate(self) -> ActionResult:
        if not self.is_on:
            return ActionResult("The sink is already off", success=False)
        self.is_on = False
        self.set_property("is_on", False)
        return ActionResult("The water stops flowing", state_changed={"is_on": False})
    
    def is_active(self) -> bool:
        return self.is_on
    
    def examine(self, character) -> ActionResult:
        state = "running with water flowing" if self.is_on else "turned off"
        return ActionResult(f"A clean kitchen sink that is currently {state}")


class Television(Object, Activatable, Usable, Examinable):
    """A TV that can be turned on/off and watched"""
    
    def __init__(self, name: str = "tv", description: str = "A large flat-screen television"):
        super().__init__(name, description)
        self.is_on = False
        self.current_user: Optional['Character'] = None
        self.channel = 1
    
    def activate(self) -> ActionResult:
        if self.is_on:
            return ActionResult("The TV is already on", success=False)
        self.is_on = True
        self.set_property("is_on", True)
        return ActionResult(f"The TV turns on, showing channel {self.channel}")
    
    def deactivate(self) -> ActionResult:
        if not self.is_on:
            return ActionResult("The TV is already off", success=False)
        self.is_on = False
        self.set_property("is_on", False)
        if self.current_user:
            self.current_user = None
        return ActionResult("The TV turns off")
    
    def is_active(self) -> bool:
        return self.is_on
    
    def start_using(self, character) -> ActionResult:
        if not self.is_on:
            return ActionResult("You need to turn the TV on first", success=False)
        if self.current_user:
            return ActionResult(f"{self.current_user.name} is already watching TV", success=False)
        self.current_user = character
        return ActionResult(f"{character.name} starts watching TV")
    
    def stop_using(self, character) -> ActionResult:
        if self.current_user != character:
            return ActionResult("You're not watching TV", success=False)
        self.current_user = None
        return ActionResult(f"{character.name} stops watching TV")
    
    def is_being_used_by(self, character) -> bool:
        return self.current_user == character
    
    def examine(self, character) -> ActionResult:
        state = "on" if self.is_on else "off"
        desc = f"A large TV that is currently {state}"
        if self.is_on:
            desc += f" and showing channel {self.channel}"
        if self.current_user:
            desc += f". {self.current_user.name} is watching it"
        return ActionResult(desc)


class Bed(Object, Usable, Examinable):
    """A bed that can be slept in"""
    
    def __init__(self, name: str = "bed", description: str = "A comfortable bed with soft pillows"):
        super().__init__(name, description)
        self.current_user: Optional['Character'] = None
        self.is_made = True
        self.comfort_level = "comfortable"
    
    def start_using(self, character) -> ActionResult:
        if self.current_user:
            return ActionResult(f"{self.current_user.name} is already sleeping in the bed", success=False)
        self.current_user = character
        return ActionResult(f"{character.name} lies down on the bed to sleep")
    
    def stop_using(self, character) -> ActionResult:
        if self.current_user != character:
            return ActionResult("You're not sleeping in this bed", success=False)
        self.current_user = None
        return ActionResult(f"{character.name} gets out of bed")
    
    def is_being_used_by(self, character) -> bool:
        return self.current_user == character
    
    def examine(self, character) -> ActionResult:
        desc = f"{self.comfort_level} bed"
        if self.is_made:
            desc += " with neatly arranged sheets"
        else:
            desc += " with rumpled sheets"
        if self.current_user:
            desc += f". {self.current_user.name} is sleeping in it"
        return ActionResult(desc)


class Chair(Object, Usable, Examinable):
    """A chair that can be sat on"""
    
    def __init__(self, name: str = "chair", description: str = "A comfortable chair"):
        super().__init__(name, description)
        self.current_user: Optional['Character'] = None
        self.comfort_level = "comfortable"
        self.material = "wood"
    
    def start_using(self, character) -> ActionResult:
        if self.current_user:
            return ActionResult(f"{self.current_user.name} is already sitting on the {self.name}", success=False)
        self.current_user = character
        return ActionResult(f"{character.name} sits down on the {self.name}")
    
    def stop_using(self, character) -> ActionResult:
        if self.current_user != character:
            return ActionResult("You're not sitting on this chair", success=False)
        self.current_user = None
        return ActionResult(f"{character.name} stands up from the {self.name}")
    
    def is_being_used_by(self, character) -> bool:
        return self.current_user == character
    
    def examine(self, character) -> ActionResult:
        desc = f"{self.comfort_level} {self.material} {self.name}"
        if self.current_user:
            desc += f". {self.current_user.name} is sitting on it"
        return ActionResult(desc)


class Table(Object, Examinable):
    """A table that can be examined"""
    
    def __init__(self, name: str = "table", description: str = "A sturdy table"):
        super().__init__(name, description)
        self.material = "wood"
        self.shape = "rectangular"
        self.surface_items: Dict[str, 'Item'] = {}
    
    def examine(self, character) -> ActionResult:
        desc = f"{self.shape} {self.material} {self.name}"
        if self.surface_items:
            items_desc = ", ".join([item.name for item in self.surface_items.values()])
            desc += f". On the table you see: {items_desc}"
        return ActionResult(desc)


class Cabinet(Object, Openable, ContainerCapability, Examinable):
    """A cabinet that can be opened and store items"""
    
    def __init__(self, name: str = "cabinet", description: str = "A wooden storage cabinet"):
        super().__init__(name, description)
        self.is_open_state = False
        self.inventory: Dict[str, 'Item'] = {}
        self.max_capacity = 15
        self.material = "wood"
    
    def open(self) -> ActionResult:
        if self.is_open_state:
            return ActionResult(f"The {self.name} is already open", success=False)
        self.is_open_state = True
        self.set_property("is_open", True)
        contents = self.list_contents()
        if contents:
            content_desc = ", ".join([item.name for item in contents])
            return ActionResult(f"You open the {self.name}. Inside you see: {content_desc}")
        return ActionResult(f"You open the {self.name}. It's empty.")
    
    def close(self) -> ActionResult:
        if not self.is_open_state:
            return ActionResult(f"The {self.name} is already closed", success=False)
        self.is_open_state = False
        self.set_property("is_open", False)
        return ActionResult(f"You close the {self.name}")
    
    def is_open(self) -> bool:
        return self.is_open_state
    
    def place_item(self, item, character) -> ActionResult:
        if not self.is_open_state:
            return ActionResult(f"The {self.name} is closed", success=False)
        if len(self.inventory) >= self.max_capacity:
            return ActionResult(f"The {self.name} is full", success=False)
        if item.name in self.inventory:
            return ActionResult(f"There's already a {item.name} in the {self.name}", success=False)
        
        # Remove from character's inventory
        if character and hasattr(character, 'inventory') and item.name in character.inventory:
            del character.inventory[item.name]
            item.owner = None
        
        # Add to cabinet
        self.inventory[item.name] = item
        item.location = self
        return ActionResult(f"You place the {item.name} in the {self.name}")
    
    def remove_item(self, item_name: str, character) -> ActionResult:
        if not self.is_open_state:
            return ActionResult(f"The {self.name} is closed", success=False)
        if item_name not in self.inventory:
            return ActionResult(f"There's no {item_name} in the {self.name}", success=False)
        
        item = self.inventory[item_name]
        del self.inventory[item_name]
        
        # Add to character's inventory
        if character and hasattr(character, 'inventory'):
            character.inventory[item_name] = item
            item.owner = character
        
        item.location = None
        return ActionResult(f"You take the {item.name} from the {self.name}")
    
    def list_contents(self) -> List:
        return list(self.inventory.values())
    
    def examine(self, character) -> ActionResult:
        state = "open" if self.is_open_state else "closed"
        desc = f"{self.material} {self.name} that is currently {state}"
        if self.is_open_state and self.inventory:
            items = ", ".join([item.name for item in self.inventory.values()])
            desc += f". Inside you can see: {items}"
        elif self.is_open_state:
            desc += ". It appears to be empty"
        return ActionResult(desc)


class Bookshelf(Object, ContainerCapability, Examinable):
    """A bookshelf that can hold books and items"""
    
    def __init__(self, name: str = "bookshelf", description: str = "A tall wooden bookshelf"):
        super().__init__(name, description)
        self.inventory: Dict[str, 'Item'] = {}
        self.max_capacity = 20
        self.material = "wood"
        self.height = "tall"
    
    def place_item(self, item, character) -> ActionResult:
        if len(self.inventory) >= self.max_capacity:
            return ActionResult(f"The {self.name} is full", success=False)
        if item.name in self.inventory:
            return ActionResult(f"There's already a {item.name} on the {self.name}", success=False)
        
        # Remove from character's inventory
        if character and hasattr(character, 'inventory') and item.name in character.inventory:
            del character.inventory[item.name]
            item.owner = None
        
        # Add to bookshelf
        self.inventory[item.name] = item
        item.location = self
        return ActionResult(f"You place the {item.name} on the {self.name}")
    
    def remove_item(self, item_name: str, character) -> ActionResult:
        if item_name not in self.inventory:
            return ActionResult(f"There's no {item_name} on the {self.name}", success=False)
        
        item = self.inventory[item_name]
        del self.inventory[item_name]
        
        # Add to character's inventory
        if character and hasattr(character, 'inventory'):
            character.inventory[item_name] = item
            item.owner = character
        
        item.location = None
        return ActionResult(f"You take the {item.name} from the {self.name}")
    
    def list_contents(self) -> List:
        return list(self.inventory.values())
    
    def examine(self, character) -> ActionResult:
        desc = f"{self.height} {self.material} {self.name}"
        if self.inventory:
            items = ", ".join([item.name for item in self.inventory.values()])
            desc += f". On the shelves you can see: {items}"
        else:
            desc += ". The shelves appear to be empty"
        return ActionResult(desc)


class Toilet(Object, Usable, Examinable):
    """A toilet that can be used"""
    
    def __init__(self, name: str = "toilet", description: str = "A standard bathroom toilet"):
        super().__init__(name, description)
        self.current_user: Optional['Character'] = None
        self.is_clean = True
    
    def start_using(self, character) -> ActionResult:
        if self.current_user:
            return ActionResult(f"{self.current_user.name} is already using the {self.name}", success=False)
        self.current_user = character
        return ActionResult(f"{character.name} uses the {self.name}")
    
    def stop_using(self, character) -> ActionResult:
        if self.current_user != character:
            return ActionResult("You're not using this toilet", success=False)
        self.current_user = None
        return ActionResult(f"{character.name} finishes using the {self.name}")
    
    def is_being_used_by(self, character) -> bool:
        return self.current_user == character
    
    def examine(self, character) -> ActionResult:
        cleanliness = "clean" if self.is_clean else "dirty"
        desc = f"{cleanliness} bathroom {self.name}"
        if self.current_user:
            desc += f". {self.current_user.name} is using it"
        return ActionResult(desc)