"""
Multi-Agent Playground - Core Agent Implementation
=================================================
Core Agent class representing individual agents in the multi-agent simulation.

This module implements the Agent class which encapsulates:
- Agent identity and personality traits (innate, learned, current state)
- Planning system (daily schedules, requirements, current actions)
- Memory system (event storage with timestamp, location, salience)
- Perception handling (visible objects and agents)
- State persistence (JSON file-based storage)

Each agent maintains its data in separate JSON files (agent.json, memory.json)
and provides methods for updating state, adding memories, and serializing
data for LLM/planner consumption.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

class Agent:
    """
    Represents an agent in the system with attributes and methods.
    Each agent's data and memory are stored in local JSON files under the agent's directory.
    """
    def __init__(self, config_path: str):
        """
        Loads agent configuration and memory from JSON files.
        Args:
            config_path (str): Path to the agent's directory (should contain agent.json and memory.json).
        """
        self.agent_dir = Path(config_path)
        
        # Load agent configuration from agent.json
        with open(self.agent_dir / "agent.json", "r", encoding="utf-8") as file:
            data: Dict[str, Any] = json.load(file)

        # Core state fields
        self.agent_id = data.get("agent_id")
        self.vision_r = data.get("vision_r", 4)
        self.retention = data.get("retention", 5)
        self.curr_time = data.get("curr_time")
        self.curr_tile = data.get("curr_tile")
        self.daily_plan_req = data.get("daily_plan_req")
        self.name = data.get("name")
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")
        self.age = data.get("age")
        self.innate = data.get("innate")
        self.learned = data.get("learned")
        self.currently = data.get("currently")
        self.lifestyle = data.get("lifestyle")
        self.living_area = data.get("living_area")
        self.daily_req = data.get("daily_req", [])
        self.f_daily_schedule = data.get("f_daily_schedule", [])
        self.f_daily_schedule_hourly_org = data.get("f_daily_schedule_hourly_org", [])
        self.act_address = data.get("act_address")
        self.act_start_time = data.get("act_start_time")
        self.act_duration = data.get("act_duration")
        self.act_description = data.get("act_description")
        self.act_pronunciation = data.get("act_pronunciation")
        self.act_event = data.get("act_event")
        self.act_obj_description = data.get("act_obj_description")
        self.act_obj_pronunciation = data.get("act_obj_pronunciation")
        self.act_obj_event = data.get("act_obj_event")
        self.chatting_with = data.get("chatting_with")
        self.chat = data.get("chat", [])
        self.chatting_with_buffer = data.get("chatting_with_buffer", {})
        self.chatting_end_time = data.get("chatting_end_time")
        self.act_path_set = data.get("act_path_set", False)
        self.planned_path = data.get("planned_path", [])

        # Load memory from memory.json
        mem_path = self.agent_dir / "memory.json"
        if mem_path.exists():
            with open(mem_path, "r", encoding="utf-8") as f:
                self.memory = json.load(f)
        else:
            self.memory = []

        # Runtime-only (not persisted, updated per perception)
        self.visible_objects = {}
        self.visible_agents = []

    def update_perception(self, perception: Dict[str, Any]):
        """
        Updates visible objects and agents from the perception dict.
        Args:
            perception (dict): Typically from the frontend.
        """
        self.visible_objects = perception.get("visible_objects", {})
        self.visible_agents = perception.get("visible_agents", [])

    def update_agent_data(self, data: Dict[str, Any]):
        """
        Updates core agent fields if present in the data dict.
        Args:
            data (dict): New values for agent state.
        """
        if "current_tile" in data:
            self.curr_tile = data["current_tile"]
        if "timestamp" in data:
            self.curr_time = data["timestamp"]
        if "currently" in data:
            self.currently = data["currently"]

    def add_memory_event(self, timestamp: str, location: str, event: str, salience: int):
        """
        Adds a new event to the agent's memory.
        Args:
            timestamp (str): ISO8601 time.
            location (str): Location string.
            event (str): Event description.
            salience (int): Emotional significance.
        """
        self.memory.append({
            "timestamp": timestamp,
            "location": location,
            "event": event,
            "salience": salience
        })

    def save(self):
        """
        Saves the agent's core data to agent.json.
        """
        data = self.__dict__.copy()
        data.pop("memory", None)         # Do not persist memory here
        data.pop("agent_dir", None)      # Do not persist the path itself
        data.pop("visible_objects", None)
        data.pop("visible_agents", None)
        with open(self.agent_dir / "agent.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def save_memory(self):
        """
        Saves the agent's memory to memory.json.
        """
        with open(self.agent_dir / "memory.json", "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=2, default=str)

    def to_state_dict(self):
        """
        Returns a dict with the agent's state, suitable for LLMs/planners.
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "curr_tile": self.curr_tile,
            "daily_req": self.daily_req,
            "memory": self.memory,
            "visible_objects": self.visible_objects,
            "visible_agents": self.visible_agents,
            "currently": self.currently,
            # Add more fields as needed
        }
