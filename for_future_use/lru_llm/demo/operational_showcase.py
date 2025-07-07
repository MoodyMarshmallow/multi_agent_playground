#!/usr/bin/env python3
"""
Arush LLM Package - Operational Showcase
========================================

This demo shows the Arush LLM package actually operating as a multi-agent system.
Watch agents make decisions, move around, chat with each other, and interact with objects
in a realistic house environment.
"""

import sys
import time
import json
import random
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

# Import the optimized components
from lru_llm.agent.memory import AgentMemory, MemoryContextBuilder
from lru_llm.agent.location import LocationTracker
from lru_llm.utils.cache import AgentDataCache
from lru_llm.utils.prompts import PromptTemplates
from lru_llm.utils.parsers import ResponseParser, ActionValidator

@dataclass
class AgentState:
    """Represents the state of an agent."""
    agent_id: str
    first_name: str
    last_name: str
    age: int
    personality: str
    occupation: str
    current_tile: List[int]
    current_room: str
    energy: int = 100
    mood: str = "neutral"
    current_goal: str = "exploring"

@dataclass
class EnvironmentObject:
    """Represents an interactive object in the environment."""
    name: str
    position: List[int]
    room: str
    state: str
    description: str
    possible_actions: List[str]

@dataclass
class AgentAction:
    """Represents an action taken by an agent."""
    agent_id: str
    action_type: str
    content: Dict[str, Any]
    emoji: str
    timestamp: str

class MockEnvironment:
    """Simulates the house environment with rooms and objects."""
    
    def __init__(self):
        self.rooms = {
            "kitchen": {"bounds": [(20, 8), (24, 12)], "description": "Modern kitchen with appliances"},
            "living_room": {"bounds": [(10, 5), (18, 12)], "description": "Comfortable living area"},
            "bedroom": {"bounds": [(15, 15), (22, 20)], "description": "Cozy bedroom with furniture"},
            "office": {"bounds": [(18, 10), (25, 15)], "description": "Home office workspace"},
            "bathroom": {"bounds": [(12, 15), (16, 18)], "description": "Bathroom with amenities"}
        }
        
        self.objects = {
            "coffee_machine": EnvironmentObject("coffee_machine", [21, 8], "kitchen", "off", 
                                              "A modern coffee machine", ["use", "clean"]),
            "refrigerator": EnvironmentObject("refrigerator", [22, 8], "kitchen", "closed",
                                            "Large refrigerator with food", ["open", "close"]),
            "sofa": EnvironmentObject("sofa", [12, 7], "living_room", "empty",
                                    "Comfortable sofa for relaxing", ["sit", "lie_down"]),
            "tv": EnvironmentObject("tv", [10, 5], "living_room", "off",
                                  "Large TV for entertainment", ["watch", "turn_on", "turn_off"]),
            "bed": EnvironmentObject("bed", [18, 17], "bedroom", "made",
                                   "Comfortable bed for sleeping", ["sleep", "sit"]),
            "desk": EnvironmentObject("desk", [20, 12], "office", "clean",
                                    "Work desk with computer", ["work", "organize"]),
            "computer": EnvironmentObject("computer", [20, 12], "office", "off",
                                        "Desktop computer for work", ["use", "turn_on", "turn_off"])
        }
    
    def get_room_for_position(self, position: List[int]) -> str:
        """Get the room name for a given position."""
        x, y = position
        for room_name, room_data in self.rooms.items():
            (min_x, min_y), (max_x, max_y) = room_data["bounds"]
            if min_x <= x <= max_x and min_y <= y <= max_y:
                return room_name
        return "unknown"
    
    def get_objects_in_room(self, room: str) -> List[EnvironmentObject]:
        """Get all objects in a specific room."""
        return [obj for obj in self.objects.values() if obj.room == room]
    
    def get_nearby_objects(self, position: List[int], radius: int = 2) -> List[EnvironmentObject]:
        """Get objects near a position."""
        nearby = []
        for obj in self.objects.values():
            distance = abs(obj.position[0] - position[0]) + abs(obj.position[1] - position[1])
            if distance <= radius:
                nearby.append(obj)
        return nearby

