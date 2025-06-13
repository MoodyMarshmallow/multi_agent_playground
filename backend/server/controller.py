"""
Multi-Agent Playground - Action Controller
==========================================
Core controller logic for processing agent actions in the simulation.

This module implements the two-step action processing pipeline:
1. Action Planning: Receives perception data and plans next action
2. Action Confirmation: Updates agent state and memory after action execution

The controller acts as an intermediary between the FastAPI endpoints
and the agent system, handling the flow of perception data, action
planning, and state updates for all agents in the simulation.
"""

from backend.character_agent.agent import Agent
from backend.character_agent.actions import ActionsMixin
from backend.character_agent.kani_implementation import call_llm_agent
from backend.config.schema import AgentActionInput, AgentActionOutput, AgentPerception, BackendAction, MoveBackendAction, ChatBackendAction, InteractBackendAction, PerceiveBackendAction, Message

def plan_next_action(agent_id: str, perception: AgentPerception) -> AgentActionOutput:
    """
    Step 1: Decide the next action (LLM/planner), given current perception.
    Do NOT update agent data yet.
    """
    agent_dir = f"data/agents/{agent_id}"
    agent = Agent(agent_dir)
    agent.update_perception(perception.model_dump())
    agent_state = agent.to_state_dict()

    # LLM/planner call (replace with real LLM logic to generate a json file that will be sent from backend to frontend!)
    next_action = call_llm_agent(agent_state, perception.model_dump())

    # Extract current tile from perception or agent state
    current_tile = perception.current_tile if perception.current_tile else agent.curr_tile
    
    # Create appropriate backend action based on action type
    backend_action = None
    if next_action["action_type"] == "move":
        # Extract destination from content
        destination = next_action["content"].get("destination_coordinates", [0, 0])
        backend_action = MoveBackendAction(
            action_type="move",
            destination_tile=tuple(destination)
        )
        # Update current_tile to destination for move actions
        current_tile = tuple(destination)
        
    elif next_action["action_type"] == "chat":
        # Extract message info from content
        message_content = next_action["content"].get("message", "")
        receiver = next_action["content"].get("receiver", "")
        message = Message(
            sender=agent_id,
            receiver=receiver,
            message=message_content,
            timestamp=perception.timestamp
        )
        backend_action = ChatBackendAction(
            action_type="chat",
            message=message
        )
        
    elif next_action["action_type"] == "interact":
        # Extract interaction details from content
        obj = next_action["content"].get("object", "")
        current_state = next_action["content"].get("current_state", "")
        new_state = next_action["content"].get("new_state", "")
        backend_action = InteractBackendAction(
            action_type="interact",
            object=obj,
            current_state=current_state,
            new_state=new_state
        )
        
    else:  # perceive or default
        backend_action = PerceiveBackendAction(action_type="perceive")

    return AgentActionOutput(
        agent_id=agent_id,
        action=backend_action,
        emoji=next_action.get("emoji", "👀"),
        timestamp=perception.timestamp,
        current_tile=current_tile
    )


def confirm_action_and_update(agent_msg: AgentActionInput) -> None:
    """
    Step 2: After frontend executes the action, it POSTs new perception/result.
    Backend updates state/memory using the reported result.
    """
    print(agent_msg)
    agent_dir = f"data/agents/{agent_msg.agent_id}"
    agent = Agent(agent_dir)
    perception = agent_msg.perception.model_dump()
    agent.update_perception(perception)
    
    # Update agent data based on action and perception
    agent_data = {
        "timestamp": agent_msg.perception.timestamp,
        "current_tile": agent_msg.perception.current_tile,
    }
    agent.update_agent_data(agent_data)

    # Get location based on visible objects' rooms if available
    location = "unknown location"
    if agent_msg.perception.visible_objects:
        rooms = set()
        for obj_data in agent_msg.perception.visible_objects.values():
            if isinstance(obj_data, dict) and "room" in obj_data:
                rooms.add(obj_data["room"])
        location = " and ".join(rooms) if rooms else "unknown location"
    
    # Create event summary from perception
    event_parts = []
    
    # Add action-specific event description
    if hasattr(agent_msg.action, 'action_type'):
        action_type = agent_msg.action.action_type
        if action_type == "move":
            if hasattr(agent_msg.action, 'destination_tile'):
                dest = agent_msg.action.destination_tile
                event_parts.append(f"I moved to position {dest}")
        elif action_type == "chat":
            if hasattr(agent_msg.action, 'message'):
                msg = agent_msg.action.message
                event_parts.append(f"I chatted with {msg.receiver}: '{msg.message}'")
        elif action_type == "interact":
            if hasattr(agent_msg.action, 'object') and hasattr(agent_msg.action, 'new_state'):
                event_parts.append(f"I interacted with {agent_msg.action.object}, changing it to {agent_msg.action.new_state}")
        elif action_type == "perceive":
            event_parts.append("I looked around and observed my surroundings")
    
    # Add visible objects
    if agent_msg.perception.visible_objects:
        visible_items = []
        for obj_name, obj_data in agent_msg.perception.visible_objects.items():
            if isinstance(obj_data, dict):
                room = obj_data.get("room", "unknown room")
                visible_items.append(f"{obj_name} in {room}")
        if visible_items:
            event_parts.append(f"I could see: {', '.join(visible_items)}")
    
    # Add visible agents
    if agent_msg.perception.visible_agents:
        event_parts.append(f"I saw these people: {', '.join(agent_msg.perception.visible_agents)}")
    
    # Add heard messages
    if agent_msg.perception.heard_messages:
        for message in agent_msg.perception.heard_messages:
            event_parts.append(f"I heard {message.sender} say to {message.receiver}: '{message.message}'")
    
    event = ". ".join(event_parts) if event_parts else "Nothing notable happened"
    
    # Update agent's currently field with the event
    agent.update_agent_data({"currently": event})
    
    # Add memory event with default salience
    agent.add_memory_event(
        timestamp=agent_msg.perception.timestamp,
        location=location,
        event=event,
        salience=1  # Default salience for basic perceptions
    )
    
    agent.save()
    agent.save_memory()

