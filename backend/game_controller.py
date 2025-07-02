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
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

# Text adventure games imports
from .text_adventure_games.games import Game
from .text_adventure_games.things import Character, Location, Item

# Agent management
from .agent_manager import AgentManager, KaniAgent

# Room-based location system only - no tiles needed


class GameController:
    """
    Main controller for the multi-agent playground.
    """
    
    def __init__(self):
        self.game: Optional[Game] = None
        self.agent_manager: Optional[AgentManager] = None
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        
        # Event system for frontend
        self.event_queue: List[Dict] = []
        self.event_id_counter = 0
        
        # Turn management
        self.turn_counter = 0
        self.max_turns_per_session = 1000
        
        # Objects registry for frontend
        self.objects_registry: Dict[str, Dict] = {}
    
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
                command, result = await self.agent_manager.execute_agent_turn(agent)
                
                # Log the action and result as an event
                self._add_event(
                    event_type="agent_action",
                    data={
                        "agent_id": agent.name,
                        "command": command,
                        "result": result,
                        "turn": self.turn_counter
                    }
                )
                
                # Advance to the next agent
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
        Create a house environment matching the Godot scene.
        """
        # Create rooms
        living_room = Location(
            "Living Room",
            "A cozy living room with a comfortable couch and TV. Sunlight streams through large windows."
        )
        
        kitchen = Location(
            "Kitchen", 
            "A modern kitchen with stainless steel appliances and granite countertops."
        )
        
        bathroom = Location(
            "Bathroom",
            "A clean bathroom with a bathtub, sink, and mirror."
        )
        
        bedroom = Location(
            "Bedroom",
            "A peaceful bedroom with a large bed and dresser. Soft lighting creates a relaxing atmosphere."
        )
        
        dining_room = Location(
            "Dining Room",
            "A formal dining room with a wooden table and elegant chairs."
        )
        
        # Connect rooms (bidirectional)
        living_room.add_connection("north", kitchen)
        kitchen.add_connection("south", living_room)
        
        living_room.add_connection("east", bedroom)
        bedroom.add_connection("west", living_room)
        
        kitchen.add_connection("east", dining_room)
        dining_room.add_connection("west", kitchen)
        
        dining_room.add_connection("south", bedroom)
        bedroom.add_connection("north", dining_room)
        
        bedroom.add_connection("northeast", bathroom)
        bathroom.add_connection("southwest", bedroom)
        
        # Add furniture and items
        couch = Item("couch", "a comfortable couch", "A plush three-seater couch perfect for relaxing.")
        couch.set_property("gettable", False)
        living_room.add_item(couch)
        
        tv = Item("tv", "a large TV", "A modern flat-screen television.")
        tv.set_property("gettable", False)
        living_room.add_item(tv)
        
        refrigerator = Item("refrigerator", "a large refrigerator", "A stainless steel refrigerator humming quietly.")
        refrigerator.set_property("gettable", False)
        kitchen.add_item(refrigerator)
        
        # Add gettable items
        book = Item("book", "a mystery novel", "A well-worn mystery novel with an intriguing cover.")
        living_room.add_item(book)
        
        apple = Item("apple", "a red apple", "A fresh, crispy apple that looks delicious.")
        apple.set_property("is_food", True)
        kitchen.add_item(apple)
        
        towel = Item("towel", "a fluffy towel", "A soft, clean towel.")
        bathroom.add_item(towel)
        
        # Create player character
        player = Character(
            "player", 
            "the main character",
            "I am exploring this house and interacting with other characters."
        )
        
        # Create other characters
        alex = Character(
            "alex_001",
            "Alex, a friendly resident",
            "I am Alex, a cheerful person who loves to chat and help others. I enjoy reading books and cooking."
        )
        
        alan = Character(
            "alan_002", 
            "Alan, a thoughtful person",
            "I am Alan, a quiet and contemplative individual. I like to observe my surroundings and think deeply about things."
        )
        
        # Place characters in different rooms
        bedroom.add_character(alex)
        kitchen.add_character(alan)
        
        # Create the game
        game = Game(
            start_at=living_room,
            player=player,
            characters=[alex, alan]
        )
        
        return game
    
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
            print(f"Warning: Could not set up AI agents: {e}")
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
    
    
    
    def _add_event(self, event_type: str, data: Dict):
        """Add an event to the queue."""
        self.event_id_counter += 1
        event = {
            "id": self.event_id_counter,
            "type": event_type,
            "timestamp": self._get_current_timestamp(),
            "data": data
        }
        self.event_queue.append(event)
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp as ISO format string."""
        return datetime.now().isoformat()
    
    def get_events_since(self, last_event_id: int) -> List[Dict]:
        """Get events since the specified ID."""
        return [e for e in self.event_queue if e["id"] > last_event_id]
    
    
    
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