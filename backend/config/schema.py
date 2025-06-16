from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union, Literal, Annotated, Tuple

# -----------------------------------------------------------------------------
# Message Model
# -----------------------------------------------------------------------------
class Message(BaseModel):
    sender: str
    receiver: str
    message: str
    timestamp: Optional[str] = None
    conversation_id: Optional[str] = None  # Added for conversation tracking
# Example
#     {
#       "sender": "alex_001",
#       "receiver": "alan_002",
#       "message": "Hey, how's it going?",
#       "timestamp": "01T04:35:20"
#     },
# -----------------------------------------------------------------------------
# Frontend Actions (Frontend → Backend)
# -----------------------------------------------------------------------------

class MoveFrontendAction(BaseModel):
    action_type: Literal["move"]
    destination_tile: Tuple[int, int]
    # use current tile from AgentPerception to determine progress

class ChatFrontendAction(BaseModel):
    action_type: Literal["chat"]
    forwarded: bool # a boolean to indicate the message was properly forwarded to the receiver. If true, the receiver will "hear" the message through their perception feild "heard_messages"

class InteractFrontendAction(BaseModel):
    action_type: Literal["interact"]
    # new object state will be sent in the perception field "visible_objects"

class PerceiveFrontendAction(BaseModel):
    action_type: Literal["perceive"]
    # no extra fields

FrontendAction = Annotated[
    Union[
        MoveFrontendAction,
        ChatFrontendAction,
        InteractFrontendAction,
        PerceiveFrontendAction
    ],
    Field(discriminator="action_type")
]

# Examples for different actions types Frontend -> Backend:

# move
# {
#   "action_type": "move",
#   "destination_tile": [21, 9],
#   "current_tile": [20, 8] // contained in AgentPerception
# }

# chat
# {
#   "action_type": "chat",
#   "forwarded": true
#   // if forwarded is true, the receiver will receive the message through their "heard_messages" in AgentPerception
# }

# {
#   "action_type": "interact"
#   // new object state is contained in "visible_objects" inside AgentPerception
# }

# {
#   "action_type": "perceive"
#   // data is collected in visible_objects, visible_agents, and chatable_agents inside AgentPerception
# }

# -----------------------------------------------------------------------------
# Backend Actions (Backend → Frontend)
# -----------------------------------------------------------------------------

class MoveBackendAction(BaseModel):
    action_type: Literal["move"]
    destination_tile: Tuple[int, int]

class ChatBackendAction(BaseModel):
    action_type: Literal["chat"]
    message: Message  # of the format defined previously with sender, receiver, message fields

class InteractBackendAction(BaseModel):
    action_type: Literal["interact"]
    object: str
    current_state: str
    new_state: str

class PerceiveBackendAction(BaseModel):
    action_type: Literal["perceive"]
    # no extra fields

BackendAction = Annotated[
    Union[
        MoveBackendAction,
        ChatBackendAction,
        InteractBackendAction,
        PerceiveBackendAction
    ],
    Field(discriminator="action_type")
]

# Examples for different actions types Backend -> Frontend:

# move
# {
#   "action_type": "move",
#   "destination_tile": [21, 9]
# }

# chat
# {
#   "action_type": "chat",
#   "message": {
#     "sender": "alex_001",
#     "receiver": "alan_002",
#     "message": "Hey, how's it going?"
#   }
# }

# interact
# {
#   "action_type": "interact",
#   "object": "bed",
#   "current_state": "messy",
#   "new_state": "made"
# }

# perceive
# {
#   "action_type": "perceive"
#   // Nothing else required
# }


# -----------------------------------------------------------------------------
# AgentPerception
# -----------------------------------------------------------------------------
# Encapsulates everything the agent "sees" or knows about the current world state.
# Sent from frontend to backend in every agent action input.
class AgentPerception(BaseModel):
    timestamp: Optional[str] = None           # Perceived world time format: 01T04:35:20
                                              # 01 is day after T is time so 04 is hour (military time), 35 is minutes, 20 is seconds                                          
    current_tile: Optional[Tuple[int, int]] = None   # (Optional) Updated [x, y] tile position
    visible_objects: Optional[Dict[str, Dict[str, Any]]] = None  # Objects visible and their states
    visible_agents: Optional[List[str]] = None              # Other agents currently visible formatted as a list of agent_ids
    chatable_agents: Optional[List[str]] = None             # Other agents currently in chatting range formatted as a list of agent_ids
    heard_messages: Optional[List[Message]] = None              # Messages heard from other agents formatted as a list of messages

#examples:
#timestamp: "01T04:35:20"

#current_tile: [20, 8]

