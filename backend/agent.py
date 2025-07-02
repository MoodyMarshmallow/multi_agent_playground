"""
Multi-Agent Playground - Simple Agent Implementation
====================================================
Simplified Agent class for compatibility with the old backend structure.

This provides a lightweight agent representation that works with the 
text adventure games framework.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

from .text_adventure_games.things import Character


class Agent:
    """
    Simple agent class for compatibility with old backend APIs.
    """
    
    def __init__(self, agent_id: str, character: Optional[Character] = None):
        """
        Initialize agent with basic data.
        
        Args:
            agent_id: Unique identifier for the agent
            character: Optional Character instance from text adventure framework
        """
        self.agent_id = agent_id
        self.character = character
        
        # Basic agent data
        self.first_name = agent_id.split('_')[0] if '_' in agent_id else agent_id
        self.last_name = ""
        self.age = 25
        self.curr_time = None
        self.curr_room = character.location.name if character and character.location else None
        
        # Personality and background
        self.backstory = character.persona if character else f"I am {agent_id}"
        self.personality = "Friendly and curious"
        self.occupation = "Resident"
        self.currently = "Exploring the house"
        self.lifestyle = "Active"
        self.daily_req = []
        self.living_area = "House"
        
        # Planning
        self.f_daily_schedule = []
        
        # Memory system
        self.memory = []
        
        # Runtime perception data
        self.visible_objects = {}
        self.visible_agents = []
        self.chatable_agents = []
        self.heard_messages = []
    
    @classmethod
    def from_directory(cls, config_path: str):
        """
        Create agent from directory structure (for compatibility).
        
        Args:
            config_path: Path to agent directory
        """
        agent_dir = Path(config_path)
        agent_file = agent_dir / "agent.json"
        
        if agent_file.exists():
            with open(agent_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            agent_id = data.get("agent_id", agent_dir.name)
            agent = cls(agent_id)
            
            # Load data from JSON
            agent.first_name = data.get("first_name", agent.first_name)
            agent.last_name = data.get("last_name", "")
            agent.age = data.get("age", 25)
            agent.curr_time = data.get("curr_time")
            agent.curr_room = data.get("curr_room")
            agent.backstory = data.get("backstory", agent.backstory)
            agent.personality = data.get("personality", agent.personality)
            agent.occupation = data.get("occupation", agent.occupation)
            agent.currently = data.get("currently", agent.currently)
            agent.lifestyle = data.get("lifestyle", agent.lifestyle)
            agent.daily_req = data.get("daily_req", [])
            agent.living_area = data.get("living_area", "House")
            agent.f_daily_schedule = data.get("f_daily_schedule", [])
            
            # Load memory
            mem_file = agent_dir / "memory.json"
            if mem_file.exists():
                try:
                    with open(mem_file, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            agent.memory = json.loads(content)
                except (json.JSONDecodeError, FileNotFoundError):
                    agent.memory = []
            
            return agent
        else:
            # Create default agent
            return cls(agent_dir.name)
    
    def update_perception(self, perception: Dict[str, Any]):
        """
        Update visible objects and agents from perception.
        
        Args:
            perception: Perception data from frontend
        """
        self.visible_objects = perception.get("visible_objects", {})
        self.visible_agents = perception.get("visible_agents", [])
        self.chatable_agents = perception.get("chatable_agents", [])
        self.heard_messages = perception.get("heard_messages", [])
    
    def update_agent_data(self, data: Dict[str, Any]):
        """
        Update core agent fields.
        
        Args:
            data: New values for agent state
        """
        if "current_room" in data:
            self.curr_room = data["current_room"]
        if "timestamp" in data:
            self.curr_time = data["timestamp"]
        if "currently" in data:
            self.currently = data["currently"]
    
    def add_memory_event(self, timestamp: str, location: str, event: str, salience: int):
        """
        Add a new event to memory.
        
        Args:
            timestamp: ISO8601 timestamp
            location: Location where event occurred
            event: Event description
            salience: Emotional significance (1-10)
        """
        self.memory.append({
            "timestamp": timestamp,
            "location": location,
            "event": event,
            "salience": salience
        })
    
    def to_state_dict(self):
        """
        Return agent state for LLMs/planners.
        """
        return {
            "agent_id": self.agent_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "curr_room": self.curr_room,
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
        Return agent summary for frontend initialization.
        """
        return {
            "agent_id": self.agent_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "curr_room": self.curr_room,
            "age": self.age,
            "occupation": self.occupation,
            "currently": self.currently,
        }
    
    def save(self):
        """
        Save agent data (placeholder - would save to data/agents/).
        """
        pass
    
    def save_memory(self):
        """
        Save memory data (placeholder - would save to data/agents/).
        """
        pass 