from collections import defaultdict
from typing import Dict, Any, Set, Type, List
from abc import ABC


class Thing(ABC):
    """
    Supertype that will add shared functionality to Items, Locations and
    Characters.
    """

    def __init__(self, name: str, description: str):
        # A short name for the thing
        self.name = name

        # A description of the thing
        self.description = description

        # A dictionary of properties and their values. Boolean properties for
        # items include: gettable, is_wearable, is_drink, is_food, is_weapon,
        #     is_container, is_surface
        self.properties = defaultdict(bool)

        # A set of special command associated with this item. The key is the
        # command text in invoke the special command. The command should be
        # implemented in the Parser.
        self.commands = set()
        
        # Auto-discover capabilities this object implements
        self.capabilities: Set[Type] = self._discover_capabilities()
        
        # Track state changes for event system
        self.state_history: List[Dict] = []


    def set_property(self, property_name: str, property):
        """
        Sets the property of this item
        """
        self.properties[property_name] = property

    def get_property(self, property_name: str, default=None):
        """
        Gets the value of this property for this item.
        Raises KeyError if property doesn't exist and no default is provided.
        """
        if property_name not in self.properties and default is None:
            raise KeyError(f"Property '{property_name}' not found on {self.__class__.__name__} '{self.name}'")
        return self.properties.get(property_name, default)

    def add_command_hint(self, command: str):
        """
        Adds a special command to this thing
        """
        self.commands.add(command)

    def get_command_hints(self):
        """
        Returns a list of special commands associated with this object
        """
        return self.commands
    
    def _discover_capabilities(self) -> Set[Type]:
        """
        Automatically discover what capabilities this object implements.
        This is done by checking if the object has the methods required by each protocol.
        """
        # Import capabilities here to avoid circular imports
        try:
            from backend.domain.value_objects.capabilities import (
                Activatable, Openable, Lockable, Usable, Container, 
                Consumable, Examinable, Recipient, Giver, Conversational
            )
        except ImportError:
            # During testing or if capabilities module isn't available
            return set()
        
        capabilities = set()
        protocols = [Activatable, Openable, Lockable, Usable, Container, 
                    Consumable, Examinable, Recipient, Giver, Conversational]
        
        for protocol in protocols:
            if self._implements_protocol(protocol):
                capabilities.add(protocol)
        
        return capabilities
    
    def _implements_protocol(self, protocol: Type) -> bool:
        """
        Check if this object implements all methods required by a protocol.
        """
        try:
            # Get all method names from the protocol
            required_methods = []
            for name in dir(protocol):
                if not name.startswith('_') and callable(getattr(protocol, name, None)):
                    required_methods.append(name)
            
            # Check if this object has all required methods
            return all(hasattr(self, method) and callable(getattr(self, method)) 
                      for method in required_methods)
        except:
            return False
    
    def can_do(self, action_type: str) -> bool:
        """
        Check if this object supports a specific action type.
        Used by generic actions to determine if they can act on this object.
        """
        # Import capabilities here to avoid circular imports
        try:
            from backend.domain.value_objects.capabilities import (
                Activatable, Openable, Lockable, Usable, Container, 
                Consumable, Examinable
            )
        except ImportError:
            return False
        
        capability_map = {
            "on": Activatable,
            "off": Activatable, 
            "activate": Activatable,
            "deactivate": Activatable,
            "open": Openable,
            "close": Openable,
            "lock": Lockable,
            "unlock": Lockable,
            "start_using": Usable,
            "stop_using": Usable,
            "place": Container,
            "remove_item": Container,
            "consume": Consumable,
            "examine": Examinable
        }
        
        required_capability = capability_map.get(action_type)
        return required_capability in self.capabilities if required_capability else False
    
    def get_object_capabilities(self) -> List[str]:
        """
        Return list of action types this object supports.
        Used for capability discovery and command suggestion.
        """
        # Import capabilities here to avoid circular imports
        try:
            from backend.domain.value_objects.capabilities import (
                Activatable, Openable, Lockable, Usable, Container, 
                Consumable, Examinable
            )
        except ImportError:
            return []
        
        actions = []
        
        if Activatable in self.capabilities:
            actions.extend(["activate", "deactivate"])
        if Openable in self.capabilities:
            actions.extend(["open", "close"])
        if Lockable in self.capabilities:
            actions.extend(["lock", "unlock"])
        if Usable in self.capabilities:
            actions.extend(["start_using", "stop_using"])
        if Container in self.capabilities:
            actions.extend(["place", "remove_item"])
        if Consumable in self.capabilities:
            actions.append("consume")
        if Examinable in self.capabilities:
            actions.append("examine")
        
        return actions
    
    def to_primitive(self) -> Dict[str, Any]:
        """
        Convert Thing to JSON-serializable dictionary for game state persistence.
        This is the missing method that subclasses were trying to call.
        """
        return {
            'name': self.name,
            'description': self.description,
            'properties': dict(self.properties),
            'commands': list(self.commands),
            'capabilities': [cap.__name__ for cap in self.capabilities] if self.capabilities else []
        }
    
    @classmethod
    def from_primitive(cls, data: Dict[str, Any], instance=None):
        """
        Create Thing from dictionary data for game state restoration.
        This is the missing method that subclasses were trying to call.
        """
        if instance is None:
            instance = cls(data['name'], data['description'])
        
        # Restore properties
        if 'properties' in data:
            for key, value in data['properties'].items():
                instance.set_property(key, value)
        
        # Restore commands
        if 'commands' in data:
            instance.commands = set(data['commands'])
        
        return instance