class MockLLMResponse:
    """Simulates realistic LLM responses for different scenarios."""
    
    @staticmethod
    def generate_perceive_response(agent: AgentState, visible_objects: List[EnvironmentObject]) -> str:
        """Generate a realistic perception response."""
        if visible_objects:
            obj_names = [obj.name for obj in visible_objects[:2]]
            responses = [
                f"I'm in the {agent.current_room}, feeling {agent.mood}. I can see {', '.join(obj_names)}.",
                f"Looking around the {agent.current_room}. I notice the {obj_names[0]} here.",
                f"I'm here in the {agent.current_room}, checking out the {obj_names[0]}. Energy: {agent.energy}%."
            ]
        else:
            responses = [
                f"I'm in the {agent.current_room}, feeling {agent.mood}. The space looks clean.",
                f"Looking around the {agent.current_room}. It's a nice, peaceful area.",
                f"I'm in the {agent.current_room}. Nothing particularly interesting catches my eye right now."
            ]
        return random.choice(responses)
    
    @staticmethod
    def generate_move_response(agent: AgentState, environment: MockEnvironment) -> Dict[str, Any]:
        """Generate a realistic movement decision."""
        possible_rooms = list(environment.rooms.keys())
        current_room = agent.current_room
        
        # Choose a different room based on agent's current goal
        if agent.current_goal == "exploring":
            target_room = random.choice([r for r in possible_rooms if r != current_room])
        elif agent.current_goal == "working":
            target_room = "office"
        elif agent.current_goal == "relaxing":
            target_room = "living_room"
        elif agent.current_goal == "eating":
            target_room = "kitchen"
        else:
            target_room = random.choice(possible_rooms)
        
        # Get a position in that room
        bounds = environment.rooms[target_room]["bounds"]
        target_x = random.randint(bounds[0][0], bounds[1][0])
        target_y = random.randint(bounds[0][1], bounds[1][1])
        
        return {
            "destination_coordinates": [target_x, target_y],
            "reason": f"I want to go to the {target_room} to continue {agent.current_goal}"
        }
    
    @staticmethod
    def generate_chat_response(agent: AgentState, target_agent: str) -> Dict[str, Any]:
        """Generate a realistic chat message."""
        messages = [
            f"Hey {target_agent}! How are you doing today?",
            f"Hi {target_agent}, I'm in the {agent.current_room}. Want to hang out?",
            f"Hello {target_agent}! I'm feeling {agent.mood} today. What are you up to?",
            f"{target_agent}, have you seen anything interesting around here?",
            f"Good to see you {target_agent}! The {agent.current_room} is nice, isn't it?"
        ]
        
        return {
            "receiver": target_agent,
            "message": random.choice(messages),
            "tone": "friendly"
        }
    
    @staticmethod
    def generate_interact_response(agent: AgentState, target_object: EnvironmentObject) -> Dict[str, Any]:
        """Generate a realistic object interaction."""
        if target_object.possible_actions:
            action = random.choice(target_object.possible_actions)
        else:
            action = "examine"
        
        return {
            "object": target_object.name,
            "action": action,
            "reason": f"I want to {action} the {target_object.name}"
        }

