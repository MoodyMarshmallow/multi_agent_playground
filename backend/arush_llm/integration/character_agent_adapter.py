"""
Character Agent Adapter
======================
Provides a compatibility layer that replicates the character_agent interface
using optimized arush_llm components.

This adapter allows existing code to use arush_llm functionality without
changing the existing API interface.
"""

import json
import os
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

from ..agent.memory import AgentMemory, MemoryContextBuilder
from ..agent.location import LocationTracker
from ..utils.prompts import PromptTemplates
from ..utils.parsers import ResponseParser
from ..utils.cache import LRUCache, AgentDataCache


class CharacterAgentAdapter:
    """
    Adapter that provides the same interface as character_agent.Agent
    but uses optimized arush_llm components internally.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize agent adapter with the same interface as character_agent.Agent.
        
        Args:
            config_path (str): Path to agent directory containing agent.json and memory.json
        """
        self.agent_dir = Path(config_path)
        
        # Load agent configuration from agent.json
        with open(self.agent_dir / "agent.json", "r", encoding="utf-8") as file:
            data: Dict[str, Any] = json.load(file)

        # Core state fields - same as character_agent.Agent
        self.agent_id = data.get("agent_id")
        self.curr_time = data.get("curr_time")
        self.curr_tile = data.get("curr_tile")
        
        # Core Identity
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")
        self.age = data.get("age")
        
        # Personality and Background
        self.backstory = data.get("backstory")
        self.personality = data.get("personality")
        self.occupation = data.get("occupation")
        self.currently = data.get("currently")
        self.lifestyle = data.get("lifestyle")
        self.daily_req = data.get("daily_req")
        self.living_area = data.get("living_area")
        
        # Planning system
        self.f_daily_schedule = data.get("f_daily_schedule", [])
        
        # Initialize arush_llm components
        self._memory = AgentMemory(self.agent_id, str(self.agent_dir))
        self._location_tracker = LocationTracker(self.agent_id, str(self.agent_dir))
        self._memory_context_builder = MemoryContextBuilder(self._memory)
        
        # Legacy compatibility - memory list interface
        self.memory = []
        self._sync_memory_from_arush_llm()
        
        # Runtime-only (not persisted, updated per perception)
        self.visible_objects = {}
        self.visible_agents = []
        self.chatable_agents = []
        self.heard_messages = []

        # Update location if available
        if self.curr_tile:
            self._location_tracker.update_position(self.curr_tile)

    def _sync_memory_from_arush_llm(self):
        """Sync the legacy memory list from arush_llm memory system."""
        try:
            # Get all memories from arush_llm and convert to legacy format
            all_memories = self._memory.get_memories_by_salience(min_salience=1)
            self.memory = [
                {
                    "timestamp": mem.get("timestamp", ""),
                    "location": mem.get("location", ""),
                    "event": mem.get("event", ""),
                    "salience": mem.get("salience", 5)
                }
                for mem in all_memories
            ]
        except Exception as e:
            print(f"Warning: Could not sync memory from arush_llm: {e}")
            self.memory = []

    def _sync_memory_to_arush_llm(self):
        """Sync any changes in legacy memory list back to arush_llm."""
        # This handles cases where legacy code modified self.memory directly
        try:
            current_arush_memories = self._memory.get_memories_by_salience(min_salience=1)
            current_count = len(current_arush_memories)
            legacy_count = len(self.memory)
            
            # If legacy memory has more entries, add the new ones to arush_llm
            if legacy_count > current_count:
                for mem in self.memory[current_count:]:
                    self._memory.add_event(
                        timestamp=mem.get("timestamp", ""),
                        location=mem.get("location", ""),
                        event=mem.get("event", ""),
                        salience=mem.get("salience", 5)
                    )
        except Exception as e:
            print(f"Warning: Could not sync memory to arush_llm: {e}")

    def update_perception(self, perception: Dict[str, Any]):
        """
        Updates visible objects and agents from the perception dict.
        Same interface as character_agent.Agent.
        """
        self.visible_objects = perception.get("visible_objects", {})
        self.visible_agents = perception.get("visible_agents", [])
        self.chatable_agents = perception.get("chatable_agents", [])
        self.heard_messages = perception.get("heard_messages", [])
        
        # Update location tracker if position changed
        current_tile = perception.get("current_tile")
        if current_tile:
            self.curr_tile = current_tile
            self._location_tracker.update_position(current_tile)
        
        # Move chat messages to heard_messages
        if hasattr(self, "chat") and self.chat:
            self.heard_messages.extend(self.chat)
            self.chat = []
            self.save()

    def update_agent_data(self, data: Dict[str, Any]):
        """
        Updates core agent fields if present in the data dict.
        Same interface as character_agent.Agent.
        """
        if "curr_tile" in data:
            self.curr_tile = data["curr_tile"]
            self._location_tracker.update_position(self.curr_tile)
        if "curr_time" in data:
            self.curr_time = data["curr_time"]
        if "currently" in data:
            self.currently = data["currently"]
        if "pending_chat_message" in data:
            self.pending_chat_message = data["pending_chat_message"]

    def add_memory_event(self, timestamp: str, location: str, event: str, salience: int):
        """
        Adds a new event to the agent's memory using arush_llm backend.
        Same interface as character_agent.Agent.
        """
        # Add to arush_llm memory system
        memory_id = self._memory.add_event(timestamp, location, event, salience)
        
        # Also add to legacy memory list for compatibility
        memory_entry = {
            "timestamp": timestamp,
            "location": location,
            "event": event,
            "salience": salience
        }
        self.memory.append(memory_entry)
        
        return memory_id

    def save(self):
        """
        Saves the agent's core data to agent.json.
        Same interface as character_agent.Agent.
        """
        # Sync any legacy memory changes to arush_llm
        self._sync_memory_to_arush_llm()
        
        # Save using original logic
        data = self.__dict__.copy()
        data.pop("memory", None)         # Do not persist memory here
        data.pop("agent_dir", None)      # Do not persist the path itself
        data.pop("visible_objects", None)
        data.pop("visible_agents", None)
        data.pop("chatable_agents", None)
        data.pop("heard_messages", None)
        # Remove arush_llm components from persistence
        data.pop("_memory", None)
        data.pop("_location_tracker", None)
        data.pop("_memory_context_builder", None)
        
        with open(self.agent_dir / "agent.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def save_memory(self):
        """
        Saves the agent's memory using arush_llm backend.
        Same interface as character_agent.Agent.
        """
        # Sync any legacy memory changes first
        self._sync_memory_to_arush_llm()
        
        # Save using arush_llm (this will update the memory.json file)
        self._memory.save_memory()

    def to_state_dict(self):
        """
        Returns a dict with the agent's state, suitable for LLMs/planners.
        Same interface as character_agent.Agent.
        """
        # Ensure memory is synced
        self._sync_memory_from_arush_llm()
        
        return {
            "agent_id": self.agent_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "curr_tile": self.curr_tile,
            "daily_req": self.daily_req,
            "memory": self.memory,
            "visible_objects": self.visible_objects,
            "visible_agents": self.visible_agents,
            "chatable_agents": self.chatable_agents,
            "heard_messages": self.heard_messages,
            "currently": self.currently,
            "backstory": self.backstory,
            "personality": self.personality,
            "occupation": self.occupation,
        }

    def to_summary_dict(self):
        """
        Returns a summary dict for API usage.
        Same interface as character_agent.Agent.
        """
        # Ensure currently is always a string for API validation
        currently_value = getattr(self, "currently", "")
        if isinstance(currently_value, dict):
            currently_value = str(currently_value)
        elif not isinstance(currently_value, str):
            currently_value = str(currently_value) if currently_value is not None else ""
        
        return {
            "agent_id": self.agent_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "curr_tile": self.curr_tile,
            "age": getattr(self, "age", None),
            "occupation": getattr(self, "occupation", None),
            "currently": currently_value,
        }

    # Additional methods that provide enhanced functionality using arush_llm
    def get_relevant_memories(self, context: str, limit: int = 5, min_salience: int = 3):
        """Get relevant memories using arush_llm's optimized retrieval."""
        return self._memory.get_relevant_memories(context, limit, min_salience)

    def get_location_context(self):
        """Get current location context using arush_llm's location tracker."""
        return self._location_tracker.get_current_location()

    def get_memory_stats(self):
        """Get memory statistics using arush_llm's analytics."""
        return self._memory.get_memory_stats()


class LLMAgentManagerAdapter:
    """
    Adapter that provides the same interface as character_agent.agent_manager
    but uses optimized arush_llm components internally.
    """
    
    def __init__(self):
        self._agents: Dict[str, CharacterAgentAdapter] = {}
        self._agent_cache = AgentDataCache(capacity=50)
        
    def get_agent(self, agent_id: str) -> CharacterAgentAdapter:
        """Get or create an agent using arush_llm backend."""
        if agent_id not in self._agents:
            agent_dir = f"../data/agents/{agent_id}"
            self._agents[agent_id] = CharacterAgentAdapter(agent_dir)
        return self._agents[agent_id]
    
    def preload_all_agents(self, agents_folder="../data/agents"):
        """Load all agents from directory."""
        if not os.path.exists(agents_folder):
            print(f"Warning: agents folder {agents_folder} does not exist")
            return
            
        for agent_id in os.listdir(agents_folder):
            agent_path = os.path.join(agents_folder, agent_id)
            if os.path.isdir(agent_path):
                self.get_agent(agent_id)
    
    def get_all_agent_summaries(self):
        """Get summary of all managed agents."""
        return [agent.to_summary_dict() for agent in self._agents.values()]
    
    def remove_agent(self, agent_id: str):
        """Remove an agent from the manager."""
        if agent_id in self._agents:
            del self._agents[agent_id]
    
    def clear_all_agents(self):
        """Clear all agents from the manager."""
        self._agents.clear()
    
    def get_active_agent_count(self) -> int:
        """Get number of active agents."""
        return len(self._agents)


# Global instance for compatibility
agent_manager = LLMAgentManagerAdapter()


# Utility functions for character_agent compatibility
def call_llm_agent(agent_state: Dict[str, Any], perception_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Legacy compatibility function for LLM agent calls.
    This should be replaced with arush_llm implementations.
    """
    # This is a placeholder - in practice, this should use the arush_llm
    # integration layer or be replaced entirely
    agent_id = agent_state.get('agent_id')
    
    # Return a simple action for compatibility
    return {
        "agent_id": agent_id,
        "action_type": "perceive",
        "content": "Looking around",
        "emoji": "👀"
    }

async def call_llm_for_action(agent_state: Dict[str, Any], perception_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Async version of call_llm_agent for compatibility.
    """
    return call_llm_agent(agent_state, perception_data)


# Additional compatibility functions expected by tests
def create_llm_agent(agent_id: str, api_key: Optional[str] = None):
    """Create a new agent instance."""
    return agent_manager.get_agent(agent_id)

def get_llm_agent(agent_id: str):
    """Get existing agent if available."""
    return agent_manager._agents.get(agent_id)

def remove_llm_agent(agent_id: str):
    """Remove an agent from manager."""
    agent_manager.remove_agent(agent_id)

def clear_all_llm_agents():
    """Clear all agents from manager."""
    agent_manager.clear_all_agents()

def get_active_agent_count() -> int:
    """Get number of active agents."""
    return agent_manager.get_active_agent_count()

# Export the main classes for compatibility
Agent = CharacterAgentAdapter 