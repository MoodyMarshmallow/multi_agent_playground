import json
from pathlib import Path
from datetime import datetime

class Agent:
    """
    Represents an agent in the system with attributes and methods
    """
    def __init__(self, config_path):
        """
        loads agent configuration from a JSON file.
        Input:
            config_path (str): path to the JSON config.
        """
        agent_dir = Path(agent_dir)
        with open(agent_dir / "agent.json", "r") as file:
            data = json.load(file)
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
        self.act_pronunciatio = data.get("act_pronunciatio")
        self.act_event = data.get("act_event")
        self.act_obj_description = data.get("act_obj_description")
        self.act_obj_pronunciatio = data.get("act_obj_pronunciatio")
        self.act_obj_event = data.get("act_obj_event")
        self.chatting_with = data.get("chatting_with")
        self.chat = data.get("chat", [])
        self.chatting_with_buffer = data.get("chatting_with_buffer", {})
        self.chatting_end_time = data.get("chatting_end_time")
        self.act_path_set = data.get("act_path_set", False)
        self.planned_path = data.get("planned_path", [])
        
        mem_path = agent_dir / "memory.json"
        if mem_path.exists():
            with open(mem_path, "r") as f:
                self.memory = json.load(f)
        else:
            self.memory = []
        
    def update_perception(self, perception):
        """
        Updates visible objects/agents from a dict.
        Input: perception (dict)
        """
        self.visible_objects = perception.get("visible_objects", {})
        self.visible_agents = perception.get("visible_agents", [])
    
    def to_state_dict(self):
        """
        Returns a dict with agent state suitable for tools/LLM/pipeline.
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "curr_tile": self.curr_tile,
            "daily_req": self.daily_req,
            "memory": self.memory,
            "visible_objects": self.visible_objects,
            "visible_agents": self.visible_agents,
            # Add more fields if tools need them
        }
        