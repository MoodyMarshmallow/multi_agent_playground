"""
Agent Goal Types
===============

Defines different types of goals that agents can be tested against.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass


class AgentGoal(ABC):
    """Base class for agent goals."""
    
    @abstractmethod
    def describe(self) -> str:
        """Return a human-readable description of the goal."""
        pass
    
    @abstractmethod
    def is_achieved(self, game_state: Dict[str, Any]) -> bool:
        """Check if the goal has been achieved given the current game state."""
        pass


@dataclass
class LocationGoal(AgentGoal):
    """Goal for agent to reach a specific location."""
    target_location: str
    description: str = ""
    
    def describe(self) -> str:
        return self.description or f"Move to {self.target_location}"
    
    def is_achieved(self, game_state: Dict[str, Any]) -> bool:
        agent_location = game_state.get("agent_location")
        return agent_location == self.target_location


@dataclass
class InventoryGoal(AgentGoal):
    """Goal for agent to have/not have specific items in inventory."""
    must_have: List[str] = None
    must_not_have: List[str] = None
    description: str = ""
    
    def __post_init__(self):
        if self.must_have is None:
            self.must_have = []
        if self.must_not_have is None:
            self.must_not_have = []
    
    def describe(self) -> str:
        if self.description:
            return self.description
        
        parts = []
        if self.must_have:
            parts.append(f"must have: {', '.join(self.must_have)}")
        if self.must_not_have:
            parts.append(f"must not have: {', '.join(self.must_not_have)}")
        
        return f"Inventory goal - {'; '.join(parts)}"
    
    def is_achieved(self, game_state: Dict[str, Any]) -> bool:
        inventory = set(game_state.get("agent_inventory", []))
        
        # Check must_have items
        for item in self.must_have:
            if item not in inventory:
                return False
        
        # Check must_not_have items
        for item in self.must_not_have:
            if item in inventory:
                return False
        
        return True


@dataclass
class InteractionGoal(AgentGoal):
    """Goal for agent to interact with specific objects or characters."""
    target: str
    interaction_type: str
    item: Optional[str] = None
    description: str = ""
    
    def describe(self) -> str:
        if self.description:
            return self.description
        
        if self.item:
            return f"{self.interaction_type} {self.item} with {self.target}"
        else:
            return f"{self.interaction_type} with {self.target}"
    
    def is_achieved(self, game_state: Dict[str, Any]) -> bool:
        # This will be checked by examining the action history
        # The test runner will track this
        return game_state.get("interaction_completed", False)


@dataclass
class ActionSequenceGoal(AgentGoal):
    """Goal for agent to perform a sequence of actions."""
    actions: List[str]
    strict_order: bool = True
    description: str = ""
    
    def describe(self) -> str:
        if self.description:
            return self.description
        
        order_desc = "in order" if self.strict_order else "in any order"
        return f"Perform actions {order_desc}: {', '.join(self.actions)}"
    
    def is_achieved(self, game_state: Dict[str, Any]) -> bool:
        # This will be checked by examining the action history
        # The test runner will track this
        return game_state.get("sequence_completed", False)


@dataclass
class CustomGoal(AgentGoal):
    """Goal with custom validation logic."""
    predicate: Callable[[Dict[str, Any]], bool]
    description: str
    
    def describe(self) -> str:
        return self.description
    
    def is_achieved(self, game_state: Dict[str, Any]) -> bool:
        return self.predicate(game_state)