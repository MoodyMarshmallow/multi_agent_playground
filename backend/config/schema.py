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

class SingleTargetedAction(BaseModel):
    """Actions that target a single object"""
    target: str

class ItemAction(BaseModel):
    """Actions that involve an item"""
    item: str

# ------------------------------
# AGENT AND WORLD MODELS
# ------------------------------

class Message(BaseModel):
    sender: str
    receiver: str
    message: str
    timestamp: Optional[str] = None
    conversation_id: Optional[str] = None

class ChatRequest(BaseModel):
    request_id: str
    sender_id: str
    recipient_id: str
    message: str
    timestamp: str
    status: Literal["pending", "accepted", "rejected", "expired"]

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

# --- GENERIC OBJECT-CENTRIC ACTIONS ---

class SetToStateAction(SingleTargetedAction):
    """Change object state (on/off, open/close, lock/unlock)"""
    action_type: Literal["set_to_state"]
    state: str  # "on", "off", "open", "close", "lock", "unlock"

class StartUsingAction(SingleTargetedAction):
    """Start using an object (using restricts agent to be at the object)"""
    action_type: Literal["start_using"]

class StopUsingAction(SingleTargetedAction):
    """Stop using an object (frees agent from being restricted to the object)"""
    action_type: Literal["stop_using"]


# --- NAVIGATION ACTIONS ---
class GoToAction(SingleTargetedAction):
    """Navigate to a specific room or object"""
    action_type: Literal["go_to"]

# --- Basic Game Actions ---
class LookAction(BaseModel):
    """Look around current location"""
    action_type: Literal["look"]

# --- ITEM ACTIONS ---
class TakeAction(SingleTargetedAction):
    """Take an item and add it to inventory"""
    action_type: Literal["take"]

class DropAction(SingleTargetedAction):
    """Drop an item from inventory"""
    action_type: Literal["drop"]

class ExamineAction(SingleTargetedAction):
    """Examine an item or object closely"""
    action_type: Literal["examine"]

class PlaceAction(BaseModel):
    """Place item in/on container or give to character"""
    action_type: Literal["place"]
    target: str      # item to place
    recipient: str   # object to place it on/in or character to give to

class ConsumeAction(SingleTargetedAction):
    """Consume an item (removes item from inventory)"""
    action_type: Literal["consume"]

# --- CHARACTER ACTIONS ---
class ChatAction(BaseModel):
    """Chat to another agent in the vicinity"""
    action_type: Literal["chat"]
    sender: str     # sender agent id
    recipient: str  # recipient agent id
    message: str

class ChatRequestAction(BaseModel):
    """Internal: Send a chat request to another agent"""
    action_type: Literal["chat_request"]
    recipient: str
    message: str  # Explanation of why agent wants to chat

class ChatResponseAction(BaseModel):
    """Internal: Accept or reject a chat request"""
    action_type: Literal["chat_response"]
    request_id: str
    accepted: bool  # True for accept, False for reject
    response_message: Optional[str] = None  # Optional response message

# --- Fallback Action ---
class NoOpAction(BaseModel):
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
        # Character Actions
        ChatAction,
        ChatRequestAction,
        ChatResponseAction,
        # Fallback
        NoOpAction,
    ],
    Field(discriminator="action_type")
]

# ------------------------------
# MAIN API PAYLOADS
# ------------------------------

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