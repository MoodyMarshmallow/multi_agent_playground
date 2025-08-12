from backend.text_adventure_games.things.objects import Object
from backend.text_adventure_games.capabilities import ActionResult, Openable, Container as ContainerCapability, Examinable
from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from backend.text_adventure_games.things.items import Item

class Container(Object, Openable, ContainerCapability, Examinable):
    """
    A container object that can hold items, be opened/closed, and is registered for lookup.
    """
    registry = {}

    def __init__(self, name: str, description: str, is_openable: bool = True, is_open: bool = False, is_locked: bool = False):
        super().__init__(name, description)
        self.set_property("is_container", True)
        self.set_property("is_openable", is_openable)
        self.set_property("is_open", is_open)
        self.set_property("is_locked", is_locked)
        self.inventory: Dict[str, 'Item'] = {}
        self.max_capacity = 10
        # Register this container by name
        Container.registry[self.name] = self

    # === OPENABLE CAPABILITY IMPLEMENTATION ===
    
    def open(self) -> ActionResult:
        """Open the container"""
        if self.get_property("is_open"):
            return ActionResult(f"The {self.name} is already open", success=False)
        
        self.set_property("is_open", True)
        contents = self.list_contents()
        if contents:
            content_desc = ", ".join([item.name for item in contents])
            return ActionResult(f"You open the {self.name}. Inside you see: {content_desc}")
        return ActionResult(f"You open the {self.name}. It's empty.")
    
    def close(self) -> ActionResult:
        """Close the container"""
        if not self.get_property("is_open"):
            return ActionResult(f"The {self.name} is already closed", success=False)
        
        self.set_property("is_open", False)
        return ActionResult(f"You close the {self.name}")
    
    def is_open(self) -> bool:
        """Check if container is open"""
        return bool(self.get_property("is_open", False))
    
    # === CONTAINER CAPABILITY IMPLEMENTATION ===
    
    def place_item(self, item, character) -> ActionResult:
        """Place an item in this container"""
        if not self.is_open():
            return ActionResult(f"The {self.name} is closed", success=False)
        
        if len(self.inventory) >= self.max_capacity:
            return ActionResult(f"The {self.name} is full", success=False)
        
        if item.name in self.inventory:
            return ActionResult(f"There's already a {item.name} in the {self.name}", success=False)
        
        # Remove from character's inventory
        if character and hasattr(character, 'inventory') and item.name in character.inventory:
            del character.inventory[item.name]
            item.owner = None
        
        # Add to container
        self.inventory[item.name] = item
        item.location = self
        return ActionResult(f"You place the {item.name} in the {self.name}")
    
    def remove_item(self, item_name: str, character) -> ActionResult:
        """Remove an item from this container"""
        if not self.is_open():
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
        """List all items in this container"""
        return list(self.inventory.values())
    
    # === EXAMINABLE CAPABILITY IMPLEMENTATION ===
    
    def examine(self, character) -> ActionResult:
        """Provide detailed examination of the container"""
        state = "open" if self.is_open() else "closed"
        desc = f"{self.description} that is currently {state}"
        
        if self.is_open() and self.inventory:
            items = ", ".join([item.name for item in self.inventory.values()])
            desc += f". Inside you can see: {items}"
        elif self.is_open():
            desc += ". It appears to be empty"
        
        return ActionResult(desc)
    
    # === LEGACY METHODS FOR COMPATIBILITY ===
    
    def add_item(self, item):
        """Legacy method - use place_item instead"""
        self.inventory[item.name] = item
        item.location = self

    def has_item(self, item_name):
        """Check if container has specific item"""
        return item_name in self.inventory

    @classmethod
    def get(cls, name):
        return cls.registry.get(name)

    @classmethod
    def all(cls):
        return list(cls.registry.values()) 