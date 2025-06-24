"""
Multi-Agent Playground - Main Controller
========================================
Core controller module that handles agent action planning, perception updates, and world state management.

This module implements the main control flow for multi-agent interactions including:
- Agent action planning and execution (move, chat, interact, perceive)
- World state perception generation and updates
- Message queue management for inter-agent communication
- Memory and event handling with salience evaluation
- LLM agent lifecycle management (creation, cleanup, status)
- Object and location tracking through spatial awareness
- JSON-based persistence for agent state and global messages

The controller serves as the bridge between the frontend (Godot) and backend systems,
orchestrating agent behaviors and maintaining consistent world state across all agents.
"""

import asyncio
import sys
from pathlib import Path
import uuid
import json
import os
from datetime import datetime, timedelta
import hashlib
from typing import Dict, Any, Optional

backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from character_agent.agent import Agent
from character_agent.actions import ActionsMixin
from character_agent.kani_agent import LLMAgent
from character_agent.agent_manager import call_llm_agent, agent_manager
from config.schema import (
    AgentActionInput, AgentActionOutput, AgentPerception, BackendAction, 
    MoveBackendAction, ChatBackendAction, InteractBackendAction, PerceiveBackendAction, Message,
    PlanActionResponse
)
from backend.objects.object_registry import object_registry

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
MESSAGES_PATH = PROJECT_ROOT / "data" / "world" / "messages.json"

# TODO: adjust/ what is a good timeout?
CONVERSATION_TIMEOUT_MINUTES = 30

# --- Utility functions ---

