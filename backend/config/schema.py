from pydantic import BaseModel
from typing import Dict, Any, List, Optional

# -----------------------------------------------------------------------------
# AgentActionContent (Reference Only)
# -----------------------------------------------------------------------------
# This class is a REFERENCE for what fields may be present in the 'content'
# dictionary for different action types ('move', 'interact', 'perceive', 'chat etc.).
# Not used directly as a type in API models for flexibility!
class AgentActionContent(BaseModel):
    destination_tile: Optional[List[int]] = None  # For move actions
    chatting_with: Optional[str] = None                  # For chat actions (future)
    message: Optional[str] = None                        # For chat actions (future)
    object: Optional[str] = None                         # For interact actions
    new_state: Optional[str] = None                      # For interact actions

# Examples for different actions types Frontend -> Backend:
# perceive
# contained in visible_objects, visible_agents, chatable_agents

# move
# "destination_tile": [21, 9]
# "current_tile": [20, 8]  conatained in agent_perception

# chat
# "chatting_with": "alex_001",
# "chatting_history":               All the messages sent so far in the frontend
# [
#     {
#       "sender": "alex_001",
#       "message": "Hey, how's it going?",
#     },
#     {
#       "sender": "alan_002", 
#       "message": "Good! Just finished cooking dinner.",
#     },
#     {
#       "sender": "alex_001",
#       "message": "That sounds delicious! What did you make?",
#     }
#   ]

# interact
# contained in visible_objects

#Examples for different actions types Backend -> Frontend:
# perceive
# Nothing required, likely for now just extends perception range and stands still

# move
# "destination_tile": [21, 9]

# chat
# "chatting_with": "alex_001",
# "full_chat":                      The fully planned out chat discussion
# [
#     {
#       "sender": "alex_001",
#       "message": "Hey, how's it going?",
#     },
#     {
#       "sender": "alan_002", 
#       "message": "Good! Just finished cooking dinner.",
#     },
#     {
#       "sender": "alex_001",
#       "message": "That sounds delicious! What did you make?",
#     },
#     {
#       "sender": "alan_002", 
#       "message": "I made a salad.",
#     },
#   ]

# interact
# "object": "bed",
# "current_state": "messy"
# "new_state": "made"

# -----------------------------------------------------------------------------
# AgentPerception
# -----------------------------------------------------------------------------
# Encapsulates everything the agent "sees" or knows about the current world state.
# Sent from frontend to backend in every agent action input.
class AgentPerception(BaseModel):
    timestamp: Optional[str] = None           # Perceived world time format: 01T04:35:20
                                              # 01 is day after T is time so 04 is hour (military time), 35 is minutes, 20 is seconds                                          
    current_tile: Optional[List[int]]   # (Optional) Updated [x, y] tile position
    visible_objects: Optional[Dict[str, Dict[str, Any]]] = None  # Objects visible and their states
    visible_agents: Optional[List[str]] = None              # Other agents currently visible formatted as a list of agent_ids
    chatable_agents: Optional[List[str]] = None             # Other agents currently in chatting range formatted as a list of agent_ids

#examples:
#timestamp: "01T04:35:20"

#current_tile: [20, 8]

# visible objects:
# {
#     "bed": {
#         "room": "bedroom",
#         "position": (21, 9),
#         "state": "made"    # These should be one word descriptions of the state of the object that are predefined and match the objects appearance in the frontend. Ex in this case could be made or messy
#     },
#     "wardrobe": {
#         "room": "bedroom",
#         "position": (20, 7),
#         "state": "open"
#     },
#     "left_bookshelf": {
#         "room": "kitchen",
#         "position": (23, 7),
#         "state": ""
#     }
# }
# visible_agents:
# [alex_001, alan_002]

# chatable_agents:
# [alex_001]

# -----------------------------------------------------------------------------
# AgentActionInput (Frontend → Backend)
# -----------------------------------------------------------------------------
# This is the main payload sent from frontend to backend,
# representing an action request along with the agent's current perception/context.
class AgentActionInput(BaseModel):
    agent_id: str                       # Which agent is acting

    action_type: str                    # e.g., 'move', 'interact', 'perceive'
    in_progress: bool = True           # Whether the action is in progress or completed
    content: Dict[str, Any]             # Action-specific details (see AgentActionContent)

    perception: AgentPerception         # What the agent perceives at the time of action

# -----------------------------------------------------------------------------
# AgentActionOutput (Backend → Frontend)
# -----------------------------------------------------------------------------
# This is the standard backend response to the frontend,
# describing the action to visualize or update, and any related info.
class AgentActionOutput(BaseModel):
    agent_id: str                       # Which agent to update
    action_type: str                    # The action being performed
    emoji: str                          # Visual representation (e.g., '🚶', '💡', '👀') sends Unicode encoding

    content: Dict[str, Any]             # Action-specific details (see AgentActionContent)
    
# -----------------------------------------------------------------------------
# simple response message
# -----------------------------------------------------------------------------
class StatusMsg(BaseModel):
    status: str

