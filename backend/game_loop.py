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
from .agent.agent_strategies import KaniAgent, ManualAgent

# --- Canonical world setup from canonical_demo.py ---
from .text_adventure_games.house import build_house_game

from .config.schema import AgentActionOutput
from .log_config import log_game_event, log_action_execution

# Module-level logger
logger = logging.getLogger(__name__)

class GameLoop:
    """
    Drives the game loop for the multi-agent playground.
    Also enqueues events for the frontend to consume.
    """
    
    def __init__(self, agent_config: Optional[Dict[str, str]] = None):
        self.game: Optional[Game] = None
        self.agent_manager: AgentManager  # Will be initialized in initialize()
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        
        # Agent configuration: maps agent_name -> agent_type ("ai" or "manual")
        self.agent_config = agent_config or {}
        
        # Event system for frontend (only AgentActionOutput objects)
        self.event_queue: List[AgentActionOutput] = []
        self.event_id_counter = 0
        
        # Turn management
        self.turn_counter = 0
        self.max_turns_per_session = 1000
        
        # Objects registry for frontend
        self.objects_registry: Dict[str, Dict] = {}
        
        # Track served events for polling endpoint
        self.last_served_event_index = 0
    
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
            if self.turn_counter >= self.max_turns_per_session:
                logger.warning("Max turns reached, stopping game.")
                break

            if not self.agent_manager:
                logger.error("Agent manager not initialized, stopping game.")
                break

            agent = self.agent_manager.get_next_agent()
            if agent:
                # Execute turn and get schema and turn-ending status
                action_schema, action_ended_turn = await self.agent_manager.execute_agent_turn(agent)
                
                # Only process if an action was actually taken
                if action_schema:
                    # Log the turn
                    turn_status = "ended turn" if action_ended_turn else "continued turn"
                    log_game_event("turn_end", {
                        "agent": agent.name,
                        "turn": self.turn_counter,
                        "action": getattr(action_schema.action, 'action_type', 'unknown'),
                        "status": turn_status
                    })
                    
                    # Add the action schema directly as an event
                    self._add_action_event(action_schema)
                
                # Only advance to the next agent if the action ended the turn
                if action_ended_turn:
                    self.agent_manager.advance_turn()
                    self.turn_counter += 1

            # Small delay to prevent a tight loop
            await asyncio.sleep(1)  # Adjust as needed
    
    async def initialize(self):
        """Initialize the game world and agents."""
        # Build the house environment
        self.game = self._build_house_environment()
        
        # Initialize agent manager
        self.agent_manager = AgentManager(self.game)
        
        # Create and register AI agents
        await self._setup_agents()
        
        # Initialize objects registry
        self._initialize_objects_registry()
        
        logger.info("Game controller initialized successfully")
    
    def _build_house_environment(self) -> Game:
        """
        Create a house environment matching the canonical canonical_demo.py world.
        """
        
        return build_house_game()
    
    async def _setup_agents(self):
        """Setup agents based on configuration (AI or manual)."""
        try:
            # Define agent personas
            agent_personas = {
                "alex_001": "I am Alex, a friendly and social person who loves to chat with others. I enjoy reading books and might want to explore the house. I'm curious about what others are doing and like to help when I can.",
                "alan_002": "I am Alan, a quiet and thoughtful person who likes to observe and think. I prefer to explore slowly and examine things carefully. I might be interested in food and practical items."
            }
            
            # Create agents based on configuration
            for agent_name, persona in agent_personas.items():
                agent_strategy = self._create_agent_strategy(agent_name, persona)
                if agent_strategy and self.agent_manager:
                    self.agent_manager.register_agent_strategy(agent_name, agent_strategy)
            
            logger.info("Agents set up successfully")
            if self.agent_config:
                manual_agents = [name for name, type_ in self.agent_config.items() if type_ == "manual"]
                ai_agents = [name for name, type_ in self.agent_config.items() if type_ == "ai"]
                logger.info(f"Manual agents: {manual_agents}")
                logger.info(f"AI agents: {ai_agents}")
            else:
                logger.info("All agents using AI (default)")
                
        except Exception as e:
            import traceback
            logger.warning(f"Could not set up agents: {e}")
            logger.warning("Full error traceback:")
            traceback.print_exc()
            logger.warning("The game will run without agent strategies")
            # Just add the characters to active agents list without strategies
            if self.agent_manager:
                self.agent_manager.active_agents.extend(["alex_001", "alan_002"])
    
    def _create_agent_strategy(self, character_name: str, persona: str):
        """Create either a manual or AI agent based on configuration."""
        agent_type = self.agent_config.get(character_name, "ai")  # Default to AI
        
        if agent_type == "manual":
            logger.info(f"Creating manual agent for {character_name}")
            return ManualAgent(character_name, persona)
        else:  # agent_type == "ai" or any other value
            try:
                logger.info(f"Creating AI agent for {character_name}")
                
                # Get initial world state by executing a look command for this character
                if self.game and character_name in self.game.characters:
                    character = self.game.characters[character_name]
                    initial_world_state = self._get_initial_world_state_for_agent(character)
                    return KaniAgent(character_name, persona, initial_world_state)
                else:
                    logger.warning(f"Character {character_name} not found, creating agent without initial state")
                    return KaniAgent(character_name, persona)
                    
            except Exception as e:
                logger.warning(f"Failed to create AI agent for {character_name}: {e}")
                logger.info(f"Falling back to manual agent for {character_name}")
                return ManualAgent(character_name, persona)
    
    def _get_initial_world_state_for_agent(self, character) -> str:
        """Get the initial world state for an agent by executing a look action."""
        from .text_adventure_games.actions.generic import EnhancedLookAction
        
        # Create and execute a look action for this character
        look_action = EnhancedLookAction(self.game, "look")
        look_action.character = character
        
        # Execute the look action to get formatted world state
        try:
            narration, schema = look_action.apply_effects()
            # Return the description which contains the formatted world state
            return schema.description if schema and schema.description else "You are in an unknown location."
        except Exception as e:
            logger.error(f"Error getting initial world state for {character.name}: {e}")
            return "You are in an unknown location. Use 'look' to see your surroundings."
    
    def set_agent_config(self, agent_config: Dict[str, str]):
        """Update agent configuration and reinitialize agents."""
        self.agent_config = agent_config
        # Note: This would require stopping and restarting the game loop
        # to take effect, or implementing hot-swapping of agent strategies
    
    def get_agent_config(self) -> Dict[str, str]:
        """Get current agent configuration."""
        return self.agent_config.copy()
    
    def _initialize_objects_registry(self):
        """Initialize the objects registry for frontend communication."""
        self.objects_registry = {}
        
        if not self.game:
            return
            
        for location_name, location in self.game.locations.items():
            for item_name, item in location.items.items():
                self.objects_registry[item_name] = {
                    "name": item_name,
                    "description": item.description,
                    "location": location_name,
                    "state": "default",  # You can expand this based on item properties
                    "gettable": item.get_property("gettable") if item.get_property("gettable") is not None else True
                }
    
    def get_world_state(self) -> Dict[str, Any]:
        """
        Get the complete state of the game world.
        """
        if not self.game or not self.agent_manager:
            return {"status": "not_initialized"}

        return {
            "agents": self.get_all_agent_states(),
            "objects": self.get_all_objects(),
            "locations": self.get_all_location_states(),
            "game_status": self.get_game_status()
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
    
    
    
    def _add_action_event(self, action_output: AgentActionOutput):
        """Add an AgentActionOutput to the event queue."""
        self.event_id_counter += 1
        
        # Print the AgentActionOutput in readable format
        self._print_action_output(action_output)
        
        self.event_queue.append(action_output)
    
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
    
    def get_events_since(self, last_timestamp: str) -> List[AgentActionOutput]:
        """Get events since the specified timestamp."""
        if not last_timestamp:
            return self.event_queue
        return [event for event in self.event_queue if event.timestamp and event.timestamp > last_timestamp]
    
    def get_unserved_events(self) -> List[AgentActionOutput]:
        """Get events that haven't been served to the polling endpoint yet."""
        unserved_events = self.event_queue[self.last_served_event_index:]
        # Update the index to mark these as served
        self.last_served_event_index = len(self.event_queue)
        return unserved_events
    
    
    
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
        self.event_queue.clear()
        self.event_id_counter = 0
        self.turn_counter = 0
        await self.start()
    
    def get_game_status(self) -> Dict:
        """Get current game status."""
        if not self.game or not self.agent_manager:
            return {"status": "not_initialized"}
        
        return {
            "status": "running",
            "turn_counter": self.turn_counter,
            "active_agents": len(self.agent_manager.active_agents),
            "total_events": len(self.event_queue),
            "locations": len(self.game.locations),
            "characters": len(self.game.characters)
        } 