"""
Capability protocols for object-centric architecture.

This module defines the interface protocols that objects can implement to advertise
their capabilities to the generic action system.
"""

from typing import Protocol, Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class ActionResult:
    """Standardized result object for all object interactions"""
    description: str
    success: bool = True
    state_changed: Optional[Dict[str, Any]] = None
    events: Optional[List[str]] = None


class Activatable(Protocol):
    """Objects that can be turned on/off or activated/deactivated"""
    
    def activate(self) -> ActionResult:
        """Turn on or activate the object"""
        ...
    
    def deactivate(self) -> ActionResult:
        """Turn off or deactivate the object"""
        ...
    
    def is_active(self) -> bool:
        """Check if object is currently active"""
        ...


class Openable(Protocol):
    """Objects that can be opened/closed"""
    
    def open(self) -> ActionResult:
        """Open the object"""
        ...
    
    def close(self) -> ActionResult:
        """Close the object"""
        ...
    
    def is_open(self) -> bool:
        """Check if object is currently open"""
        ...


class Lockable(Protocol):
    """Objects that can be locked/unlocked"""
    
    def lock(self) -> ActionResult:
        """Lock the object"""
        ...
    
    def unlock(self) -> ActionResult:
        """Unlock the object"""
        ...
    
    def is_locked(self) -> bool:
        """Check if object is currently locked"""
        ...


class Usable(Protocol):
    """Objects that can be used by characters"""
    
    def start_using(self, character) -> ActionResult:
        """Character starts using this object"""
        ...
    
    def stop_using(self, character) -> ActionResult:
        """Character stops using this object"""
        ...
    
    def is_being_used_by(self, character) -> bool:
        """Check if character is currently using this object"""
        ...


class Container(Protocol):
    """Objects that can hold items"""
    
    def place_item(self, item, character) -> ActionResult:
        """Place an item in this container"""
        ...
    
    def remove_item(self, item_name: str, character) -> ActionResult:
        """Remove an item from this container"""
        ...
    
    def list_contents(self) -> List:
        """List all items in this container"""
        ...


class Recipient(Protocol):
    """Entities that can receive items (characters, containers, etc.)"""
    
    def receive_item(self, item, giver) -> ActionResult:
        """Receive an item from a giver"""
        ...
    
    def can_receive(self, item) -> bool:
        """Check if this recipient can accept the item"""
        ...


class Giver(Protocol):
    """Entities that can give items to others"""
    
    def give_item(self, item_name: str, recipient) -> ActionResult:
        """Give an item to a recipient"""
        ...
    
    def has_item(self, item_name: str) -> bool:
        """Check if this entity has the specified item"""
        ...


class Conversational(Protocol):
    """Entities that can be talked to"""
    
    def talk_to(self, speaker, message: str = "") -> ActionResult:
        """Handle conversation with this entity"""
        ...
    
    def can_talk(self) -> bool:
        """Check if this entity can be talked to"""
        ...


class Consumable(Protocol):
    """Items that can be consumed (eaten, drunk, etc.)"""
    
    def consume(self, character) -> ActionResult:
        """Character consumes this item"""
        ...


class Examinable(Protocol):
    """Objects that provide detailed examination"""
    
    def examine(self, character) -> ActionResult:
        """Provide detailed examination of this object"""
        ...