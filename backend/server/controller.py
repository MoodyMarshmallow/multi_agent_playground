import asyncio
import sys
from pathlib import Path
import uuid
import json
import os
from datetime import datetime, timedelta
import hashlib

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

# TODO: adjust/ what is a good timeout?
CONVERSATION_TIMEOUT_MINUTES = 30

# --- Utility functions ---

def load_json(path, default):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def parse_timestamp(timestamp_str):
    """Parse timestamp string that could be in either short format (01T04:35:20) or full ISO format (2024-06-13T10:00:00)"""
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
    Find existing conversation between these agents or create a new one.
    A conversation is considered active if:
    1. It's between the same agents (in either direction)
    2. The last message was within CONVERSATION_TIMEOUT_MINUTES
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
    # inject_messages_for_agent(agent_id, agent, perception_dict)
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

    # Chat handling: process messages in heard_messages
    action = getattr(agent_msg, "action", None)
    if action and getattr(action, "action_type", None) == "chat":
        # For chat actions, store the heard_messages (messages sent TO this agent FROM other agents)
        heard_messages = getattr(agent_msg.perception, "heard_messages", [])
        location = getattr(agent, "curr_tile", None)
        
        # Process each message in heard_messages
        for msg in heard_messages:
            # Save the message to the queue
            append_message_to_queue(msg, location)
            
            # Update receiver's memory (this agent)
            receiver_event_str = f"Received message from {msg.sender}: '{msg.message}'"
            receiver_salience = evaluate_event_salience(agent, receiver_event_str)
            agent.add_memory_event(
                timestamp=msg.timestamp,
                location=location,
                event=receiver_event_str,
                salience=receiver_salience
            )
            
            # Update sender's memory (other agent)
            sender_agent_dir = PROJECT_ROOT / "data" / "agents" / msg.sender
            if sender_agent_dir.exists():
                sender_agent = Agent(sender_agent_dir)
                sender_event_str = f"Sent message to {msg.receiver}: '{msg.message}'"
                sender_salience = evaluate_event_salience(sender_agent, sender_event_str)
                sender_agent.add_memory_event(
                    timestamp=msg.timestamp,
                    location=location,
                    event=sender_event_str,
                    salience=sender_salience
                )
                sender_agent.save_memory()
    
    # Save both agent state and memory at the end
    agent.save()
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
