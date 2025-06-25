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

from arush_llm.agent.memory import AgentMemory
from arush_llm.agent.location import LocationTracker  
from arush_llm.utils.prompts import PromptTemplates
from arush_llm.utils.parsers import ResponseParser
from arush_llm.utils.cache import LRUCache

# Arush LLM imports - replaces character_agent
from arush_llm.integration.character_agent_adapter import CharacterAgentAdapter as Agent, agent_manager
from backend.config.schema import (
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
# TODO: neeed to replace this with the actual location of the agent from spatial memory
def extract_location(perception):
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
    Build an event string summarizing the action and perception.
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
    # 1. Get basic agent info (simplified for demo)
    timestamp = datetime.now().strftime("%dT%H:%M:%S")
    
    # 2. Use arush_llm LocationTracker to get current position
    location_tracker = LocationTracker(agent_id)
    location_data = location_tracker.get_current_location()
    current_tile = location_data.get("position", [0, 0]) if location_data else [0, 0]
    
    # 3. Find visible objects (simplified for demo)
    visible_objects = {}
    # In a real implementation, this would query the world state
    # For demo, we'll return empty objects
    
    # 4. Find visible agents (simplified for demo)
    visible_agents = []
    chatable_agents = []
    
    # For demo, simulate other agents being visible if they exist
    all_agent_ids = ["alex_001", "alan_002", "test_agent"]
    for other_id in all_agent_ids:
        if other_id != agent_id:
            # In a real implementation, check if agents are close enough
            visible_agents.append(other_id)
            chatable_agents.append(other_id)
    
    # 5. Collect undelivered messages for this agent
    heard_messages = []
    if MESSAGES_PATH.exists():
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
            save_json(MESSAGES_PATH, queue)
    
    # 6. Return up-to-date perception
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
    # 1. Get latest perception for this agent from the world state
    perception = get_updated_perception_for_agent(agent_id)
    perception_dict = perception.model_dump()
    
    # 2. Initialize arush_llm components
    memory = AgentMemory(agent_id)
    location_tracker = LocationTracker(agent_id)
    prompt_templates = PromptTemplates()
    parser = ResponseParser()
    
    # 3. Update location and memory with current perception
    if perception.current_tile:
        location_tracker.update_position(perception.current_tile)
    
    # 4. Generate action using arush_llm
    current_location_data = location_tracker.get_current_location()
    current_location = current_location_data.get("room", "unknown") if current_location_data else "unknown"
    
    # Add heard messages to memory
    for msg in perception.heard_messages or []:
        memory.add_event(
            timestamp=msg.timestamp,
            location=current_location,
            event=f"Heard from {msg.sender}: {msg.message}",
            salience=8
        )
    context = memory.get_relevant_memories(context=current_location, limit=10)
    
    # Build available actions list
    available_actions = ["move", "chat", "interact", "perceive"]
    
    # Create prompt for LLM (simplified for demo)
    # In a real implementation, this would be sent to an LLM
    context_str = "; ".join([mem.get("event", "") for mem in context]) if context else "No context"
    prompt = prompt_templates.generate_perceive_prompt(
        agent_data={"agent_id": agent_id},
        perception_data=perception_dict,
        memory_context=context_str,
        timestamp=perception.timestamp or datetime.now().strftime("%dT%H:%M:%S")
    )
    
    # Parse response (simplified for demo)
    action_type = "perceive"  # Default safe action
    emoji = "👀"
    backend_action = PerceiveBackendAction(action_type="perceive")
    current_tile = perception.current_tile or [0, 0]
    
    # Simple round-robin demo behavior
    import random
    if random.random() < 0.3:  # 30% chance to move
        action_type = "move"
        # Move to a nearby position
        x, y = current_tile if current_tile else [0, 0]
        destination = [x + random.randint(-2, 2), y + random.randint(-2, 2)]
        backend_action = MoveBackendAction(action_type="move", destination_tile=tuple(destination))
        current_tile = destination
        emoji = "🚶"
        
        # Update location tracker
        location_tracker.update_position(destination)
        
        # Add memory event
        memory.add_event(
            timestamp=perception.timestamp or datetime.now().strftime("%dT%H:%M:%S"),
            location=f"tile_{destination[0]}_{destination[1]}",
            event=f"Moved to position {destination}",
            salience=5
        )
    
    elif random.random() < 0.2 and perception.chatable_agents:  # 20% chance to chat
        action_type = "chat"
        receiver = random.choice(perception.chatable_agents)
        greetings = ["Hello!", "How are you?", "Nice day!", "What's up?"]
        message_text = random.choice(greetings)
        
        msg = Message(
            sender=agent_id,
            receiver=receiver,
            message=message_text,
            timestamp=perception.timestamp or datetime.now().strftime("%dT%H:%M:%S")
        )
        append_message_to_queue(msg, current_tile)
        backend_action = ChatBackendAction(action_type="chat", message=msg)
        emoji = "💬"
        
        # Add memory event
        memory.add_event(
            timestamp=perception.timestamp or datetime.now().strftime("%dT%H:%M:%S"),
            location=current_location,
            event=f"Chatted with {receiver}: {message_text}",
            salience=7
        )

    # 5. Save memory state
    memory.cleanup_old_memories(days_to_keep=7)
    
    # 6. Get updated perception
    latest_perception = get_updated_perception_for_agent(agent_id)

    return PlanActionResponse(
        action=AgentActionOutput(
            agent_id=agent_id,
            action=backend_action,
            emoji=emoji,
            timestamp=perception.timestamp or datetime.now().strftime("%dT%H:%M:%S"),
            current_tile=current_tile
        ),
        perception=latest_perception
    )

def confirm_action_and_update(agent_msg: AgentActionInput) -> None:
    """Update agent state and memory after action confirmation"""
    try:
        # Initialize arush_llm components
        memory = AgentMemory(agent_msg.agent_id)
        location_tracker = LocationTracker(agent_msg.agent_id)
        
        # Update location if position changed
        if agent_msg.perception.current_tile:
            location_tracker.update_position(agent_msg.perception.current_tile)
        
        # Get current location for events
        current_location_data = location_tracker.get_current_location()
        current_location = current_location_data.get("room", "unknown") if current_location_data else "unknown"
        
        # Build event description from action
        event_parts = []
        action = getattr(agent_msg, "action", None)
        if action:
            action_type = getattr(action, "action_type", "unknown")
            if action_type == "move":
                dest = getattr(action, "destination_tile", agent_msg.perception.current_tile)
                event_parts.append(f"Moved to tile {dest}")
            elif action_type == "chat":
                event_parts.append("Engaged in conversation")
            elif action_type == "interact":
                event_parts.append("Interacted with object")
            elif action_type == "perceive":
                event_parts.append("Observed surroundings")
        
        # Add perception context
        if agent_msg.perception.visible_agents:
            event_parts.append(f"Near agents: {', '.join(agent_msg.perception.visible_agents)}")
        if agent_msg.perception.visible_objects:
            obj_count = len(agent_msg.perception.visible_objects)
            event_parts.append(f"Observed {obj_count} objects")
        
        event_description = "; ".join(event_parts) if event_parts else "Activity completed"
        
        # Add event to memory
        memory.add_event(
            timestamp=agent_msg.perception.timestamp or datetime.now().strftime("%dT%H:%M:%S"),
            location=current_location,
            event=event_description,
            salience=5
        )
        
        # Process heard messages
        if agent_msg.perception.heard_messages:
            for msg in agent_msg.perception.heard_messages:
                memory.add_event(
                    timestamp=msg.get("timestamp", agent_msg.perception.timestamp),
                    location=current_location,
                    event=f"Heard from {msg.get('sender', 'unknown')}: {msg.get('message', '')}",
                    salience=8
                )
        
        # Clean up old memories
        memory.cleanup_old_memories(days_to_keep=7)
        
    except Exception as e:
        print(f"Error in confirm_action_and_update for agent {agent_msg.agent_id}: {e}")
        # Don't fail the request, just log the error

# Removed LLMAgent functions - using arush_llm instead

def evaluate_event_salience(agent: Agent, event_description: str) -> int:
    """Simple salience evaluation using arush_llm components"""
    # For demo purposes, return a simple salience score
    keywords = ["important", "urgent", "message", "chat", "move", "interact"]
    salience = 3  # Base salience
    for keyword in keywords:
        if keyword.lower() in event_description.lower():
            salience += 2
    return min(salience, 10)  # Cap at 10
