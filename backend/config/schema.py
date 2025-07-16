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

class ToggleState(str, Enum):
    """Common toggle states"""
    ON = "on"
    OFF = "off"

class BaseAction(BaseModel):
    """Base class for all actions"""
    action_type: str

class TargetedAction(BaseAction):
    """Actions that target a specific object"""
    target: str

class ItemAction(BaseAction):
    """Actions that involve an item"""
    item: str

class ValueAction(BaseAction):
    """Actions that set a numeric value"""
    target: str
    value: int
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

# --- Appliance Actions ---
class ToggleSinkAction(BaseAction):
    """Turn sink on or off"""
    action_type: Literal["turn_on_sink", "turn_off_sink"]

class FillCupAction(BaseAction):
    """Fill a cup with water"""
    action_type: Literal["fill_cup"]

class FillBathtubAction(BaseAction):
    """Fill the bathtub with water"""
    action_type: Literal["fill_bathtub"]

class UseWashingMachineAction(BaseAction):
    """Use the washing machine"""
    action_type: Literal["use_washing_machine"]

# --- Cleaning Actions ---
class CleanItemAction(TargetedAction):
    """Clean a specific item (bed, sink, table, etc.)"""
    action_type: Literal["clean_item"]

# --- Container Actions ---
class ToggleContainerAction(TargetedAction):
    """Open or close containers (drawer, cabinet, fridge, etc.)"""
    action_type: Literal["open_item", "close_item"]

class TakeFromContainerAction(BaseAction):
    """Take an item from a container"""
    action_type: Literal["take_from_container"]
    item: str         # What to take (e.g., "apple", "note")
    container: str    # From which container (e.g., "fridge", "drawer")

# --- Door Actions ---
class ToggleDoorLockAction(TargetedAction):
    """Lock or unlock doors"""
    action_type: Literal["unlock_door", "lock_door"]
    target: str = "entry door"

# --- Entertainment Actions ---
class WatchTVAction(BaseAction):
    """Watch television"""
    action_type: Literal["watch_tv"]

class PlayPoolAction(BaseAction):
    """Play pool/billiards"""
    action_type: Literal["play_pool"]

class TakeBathAction(BaseAction):
    """Take a bath"""
    action_type: Literal["take_bath"]

class UseComputerAction(BaseAction):
    """Use the computer"""
    action_type: Literal["use_computer"]

# --- Power/Electronics Actions ---
class ToggleItemAction(TargetedAction):
    """Turn items on or off (lamp, oven, tv, computer, etc.)"""
    action_type: Literal["turn_on_item", "turn_off_item"]

class SetTemperatureAction(ValueAction):
    """Set temperature for appliances (oven, fridge, grill, thermostat)"""
    action_type: Literal["set_temperature"]

class AdjustBrightnessAction(ValueAction):
    """Adjust brightness of lights"""
    action_type: Literal["adjust_brightness"]

class AdjustVolumeAction(ValueAction):
    """Adjust volume of devices (tv, alarm clock)"""
    action_type: Literal["adjust_volume"]

# --- Movement Actions ---
class MoveAction(BaseAction):
    """Move in a specific direction"""
    action_type: Literal["move"]
    direction: Direction

# --- Basic Game Actions ---
class LookAction(BaseAction):
    """Look around current location"""
    action_type: Literal["look"]

class InventoryAction(BaseAction):
    """Check inventory contents"""
    action_type: Literal["inventory"]

class GetItemAction(ItemAction):
    """Pick up an item"""
    action_type: Literal["get_item"]

class DropItemAction(ItemAction):
    """Drop an item from inventory"""
    action_type: Literal["drop_item"]

class GiveItemAction(ItemAction):
    """Give an item to another character"""
    action_type: Literal["give_item"]
    target: str   # character to give item to

class ExamineAction(TargetedAction):
    """Examine an item or object closely"""
    action_type: Literal["examine"]

# --- Fallback Action ---
class NoOpAction(BaseAction):
    """No-operation action used when no valid action can be performed"""
    action_type: Literal["noop"]
    reason: Optional[str] = "Command not recognized or invalid"

# --- UNIFIED ACTION TYPE ---
HouseAction = Annotated[
    Union[
        # Basic Game Actions
        LookAction,
        InventoryAction,
        GetItemAction,
        DropItemAction,
        GiveItemAction,
        ExamineAction,
        # Movement
        MoveAction,
        # Appliance Actions
        ToggleSinkAction,
        FillCupAction,
        FillBathtubAction,
        UseWashingMachineAction,
        # Cleaning Actions
        CleanItemAction,
        # Container Actions
        ToggleContainerAction,
        TakeFromContainerAction,
        # Door Actions
        ToggleDoorLockAction,
        # Entertainment Actions
        WatchTVAction,
        PlayPoolAction,
        TakeBathAction,
        UseComputerAction,
        # Power/Electronics Actions
        ToggleItemAction,
        SetTemperatureAction,
        AdjustBrightnessAction,
        AdjustVolumeAction,
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