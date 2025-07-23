from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union, Literal, Annotated, Tuple
from enum import Enum

'''
This is the schema defined for fastapi based on response for api calls
'''

# ------------------------------
# BASE CLASSES AND COMMON TYPES
# ------------------------------

class Direction(str, Enum):
    """Common movement directions"""
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"

class BaseAction(BaseModel):
    """Base class for all actions"""
    action_type: str

class TargetedAction(BaseAction):
    """Actions that target a specific object"""
    target: str

class ItemAction(BaseAction):
    """Actions that involve an item"""
    item: str

# ------------------------------
# AGENT AND WORLD MODELS (optional) - we can remove this if we don't need it
# ------------------------------

class Message(BaseModel):
    sender: str
    receiver: str
    message: str
    timestamp: Optional[str] = None
    conversation_id: Optional[str] = None

class AgentPerception(BaseModel):
    timestamp: Optional[str] = None
    current_room: Optional[str] = None
    visible_objects: Optional[Dict[str, Dict[str, Any]]] = None
    visible_agents: Optional[List[str]] = None
    chatable_agents: Optional[List[str]] = None
    heard_messages: Optional[List[Message]] = None

# ------------------------------
# HOUSE ACTIONS
# ------------------------------

# --- GENERIC OBJECT-CENTRIC ACTIONS (Following Schema_planning_final.md) ---

class SetToStateAction(TargetedAction):
    """Change object state (on/off, open/close, lock/unlock)"""
    action_type: Literal["set_to_state"]
    state: str  # "on", "off", "open", "close", "lock", "unlock"

class StartUsingAction(TargetedAction):
    """Start using an object (using restricts agent to be at the object)"""
    action_type: Literal["start_using"]

class StopUsingAction(TargetedAction):
    """Stop using an object (frees agent from being restricted to the object)"""
    action_type: Literal["stop_using"]


# --- NAVIGATION ACTIONS ---
class GoToAction(TargetedAction):
    """Navigate to a specific room or object"""
    action_type: Literal["go_to"]

# --- Basic Game Actions ---
class LookAction(BaseAction):
    """Look around current location"""
    action_type: Literal["look"]

# --- ITEM ACTIONS ---
class TakeAction(TargetedAction):
    """Take an item and add it to inventory"""
    action_type: Literal["take"]

class DropAction(TargetedAction):
    """Drop an item from inventory"""
    action_type: Literal["drop"]

class ExamineAction(TargetedAction):
    """Examine an item or object closely"""
    action_type: Literal["examine"]

class PlaceAction(BaseAction):
    """Place item in/on container or give to character"""
    action_type: Literal["place"]
    target: str      # item to place
    recipient: str   # object to place it on/in or character to give to

class ConsumeAction(TargetedAction):
    """Consume an item (removes item from inventory)"""
    action_type: Literal["consume"]

# --- Fallback Action ---
class NoOpAction(BaseAction):
    """No-operation action used when no valid action can be performed"""
    action_type: Literal["noop"]
    reason: Optional[str] = "Command not recognized or invalid"

# --- UNIFIED ACTION TYPE ---
# --- UNIFIED ACTION TYPE (Generic Object-Centric Actions) ---
HouseAction = Annotated[
    Union[
        # Basic Game Actions
        LookAction,
        # Navigation Actions
        GoToAction,
        # Object Actions
        SetToStateAction,
        StartUsingAction,
        StopUsingAction,
        # Item Actions
        TakeAction,
        DropAction,
        ExamineAction,
        PlaceAction,
        ConsumeAction,
        # Fallback
        NoOpAction,
    ],
    Field(discriminator="action_type")
]

# ------------------------------
# MAIN API PAYLOADS
# ------------------------------

# class AgentActionInput(BaseModel):
#     agent_id: str
#     action: HouseAction
#     in_progress: bool = True
#     perception: AgentPerception

class AgentActionOutput(BaseModel):
    agent_id: str
    action: HouseAction
    timestamp: Optional[str] = None
    current_room: Optional[str] = None
    description: Optional[str] = None  # for chat box description


class AgentPlanRequest(BaseModel):
    agent_id: str
    perception: AgentPerception

class StatusMsg(BaseModel):
    status: str

# ------------------------------
# GAME/EVENT/WORLD STATE
# ------------------------------

class GameEvent(BaseModel):
    id: int
    type: str
    timestamp: str
    data: Dict[str, Any]

class GameEventList(BaseModel):
    events: List[GameEvent]

class WorldStateResponse(BaseModel):
    agents: Dict[str, Any]
    objects: List[Any]
    locations: Dict[str, Any]
    game_status: Dict[str, Any]

class GameStatus(BaseModel):
    status: str
    turn_counter: int
    active_agents: int
    total_events: int
    locations: int
    characters: int

# ------------------------------
# (expand as needed for objects, agents, locations, etc.)
# TODO: we can remove this if we don't need it
# ------------------------------
class AgentStateResponse(BaseModel):
    agent_id: str
    location: Optional[str]
    inventory: List[str]
    properties: Dict[str, Any]
    
class GameObject(BaseModel):
    name: str
    description: str
    location: str
    state: str
    gettable: bool