# visible objects:
# {
#     "bed": {
#         "room": "bedroom",
#         "position": [21, 9],
#         "state": "made"    # These should be one word descriptions of the state of the object that are predefined and match the objects appearance in the frontend. Ex in this case could be made or messy
#     },
#     "wardrobe": {
#         "room": "bedroom",
#         "position": [20, 7],
#         "state": "open"
#     },
#     "left_bookshelf": {
#         "room": "kitchen",
#         "position": [23, 7],
#         "state": ""
#     }
# }

# visible_agents:
# [alex_001, alan_002]

# chatable_agents:
# [alex_001]

# heard_messages:
# [
#     {
#       "sender": "alex_001",
#       "receiver": "alan_002",
#       "message": "Hey, how's it going?",
#     },
#     {
#       "sender": "alan_004",
#       "receiver": "alex_007",
#       "message": "Wow! It's so sunny outside!",
#     }
# ]


# Full Example:
# {
#   "timestamp": "01T04:35:20",
#   "current_tile": [20, 8],
#   "visible_objects": {
#     "bed": {
#       "room": "bedroom",
#       "position": [21, 9],
#       "state": "made"
#     },
#     "wardrobe": {
#       "room": "bedroom",
#       "position": [20, 7],
#       "state": "open"
#     },
#     "left_bookshelf": {
#       "room": "kitchen",
#       "position": [23, 7],
#       "state": ""
#     }
#   },
#   "visible_agents": ["alex_001", "alan_002"],
#   "chatable_agents": ["alex_001"],
#   "heard_messages": [
#     {
#       "sender": "alex_001",
#       "receiver": "alan_002",
#       "message": "Hey, how's it going?"
#     },
#     {
#       "sender": "alan_004",
#       "receiver": "alex_007",
#       "message": "Wow! It's so sunny outside!"
#     }
#   ]
# }

# -----------------------------------------------------------------------------
# AgentActionInput (Frontend → Backend)
# -----------------------------------------------------------------------------
# This is the main payload sent from frontend to backend,
# representing an action request along with the agent's current perception/context.
class AgentActionInput(BaseModel):
    agent_id: str                       # Which agent is acting
    action: FrontendAction              # The action being performed
    in_progress: bool = True            # Whether the action is in progress or completed
    perception: AgentPerception         # What the agent perceives at the time of action

# Full Example:
# {
#   "agent_id": "alan_002",
#   "action": {
#     "action_type": "chat",
#     "forwarded": true
#   },
#   "in_progress": true,
#   "perception": {
#     "timestamp": "01T04:35:20",
#     "current_tile": [20, 8],
#     "visible_objects": {
#       "bed": {
#         "room": "bedroom",
#         "position": [21, 9],
#         "state": "messy"
#       },
#       "wardrobe": {
#         "room": "bedroom",
#         "position": [20, 7],
#         "state": "closed"
#       }
#     },
#     "visible_agents": ["alex_001"],
#     "chatable_agents": ["alex_001"],
#     "heard_messages": [
#       {
#         "sender": "alex_001",
#         "receiver": "alan_002",
#         "message": "Hey, how's it going?"
#       }
#     ]
#   }
# }

# -----------------------------------------------------------------------------
# AgentActionOutput (Backend → Frontend)
# -----------------------------------------------------------------------------
# This is the standard backend response to the frontend,
# describing the action to visualize or update, and any related info.
class AgentActionOutput(BaseModel):
    agent_id: str                       # Which agent to update
    action: BackendAction               # The action to be performed    
    emoji: str                          # Visual representation (e.g., '🚶', '💡', '👀') sends Unicode encoding
    timestamp: Optional[str] = None     # Timestamp to order actions                      
    current_tile: Optional[Tuple[int, int]]   # [x, y] tile position

# Full Example:
# {
#   "agent_id": "alan_002",
#   "action": {
#     "action_type": "chat",
#     "message": {
#       "sender": "alex_001",
#       "receiver": "alan_002",
#       "message": "Hey, how's it going?",
#       "timestamp": "01T04:35:20"
#     }
#   },
#   "emoji": "💬",
#   "timestamp": "01T04:35:20",
#   "current_tile": [20, 8]
# }

# -----------------------------------------------------------------------------
# simple response message
# -----------------------------------------------------------------------------
class StatusMsg(BaseModel):
    status: str

# -----------------------------------------------------------------------------
# AgentPlanRequest (Frontend → Backend) for batch processing
# -----------------------------------------------------------------------------
class AgentPlanRequest(BaseModel):
    agent_id: str
    perception: AgentPerception

# Full Example:

