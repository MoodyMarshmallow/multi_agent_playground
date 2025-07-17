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
    has_items: List[str] = None
    lacks_items: List[str] = None
    
    def __post_init__(self):
        if self.has_items is None:
            self.has_items = []
        if self.lacks_items is None:
            self.lacks_items = []
    
    def check(self, game_state: Dict[str, Any], action_history: List[Any]) -> bool:
        inventory = set(game_state.get("agent_inventory", []))
        
        # Check has_items
        for item in self.has_items:
            if item not in inventory:
                return False
        
        # Check lacks_items
        for item in self.lacks_items:
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