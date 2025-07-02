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
from .agent_manager import AgentManager, KaniAgent, SimpleRandomAgent

# Schema imports
from .config.schema import (
    AgentSummary, AgentPerception, AgentActionInput, AgentActionOutput,
    PlanActionResponse, BackendAction, MoveBackendAction, ChatBackendAction,
    InteractBackendAction, PerceiveBackendAction, Message
)

# Room-based location system only - no tiles needed


class GameController:
    """
    Main controller for the multi-agent playground.
    """
    
    def __init__(self):
        self.game: Optional[Game] = None
        self.agent_manager: Optional[AgentManager] = None
        
        # Event system for frontend
        self.event_queue: List[Dict] = []
        self.event_id_counter = 0
        
        # Turn management
        self.turn_counter = 0
        self.max_turns_per_session = 1000
        
        # Objects registry for frontend
        self.objects_registry: Dict[str, Dict] = {}
    
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
            print("Using random agents as fallback")
            
            # Fallback to simple agents
            self.agent_manager.register_agent_strategy("alex_001", SimpleRandomAgent())
            self.agent_manager.register_agent_strategy("alan_002", SimpleRandomAgent())
    
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
    
    async def plan_agent_action(self, agent_id: str) -> PlanActionResponse:
        """
        Plan an action for an agent using their AI strategy.
        """
        if not self.game or not self.agent_manager:
            raise RuntimeError("Game not initialized")
        
        character = self.game.characters.get(agent_id)
        if not character:
            raise KeyError(f"Agent {agent_id} not found")
        
        # Get current perception
        perception = self._get_agent_perception(character)
        
        # Check if agent has a strategy
        if agent_id not in self.agent_manager.agent_strategies:
            # Return a default perceive action
            action = AgentActionOutput(
                agent_id=agent_id,
                action=PerceiveBackendAction(action_type="perceive"),
                emoji="👀",
                timestamp=self._get_current_timestamp(),
                current_room=character.location.name if character.location else None
            )
        else:
            # Get world state and plan action
            world_state = self.agent_manager.get_world_state_for_agent(character)
            strategy = self.agent_manager.agent_strategies[agent_id]
            
            try:
                command = await strategy.select_action(world_state)
                action = self._convert_command_to_action(agent_id, command, character)
            except Exception as e:
                print(f"Error planning action for {agent_id}: {e}")
                action = AgentActionOutput(
                    agent_id=agent_id,
                    action=PerceiveBackendAction(action_type="perceive"),
                    emoji="❌",
                    timestamp=self._get_current_timestamp(),
                    current_room=character.location.name if character.location else None
                )
        
        return PlanActionResponse(
            action=action,
            perception=perception
        )
    
    async def confirm_agent_action(self, action_input: AgentActionInput):
        """
        Confirm and execute an agent's action, updating the game state.
        """
        if not self.game:
            raise RuntimeError("Game not initialized")
        
        agent_id = action_input.agent_id
        character = self.game.characters.get(agent_id)
        if not character:
            raise KeyError(f"Agent {agent_id} not found")
        
        # Execute the action based on its type
        action = action_input.action
        
        if action.action_type == "move":
            await self._execute_move_action(character, action)
        elif action.action_type == "chat":
            await self._execute_chat_action(character, action)
        elif action.action_type == "interact":
            await self._execute_interact_action(character, action)
        elif action.action_type == "perceive":
            # Perceive actions don't change state, just return current perception
            pass
        
        # Add event to queue
        self._add_event(action.action_type, {
            "agent_id": agent_id,
            "action": action.dict(),
            "timestamp": self._get_current_timestamp()
        })
    
    def _convert_command_to_action(self, agent_id: str, command: str, character: Character) -> AgentActionOutput:
        """Convert a text command to an AgentActionOutput."""
        command_parts = command.lower().split()
        
        if not command_parts:
            return AgentActionOutput(
                agent_id=agent_id,
                action=PerceiveBackendAction(action_type="perceive"),
                emoji="👀",
                timestamp=self._get_current_timestamp(),
                current_room=character.location.name if character.location else None
            )
        
        action_verb = command_parts[0]
        
        # Movement commands
        if action_verb == "go" and len(command_parts) > 1:
            direction = command_parts[1]
            if character.location and direction in character.location.connections:
                destination = character.location.connections[direction]
                
                return AgentActionOutput(
                    agent_id=agent_id,
                    action=MoveBackendAction(
                        action_type="move",
                        destination_room=destination.name
                    ),
                    emoji="🚶",
                    timestamp=self._get_current_timestamp(),
                    current_room=character.location.name
                )
        
        # Chat commands (basic implementation)
        if action_verb == "say" or "hello" in command or "hi" in command:
            # For now, create a simple greeting message
            message = Message(
                sender=agent_id,
                receiver="player",  # Default to player
                message="Hello!",
                timestamp=self._get_current_timestamp()
            )
            
            return AgentActionOutput(
                agent_id=agent_id,
                action=ChatBackendAction(
                    action_type="chat",
                    message=message
                ),
                emoji="💬",
                timestamp=self._get_current_timestamp(),
                current_room=character.location.name
            )
        
        # Interact commands
        if action_verb in ["get", "take", "examine", "use"]:
            object_name = " ".join(command_parts[1:]) if len(command_parts) > 1 else "unknown"
            
            return AgentActionOutput(
                agent_id=agent_id,
                action=InteractBackendAction(
                    action_type="interact",
                    object=object_name,
                    current_state="default",
                    new_state="interacted"
                ),
                emoji="🤏",
                timestamp=self._get_current_timestamp(),
                current_room=character.location.name
            )
        
        # Default to perceive
        return AgentActionOutput(
            agent_id=agent_id,
            action=PerceiveBackendAction(action_type="perceive"),
            emoji="👀",
            timestamp=self._get_current_timestamp(),
            current_room=character.location.name if character.location else None
        )
    
    async def _execute_move_action(self, character: Character, action):
        """Execute a move action."""
        if hasattr(action, 'destination_room'):
            destination_name = action.destination_room
            destination = self.game.locations.get(destination_name)
            
            if destination and character.location:
                # Remove from current location
                character.location.remove_character(character)
                # Add to new location
                destination.add_character(character)
                character.location = destination
    
    async def _execute_chat_action(self, character: Character, action):
        """Execute a chat action."""
        # In a full implementation, this would handle message routing
        pass
    
    async def _execute_interact_action(self, character: Character, action):
        """Execute an interact action."""
        # In a full implementation, this would handle object interactions
        pass
    
    def _get_agent_perception(self, character: Character) -> AgentPerception:
        """Generate agent perception data."""
        if not character.location:
            return AgentPerception()
        
        # Get visible objects in location
        visible_objects = {}
        for item_name, item in character.location.items.items():
            visible_objects[item_name] = {
                "room": character.location.name,
                "state": "default"
            }
        
        # Get visible agents
        visible_agents = [
            char_name for char_name in character.location.characters.keys()
            if char_name != character.name
        ]
        
        return AgentPerception(
            timestamp=self._get_current_timestamp(),
            current_room=character.location.name,
            visible_objects=visible_objects,
            visible_agents=visible_agents,
            chatable_agents=visible_agents,  # For simplicity, all visible agents are chatable
            heard_messages=[]  # Would implement message system here
        )
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in the expected format."""
        return datetime.now().strftime("%dT%H:%M:%S")
    
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
    
    def get_events_since(self, last_event_id: int) -> List[Dict]:
        """Get events since the specified ID."""
        return [e for e in self.event_queue if e["id"] > last_event_id]
    
    def get_all_agent_summaries(self) -> List[AgentSummary]:
        """Get summaries of all agents."""
        if not self.game:
            return []
        
        summaries = []
        for agent_name, character in self.game.characters.items():
            summaries.append(AgentSummary(
                agent_id=agent_name,
                curr_room=character.location.name if character.location else None
            ))
        
        return summaries
    
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
    
    def reset_objects(self):
        """Reset all objects to initial state."""
        self._initialize_objects_registry()
    
    async def reset(self):
        """Reset the entire game."""
        await self.initialize()
        self.event_queue.clear()
        self.event_id_counter = 0
        self.turn_counter = 0
    
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