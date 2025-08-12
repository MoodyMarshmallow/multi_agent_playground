from .base import Thing
from .items import Item
from .locations import Location
from backend.text_adventure_games.capabilities import ActionResult, Recipient, Giver, Conversational, Examinable
from ..utils import remove_item_safely
from typing import Dict, Any, Optional


class Character(Thing, Recipient, Giver, Conversational, Examinable):
    """
    This class represents the player and non-player characters (NPC).
    Characters have:
    * A name (cab be general like "gravedigger")
    * A description ('You might want to talk to the gravedigger, specially if
      your looking for a friend, he might be odd but you will find a friend in
      him.')
    * A persona written in the first person ("I am low paid labor in this town.
      I do a job that many people shun because of my contact with death. I am
      very lonely and wish I had someone to talk to who isn't dead.")
    * A location (the place in the game where they currently are)
    * An inventory of items that they are carrying (a dictionary mapping from
      item name to Item instance)
    * TODO: A dictionary of items that they are currently wearing
    * TODO: A dictionary of items that they are currently weilding
    """

    def __init__(
        self, name: str, description: str, persona: str = "",
    ):
        super().__init__(name, description)
        
        # Existing character properties (maintain compatibility with current agent system)
        self.persona = persona  # Used by Kani agents for AI personality
        self.inventory: Dict[str, Item] = {}     # Dict mapping item_name -> Item (existing pattern)
        self.location: Location  # Current Location object - initialized by game setup
        self.current_container: Optional[Any] = None  # Track if character is inside a container
        
        # Existing properties (maintain compatibility)
        self.set_property("character_type", "notset")
        self.set_property("is_dead", False)
        self.gettable = False
        
        # Character limits for gameplay balance
        self.max_inventory = 10

    def to_primitive(self):
        """
        Converts this object into a dictionary of values the can be safely
        serialized to JSON.

        Notice that object instances are replaced with their name. This
        prevents circular references that interfere with recursive
        serialization.
        """
        thing_data = super().to_primitive()
        thing_data['persona'] = self.persona

        inventory = {}
        for k, v in self.inventory.items():
            if hasattr(v, 'to_primitive'):
                inventory[k] = v.to_primitive()
            else:
                inventory[k] = v
        thing_data['inventory'] = inventory

        if self.location and hasattr(self.location, 'name'):
            thing_data['location'] = self.location.name
        elif self.location:
            thing_data['location'] = self.location
        return thing_data

    @classmethod
    def from_primitive(cls, data, instance=None):
        """
        Converts a dictionary of primitive values into a character instance.

        Notice that the from_primitive method is called for items.
        """
        instance = cls(data['name'], data['description'], data['persona'])
        super().from_primitive(data, instance=instance)
        # Location should always be provided in properly serialized data
        location_data = data.get('location')
        if location_data is None:
            raise ValueError(f"Character {instance.name} deserialized without location data")
        instance.location = location_data  # type: ignore # Location will be resolved by game setup
        instance.inventory = {
            k: Item.from_primitive(v) for k, v in data['inventory'].items()
        }
        return instance

    def add_to_inventory(self, item):
        """
        Add an item to the character's inventory.
        """
        if item.location is not None:
            remove_item_safely(item.location, item, self)
            item.location = None
        self.inventory[item.name] = item
        item.owner = self

    def is_in_inventory(self, item):
        """
        Checks if a character has the item in their inventory
        """
        return item.name in self.inventory

    def remove_from_inventory(self, item):
        """
        Removes an item to a character's inventory.
        """
        item.owner = None
        self.inventory.pop(item.name)
    
    # === CAPABILITY IMPLEMENTATIONS ===
    
    # Recipient capability - for PlaceAction (giving items to characters)
    def receive_item(self, item, giver) -> ActionResult:
        """
        Handle receiving items from other characters or containers.
        This enables PlaceAction to work with characters as recipients.
        """
        if len(self.inventory) >= self.max_inventory:
            return ActionResult(f"{self.name}'s hands are full", success=False)
        
        if item.name in self.inventory:
            return ActionResult(f"{self.name} already has a {item.name}", success=False)
        
        # Use existing method to maintain compatibility
        self.add_to_inventory(item)
        
        # Remove from giver's inventory if they have one
        if hasattr(giver, 'inventory') and item.name in giver.inventory:
            giver.remove_from_inventory(item)
        
        return ActionResult(f"{giver.name} gives the {item.name} to {self.name}")
    
    def can_receive(self, item) -> bool:
        """Check if character can receive an item"""
        return len(self.inventory) < self.max_inventory and item.name not in self.inventory
    
    # Giver capability - for characters giving items to others
    def give_item(self, item_name: str, recipient) -> ActionResult:
        """
        Handle giving items to other characters or containers.
        This enables enhanced giving mechanics.
        """
        if not self.has_item(item_name):
            return ActionResult(f"{self.name} doesn't have a {item_name}", success=False)
        
        if not hasattr(recipient, 'can_receive') or not recipient.can_receive(self.inventory[item_name]):
            return ActionResult(f"{recipient.name} can't take the {item_name}", success=False)
        
        item = self.inventory[item_name]
        return recipient.receive_item(item, self)
    
    def has_item(self, item_name: str) -> bool:
        """Check if character has specific item"""
        return item_name in self.inventory
    
    # Conversational capability - for talk actions
    def talk_to(self, speaker, message: str = "") -> ActionResult:
        """
        Handle conversations with this character.
        For AI-controlled characters, this could integrate with their persona.
        """
        if speaker == self:
            return ActionResult("You can't talk to yourself", success=False)
        
        if message:
            response = f"{speaker.name} says to {self.name}: '{message}'"
        else:
            response = f"{speaker.name} talks to {self.name}"
        
        # For AI agents, could generate persona-based responses
        # This doesn't interfere with Kani agents - they still use submit_command()
        if self.persona and len(self.persona) > 0:
            # Simple acknowledgment that shows persona awareness
            response += f"\n{self.name} listens thoughtfully"
        
        return ActionResult(response)
    
    def can_talk(self) -> bool:
        """Characters can always be talked to"""
        return True
    
    # Examinable capability - for examine actions
    def examine(self, character) -> ActionResult:
        """
        Provide detailed character examination.
        Shows description, persona hints, and visible inventory.
        """
        desc = f"{self.description}"
        
        # Add persona hints without revealing the full prompt (keeps AI agent privacy)
        if self.persona and len(self.persona) > 0:
            desc += f" {self.name} has a thoughtful demeanor."
        
        # Show visible inventory items
        if self.inventory:
            visible_items = [name for name, item in self.inventory.items() 
                           if not item.get_property("hidden", False)]
            if visible_items:
                items_list = ", ".join(visible_items)
                desc += f" {self.name} is carrying: {items_list}."
        else:
            desc += f" {self.name} doesn't appear to be carrying anything."
        
        return ActionResult(desc)
    
    # === AGENT SYSTEM INTEGRATION HELPERS ===
    
    def get_agent_state(self) -> Dict[str, Any]:
        """
        Helper method for game loop integration.
        Returns agent state in format expected by current system.
        """
        return {
            "agent_id": self.name,
            "location": self.location.name if self.location else None,
            "inventory": list(self.inventory.keys()),
            "properties": self.properties
        }
    
    def is_ai_controlled(self) -> bool:
        """
        Helper to check if this character is controlled by a Kani agent.
        Can be used to determine if character should respond automatically.
        """
        return self.get_property("character_type") == "ai_agent"
