"""
Multi-Agent Playground - Game Controller
=======================================
Main controller that bridges HTTP endpoints with the text adventure games
framework and manages multi-agent interactions.

This implements:
- Game world initialization using text adventure framework
- Multi-agent turn management  
- Event queue for frontend synchronization
- Action planning and execution for LLM agents
- World state management and perception generation
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Text adventure games imports
from .text_adventure_games.games import Game

# Agent management
from .agent import AgentManager
from .infrastructure.agents.kani_agent import KaniAgent, ManualAgent

from config.schema import AgentActionOutput
from .log_config import log_game_event, log_action_execution

# Application service import
from .application.services.game_orchestrator import GameOrchestrator
from .domain.events.domain_event import AgentActionEvent
from .domain.events.event_bus import EventBus

# Module-level logger
logger = logging.getLogger(__name__)

class GameLoop:
    """
    Drives the game loop for the multi-agent playground.
    Also enqueues events for the frontend to consume.
    
    NOTE: This class now delegates most logic to GameOrchestrator while
    maintaining backward compatibility for all public APIs.
    """
    
    def __init__(self, config_file_path: str, agent_config: Optional[Dict[str, str]] = None,
                 world_config_path: Optional[str] = None):
        # Initialize the application orchestrator
        self._orchestrator = GameOrchestrator(config_file_path, world_config_path)
        
        # Legacy properties maintained for backward compatibility
        self.agent_config = agent_config or {}
        self.config_file_path = config_file_path
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        
    
    # Legacy properties for backward compatibility
    @property
    def game(self) -> Optional[Game]:
        """Get the game instance from orchestrator."""
        return self._orchestrator.get_infrastructure_game()
    
    @property
    def agent_manager(self) -> Optional[AgentManager]:
        """Get the agent manager from orchestrator."""
        return self._orchestrator.get_agent_manager()
    
    @property
    def turn_counter(self) -> int:
        """Get the turn counter from orchestrator."""
        game_state = self._orchestrator.get_game_state_entity()
        return game_state.turn_counter if game_state else 0
    
    @property
    def max_turns_per_session(self) -> int:
        """Get the max turns per session from orchestrator."""
        game_state = self._orchestrator.get_game_state_entity()
        return game_state.max_turns_per_session if game_state else 1000
    
    @property
    def objects_registry(self) -> Dict[str, Dict]:
        """Get the objects registry from orchestrator."""
        return self._orchestrator.get_objects_registry()
    
    async def start(self):
        """Initialize and start the game loop in the background."""
        if not self.is_running:
            await self.initialize()
            self.is_running = True
            self.task = asyncio.create_task(self.run_game_loop())
            logger.info("Game loop started in the background")

    async def stop(self):
        """Stop the game loop."""
        if self.is_running and self.task:
            self.is_running = False
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass  # Expected
            logger.info("Game loop stopped")

    async def run_game_loop(self):
        """The main game loop where agents take turns."""
        while self.is_running:
            # Delegate to orchestrator for turn execution
            try:
                action_schema, action_ended_turn = await self._orchestrator.execute_next_turn()
                
                # Log the turn if an action was taken
                if action_schema:
                    game_state = self._orchestrator.get_game_state_entity()
                    turn_counter = game_state.turn_counter if game_state else 0
                    
                    turn_status = "ended turn" if action_ended_turn else "continued turn"
                    log_game_event("turn_end", {
                        "agent": action_schema.get('agent_id', 'unknown'),
                        "turn": turn_counter,
                        "action": action_schema.get('action', {}).get('action_type', 'unknown'),
                        "status": turn_status
                    })
                
                # If no action was taken and no turn ended, we should break to avoid infinite loop
                if not action_schema and not action_ended_turn:
                    logger.info("No more actions to process, stopping game loop.")
                    break
                    
            except Exception as e:
                logger.error(f"Error in game loop: {e}")
                break

            # Small delay to prevent a tight loop
            await asyncio.sleep(1)  # Adjust as needed
    
    async def initialize(self):
        """Initialize the game world and agents."""
        # Delegate initialization to orchestrator
        await self._orchestrator.initialize()
        logger.info("Game controller initialized successfully")
    
    # Remove old implementation methods - now handled by orchestrator
    
    # Agent setup now handled by orchestrator
    
    # Agent strategy creation now handled by orchestrator
    
    # World state queries now handled by orchestrator
    
    def set_agent_config(self, agent_config: Dict[str, str]):
        """Update agent configuration and reinitialize agents."""
        self.agent_config = agent_config
        # Note: This would require stopping and restarting the game loop
        # to take effect, or implementing hot-swapping of agent strategies
    
    def get_agent_config(self) -> Dict[str, str]:
        """Get current agent configuration."""
        return self.agent_config.copy()
    
    # Objects registry initialization now handled by orchestrator
    
    async def get_world_state(self) -> Dict[str, Any]:
        """
        Get the complete state of the game world.
        """
        if not self.game or not self.agent_manager:
            return {"status": "not_initialized"}

        return {
            "agents": self.get_all_agent_states(),
            "objects": self.get_all_objects(),
            "locations": self.get_all_location_states(),
            "game_status": await self.get_game_status()
        }

    def get_all_agent_states(self) -> Dict[str, Dict]:
        """Get the state of all agents."""
        if not self.game:
            return {}
        
        states = {}
        for agent_id, character in self.game.characters.items():
            states[agent_id] = self.get_agent_state(agent_id)
        return states

    def get_all_location_states(self) -> Dict[str, Dict]:
        """Get the state of all locations."""
        if not self.game:
            return {}

        states = {}
        for loc_name, location in self.game.locations.items():
            states[loc_name] = {
                "name": loc_name,
                "description": location.description,
                "items": list(location.items.keys()),
                "characters": list(location.characters.keys()),
                "connections": {d: l.name for d, l in location.connections.items()}
            }
        return states
    
    
    
    def _print_action_output(self, action_output: AgentActionOutput):
        """Print AgentActionOutput in a readable format."""
        # Check if this is a noop action (non-fatal error)
        is_noop = action_output.action.action_type == "noop"
        
        if is_noop:
            # Log action error as WARNING level (abnormal behavior)
            error_details = []
            error_details.append(f"Agent: {action_output.agent_id}")
            error_details.append(f"Location: {action_output.current_room or 'Unknown'}")
            error_details.append(f"Error Type: Invalid Action (noop)")
            
            # Add action fields for debugging
            action_fields = self._get_action_fields(action_output.action)
            if action_fields:
                for field_name, field_value in action_fields.items():
                    if field_value is not None:
                        error_details.append(f"{field_name.title()}: {field_value}")
            
            error_details.append(f"Timestamp: {action_output.timestamp}")
            
            if action_output.description:
                error_details.append(f"Error Details: {action_output.description}")
            
            # Log as warning since this is abnormal behavior
            logger.warning("ACTION ERROR - " + " | ".join(error_details))
        else:
            # Normal action output - log as INFO (verbose mode only)
            success_details = []
            success_details.append(f"Agent: {action_output.agent_id}")
            success_details.append(f"Location: {action_output.current_room or 'Unknown'}")
            success_details.append(f"Action: {action_output.action.action_type}")
            
            # Add action fields dynamically (excluding action_type which we already showed)
            action_fields = self._get_action_fields(action_output.action)
            if action_fields:
                for field_name, field_value in action_fields.items():
                    if field_value is not None:  # Only show fields with values
                        success_details.append(f"{field_name.title()}: {field_value}")
            
            success_details.append(f"Timestamp: {action_output.timestamp}")
            
            if action_output.description:
                success_details.append(f"Result: {action_output.description}")
            
            # Log as info (only shown in verbose mode)
            logger.info("ACTION EXECUTED - " + " | ".join(success_details))
    
    def _get_action_fields(self, action) -> dict:
        """Extract all fields from an action object, excluding action_type."""
        fields = {}
        
        # Get all fields from the Pydantic model
        if hasattr(action, '__fields__'):
            # Pydantic v1 style
            for field_name in action.__fields__:
                if field_name != 'action_type':
                    fields[field_name] = getattr(action, field_name, None)
        elif hasattr(action, 'model_fields'):
            # Pydantic v2 style
            for field_name in action.model_fields:
                if field_name != 'action_type':
                    fields[field_name] = getattr(action, field_name, None)
        else:
            # Fallback: use __dict__ but filter out private attributes
            for field_name, field_value in action.__dict__.items():
                if not field_name.startswith('_') and field_name != 'action_type':
                    fields[field_name] = field_value
        
        return fields
    

    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp as ISO format string."""
        return datetime.now().isoformat()
    
    async def get_events_since(self, last_timestamp: str) -> List[AgentActionOutput]:
        """Get events since the specified timestamp."""
        event_bus = self._orchestrator.get_event_bus()
        if not event_bus:
            return []
        
        if not last_timestamp:
            # Get all agent action events
            domain_events = await event_bus.get_events_since("1970-01-01T00:00:00", "agent_action")
        else:
            domain_events = await event_bus.get_events_since(last_timestamp, "agent_action")
        
        # Convert domain events back to AgentActionOutput format
        agent_action_outputs = []
        for event in domain_events:
            if isinstance(event, AgentActionEvent):
                agent_action_outputs.append(AgentActionOutput(**event.to_agent_action_output()))
        
        return agent_action_outputs
    
    async def get_unserved_events(self) -> List[AgentActionOutput]:
        """Get events that haven't been served to the polling endpoint yet."""
        event_bus = self._orchestrator.get_event_bus()
        if not event_bus:
            return []
        
        # Get unserved events from event bus
        domain_events = await event_bus.get_unserved_events("frontend")
        
        # Convert to AgentActionOutput format and mark as served
        agent_action_outputs = []
        event_ids_to_mark = []
        
        for event in domain_events:
            if isinstance(event, AgentActionEvent):
                agent_action_outputs.append(AgentActionOutput(**event.to_agent_action_output()))
                event_ids_to_mark.append(event.event_id)
        
        # Mark events as served
        if event_ids_to_mark:
            await event_bus.mark_events_served(event_ids_to_mark, "frontend")
        
        return agent_action_outputs
    
    
    
    def get_agent_state(self, agent_id: str) -> Dict:
        """Get current state of a specific agent."""
        if not self.game:
            raise RuntimeError("Game not initialized")
        
        character = self.game.characters.get(agent_id)
        if not character:
            raise KeyError(f"Agent {agent_id} not found")
        
        return {
            "agent_id": agent_id,
            "location": character.location.name if character.location else None,
            "inventory": list(character.inventory.keys()),
            "properties": character.properties
        }
    
    def get_all_objects(self) -> List[Dict]:
        """Get all objects and their states."""
        return list(self.objects_registry.values())
    
    
    
    async def reset(self):
        """Reset the entire game."""
        await self.stop()
        
        # Reset orchestrator state (includes event bus reset)
        await self._orchestrator.reset()
        
        await self.start()
    
    async def get_game_status(self) -> Dict:
        """Get current game status."""
        if not self.game or not self.agent_manager:
            return {"status": "not_initialized"}
        
        # Get event count from event bus
        event_bus = self._orchestrator.get_event_bus()
        total_events = 0
        if event_bus:
            total_events = await event_bus.get_event_count()
        
        return {
            "status": "running",
            "turn_counter": self.turn_counter,
            "active_agents": len(self.agent_manager.active_agents),
            "total_events": total_events,
            "locations": len(self.game.locations),
            "characters": len(self.game.characters)
        } 