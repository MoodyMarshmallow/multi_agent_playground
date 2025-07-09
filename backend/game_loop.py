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

# Text adventure games imports
from .text_adventure_games.games import Game
from .text_adventure_games.things import Character, Location, Item

# Agent management
from .agent_manager import AgentManager, KaniAgent

# --- Canonical world setup from canonical_demo.py ---
from .text_adventure_games.house import build_house_game

from .config.schema import AgentActionOutput

class GameLoop:
    """
    Drives the game loop for the multi-agent playground.
    Also enqueues events for the frontend to consume.
    """
    
    def __init__(self):
        self.game: Optional[Game] = None
        self.agent_manager: Optional[AgentManager] = None
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        
        # Event system for frontend (only AgentActionOutput objects)
        self.event_queue: List[AgentActionOutput] = []
        self.event_id_counter = 0
        
        # Turn management
        self.turn_counter = 0
        self.max_turns_per_session = 1000
        
        # Objects registry for frontend
        self.objects_registry: Dict[str, Dict] = {}
        
        # Latest agent actions for polling
        self.latest_agent_actions: Dict[str, AgentActionOutput] = {}
    
    async def start(self):
        """Initialize and start the game loop in the background."""
        if not self.is_running:
            await self.initialize()
            self.is_running = True
            self.task = asyncio.create_task(self.run_game_loop())
            print("Game loop started in the background")

    async def stop(self):
        """Stop the game loop."""
        if self.is_running and self.task:
            self.is_running = False
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass  # Expected
            print("Game loop stopped")

    async def run_game_loop(self):
        """The main game loop where agents take turns."""
        while self.is_running:
            if self.turn_counter >= self.max_turns_per_session:
                print("Max turns reached, stopping game.")
                break

            agent = self.agent_manager.get_next_agent()
            if agent:
                # Execute turn and get schema
                action_schema = await self.agent_manager.execute_agent_turn(agent)
                
                # Only process if an action was actually taken
                if action_schema:
                    # Log the turn
                    print(f"Turn {self.turn_counter}: {agent.name} executed action")
                    
                    # Add the action schema directly as an event
                    self._add_action_event(action_schema)
                    
                    # Store the structured action for polling
                    self.latest_agent_actions[agent.name] = action_schema
                
                # Advance to the next agent (whether action succeeded or not)
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
        
        print("Game controller initialized successfully")
    
    def _build_house_environment(self) -> Game:
        """
        Create a house environment matching the canonical canonical_demo.py world.
        """
        
        return build_house_game()
    
    async def _setup_agents(self):
        """Setup AI agents for the non-player characters."""
        try:
            # Create Kani agents for each NPC
            alex_agent = KaniAgent(
                character_name="alex_001",
                persona="I am Alex, a friendly and social person who loves to chat with others. I enjoy reading books and might want to explore the house. I'm curious about what others are doing and like to help when I can."
            )
            
            alan_agent = KaniAgent(
                character_name="alan_002",
                persona="I am Alan, a quiet and thoughtful person who likes to observe and think. I prefer to explore slowly and examine things carefully. I might be interested in food and practical items."
            )
            
            # Register agents with the agent manager
            self.agent_manager.register_agent_strategy("alex_001", alex_agent)
            self.agent_manager.register_agent_strategy("alan_002", alan_agent)
            
            print("AI agents set up successfully")
        except Exception as e:
            import traceback
            print(f"Warning: Could not set up AI agents: {e}")
            print(f"Full error traceback:")
            traceback.print_exc()
            print("The game will run without AI agents for NPCs")
            # Just add the characters to active agents list without AI strategies
            self.agent_manager.active_agents.extend(["alex_001", "alan_002"])
    
    def _initialize_objects_registry(self):
        """Initialize the objects registry for frontend communication."""
        self.objects_registry = {}
        
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
        
        # Add event metadata to the action output
        action_output.event_id = self.event_id_counter
        action_output.event_type = "agent_action"
        
        # Print the AgentActionOutput in readable format
        self._print_action_output(action_output)
        
        self.event_queue.append(action_output)
    
    def _print_action_output(self, action_output: AgentActionOutput):
        """Print AgentActionOutput in a readable format."""
        print(f"\nEVENT #{action_output.event_id} ADDED TO QUEUE:")
        print("═" * 60)
        print(f"Agent: {action_output.agent_id}")
        print(f"Location: {action_output.current_room or 'Unknown'}")
        print(f"Action Type: {action_output.action.action_type}")
        
        # Print all action fields dynamically (excluding action_type which we already showed)
        action_fields = self._get_action_fields(action_output.action)
        if action_fields:
            for field_name, field_value in action_fields.items():
                if field_value is not None:  # Only show fields with values
                    print(f"{field_name.title()}: {field_value}")
        
        if action_output.current_object:
            print(f"Current Object: {action_output.current_object}")
        
        print(f"Timestamp: {action_output.timestamp}")
        
        if action_output.description:
            print(f"Description:")
            print("─" * 40)
            print(action_output.description)
            print("─" * 40)
        
        print("═" * 60)
    
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
    
    def get_events_since(self, last_event_id: int) -> List[AgentActionOutput]:
        """Get events since the specified ID."""
        return [event for event in self.event_queue if event.event_id > last_event_id]
    
    
    
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