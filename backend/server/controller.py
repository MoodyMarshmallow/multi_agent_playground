import asyncio
import sys
from pathlib import Path
import uuid
import json
import os

backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from character_agent.agent import Agent
from character_agent.actions import ActionsMixin
from character_agent.kani_implementation import LLMAgent
from config.schema import (
    AgentActionInput, AgentActionOutput, AgentPerception, BackendAction, 
    MoveBackendAction, ChatBackendAction, InteractBackendAction, PerceiveBackendAction, Message
)

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
MESSAGES_PATH = PROJECT_ROOT / "data" / "world" / "messages.json"

# --- Utility functions ---

def load_json(path, default):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# --- Message handling ---

def append_message_to_queue(msg, location):
    queue = load_json(MESSAGES_PATH, [])
    queue.append({
        "sender": msg.sender,
        "receiver": msg.receiver,
        "message": msg.message,
        "timestamp": msg.timestamp,
        "conversation_id": msg.conversation_id,
        "location": location,
        "delivered": False
    })
    save_json(MESSAGES_PATH, queue)
    
# this if for the agent to see the messages that it has not seen yet
def inject_messages_for_agent(agent_id, agent, perception):
    if not MESSAGES_PATH.exists():
        return
    queue = load_json(MESSAGES_PATH, [])
    heard = []
    updated = False
    for msg in queue:
        if msg["receiver"] == agent_id and not msg["delivered"]:
            heard.append({
                "sender": msg["sender"],
                "receiver": msg["receiver"],
                "message": msg["message"],
                "timestamp": msg["timestamp"],
                "conversation_id": msg.get("conversation_id")
            })
            msg["delivered"] = True
            event_str = f"Received message from {msg['sender']}: '{msg['message']}'"
            salience = evaluate_event_salience(agent, event_str)
            agent.add_memory_event(
                timestamp=msg["timestamp"],
                location=msg.get("location"),
                event=event_str,
                salience=salience
            )
            agent.save_memory()
            updated = True
    if heard:
        perception["heard_messages"] = perception.get("heard_messages", []) + heard
    if updated:
        save_json(MESSAGES_PATH, queue)

# --- Event and location helpers ---

def extract_location(perception):
    if perception.get("visible_objects"):
        rooms = {
            obj_data.get("room", "unknown location")
            for obj_data in perception["visible_objects"].values() if isinstance(obj_data, dict)
        }
        return " and ".join(rooms) if rooms else "unknown location"
    return "unknown location"

def build_event_description(agent_msg):
    # Build an event string summarizing the action and perception
    action = getattr(agent_msg, "action", None)
    perception = getattr(agent_msg, "perception", None)
    parts = []
    if action and hasattr(action, 'action_type'):
        t = action.action_type
        if t == "move" and hasattr(action, 'destination_tile'):
            parts.append(f"I moved to position {action.destination_tile}")
        elif t == "chat" and hasattr(action, 'message'):
            msg = action.message
            parts.append(f"I chatted with {msg.receiver}: '{msg.message}'")
        elif t == "interact" and hasattr(action, 'object') and hasattr(action, 'new_state'):
            parts.append(f"I interacted with {action.object}, changing it to {action.new_state}")
        elif t == "perceive":
            parts.append("I looked around and observed my surroundings")
    # Perception details
    if perception:
        if perception.visible_objects:
            visible_items = [
                f"{obj_name} in {obj_data.get('room', 'unknown room')}"
                for obj_name, obj_data in perception.visible_objects.items()
                if isinstance(obj_data, dict)
            ]
            if visible_items:
                parts.append(f"I could see: {', '.join(visible_items)}")
        if perception.visible_agents:
            parts.append(f"I saw these people: {', '.join(perception.visible_agents)}")
        if perception.heard_messages:
            for message in perception.heard_messages:
                parts.append(f"I heard {message.sender} say to {message.receiver}: '{message.message}'")
    return ". ".join(parts) if parts else "Nothing notable happened"

