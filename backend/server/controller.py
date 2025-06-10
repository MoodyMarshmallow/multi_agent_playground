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
from backend.character_agent.kani_implementation import LLMAgent
from backend.config.schema import AgentActionInput, AgentActionOutput, AgentPerception

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
    next_action = LLMAgent.call_llm_agent(agent_state, perception.model_dump())

    return AgentActionOutput(
        agent_id=next_action["agent_id"],
        action_type=next_action["action_type"],
        content=next_action["content"],
        emoji=next_action["emoji"],
        current_tile=next_action["current_tile"],
        current_location=next_action["current_location"],
    )


def confirm_action_and_update(agent_msg: AgentActionInput) -> AgentActionOutput:
    """
    Step 2: After frontend executes the action, it POSTs new perception/result.
    Backend updates state/memory using the reported result.
    """
    print(agent_msg)
    agent_dir = f"data/agents/{agent_msg.agent_id}"
    agent = Agent(agent_dir)
    perception = agent_msg.perception.model_dump()
    agent.update_perception(perception)
    agent_data = agent_msg.content.copy()
    agent_data.update({
        "timestamp": agent_msg.timestamp,
        "current_tile": agent_msg.perception.current_tile,
    })
    agent.update_agent_data(agent_data)

    
    # Get location based on visible objects' rooms
    rooms = set(obj["room"] for obj in perception["visible_objects"].values())
    location = " and ".join(rooms) if rooms else "unknown location"
    
    # Create event summary from perception
    visible_items = [f"{obj['name']} in {obj['room']}" for obj in perception["visible_objects"].values()]
    visible_agents = [f"{agent_info['name']}" for agent_info in perception["visible_agents"]]
    
    event_parts = []
    if perception.get("self_state"):
        event_parts.append(f"I was {perception['self_state']}")
    if visible_items:
        event_parts.append(f"I could see: {', '.join(visible_items)}")
    if visible_agents:
        event_parts.append(f"I saw these people: {', '.join(visible_agents)}")
    
    event = ". ".join(event_parts) if event_parts else "Nothing notable happened"
    
    # Update agent's currently field with the event
    agent.update_agent_data({"currently": event})
    
    # Add memory event with either specified or default salience
    agent.add_memory_event(
        timestamp=agent_msg.timestamp,
        location=location,
        event=event,
        salience=agent_msg.content.get("salience", 1)  # Default salience of 1 for basic perceptions
    )
    
    agent.save()
    agent.save_memory()

