"""
This file implements action functions for character agents.
"""

from typing import Annotated, Dict, Any
from kani import ai_function
import json

class ActionsMixin:
    """
    This class implements action functions for character agents.
    Produces JSON output to send to the frontend.
    """
    
    def __init__(self):
        # This should be set by the character class that uses this mixin
        self.agent_id = getattr(self, 'agent_id', 'unknown_agent')
    
    @ai_function()
    def move(self,
             destination_coordinates: Annotated[tuple[int, int], "The coordinates to move to"],
             action_emoji: Annotated[str, "The emoji representing the action"]
             ) -> Dict[str, Any]:
        """
        Move to the specified coordinates.
        Returns JSON action for frontend communication.
        """
        action_json = {
            "agent_id": getattr(self, 'agent_id', 'unknown_agent'),
            "action_type": "move",
            "content": {
                "destination_coordinates": list(destination_coordinates)  # Convert tuple to list for JSON
            },
            "emoji": action_emoji
        }
        
        # Print JSON for debugging/logging
        print(f"Move action: {json.dumps(action_json, indent=2)}")
        
        return action_json
    
    @ai_function()
    def interact(self,
                 object: Annotated[str, "The object to interact with"],
                 new_state: Annotated[str, "The state the object should be changed to"],
                 action_emoji: Annotated[str, "The emoji representing the action"]
                 ) -> Dict[str, Any]:
        """
        Interact with the specified object.
        Returns JSON action for frontend communication.
        """
        action_json = {
            "agent_id": getattr(self, 'agent_id', 'unknown_agent'),
            "action_type": "interact",
            "content": {
                "object": object,
                "new_state": new_state
            },
            "emoji": action_emoji
        }
        
        # Print JSON for debugging/logging
        print(f"Interact action: {json.dumps(action_json, indent=2)}")
        
        return action_json

    @ai_function()
    def perceive(self,
                 action_emoji: Annotated[str, "The emoji representing the action"]
                 ) -> Dict[str, Any]:
        """
        Perceive the objects in the agent's visible area.
        Returns JSON action for frontend communication.
        """
        
        action_json = {
            "agent_id": getattr(self, 'agent_id', 'unknown_agent'),
            "action_type": "perceive",
            "content": {
            },
            "emoji": action_emoji
        }
        
        # Print JSON for debugging/logging
        print(f"Perceive action: {json.dumps(action_json, indent=2)}")
        
        return action_json
        
        
        