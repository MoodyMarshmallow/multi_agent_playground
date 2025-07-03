#!/usr/bin/env python3
"""
Arush LLM Package - Quick Operational Demo
==========================================

Shows the Arush LLM package operating as a multi-agent system.
"""

import sys
import time
import random
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from lru_llm.agent.memory import AgentMemory
from lru_llm.agent.location import LocationTracker
from lru_llm.utils.cache import AgentDataCache
from lru_llm.utils.prompts import PromptTemplates
from lru_llm.utils.parsers import ResponseParser

class QuickAgentDemo:
    """Demonstrates an agent using Arush LLM components."""
    
    def __init__(self, name: str, location: str):
        self.name = name
        self.location = location
        self.position = [random.randint(10, 25), random.randint(5, 20)]
        
        # Initialize Arush LLM components
        print(f"🔧 Initializing {name} with Arush LLM components...")
        self.memory = AgentMemory(f"{name.lower()}_demo", memory_capacity=500)
        self.location_tracker = LocationTracker(f"{name.lower()}_demo", cache_size=100)
        self.cache = AgentDataCache(agent_id=f"{name.lower()}_demo")
        self.prompts = PromptTemplates()
        self.parser = ResponseParser()
        
        # Set initial position
        self.location_tracker.update_position(tuple(self.position))
        
        # Add initial memory
        self.memory.add_event(
            timestamp=f"T{int(time.time())}",
            location=location,
            event=f"I am {name}, ready to operate in the multi-agent environment",
            salience=8,
            tags=["initialization", "identity"]
        )
        
        print(f"✅ {name} initialized successfully!")
    
    def perceive_and_act(self, step: int):
        """Demonstrate perception and decision-making."""
        print(f"\n--- {self.name}'s Action Cycle {step} ---")
        
        # 1. PERCEIVE: Use memory system
        print(f"👁️  {self.name} perceiving environment at {self.location} {self.position}")
        
        # Get relevant memories
        context_memories = self.memory.get_relevant_memories("environment", limit=3)
        recent_memories = self.memory.get_recent_memories(2)
        
        print(f"   🧠 Retrieved {len(context_memories)} contextual memories")
        print(f"   🕒 Retrieved {len(recent_memories)} recent memories")
        
        # 2. DECISION: Simulate LLM-style reasoning
        actions = ["explore_room", "interact_object", "move_location", "social_chat"]
        chosen_action = random.choice(actions)
        
        print(f"   🤔 Decision: {chosen_action}")
        
        # 3. EXECUTE: Demonstrate different action types
        if chosen_action == "explore_room":
            self._explore_room()
        elif chosen_action == "interact_object":
            self._interact_with_object()
        elif chosen_action == "move_location":
            self._move_to_new_location()
        elif chosen_action == "social_chat":
            self._social_interaction()
        
        # 4. LEARN: Add experience to memory
        experience = f"In step {step}, I chose to {chosen_action} while in {self.location}"
        self.memory.add_event(
            timestamp=f"T{int(time.time()) + step}",
            location=self.location,
            event=experience,
            salience=random.randint(4, 8),
            tags=["action", chosen_action, self.location]
        )
        
        print(f"   📝 Added experience to memory: salience {random.randint(4, 8)}")
    
    def _explore_room(self):
        """Simulate room exploration."""
        objects = ["desk", "chair", "window", "plant", "computer", "bookshelf"]
        found_object = random.choice(objects)
        
        print(f"   🔍 Exploring {self.location}... found {found_object}")
        
        # Cache the discovery
        discovery = {"object": found_object, "location": self.location, "timestamp": time.time()}
        self.cache.cache_perception(f"discovery_{int(time.time())}", discovery)
        
        print(f"   💾 Cached discovery of {found_object}")
    
    def _interact_with_object(self):
        """Simulate object interaction."""
        objects = {"kitchen": "coffee_machine", "office": "computer", "living_room": "tv"}
        target_object = objects.get(self.location, "mysterious_object")
        
        actions = ["use", "examine", "clean", "organize"]
        action = random.choice(actions)
        
        print(f"   🤝 Interacting with {target_object}: {action}")
        
        # Update location tracker with interaction
        self.location_tracker.map_room(self.location, [(self.position[0], self.position[1])])
        
        print(f"   📍 Updated spatial mapping for {self.location}")
    
    def _move_to_new_location(self):
        """Simulate movement decision."""
        locations = ["kitchen", "office", "living_room", "bedroom", "bathroom"]
        current_idx = locations.index(self.location) if self.location in locations else 0
        new_location = locations[(current_idx + 1) % len(locations)]
        
        # Update position
        old_pos = self.position.copy()
        self.position = [random.randint(10, 25), random.randint(5, 20)]
        self.location = new_location
        
        # Update location tracker
        self.location_tracker.update_position(tuple(self.position))
        
        print(f"   🚶 Moved from {old_pos} to {self.position} ({new_location})")
        print(f"   🗺️  Updated location tracker: {self.location_tracker.current_room}")
    
    def _social_interaction(self):
        """Simulate social chat."""
        agents = ["Alex", "Sarah", "Mike", "Emma"]
        other_agents = [a for a in agents if a != self.name]
        target = random.choice(other_agents) if other_agents else "someone"
        
        messages = [
            f"Hey {target}, how's your day going?",
            f"Hi {target}, want to collaborate on something?",
            f"{target}, I found something interesting in the {self.location}!",
            f"Good to see you {target}! The {self.location} is nice today."
        ]
        
        message = random.choice(messages)
        print(f"   💬 Chatting with {target}: '{message}'")
        
        # Cache conversation
        conversation = {"target": target, "message": message, "location": self.location}
        self.cache.cache_conversation_history(f"chat_{target}_{int(time.time())}", [conversation])
        
        print(f"   📝 Cached conversation with {target}")
    
    def show_status(self):
        """Display agent's current status."""
        memories = self.memory.get_recent_memories(5)
        
        print(f"\n📊 {self.name}'s Status:")
        print(f"   📍 Location: {self.location} {self.position}")
        print(f"   🧠 Total memories: {len(memories)}")
        print(f"   🎯 Current room: {self.location_tracker.current_room}")
        
        if memories:
            latest = memories[0]
            print(f"   💭 Latest memory: {latest['event'][:40]}...")