def load_json(path, default):
    """
    Load JSON data from a file, returning a default value if the file doesn't exist.
    
    Args:
        path: File path to the JSON file
        default: Default value to return if file doesn't exist or can't be read
        
    Returns:
        The loaded JSON data as a Python object, or the default value if loading fails
    """
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, data):
    """
    Save Python data as JSON to a file with pretty formatting.
    
    Args:
        path: File path where the JSON should be saved
        data: Python object to serialize and save as JSON
        
    Returns:
        None
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def parse_timestamp(timestamp_str):
    """
    Parse timestamp string that could be in either short format (01T04:35:20) or full ISO format (2024-06-13T10:00:00).
    
    Args:
        timestamp_str (str): Timestamp string in either full ISO format or short day+time format
        
    Returns:
        datetime: Parsed datetime object, or current time if parsing fails
    """
    try:
        # Try the full ISO format first
        return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        try:
            # Try the short format - use current date with the time from timestamp
            current_date = datetime.now().date()
            time_part = datetime.strptime(timestamp_str, "%dT%H:%M:%S").time()
            return datetime.combine(current_date, time_part)
        except ValueError:
            # If both fail, return current time as fallback
            return datetime.now()

# --- Message handling ---

def get_or_create_conversation_id(sender: str, receiver: str, queue: list) -> str:
    """
    Find existing conversation between two agents or create a new one.
    
    A conversation is considered active if:
    1. It's between the same agents (in either direction)
    2. The last message was within CONVERSATION_TIMEOUT_MINUTES
    
    Args:
        sender (str): ID of the agent sending the message
        receiver (str): ID of the agent receiving the message  
        queue (list): List of existing message dictionaries
        
    Returns:
        str: UUID string for the conversation ID (existing or newly generated)
    """
    print(f"DEBUG: get_or_create_conversation_id - {sender} -> {receiver}")
    print(f"DEBUG: Queue has {len(queue)} messages")
    
    # Sort messages by timestamp to find the most recent conversation
    sorted_messages = sorted(queue, key=lambda x: x.get("timestamp", ""), reverse=True)
    
    # Look for recent messages between these agents (in either direction)
    for msg in sorted_messages:
        print(f"DEBUG: Checking message: {msg['sender']} -> {msg['receiver']} at {msg['timestamp']}")
        # Check if this message is between the same two agents (either direction)
        if ((msg["sender"] == sender and msg["receiver"] == receiver) or 
            (msg["sender"] == receiver and msg["receiver"] == sender)):
            
            print(f"DEBUG: Found matching conversation: {msg['conversation_id']}")
            # Check if conversation is still active based on time
            try:
                msg_time = parse_timestamp(msg["timestamp"])
                current_time = datetime.now()
                
                # If the message is recent enough, use its conversation_id
                if current_time - msg_time < timedelta(minutes=CONVERSATION_TIMEOUT_MINUTES):
                    print(f"DEBUG: Using existing conversation_id: {msg['conversation_id']}")
                    return msg["conversation_id"]
                else:
                    print(f"DEBUG: Message too old, creating new conversation")
            except Exception as e:
                print(f"Error parsing timestamp {msg['timestamp']}: {e}")
                # If timestamp parsing fails, still use the conversation_id if it exists
                if msg.get("conversation_id"):
                    print(f"DEBUG: Using conversation_id despite timestamp error: {msg['conversation_id']}")
                    return msg["conversation_id"]
    
    # If no active conversation found, create a deterministic conversation ID
    # based on the agent pair and current time (rounded to nearest minute)
    current_time = datetime.now()
    time_key = current_time.strftime("%Y%m%d%H%M")  # Round to nearest minute
    agent_pair = sorted([sender, receiver])  # Sort to ensure consistent ordering
    conversation_key = f"{agent_pair[0]}_{agent_pair[1]}_{time_key}"
    
    print(f"DEBUG: Creating deterministic conversation_id for key: {conversation_key}")
    
    # Create a deterministic UUID based on the conversation key
    hash_object = hashlib.md5(conversation_key.encode())
    hash_hex = hash_object.hexdigest()
    
    # Convert to UUID format
    uuid_str = f"{hash_hex[:8]}-{hash_hex[8:12]}-{hash_hex[12:16]}-{hash_hex[16:20]}-{hash_hex[20:32]}"
    print(f"DEBUG: Generated conversation_id: {uuid_str}")
    return uuid_str

def append_message_to_queue(msg, location):
    """
    Add a message to the global message queue and save it to disk.
    
    Args:
        msg: Message object with sender, receiver, message, timestamp attributes
        location: Current location/tile where the message was sent
        
    Returns:
        None
    """
    queue = load_json(MESSAGES_PATH, [])
    print(f"DEBUG: append_message_to_queue - Queue has {len(queue)} messages before adding")
    
    # Get or create conversation ID
    conversation_id = get_or_create_conversation_id(msg.sender, msg.receiver, queue)
    print(f"DEBUG: append_message_to_queue - Using conversation_id: {conversation_id}")
    
    queue.append({
        "sender": msg.sender,
        "receiver": msg.receiver,
        "message": msg.message,
        "timestamp": msg.timestamp,
        "conversation_id": conversation_id,
        "location": location,
        "delivered": False
    })
    save_json(MESSAGES_PATH, queue)
    print(f"DEBUG: append_message_to_queue - Queue now has {len(queue)} messages after adding")
    
# this if for the agent to see the messages that it has not seen yet
# for example, in 1st round agent a sent a message to agent b, but agent b did not see it yet, then it can extract the message from the queue if it is not delivered yet
# but currently we do not save the message into the queue when agent a sent a message to agent b
# def inject_messages_for_agent(agent_id, agent, perception):
#     if not MESSAGES_PATH.exists():
#         return
#     queue = load_json(MESSAGES_PATH, [])
#     heard = []
#     updated = False
#     for msg in queue:
#         if msg["receiver"] == agent_id and not msg["delivered"]:
#             heard.append({
#                 "sender": msg["sender"],
#                 "receiver": msg["receiver"],
#                 "message": msg["message"],
#                 "timestamp": msg["timestamp"],
#                 "conversation_id": msg.get("conversation_id")
#             })
#             msg["delivered"] = True
#             event_str = f"Received message from {msg['sender']}: '{msg['message']}'"
#             salience = evaluate_event_salience(agent, event_str)
#             agent.add_memory_event(
#                 timestamp=msg["timestamp"],
#                 location=msg.get("location"),
#                 event=event_str,
#                 salience=salience
#             )
#             updated = True
#     if heard:
#         perception["heard_messages"] = perception.get("heard_messages", []) + heard
#     if updated:
#         save_json(MESSAGES_PATH, queue)
#         # Save memory after processing all messages
#         agent.save_memory()

# --- Event and location helpers ---
# TODO: neeed to replace this with the actual location of the agent from spatial memory
def extract_location(perception):
    """
    Extract location information from agent perception data.
    
    Args:
        perception: AgentPerception object or dict containing visible_objects
        
    Returns:
        str: Human-readable location description based on visible objects' rooms
    """
    # For Pydantic BaseModel, just use dot notation
    visible_objects = perception.visible_objects
    if visible_objects:
        rooms = {
            obj_data.get("room", "unknown location")
            for obj_data in visible_objects.values() if isinstance(obj_data, dict)
        }
        return " and ".join(rooms) if rooms else "unknown location"
    return "unknown location"

def build_event_description(next_action, perception):
    """
    Build a descriptive event string summarizing the action taken and perception received.
    
    Args:
        next_action (dict): Dictionary containing action_type and content details
        perception: AgentPerception object with visible_objects, visible_agents, heard_messages
        
    Returns:
        str: Human-readable description of what happened during this action/perception cycle
    """
    parts = []
    # Action details
    if next_action:
        t = next_action.get("action_type")
        if t == "move":
            destination = next_action.get("content", {}).get("destination_coordinates")
            if destination is not None:
                parts.append(f"I moved to position {destination}")
        elif t == "chat":
            content = next_action.get("content", {})
            receiver = content.get("receiver", "")
            msg = content.get("message", "")
            parts.append(f"I chatted with {receiver}: '{msg}'")
        elif t == "interact":
            content = next_action.get("content", {})
            obj = content.get("object", "")
            new_state = content.get("new_state", "")
            parts.append(f"I interacted with {obj}, changing it to {new_state}")
        elif t == "perceive":
            parts.append("I looked around and observed my surroundings")
    # Perception details
    if perception:
        if hasattr(perception, "visible_objects") and perception.visible_objects:
            visible_items = [
                f"{obj_name} in {obj_data.get('room', 'unknown room')}"
                for obj_name, obj_data in perception.visible_objects.items()
                if isinstance(obj_data, dict)
            ]
            if visible_items:
                parts.append(f"I could see: {', '.join(visible_items)}")
        if hasattr(perception, "visible_agents") and perception.visible_agents:
            parts.append(f"I saw these people: {', '.join(perception.visible_agents)}")
        if hasattr(perception, "heard_messages") and perception.heard_messages:
            for message in perception.heard_messages:
                parts.append(f"I heard {message.sender} say to {message.receiver}: '{message.message}'")
    return ". ".join(parts) if parts else "Nothing notable happened"


def get_updated_perception_for_agent(agent_id: str) -> AgentPerception:
    """
    Generate current perception data for an agent based on world state.
    
    Collects information about visible objects, visible agents, and undelivered messages
    from the current world state and returns it as a structured perception object.
    
    Args:
        agent_id (str): The ID of the agent to generate perception for
        
    Returns:
        AgentPerception: Object containing timestamp, current_tile, visible_objects,
                        visible_agents, chatable_agents, and heard_messages
    """
    # 1. Load the agent instance from the LLMAgentManager
    agent = agent_manager.get_agent(agent_id).agent 
    current_tile = agent.curr_tile
    timestamp = datetime.now().strftime("%dT%H:%M:%S")
    
    # 2. Find visible objects (same tile or room as the agent)
    visible_objects = {}
    for obj_name, obj in object_registry.items():
        # Check for visibility logic (here: tile-based, you could use room instead)
        if getattr(obj, 'position', None) == current_tile:
            visible_objects[obj_name] = {
                "room": getattr(obj, "room", "unknown"),
                "position": getattr(obj, "position", None),
                "state": getattr(obj, "state", None)
            }
    
    # 3. Find visible agents (excluding self) - loop through all LLMAgents in manager
    visible_agents = []
    chatable_agents = []
    for other_id, llm_agent in agent_manager._agents.items():
        if other_id == agent_id:
            continue
        other_agent = llm_agent.agent  # Each LLMAgent stores a .agent (real Agent object)
        if getattr(other_agent, 'curr_tile', None) == current_tile:
            visible_agents.append(other_id)
            chatable_agents.append(other_id)  # If you want more complex logic, change here
    
    # 4. Collect undelivered messages for this agent
    heard_messages = []
    queue = load_json(MESSAGES_PATH, [])
    updated = False
    for msg in queue:
        if msg["receiver"] == agent_id and not msg.get("delivered", False):
            heard_messages.append(Message(
                sender=msg["sender"],
                receiver=msg["receiver"],
                message=msg["message"],
                timestamp=msg.get("timestamp"),
                conversation_id=msg.get("conversation_id"),
            ))
            msg["delivered"] = True
            updated = True
    if updated:
        save_json(MESSAGES_PATH, queue)  # Only if any delivery status was changed
    
    # 5. Return up-to-date perception
    return AgentPerception(
        timestamp=timestamp,
        current_tile=current_tile,
        visible_objects=visible_objects,
        visible_agents=visible_agents,
        chatable_agents=chatable_agents,
        heard_messages=heard_messages
    )

# --- Core controller functions ---

def plan_next_action(agent_id: str) -> PlanActionResponse:
    """
    Plan and execute the next action for an agent based on current world state.
    
    This is the main controller function that:
    1. Gets updated perception for the agent
    2. Uses the LLM to decide on the next action
    3. Immediately applies the action to update world state
    4. Records the event in agent memory
    5. Returns the action and updated perception
    
    Args:
        agent_id (str): The ID of the agent to plan an action for
        
    Returns:
        PlanActionResponse: Object containing the planned action and updated perception
    """
    # 1. Get latest perception for this agent from the world state (not from passed-in parameter)
    perception = get_updated_perception_for_agent(agent_id)
    perception_dict = perception.model_dump()
    
    agent_dir = PROJECT_ROOT / "data" / "agents" / agent_id
    agent = Agent(agent_dir)
    agent.update_perception(perception.model_dump())
    agent.heard_messages = perception_dict.get("heard_messages", [])
    agent_state = agent.to_state_dict()

    # 1. Decide next action using LLM
    next_action = call_llm_agent(agent_state, perception_dict)
    current_tile = perception.current_tile or agent.curr_tile

    action_type = next_action.get("action_type")
    backend_action = None

    # 2. Immediately apply the action and update agent/object state
    if action_type == "move":
        destination = next_action["content"].get("destination_coordinates", [0, 0])
        backend_action = MoveBackendAction(action_type="move", destination_tile=tuple(destination))
        current_tile = tuple(destination)
        # Optionally update the agent's location here
        agent.update_agent_data({"current_tile": current_tile})
    elif action_type == "chat":
        content = next_action["content"]
        msg = Message(
            sender=agent_id,
            receiver=content.get("receiver", ""),
            message=content.get("message", ""),
            timestamp=perception.timestamp,
            conversation_id=content.get("conversation_id", "")
        )
        append_message_to_queue(msg, current_tile)
        backend_action = ChatBackendAction(action_type="chat", message=msg)
        # Optionally record chat history
    elif action_type == "interact":
        content = next_action["content"]
        # TODO: Here, actually update the object state in backend
        backend_action = InteractBackendAction(
            action_type="interact",
            object=content.get("object", ""),
            current_state=content.get("current_state", ""),
            new_state=content.get("new_state", "")
        )
        # Here you would also update your object_registry, for example:
        # object_registry[content["object"]].transition(content["new_state"])
    else:
        backend_action = PerceiveBackendAction(action_type="perceive")

    # Record event/memory as before
    event = build_event_description(next_action, perception)
    location = extract_location(perception)
    salience = evaluate_event_salience(agent, event)
    agent.update_agent_data({"currently": event})
    agent.add_memory_event(
        timestamp=perception.timestamp,
        location=location,
        event=event,
        salience=salience
    )
    agent.save()
    agent.save_memory()

    latest_perception = get_updated_perception_for_agent(agent_id)

    return PlanActionResponse(
        action=AgentActionOutput(
            agent_id=agent_id,
            action=backend_action,
            emoji=next_action.get("emoji", "👀"),
            timestamp=perception.timestamp,
            current_tile=current_tile
        ),
        perception=latest_perception
    )

# def confirm_action_and_update(agent_msg: AgentActionInput) -> None:
#     agent_dir = PROJECT_ROOT / "data" / "agents" / agent_msg.agent_id
#     agent = Agent(agent_dir)
#     perception = agent_msg.perception.model_dump()
#     agent.update_perception(perception)
#     agent_data = {
#         "timestamp": agent_msg.perception.timestamp,
#         "current_tile": agent_msg.perception.current_tile,
#     }
#     agent.update_agent_data(agent_data)
#     location = extract_location(perception)
#     event = build_event_description(agent_msg)
#     agent.update_agent_data({"currently": event})
#     salience = evaluate_event_salience(agent, event)
#     agent.add_memory_event(
#         timestamp=agent_msg.perception.timestamp,
#         location=location,
#         event=event,
#         salience=salience
#     )

#     # Chat handling: process messages in heard_messages
#     action = getattr(agent_msg, "action", None)
#     if action and getattr(action, "action_type", None) == "chat":
#         # For chat actions, store the heard_messages (messages sent TO this agent FROM other agents)
#         heard_messages = getattr(agent_msg.perception, "heard_messages", [])
#         location = getattr(agent, "curr_tile", None)
        
#         # Process each message in heard_messages
#         for msg in heard_messages:
#             # Save the message to the queue
#             append_message_to_queue(msg, location)
            
#             # Update receiver's memory (this agent)
#             receiver_event_str = f"Received message from {msg.sender}: '{msg.message}'"
#             receiver_salience = evaluate_event_salience(agent, receiver_event_str)
#             agent.add_memory_event(
#                 timestamp=msg.timestamp,
#                 location=location,
#                 event=receiver_event_str,
#                 salience=receiver_salience
#             )
            
#             # Update sender's memory (other agent)
#             sender_agent_dir = PROJECT_ROOT / "data" / "agents" / msg.sender
#             if sender_agent_dir.exists():
#                 sender_agent = Agent(sender_agent_dir)
#                 sender_event_str = f"Sent message to {msg.receiver}: '{msg.message}'"
#                 sender_salience = evaluate_event_salience(sender_agent, sender_event_str)
#                 sender_agent.add_memory_event(
#                     timestamp=msg.timestamp,
#                     location=location,
#                     event=sender_event_str,
#                     salience=sender_salience
#                 )
#                 sender_agent.save_memory()
    
#     # Save both agent state and memory at the end
#     agent.save()
#     agent.save_memory()




def evaluate_event_salience(agent: Agent, event_description: str) -> int:
    """
    Evaluate how important/salient an event is for a given agent using LLM.
    
    Uses the agent's LLM to determine the importance of an event on a scale,
    which helps prioritize which memories to retain and retrieve.
    
    Args:
        agent (Agent): The agent for whom to evaluate the event
        event_description (str): Description of the event to evaluate
        
    Returns:
        int: Salience score (typically 1-10), with 5 as default fallback on error
    """
    try:
        # Use the managed LLMAgent directly from agent_manager
        llm_agent = agent_manager.get_agent(agent.agent_id)
        
        salience = asyncio.run(llm_agent.evaluate_event_salience(event_description))
        print(f"Event salience evaluation: '{event_description}' = {salience}")
        return salience
    except Exception as e:
        print(f"Error evaluating salience: {e}")
        return 5  # Default fallback
