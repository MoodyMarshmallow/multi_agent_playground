"""
Schema conversion utilities for action results.
"""

from datetime import datetime
from config.schema import AgentActionOutput


class SchemaExporter:
    """
    Handles conversion of action results to schema objects for API responses.
    """
    
    def __init__(self, game):
        self.game = game
    
    def get_schema(self) -> AgentActionOutput:
        """
        Export the last action as an AgentActionOutput schema object.
        The description is narrative and user-friendly for the GUI chat, while the reason in NoOpAction remains technical.
        
        Returns:
            AgentActionOutput: Schema object representing the last action
            
        Raises:
            RuntimeError: If no action has been taken yet
        """
        if not self.game._last_action_result or not self.game._last_action_agent_id:
            raise RuntimeError("No action has been taken yet.")
            
        agent = self.game.characters.get(self.game._last_action_agent_id)
        current_room = agent.location.name if agent and agent.location else None
        
        # Compose a technical, GUI-friendly description
        # 1. Always include the action type and affected object (if any)
        action_type = getattr(self.game._last_action_result.house_action, 'action_type', 'noop')
        affected_object = self.game._last_action_result.object_id
        
        # 2. For NoOp, treat as non-fatal error with informative feedback
        if action_type == 'noop':
            # Get the actual reason from the action result
            action_reason = getattr(self.game._last_action_result.house_action, 'reason', 'Unknown command or invalid action')
            
            # Create error-focused description for agents
            description = f"ACTION FAILED: {action_reason}"
            
            # Add current context to help agent understand their situation
            if agent and agent.location:
                visible_items = [item.name for item in agent.location.items.values()]
                visible_characters = [char.name for char in agent.location.characters.values() if char.name != agent.name]
                available_exits = [f"{direction} to {destination.name}" for direction, destination in agent.location.connections.items()]
                
                context_lines = [f"You are currently in {current_room}."]
                if visible_items:
                    context_lines.append(f"Available items: {', '.join(visible_items)}")
                if visible_characters:
                    context_lines.append(f"Other characters: {', '.join(visible_characters)}")
                if available_exits:
                    context_lines.append(f"Available exits: {', '.join(available_exits)}")
                
                description += f" {' '.join(context_lines)}"
            
            reason = action_reason
        else:
            # For real actions, use the action result's description (assumed user-facing)
            description = self.game._last_action_result.description
            reason = None
            
        # Context for frontend (not in main description)
        visible_items = []
        visible_characters = []
        available_exits = []
        if agent and agent.location:
            visible_items = [item.name for item in agent.location.items.values()]
            visible_characters = [char.name for char in agent.location.characters.values() if char.name != agent.name]
            available_exits = [f"{direction} to {destination.name}" for direction, destination in agent.location.connections.items()]
            
        # Patch the NoOpAction reason if needed
        action_obj = self.game._last_action_result.house_action
        if action_type == 'noop' and hasattr(action_obj, 'reason'):
            action_obj.reason = reason
            
        return AgentActionOutput(
            agent_id=self.game._last_action_agent_id,
            action=action_obj,
            timestamp=datetime.now().isoformat(),
            current_room=current_room,
            description=description
        )