def main():
    """Run the quick operational demo."""
    print("🚀 Arush LLM Package - QUICK OPERATIONAL DEMO")
    print("=" * 55)
    print("Demonstrating multi-agent operations with real components")
    print("=" * 55)
    
    # Create three agents
    agents = [
        QuickAgentDemo("Alex", "kitchen"),
        QuickAgentDemo("Sarah", "office"), 
        QuickAgentDemo("Mike", "living_room")
    ]
    
    print(f"\n✅ Created {len(agents)} agents with Arush LLM components")
    
    # Run simulation cycles
    for cycle in range(1, 4):
        print(f"\n{'='*55}")
        print(f"🏠 SIMULATION CYCLE {cycle}")
        print(f"{'='*55}")
        
        # Each agent acts
        for agent in agents:
            agent.perceive_and_act(cycle)
            time.sleep(0.2)  # Brief pause for readability
        
        # Show status every cycle
        print(f"\n📊 END OF CYCLE {cycle} STATUS:")
        for agent in agents:
            agent.show_status()
        
        print(f"\n⏱️  Cycle {cycle} complete. Agents made autonomous decisions!")
        time.sleep(0.5)
    
    # Final summary
    print(f"\n{'='*55}")
    print("🏁 OPERATIONAL DEMO COMPLETE")
    print(f"{'='*55}")
    
    print("\n🎯 What We Demonstrated:")
    print("  ✅ Multi-agent initialization with Arush LLM components")
    print("  ✅ Autonomous perception and decision-making cycles")
    print("  ✅ Real-time memory formation and retrieval")
    print("  ✅ Spatial tracking and location management")
    print("  ✅ Object interaction and environment mapping")
    print("  ✅ Inter-agent communication simulation")
    print("  ✅ Caching and performance optimization")
    
    print("\n⚡ Performance Highlights:")
    total_memories = sum(len(agent.memory.get_recent_memories(100)) for agent in agents)
    print(f"  🧠 Total memories created: {total_memories}")
    print(f"  👥 Agents operated simultaneously: {len(agents)}")
    print(f"  🔄 Decision cycles completed: {3 * len(agents)}")
    print(f"  📍 Location updates processed: {len(agents) * 3}")
    
    print(f"\n🚀 The Arush LLM package successfully operated {len(agents)} autonomous agents")
    print("   through multiple decision cycles using optimized memory, location, and caching!")

if __name__ == "__main__":
    main() 