class AgentSimulator:
    """Simulates a complete agent using the Arush LLM components."""
    
    def __init__(self, agent_state: AgentState, environment: MockEnvironment):
        self.agent_state = agent_state
        self.environment = environment
        
        # Initialize Arush LLM components
        self.memory = AgentMemory(agent_state.agent_id, memory_capacity=1000)
        self.location_tracker = LocationTracker(agent_state.agent_id, cache_size=200)
        self.cache = AgentDataCache(agent_id=agent_state.agent_id)
        self.prompt_templates = PromptTemplates()
        self.response_parser = ResponseParser()
        self.action_validator = ActionValidator()
        self.context_builder = MemoryContextBuilder(self.memory)
        
        # Update initial position
        self.location_tracker.update_position(tuple(agent_state.current_tile))
        
        # Add initial memory
        self.memory.add_event(
            timestamp=self._get_timestamp(),
            location=agent_state.current_room,
            event=f"I am {agent_state.first_name}, starting my day in the {agent_state.current_room}",
            salience=8,
            tags=["initialization", "identity"]
        )
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        return f"T{int(time.time() * 1000)}"
    
    def perceive_environment(self) -> AgentAction:
        """Simulate the perceive action."""
        print(f"🔍 {self.agent_state.first_name} is perceiving their environment...")
        
        # Get visible objects
        visible_objects = self.environment.get_nearby_objects(self.agent_state.current_tile)
        
        # Build context using memory
        relevant_memories = self.memory.get_relevant_memories("perception", limit=3)
        
        # Generate LLM response (simulated)
        perception_text = MockLLMResponse.generate_perceive_response(self.agent_state, visible_objects)
        
        # Add to memory
        self.memory.add_event(
            timestamp=self._get_timestamp(),
            location=self.agent_state.current_room,
            event=perception_text,
            salience=5,
            tags=["perception", self.agent_state.current_room]
        )
        
        return AgentAction(
            agent_id=self.agent_state.agent_id,
            action_type="perceive",
            content={"observation": perception_text, "visible_objects": [obj.name for obj in visible_objects]},
            emoji="👀",
            timestamp=self._get_timestamp()
        )
    
    def make_movement_decision(self) -> AgentAction:
        """Simulate the move action."""
        print(f"🚶 {self.agent_state.first_name} is deciding where to move...")
        
        # Get movement context from memory
        location_memories = self.memory.get_location_memories(self.agent_state.current_room, limit=2)
        
        # Generate movement decision (simulated LLM)
        movement_data = MockLLMResponse.generate_move_response(self.agent_state, self.environment)
        
        # Update agent position
        new_position = movement_data["destination_coordinates"]
        self.agent_state.current_tile = new_position
        new_room = self.environment.get_room_for_position(new_position)
        old_room = self.agent_state.current_room
        self.agent_state.current_room = new_room
        
        # Update location tracker
        self.location_tracker.update_position(tuple(new_position))
        
        # Add to memory
        self.memory.add_event(
            timestamp=self._get_timestamp(),
            location=f"{old_room} -> {new_room}",
            event=f"I moved to {new_position} in {new_room} because {movement_data.get('reason', 'I wanted to explore')}",
            salience=6,
            tags=["movement", new_room]
        )
        
        return AgentAction(
            agent_id=self.agent_state.agent_id,
            action_type="move",
            content=movement_data,
            emoji="🚶",
            timestamp=self._get_timestamp()
        )
    
    def chat_with_others(self, available_agents: List[str]) -> Optional[AgentAction]:
        """Simulate the chat action."""
        if not available_agents:
            return None
        
        target_agent = random.choice(available_agents)
        print(f"💬 {self.agent_state.first_name} is chatting with {target_agent}...")
        
        # Get conversation context
        conversation_memories = self.memory.get_conversation_context(target_agent, limit=2)
        
        # Generate chat response (simulated LLM)
        chat_data = MockLLMResponse.generate_chat_response(self.agent_state, target_agent)
        
        # Add to memory
        self.memory.add_event(
            timestamp=self._get_timestamp(),
            location=self.agent_state.current_room,
            event=f"I chatted with {target_agent}: '{chat_data['message']}'",
            salience=7,
            tags=["conversation", target_agent, self.agent_state.current_room]
        )
        
        return AgentAction(
            agent_id=self.agent_state.agent_id,
            action_type="chat",
            content=chat_data,
            emoji="💬",
            timestamp=self._get_timestamp()
        )
    
    def interact_with_object(self) -> Optional[AgentAction]:
        """Simulate the interact action."""
        nearby_objects = self.environment.get_nearby_objects(self.agent_state.current_tile)
        if not nearby_objects:
            return None
        
        target_object = random.choice(nearby_objects)
        print(f"🤝 {self.agent_state.first_name} is interacting with {target_object.name}...")
        
        # Generate interaction response (simulated LLM)
        interaction_data = MockLLMResponse.generate_interact_response(self.agent_state, target_object)
        
        # Update object state (simulated)
        if interaction_data["action"] == "use" and target_object.name == "coffee_machine":
            target_object.state = "brewing"
        elif interaction_data["action"] == "sit" and target_object.name == "sofa":
            target_object.state = "occupied"
        
        # Add to memory
        self.memory.add_event(
            timestamp=self._get_timestamp(),
            location=self.agent_state.current_room,
            event=f"I interacted with {target_object.name}: {interaction_data['action']} - {interaction_data.get('reason', '')}",
            salience=6,
            tags=["interaction", target_object.name, self.agent_state.current_room]
        )
        
        return AgentAction(
            agent_id=self.agent_state.agent_id,
            action_type="interact",
            content=interaction_data,
            emoji="🤝",
            timestamp=self._get_timestamp()
        )
    
    def update_mood_and_goals(self):
        """Update agent's internal state based on recent activities."""
        recent_memories = self.memory.get_recent_memories(5)
        
        # Simple mood/goal updating logic
        interaction_count = sum(1 for m in recent_memories if "interaction" in m.get("tags", []))
        chat_count = sum(1 for m in recent_memories if "conversation" in m.get("tags", []))
        
        if interaction_count > 2:
            self.agent_state.mood = "productive"
            self.agent_state.current_goal = "working"
        elif chat_count > 1:
            self.agent_state.mood = "social"
            self.agent_state.current_goal = "socializing"
        else:
            self.agent_state.mood = "exploratory"
            self.agent_state.current_goal = "exploring"
        
        # Update energy (simple simulation)
        self.agent_state.energy = max(20, self.agent_state.energy - random.randint(5, 15))

