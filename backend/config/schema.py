from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union, Literal, Annotated, Tuple

# -----------------------------------------------------------------------------
# Agent Summary Model
# This is a summary of the agent's information that is sent to the frontend for initialization. 
# -----------------------------------------------------------------------------
class AgentSummary(BaseModel):
    agent_id: str
    curr_room: Optional[str]

# -----------------------------------------------------------------------------
# Message Model
# -----------------------------------------------------------------------------
class Message(BaseModel):
    sender: str
    receiver: str
    message: str
    timestamp: Optional[str] = None
    conversation_id: Optional[str] = None

# -----------------------------------------------------------------------------
# Frontend Actions (Frontend → Backend)
# -----------------------------------------------------------------------------

class MoveFrontendAction(BaseModel):
    action_type: Literal["move"]
    destination_room: str

class ChatFrontendAction(BaseModel):
    action_type: Literal["chat"]
    forwarded: bool

class InteractFrontendAction(BaseModel):
    action_type: Literal["interact"]

class PerceiveFrontendAction(BaseModel):
    action_type: Literal["perceive"]

FrontendAction = Annotated[
    Union[
        MoveFrontendAction,
        ChatFrontendAction,
        InteractFrontendAction,
        PerceiveFrontendAction
    ],
    Field(discriminator="action_type")
]

# -----------------------------------------------------------------------------
# Backend Actions (Backend → Frontend)
# -----------------------------------------------------------------------------

class MoveBackendAction(BaseModel):
    action_type: Literal["move"]
    destination_room: str

class ChatBackendAction(BaseModel):
    action_type: Literal["chat"]
    message: Message

class InteractBackendAction(BaseModel):
    action_type: Literal["interact"]
    object: str
    current_state: str
    new_state: str

class PerceiveBackendAction(BaseModel):
    action_type: Literal["perceive"]

BackendAction = Annotated[
    Union[
        MoveBackendAction,
        ChatBackendAction,
        InteractBackendAction,
        PerceiveBackendAction
    ],
    Field(discriminator="action_type")
]

# -----------------------------------------------------------------------------
# AgentPerception
# -----------------------------------------------------------------------------
class AgentPerception(BaseModel):
    timestamp: Optional[str] = None
    current_room: Optional[str] = None
    visible_objects: Optional[Dict[str, Dict[str, Any]]] = None
    visible_agents: Optional[List[str]] = None
    chatable_agents: Optional[List[str]] = None
    heard_messages: Optional[List[Message]] = None

# -----------------------------------------------------------------------------
# Action Input/Output Models
# -----------------------------------------------------------------------------

class AgentActionInput(BaseModel):
    agent_id: str
    action: FrontendAction
    in_progress: bool = True
    perception: AgentPerception

class AgentActionOutput(BaseModel):
    agent_id: str
    action: BackendAction
    emoji: str
    timestamp: Optional[str] = None
    current_room: Optional[str] = None

class PlanActionResponse(BaseModel):
    action: AgentActionOutput
    perception: AgentPerception

class StatusMsg(BaseModel):
    status: str

class AgentPlanRequest(BaseModel):
    agent_id: str
    perception: AgentPerception 