# --- Core controller functions ---

def plan_next_action(agent_id: str, perception: AgentPerception) -> AgentActionOutput:
    agent_dir = PROJECT_ROOT / "data" / "agents" / agent_id
    agent = Agent(agent_dir)
    agent.update_perception(perception.model_dump())
    perception_dict = perception.model_dump()
    inject_messages_for_agent(agent_id, agent, perception_dict)
    agent.heard_messages = perception_dict.get("heard_messages", [])
    agent_state = agent.to_state_dict()
    next_action = LLMAgent.call_llm_agent(agent_state, perception_dict)
    current_tile = perception.current_tile or agent.curr_tile

    action_type = next_action.get("action_type")
    backend_action = None

    if action_type == "move":
        destination = next_action["content"].get("destination_coordinates", [0, 0])
        backend_action = MoveBackendAction(action_type="move", destination_tile=tuple(destination))
        current_tile = tuple(destination)
    elif action_type == "chat":
        content = next_action["content"]
        msg = Message(
            sender=agent_id,
            receiver=content.get("receiver", ""),
            message=content.get("message", ""),
            timestamp=perception.timestamp,
            conversation_id=content.get("conversation_id", "")
        )
        backend_action = ChatBackendAction(action_type="chat", message=msg)
    elif action_type == "interact":
        content = next_action["content"]
        backend_action = InteractBackendAction(
            action_type="interact",
            object=content.get("object", ""),
            current_state=content.get("current_state", ""),
            new_state=content.get("new_state", "")
        )
    else:
        backend_action = PerceiveBackendAction(action_type="perceive")

    return AgentActionOutput(
        agent_id=agent_id,
        action=backend_action,
        emoji=next_action.get("emoji", "👀"),
        timestamp=perception.timestamp,
        current_tile=current_tile
    )

def confirm_action_and_update(agent_msg: AgentActionInput) -> None:
    agent_dir = PROJECT_ROOT / "data" / "agents" / agent_msg.agent_id
    agent = Agent(agent_dir)
    perception = agent_msg.perception.model_dump()
    agent.update_perception(perception)
    agent_data = {
        "timestamp": agent_msg.perception.timestamp,
        "current_tile": agent_msg.perception.current_tile,
    }
    agent.update_agent_data(agent_data)
    location = extract_location(perception)
    event = build_event_description(agent_msg)
    agent.update_agent_data({"currently": event})
    salience = evaluate_event_salience(agent, event)
    agent.add_memory_event(
        timestamp=agent_msg.perception.timestamp,
        location=location,
        event=event,
        salience=salience
    )
    agent.save()
    agent.save_memory()

    # Chat handling: extract message from heard_messages in perception
    action = getattr(agent_msg, "action", None)
    if action and getattr(action, "action_type", None) == "chat":
        heard_messages = getattr(agent_msg.perception, "heard_messages", [])
        # Find the message sent by this agent in heard_messages
        msg_dict = next(
            (m for m in heard_messages if m.sender == agent_msg.agent_id),
            None
        )
        if msg_dict:
            msg = Message(**msg_dict)
            location = getattr(agent, "curr_tile", None)
            append_message_to_queue(msg, location)
            event_str = f"Sent message to {msg.receiver}: '{msg.message}'"
            salience = evaluate_event_salience(agent, event_str)
            agent.add_memory_event(
                timestamp=msg.timestamp,
                location=location,
                event=event_str,
                salience=salience
            )
            agent.save_memory()

def evaluate_event_salience(agent: Agent, event_description: str) -> int:
    try:
        llm_agent = LLMAgent(agent)
        salience = asyncio.run(llm_agent.evaluate_event_salience(event_description))
        print(f"Event salience evaluation: '{event_description}' = {salience}")
        return salience
    except Exception as e:
        print(f"Error evaluating salience: {e}")
        return 5  # Default fallback