class OperationalShowcase:
    """Main showcase orchestrating the multi-agent simulation."""
    
    def __init__(self):
        self.environment = MockEnvironment()
        self.agents = self._create_agents()
        self.simulation_step = 0
        
    def _create_agents(self) -> Dict[str, AgentSimulator]:
        """Create a set of diverse agents."""
        agent_configs = [
            {
                "agent_id": "alex_001",
                "first_name": "Alex",
                "last_name": "Chen",
                "age": 28,
                "personality": "curious and analytical",
                "occupation": "Software Developer",
                "current_tile": [21, 9],
                "current_room": "kitchen"
            },
            {
                "agent_id": "sarah_002", 
                "first_name": "Sarah",
                "last_name": "Johnson",
                "age": 32,
                "personality": "friendly and organized",
                "occupation": "Project Manager",
                "current_tile": [14, 8],
                "current_room": "living_room"
            },
            {
                "agent_id": "mike_003",
                "first_name": "Mike",
                "last_name": "Rodriguez",
                "age": 25,
                "personality": "energetic and creative", 
                "occupation": "Designer",
                "current_tile": [19, 12],
                "current_room": "office"
            }
        ]
        
        agents = {}
        for config in agent_configs:
            state = AgentState(**config)
            agents[config["agent_id"]] = AgentSimulator(state, self.environment)
        
        return agents
    
    def run_simulation_step(self):
        """Run one step of the simulation."""
        self.simulation_step += 1
        print(f"\n{'='*60}")
        print(f"🏠 SIMULATION STEP {self.simulation_step}")
        print(f"{'='*60}")
        
        # Each agent takes an action
        for agent_id, agent_sim in self.agents.items():
            print(f"\n--- {agent_sim.agent_state.first_name}'s Turn ---")
            print(f"📍 Location: {agent_sim.agent_state.current_room} {agent_sim.agent_state.current_tile}")
            print(f"🎯 Goal: {agent_sim.agent_state.current_goal} | Mood: {agent_sim.agent_state.mood} | Energy: {agent_sim.agent_state.energy}%")
            
            # Decide action type based on agent's personality and situation
            action_type = self._choose_action_for_agent(agent_sim)
            
            action = None
            if action_type == "perceive":
                action = agent_sim.perceive_environment()
            elif action_type == "move":
                action = agent_sim.make_movement_decision()
            elif action_type == "chat":
                other_agents = [a.agent_state.first_name for aid, a in self.agents.items() if aid != agent_id]
                action = agent_sim.chat_with_others(other_agents)
            elif action_type == "interact":
                action = agent_sim.interact_with_object()
            
            if action:
                self._display_action(action)
                
            # Update agent state
            agent_sim.update_mood_and_goals()
            
            # Small delay for readability
            time.sleep(0.3)
    
    def _choose_action_for_agent(self, agent_sim: AgentSimulator) -> str:
        """Choose an appropriate action for the agent based on context."""
        personality = agent_sim.agent_state.personality
        energy = agent_sim.agent_state.energy
        current_goal = agent_sim.agent_state.current_goal
        
        # Weighted action selection
        if energy < 30:
            return "perceive"  # Low energy, just observe
        elif "social" in personality or current_goal == "socializing":
            return random.choices(["chat", "move", "perceive"], weights=[0.5, 0.3, 0.2])[0]
        elif "analytical" in personality or current_goal == "working":
            return random.choices(["interact", "perceive", "move"], weights=[0.4, 0.4, 0.2])[0]
        elif "energetic" in personality or current_goal == "exploring":
            return random.choices(["move", "interact", "chat"], weights=[0.4, 0.3, 0.3])[0]
        else:
            return random.choice(["perceive", "move", "chat", "interact"])
    
    def _display_action(self, action: AgentAction):
        """Display the action taken by an agent."""
        print(f"   {action.emoji} ACTION: {action.action_type.upper()}")
        
        if action.action_type == "perceive":
            print(f"      👁️  Observation: {action.content.get('observation', 'Looking around...')}")
            if action.content.get('visible_objects'):
                print(f"      🔍 Visible: {', '.join(action.content['visible_objects'])}")
                
        elif action.action_type == "move":
            dest = action.content.get('destination_coordinates', [0, 0])
            reason = action.content.get('reason', 'Exploring')
            print(f"      🗺️  Moving to: {dest}")
            print(f"      💭 Reason: {reason}")
            
        elif action.action_type == "chat":
            receiver = action.content.get('receiver', 'someone')
            message = action.content.get('message', 'Hello!')
            print(f"      💌 To {receiver}: '{message}'")
            
        elif action.action_type == "interact":
            obj = action.content.get('object', 'something')
            act = action.content.get('action', 'examine')
            reason = action.content.get('reason', 'Just curious')
            print(f"      🎮 Action: {act} {obj}")
            print(f"      💭 Reason: {reason}")
    
    def display_agent_status(self):
        """Display current status of all agents."""
        print(f"\n{'='*60}")
        print("📊 AGENT STATUS SUMMARY")
        print(f"{'='*60}")
        
        for agent_id, agent_sim in self.agents.items():
            agent = agent_sim.agent_state
            recent_memories = agent_sim.memory.get_recent_memories(3)
            
            print(f"\n🧑 {agent.first_name} ({agent.occupation})")
            print(f"   📍 Location: {agent.current_room} {agent.current_tile}")
            print(f"   🎯 Goal: {agent.current_goal} | Mood: {agent.mood} | Energy: {agent.energy}%")
            print(f"   🧠 Recent memories: {len(recent_memories)}")
            
            if recent_memories:
                latest = recent_memories[0]
                print(f"   💭 Latest: {latest['event'][:50]}...")
    
    def display_environment_status(self):
        """Display current state of the environment."""
        print(f"\n{'='*60}")
        print("🏠 ENVIRONMENT STATUS")
        print(f"{'='*60}")
        
        for room_name, room_data in self.environment.rooms.items():
            objects_in_room = self.environment.get_objects_in_room(room_name)
            agents_in_room = [a.agent_state.first_name for a in self.agents.values() 
                            if a.agent_state.current_room == room_name]
            
            print(f"\n🏘️  {room_name.upper()}: {room_data['description']}")
            if agents_in_room:
                print(f"   👥 Agents: {', '.join(agents_in_room)}")
            if objects_in_room:
                for obj in objects_in_room:
                    print(f"   📦 {obj.name}: {obj.state}")

