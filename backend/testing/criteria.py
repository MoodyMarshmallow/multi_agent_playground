"""
Success and Failure Criteria
============================

Defines criteria for determining test success and failure.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass


class Criterion(ABC):
    """Base class for test criteria."""
    
    @abstractmethod
    def check(self, game_state: Dict[str, Any], action_history: List[Any]) -> bool:
        """Check if the criterion is met."""
        pass
    
    @abstractmethod
    def describe(self) -> str:
        """Return a human-readable description of the criterion."""
        pass


@dataclass
class LocationCriterion(Criterion):
    """Criterion based on agent location."""
    location: str
    
    def check(self, game_state: Dict[str, Any], action_history: List[Any]) -> bool:
        return game_state.get("agent_location") == self.location
    
    def describe(self) -> str:
        return f"Agent must be at {self.location}"


@dataclass
class InventoryCriterion(Criterion):
    """Criterion based on agent inventory."""
    has_items: Optional[List[str]] = None
    lacks_items: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.has_items is None:
            self.has_items = []
        if self.lacks_items is None:
            self.lacks_items = []
    
    def check(self, game_state: Dict[str, Any], action_history: List[Any]) -> bool:
        inventory = set(game_state.get("agent_inventory", []))
        
        # Check has_items
        for item in self.has_items or []:
            if item not in inventory:
                return False
        
        # Check lacks_items
        for item in self.lacks_items or []:
            if item in inventory:
                return False
        
        return True
    
    def describe(self) -> str:
        parts = []
        if self.has_items:
            parts.append(f"has {', '.join(self.has_items)}")
        if self.lacks_items:
            parts.append(f"lacks {', '.join(self.lacks_items)}")
        return f"Inventory: {'; '.join(parts)}"


@dataclass
class ActionCriterion(Criterion):
    """Criterion based on specific action being performed."""
    action_type: str
    target: Optional[str] = None
    item: Optional[str] = None
    
    def check(self, game_state: Dict[str, Any], action_history: List[Any]) -> bool:
        for action_output in action_history:
            if hasattr(action_output, 'action') and hasattr(action_output.action, 'action_type'):
                if action_output.action.action_type == self.action_type:
                    # Check additional criteria
                    if self.target and hasattr(action_output.action, 'target'):
                        if action_output.action.target != self.target:
                            continue
                    if self.item and hasattr(action_output.action, 'item'):
                        if action_output.action.item != self.item:
                            continue
                    return True
        return False
    
    def describe(self) -> str:
        desc = f"Action {self.action_type}"
        if self.target:
            desc += f" on {self.target}"
        if self.item:
            desc += f" with {self.item}"
        return desc


@dataclass
class StateCriterion(Criterion):
    """Criterion based on custom state predicate."""
    predicate: Callable[[Dict[str, Any]], bool]
    description: str
    
    def check(self, game_state: Dict[str, Any], action_history: List[Any]) -> bool:
        return self.predicate(game_state)
    
    def describe(self) -> str:
        return self.description


@dataclass
class TimeCriterion(Criterion):
    """Criterion based on time/turn limits."""
    max_turns: int
    
    def check(self, game_state: Dict[str, Any], action_history: List[Any]) -> bool:
        return len(action_history) <= self.max_turns
    
    def describe(self) -> str:
        return f"Complete within {self.max_turns} turns"


# Failure Criteria

@dataclass
class TimeoutCriterion(Criterion):
    """Failure criterion for test timeout."""
    max_turns: int
    
    def check(self, game_state: Dict[str, Any], action_history: List[Any]) -> bool:
        return len(action_history) >= self.max_turns
    
    def describe(self) -> str:
        return f"Test times out after {self.max_turns} turns"


@dataclass
class ImpossibleActionCriterion(Criterion):
    """Failure criterion for repeated impossible actions."""
    max_impossible_actions: int = 5
    
    def check(self, game_state: Dict[str, Any], action_history: List[Any]) -> bool:
        impossible_count = 0
        for action_output in action_history[-10:]:  # Check last 10 actions
            if hasattr(action_output, 'action') and hasattr(action_output.action, 'action_type'):
                if action_output.action.action_type == "noop":
                    impossible_count += 1
                    if impossible_count >= self.max_impossible_actions:
                        return True
        return False
    
    def describe(self) -> str:
        return f"Agent attempts {self.max_impossible_actions} impossible actions"


@dataclass
class LoopCriterion(Criterion):
    """Failure criterion for action loops."""
    max_repeats: int = 3
    window_size: int = 6
    
    def check(self, game_state: Dict[str, Any], action_history: List[Any]) -> bool:
        if len(action_history) < self.window_size:
            return False
        
        recent_actions = action_history[-self.window_size:]
        action_commands = []
        
        for action_output in recent_actions:
            if hasattr(action_output, 'action') and hasattr(action_output.action, 'action_type'):
                action_commands.append(action_output.action.action_type)
        
        # Check for repeated patterns
        if len(action_commands) >= self.max_repeats * 2:
            pattern_size = len(action_commands) // self.max_repeats
            for size in range(1, pattern_size + 1):
                pattern = action_commands[:size]
                matches = 0
                for i in range(0, len(action_commands), size):
                    if action_commands[i:i+size] == pattern:
                        matches += 1
                    else:
                        break
                if matches >= self.max_repeats:
                    return True
        
        return False
    
    def describe(self) -> str:
        return f"Agent repeats action pattern {self.max_repeats} times"


@dataclass
class ActionSequenceCriterion(Criterion):
    """Criterion based on performing a sequence of actions."""
    actions: List[str]
    strict_order: bool = True
    description: str = ""
    
    def check(self, game_state: Dict[str, Any], action_history: List[Any]) -> bool:
        if not action_history:
            return False
            
        # Extract action types from history
        action_types = []
        for action_output in action_history:
            if hasattr(action_output, 'action') and hasattr(action_output.action, 'action_type'):
                action_types.append(action_output.action.action_type)
        
        if self.strict_order:
            return self._check_strict_order(action_types)
        else:
            return self._check_any_order(action_types)
    
    def _check_strict_order(self, action_types: List[str]) -> bool:
        """Check if actions appear in the specified order."""
        if not self.actions:
            return True
            
        required_actions = self.actions.copy()
        
        for action_type in action_types:
            if required_actions and action_type == required_actions[0]:
                required_actions.pop(0)
                if not required_actions:
                    return True
        
        return False
    
    def _check_any_order(self, action_types: List[str]) -> bool:
        """Check if all actions appear in any order."""
        if not self.actions:
            return True
            
        required_actions = set(self.actions)
        performed_actions = set(action_types)
        
        return required_actions.issubset(performed_actions)
    
    def describe(self) -> str:
        if self.description:
            return self.description
        
        order_desc = "in order" if self.strict_order else "in any order"
        return f"Perform actions {order_desc}: {', '.join(self.actions)}"


# Object-Centric Architecture Criteria

@dataclass
class ObjectStateCriterion(Criterion):
    """Criterion based on smart object state (on/off, open/closed, etc.)"""
    object_name: str
    state_property: str  # e.g., "is_active", "is_open" 
    expected_value: Any  # e.g., True, False, "open"
    
    def check(self, game_state: Dict[str, Any], action_history: List[Any]) -> bool:
        # Get object state from game state
        objects = game_state.get("world_objects", {})
        for location_objects in objects.values():
            if self.object_name in location_objects:
                obj = location_objects[self.object_name]
                if hasattr(obj, self.state_property):
                    actual_value = getattr(obj, self.state_property)
                    # Handle callable properties like is_active()
                    if callable(actual_value):
                        actual_value = actual_value()
                    return actual_value == self.expected_value
        return False
    
    def describe(self) -> str:
        return f"Object {self.object_name}.{self.state_property} should be {self.expected_value}"


@dataclass
class CapabilityUsageCriterion(Criterion):
    """Criterion based on successful use of object capabilities"""
    object_name: str
    capability_type: str  # e.g., "Activatable", "Usable", "Container"
    
    def check(self, game_state: Dict[str, Any], action_history: List[Any]) -> bool:
        # Check if agent successfully used capability
        capability_actions = {
            "Activatable": ["set_to_state"],
            "Usable": ["start_using", "stop_using"],  
            "Container": ["place", "set_to_state"],
            "Openable": ["set_to_state"],
            "Consumable": ["consume"],
            "Examinable": ["examine"]
        }
        
        required_actions = capability_actions.get(self.capability_type, [])
        
        for action_output in action_history:
            if hasattr(action_output, 'action') and hasattr(action_output.action, 'action_type'):
                if (action_output.action.action_type in required_actions and 
                    hasattr(action_output.action, 'target') and 
                    action_output.action.target == self.object_name):
                    return True
        return False
    
    def describe(self) -> str:
        return f"Agent should use {self.capability_type} capability on {self.object_name}"


@dataclass
class SmartObjectInteractionCriterion(Criterion):
    """Criterion for specific smart object interactions"""
    object_name: str
    interaction_type: str  # e.g., "activate", "open", "use", "place_item"
    success_required: bool = True
    
    def check(self, game_state: Dict[str, Any], action_history: List[Any]) -> bool:
        interaction_map = {
            "activate": "set_to_state",
            "open": "set_to_state", 
            "close": "set_to_state",
            "use": "start_using",
            "stop_use": "stop_using",
            "place_item": "place",
            "consume": "consume",
            "examine": "examine"
        }
        
        target_action = interaction_map.get(self.interaction_type)
        if not target_action:
            return False
            
        for action_output in action_history:
            if (hasattr(action_output, 'action') and 
                hasattr(action_output.action, 'action_type') and
                action_output.action.action_type == target_action):
                
                if hasattr(action_output.action, 'target'):
                    if action_output.action.target == self.object_name:
                        # Check if success is required
                        if self.success_required:
                            return not hasattr(action_output, 'success') or action_output.success
                        return True
        return False
    
    def describe(self) -> str:
        success_desc = " successfully" if self.success_required else ""
        return f"Agent should{success_desc} {self.interaction_type} {self.object_name}"


@dataclass  
class ContainerOperationCriterion(Criterion):
    """Criterion for container operations (open, place, remove)"""
    container_name: str
    operations: List[str]  # e.g., ["open", "place_item", "close"]
    strict_order: bool = False
    
    def check(self, game_state: Dict[str, Any], action_history: List[Any]) -> bool:
        operation_map = {
            "open": "set_to_state",
            "close": "set_to_state", 
            "place_item": "place",
            "remove_item": "take",  # taking from container
        }
        
        # Extract actions targeting this container
        container_actions = []
        for action_output in action_history:
            if (hasattr(action_output, 'action') and 
                hasattr(action_output.action, 'action_type')):
                
                action = action_output.action
                # Check if action targets this container
                if (hasattr(action, 'target') and action.target == self.container_name) or \
                   (hasattr(action, 'recipient') and action.recipient == self.container_name):
                    container_actions.append(action.action_type)
        
        # Check if required operations were performed
        required_action_types = [operation_map[op] for op in self.operations if op in operation_map]
        
        if self.strict_order:
            # Check if actions appear in required order
            required_index = 0
            for action_type in container_actions:
                if (required_index < len(required_action_types) and 
                    action_type == required_action_types[required_index]):
                    required_index += 1
            return required_index == len(required_action_types)
        else:
            # Check if all required actions were performed
            return all(action_type in container_actions for action_type in required_action_types)
    
    def describe(self) -> str:
        order_desc = " in order" if self.strict_order else ""
        return f"Perform operations on {self.container_name}{order_desc}: {', '.join(self.operations)}"


@dataclass
class FurnitureUsageCriterion(Criterion):
    """Criterion for furniture usage (sitting, sleeping, etc.)"""
    furniture_name: str
    usage_type: str  # e.g., "sit", "sleep", "use"
    
    def check(self, game_state: Dict[str, Any], action_history: List[Any]) -> bool:
        for action_output in action_history:
            if (hasattr(action_output, 'action') and 
                hasattr(action_output.action, 'action_type') and
                action_output.action.action_type == "start_using"):
                
                if (hasattr(action_output.action, 'target') and 
                    action_output.action.target == self.furniture_name):
                    return True
        return False
    
    def describe(self) -> str:
        return f"Agent should {self.usage_type} on {self.furniture_name}"


@dataclass
class CapabilityDiscoveryCriterion(Criterion):
    """Criterion for testing capability discovery and usage"""
    object_name: str
    expected_capabilities: List[str]  # e.g., ["Activatable", "Examinable"]
    
    def check(self, game_state: Dict[str, Any], action_history: List[Any]) -> bool:
        # Check if agent discovered and used the expected capabilities
        capability_actions = {
            "Activatable": ["set_to_state"],
            "Usable": ["start_using", "stop_using"],
            "Container": ["place"],
            "Openable": ["set_to_state"], 
            "Consumable": ["consume"],
            "Examinable": ["examine"]
        }
        
        used_capabilities = set()
        
        for action_output in action_history:
            if (hasattr(action_output, 'action') and 
                hasattr(action_output.action, 'action_type')):
                
                action = action_output.action
                if hasattr(action, 'target') and action.target == self.object_name:
                    # Check which capability was used
                    for capability, actions in capability_actions.items():
                        if action.action_type in actions:
                            used_capabilities.add(capability)
        
        # Check if all expected capabilities were used
        return all(cap in used_capabilities for cap in self.expected_capabilities)
    
    def describe(self) -> str:
        return f"Agent should discover and use capabilities on {self.object_name}: {', '.join(self.expected_capabilities)}"