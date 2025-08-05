"""
Capability discovery logic for objects.
"""

from typing import Set, Type, List
import inspect


def discover_capabilities(obj) -> Set[Type]:
    """
    Automatically discover what capabilities an object implements.
    This is done by checking if the object has the methods required by each protocol.
    
    Args:
        obj: The object to check for capabilities
        
    Returns:
        Set[Type]: Set of capability protocol types that the object implements
    """
    # Import capabilities here to avoid circular imports
    try:
        from backend.text_adventure_games.capabilities import (
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
        if implements_protocol(obj, protocol):
            capabilities.add(protocol)
    
    return capabilities


def implements_protocol(obj, protocol: Type) -> bool:
    """
    Check if an object implements all methods required by a protocol.
    
    Args:
        obj: The object to check
        protocol: The protocol type to check against
        
    Returns:
        bool: True if the object implements all required methods
    """
    try:
        # Get all method names from the protocol
        required_methods = []
        for name in dir(protocol):
            if not name.startswith('_') and callable(getattr(protocol, name, None)):
                required_methods.append(name)
        
        # Check if this object has all required methods
        return all(hasattr(obj, method) and callable(getattr(obj, method)) 
                  for method in required_methods)
    except:
        return False


def can_do_action(obj, action_type: str) -> bool:
    """
    Check if an object supports a specific action type.
    Used by generic actions to determine if they can act on this object.
    
    Args:
        obj: The object to check
        action_type: The action type to check for
        
    Returns:
        bool: True if the object can perform the action
    """
    # Import capabilities here to avoid circular imports
    try:
        from backend.text_adventure_games.capabilities import (
            Activatable, Openable, Lockable, Usable, Container, 
            Consumable, Examinable
        )
    except ImportError:
        return False
    
    # Get object capabilities
    capabilities = getattr(obj, 'capabilities', None)
    if capabilities is None:
        capabilities = discover_capabilities(obj)
    
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
    return required_capability in capabilities if required_capability else False


def get_object_capabilities(obj) -> List[str]:
    """
    Return list of action types an object supports.
    Used for capability discovery and command suggestion.
    
    Args:
        obj: The object to get capabilities for
        
    Returns:
        List[str]: List of action type strings
    """
    # Import capabilities here to avoid circular imports
    try:
        from backend.text_adventure_games.capabilities import (
            Activatable, Openable, Lockable, Usable, Container, 
            Consumable, Examinable
        )
    except ImportError:
        return []
    
    # Get object capabilities
    capabilities = getattr(obj, 'capabilities', None)
    if capabilities is None:
        capabilities = discover_capabilities(obj)
    
    actions = []
    
    if Activatable in capabilities:
        actions.extend(["activate", "deactivate"])
    if Openable in capabilities:
        actions.extend(["open", "close"])
    if Lockable in capabilities:
        actions.extend(["lock", "unlock"])
    if Usable in capabilities:
        actions.extend(["start_using", "stop_using"])
    if Container in capabilities:
        actions.extend(["place", "remove_item"])
    if Consumable in capabilities:
        actions.append("consume")
    if Examinable in capabilities:
        actions.append("examine")
    
    return actions