def main():
    """Run the operational showcase."""
    print("🚀 Arush LLM Package - OPERATIONAL SHOWCASE")
    print("=" * 60)
    print("Watch real agents operating in a multi-agent environment!")
    print("Agents will perceive, move, chat, and interact autonomously.")
    print("=" * 60)
    
    showcase = OperationalShowcase()
    
    # Initial status
    showcase.display_environment_status()
    showcase.display_agent_status()
    
    # Run simulation steps
    try:
        for step in range(6):  # Run 6 simulation steps
            showcase.run_simulation_step()
            
            if step % 2 == 1:  # Every 2 steps, show status
                showcase.display_agent_status()
            
            # Brief pause between steps
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Simulation stopped by user")
    
    # Final status
    print(f"\n{'='*60}")
    print("🏁 SIMULATION COMPLETE")
    print(f"{'='*60}")
    
    showcase.display_agent_status()
    showcase.display_environment_status()
    
    # Performance summary
    print(f"\n📈 PERFORMANCE METRICS:")
    total_memories = sum(len(a.memory.get_recent_memories(100)) for a in showcase.agents.values())
    print(f"   🧠 Total memories created: {total_memories}")
    print(f"   👥 Agents simulated: {len(showcase.agents)}")
    print(f"   🏠 Rooms explored: {len(showcase.environment.rooms)}")
    print(f"   📦 Objects available: {len(showcase.environment.objects)}")
    print(f"   ⏱️  Simulation steps: {showcase.simulation_step}")
    
    print(f"\n✅ The Arush LLM package successfully orchestrated {showcase.simulation_step} simulation steps")
    print("   with agents making autonomous decisions using optimized memory, location, and caching systems!")

if __name__ == "__main__":
    main() 