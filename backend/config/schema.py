from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union, Literal, Annotated, Tuple

'''
This is the schema defined for fastapi based on response for api calls
'''
# ------------------------------
# AGENT AND WORLD MODELS (optional) - we can remove this if we don't need it
# ------------------------------
class AgentSummary(BaseModel):
    agent_id: str
    curr_tile: Optional[List[int]] = None
    curr_room: Optional[str] = None

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

# --- Appliance ---
class TurnOnSinkAction(BaseModel):
    action_type: Literal["turn_on_sink"]

class TurnOffSinkAction(BaseModel):
    action_type: Literal["turn_off_sink"]

class FillCupAction(BaseModel):
    action_type: Literal["fill_cup"]

class FillBathtubAction(BaseModel):
    action_type: Literal["fill_bathtub"]

class UseWashingMachineAction(BaseModel):
    action_type: Literal["use_washing_machine"]

# --- Cleaning ---
class CleanItemAction(BaseModel):
    action_type: Literal["clean_item"]
    target: str   # e.g., "bed", "sink", "table"

# --- Containers ---
class OpenItemAction(BaseModel):
    action_type: Literal["open_item"]
    target: str   # e.g., "drawer", "cabinet", "fridge", "entry door"

class CloseItemAction(BaseModel):
    action_type: Literal["close_item"]
    target: str

class TakeFromContainerAction(BaseModel):
    action_type: Literal["take_from_container"]
    item: str         # What to take (e.g., "apple", "note")
    container: str    # From which container (e.g., "fridge", "drawer")

# --- Door ---
class UnlockDoorAction(BaseModel):
    action_type: Literal["unlock_door"]
    target: str = "entry door"

class LockDoorAction(BaseModel):
    action_type: Literal["lock_door"]
    target: str = "entry door"

# --- Entertainment ---
class WatchTVAction(BaseModel):
    action_type: Literal["watch_tv"]

class PlayPoolAction(BaseModel):
    action_type: Literal["play_pool"]

class TakeBathAction(BaseModel):
    action_type: Literal["take_bath"]

class UseComputerAction(BaseModel):
    action_type: Literal["use_computer"]

# --- Power/Electronics ---
class TurnOnItemAction(BaseModel):
    action_type: Literal["turn_on_item"]
    target: str   # e.g., "lamp", "oven", "tv", "computer"

class TurnOffItemAction(BaseModel):
    action_type: Literal["turn_off_item"]
    target: str

class SetTemperatureAction(BaseModel):
    action_type: Literal["set_temperature"]
    target: str   # e.g., "oven", "fridge", "grill", "thermostat"
    value: int    # temperature value

class AdjustBrightnessAction(BaseModel):
    action_type: Literal["adjust_brightness"]
    target: str   # e.g., "lamp"
    value: int    # brightness value

class AdjustVolumeAction(BaseModel):
    action_type: Literal["adjust_volume"]
    target: str   # e.g., "tv", "alarm clock"
    value: int    # volume value

# --- UNION OF ALL ACTIONS ---
HouseAction = Annotated[
    Union[
        # Appliance
        TurnOnSinkAction,
        TurnOffSinkAction,
        FillCupAction,
        FillBathtubAction,
        UseWashingMachineAction,
        # Cleaning
        CleanItemAction,
        # Containers
        OpenItemAction,
        CloseItemAction,
        TakeFromContainerAction,
        # Door
        UnlockDoorAction,
        LockDoorAction,
        # Entertainment
        WatchTVAction,
        PlayPoolAction,
        TakeBathAction,
        UseComputerAction,
        # Power/Electronics
        TurnOnItemAction,
        TurnOffItemAction,
        SetTemperatureAction,
        AdjustBrightnessAction,
        AdjustVolumeAction,
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
    emoji: str
    timestamp: Optional[str] = None
    current_room: Optional[str] = None

class PlanActionResponse(BaseModel):
    action: AgentActionOutput
    perception: AgentPerception

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
