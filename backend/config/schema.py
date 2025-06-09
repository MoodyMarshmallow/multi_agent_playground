from pydantic import BaseModel
from typing import Dict, Any, List, Optional

# -----------------------------------------------------------------------------
# AgentActionContent (Reference Only)
# -----------------------------------------------------------------------------
# This class is a REFERENCE for what fields may be present in the 'content'
# dictionary for different action types ('move', 'interact', etc.).
# Not used directly as a type in API models for flexibility!
class AgentActionContent(BaseModel):
    destination_coordinates: Optional[List[int]] = None  # For move actions
    chatting_with: Optional[str] = None                  # For chat actions (future)
    message: Optional[str] = None                        # For chat actions (future)
    object: Optional[str] = None                         # For interact actions
    new_state: Optional[str] = None                      # For interact actions

# -----------------------------------------------------------------------------
# AgentPerception
# -----------------------------------------------------------------------------
# Encapsulates everything the agent "sees" or knows about the current world state.
# Sent from frontend to backend in every agent action input.
class AgentPerception(BaseModel):
    self_state: Optional[str] = None                        # Description of agent's current state
    visible_objects: Optional[Dict[str, Dict[str, Any]]] = None  # Objects visible and their states
    visible_agents: Optional[List[str]] = None              # Other agents currently visible
    current_time: Optional[str] = None                      # Perceived world time (ISO format)

# -----------------------------------------------------------------------------
# AgentActionInput (Frontend → Backend)
# -----------------------------------------------------------------------------
# This is the main payload sent from frontend to backend,
# representing an action request along with the agent's current perception/context.
class AgentActionInput(BaseModel):
    agent_id: str                       # Which agent is acting
    timestamp: str                      # When the action occurs (ISO 8601)
    action_type: str                    # e.g., 'move', 'interact', 'perceive'
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
    content: Dict[str, Any]             # Action-specific details (see AgentActionContent)
    emoji: str                          # Visual representation (e.g., '🚶', '💡', '👀')
    current_tile: Optional[List[int]] = None     # (Optional) Updated [x, y] tile position
    current_location: Optional[str] = None       # (Optional) Updated semantic location (e.g., 'kitchen')
    
    
# -----------------------------------------------------------------------------
# simple response message
# -----------------------------------------------------------------------------
class StatusMsg(BaseModel):
    status: str

