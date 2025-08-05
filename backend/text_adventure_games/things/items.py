from .base import Thing
from backend.text_adventure_games.capabilities import ActionResult, Examinable, Consumable, Usable
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from backend.text_adventure_games.things.characters import Character


class Item(Thing, Examinable):
    """Items are objects that a player can get, or scenery that a player can
    examine."""

    def __init__(
        self, name: str, description: str, examine_text: str = "",
    ):
        super().__init__(name, description)

        # The detailed description of the player examines the object.
        self.examine_text = examine_text

        # If an item is gettable, then the player can get it and put it in
        # their inventory.
        self.set_property("gettable", True)

        # It might be at a location
        self.location = None

        # It might be in a character's inventory
        self.owner = None

    def to_primitive(self):
        """
        Converts this object into a dictionary of values the can be safely
        serialized to JSON.

        Notice that object instances are replaced with their name. This
        prevents circular references that interfere with recursive
        serialization.
        """
        thing_data = super().to_primitive()
        thing_data['examine_text'] = self.examine_text

        if self.location and hasattr(self.location, 'name'):
            thing_data['location'] = self.location.name
        elif self.location and isinstance(self.location, str):
            thing_data['location'] = self.location

        if self.owner and hasattr(self.owner, 'name'):
            thing_data['owner'] = self.owner.name
        elif self.owner and isinstance(self.owner, str):
            thing_data['owner'] = self.owner

        return thing_data

    @classmethod
    def from_primitive(cls, data, instance=None):
        """
        Converts a dictionary of primitive values into an item instance.
        """
        instance = cls(data['name'], data['description'], data['examine_text'])
        super().from_primitive(data, instance)
        if 'location' in data:
            instance.location = data['location']
        if 'owner' in data:
            instance.owner = data['owner']
        return instance
    
    # === EXAMINABLE CAPABILITY IMPLEMENTATION ===
    
    def examine(self, character) -> ActionResult:
        """Provide detailed examination of this item"""
        if self.examine_text and len(self.examine_text.strip()) > 0:
            return ActionResult(self.examine_text)
        else:
            return ActionResult(f"You examine the {self.name}. {self.description}")


class ConsumableItem(Item, Consumable):
    """Items that can be consumed (eaten, drunk, etc.)"""
    
    def __init__(self, name: str, description: str, examine_text: str = "", 
                 consume_text: str = "", restores_health: int = 0):
        super().__init__(name, description, examine_text)
        self.consume_text = consume_text or f"You consume the {name}"
        self.restores_health = restores_health
        self.set_property("consumable", True)
    
    def consume(self, character) -> ActionResult:
        """Character consumes this item"""
        if not character.is_in_inventory(self):
            return ActionResult(f"{character.name} doesn't have the {self.name}", success=False)
        
        # Remove from inventory
        character.remove_from_inventory(self)
        
        # Apply effects if any
        if self.restores_health > 0:
            # Could implement health system here
            effect_desc = f" {character.name} feels refreshed."
        else:
            effect_desc = ""
        
        return ActionResult(f"{self.consume_text}{effect_desc}")


class DrinkableItem(ConsumableItem):
    """Items that can be drunk"""
    
    def __init__(self, name: str, description: str, examine_text: str = ""):
        super().__init__(name, description, examine_text, 
                        consume_text=f"You drink the {name}", restores_health=5)
        self.set_property("drinkable", True)


class EdibleItem(ConsumableItem):
    """Items that can be eaten"""
    
    def __init__(self, name: str, description: str, examine_text: str = ""):
        super().__init__(name, description, examine_text,
                        consume_text=f"You eat the {name}", restores_health=10)
        self.set_property("edible", True)


class ClothingItem(Item):
    """Items of clothing that can be worn (conceptually)"""
    
    def __init__(self, name: str, description: str, examine_text: str = "", 
                 clothing_type: str = "clothing", material: str = "fabric"):
        super().__init__(name, description, examine_text)
        self.clothing_type = clothing_type  # jacket, hat, boots, scarf, etc.
        self.material = material
        self.set_property("clothing", True)
        self.set_property("clothing_type", clothing_type)
    
    def examine(self, character) -> ActionResult:
        if self.examine_text and len(self.examine_text.strip()) > 0:
            return ActionResult(self.examine_text)
        else:
            desc = f"{self.clothing_type} made of {self.material}. {self.description}"
            return ActionResult(desc)


class UtilityItem(Item, Usable):
    """Items that can be used for various purposes"""
    
    def __init__(self, name: str, description: str, examine_text: str = "",
                 utility_type: str = "tool", use_text: str = ""):
        super().__init__(name, description, examine_text)
        self.utility_type = utility_type  # tool, utensil, etc.
        self.use_text = use_text or f"You use the {name}"
        self.current_user: Optional['Character'] = None
        self.set_property("utility", True)
        self.set_property("utility_type", utility_type)
    
    def start_using(self, character) -> ActionResult:
        if self.current_user:
            return ActionResult(f"{self.current_user.name} is already using the {self.name}", success=False)
        if not character.is_in_inventory(self):
            return ActionResult(f"{character.name} needs to be holding the {self.name} to use it", success=False)
        
        self.current_user = character
        return ActionResult(f"{character.name} starts using the {self.name}")
    
    def stop_using(self, character) -> ActionResult:
        if self.current_user != character:
            return ActionResult("You're not using this item", success=False)
        self.current_user = None
        return ActionResult(f"{character.name} stops using the {self.name}")
    
    def is_being_used_by(self, character) -> bool:
        return self.current_user == character
    
    def examine(self, character) -> ActionResult:
        if self.examine_text and len(self.examine_text.strip()) > 0:
            return ActionResult(self.examine_text)
        else:
            desc = f"{self.utility_type}: {self.description}"
            if self.current_user:
                desc += f". {self.current_user.name} is currently using it"
            return ActionResult(desc)


class BookItem(Item):
    """Books and readable items"""
    
    def __init__(self, name: str, description: str, examine_text: str = "",
                 title: str = "", author: str = "", content: str = ""):
        super().__init__(name, description, examine_text)
        self.title = title or name.title()
        self.author = author
        self.content = content or "The pages contain interesting text."
        self.set_property("readable", True)
        self.set_property("book", True)
    
    def examine(self, character) -> ActionResult:
        if self.examine_text and len(self.examine_text.strip()) > 0:
            return ActionResult(self.examine_text)
        else:
            desc = f"A book titled '{self.title}'"
            if self.author:
                desc += f" by {self.author}"
            desc += f". {self.description}"
            if self.content and len(self.content) > 0:
                desc += f"\n\nYou read: {self.content}"
            return ActionResult(desc)


class BeddingItem(Item):
    """Bedding items like quilts, pillows, blankets"""
    
    def __init__(self, name: str, description: str, examine_text: str = "",
                 bedding_type: str = "bedding", material: str = "fabric", color: str = ""):
        super().__init__(name, description, examine_text)
        self.bedding_type = bedding_type  # quilt, pillow, blanket, etc.
        self.material = material
        self.color = color
        self.set_property("bedding", True)
        self.set_property("bedding_type", bedding_type)
        if color:
            self.set_property("color", color)
    
    def examine(self, character) -> ActionResult:
        if self.examine_text and len(self.examine_text.strip()) > 0:
            return ActionResult(self.examine_text)
        else:
            desc = f"{self.bedding_type}"
            if self.color:
                desc += f" in {self.color}"
            desc += f" made of {self.material}. {self.description}"
            return ActionResult(desc)
