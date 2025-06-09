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
from character_agent.actions import ActionsMixin
from backend.character_agent.kani_implementation import call_llm_agent
from config.schema import AgentActionInput, AgentActionOutput, AgentPerception

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

    return AgentActionOutput(
        agent_id=next_action["agent_id"],
        action_type=next_action["action_type"],
        content=next_action["content"],
        emoji=next_action["emoji"],
        current_tile=None,
        current_location=None,
    )


def confirm_action_and_update(agent_msg: AgentActionInput) -> AgentActionOutput:
    """
    Step 2: After frontend executes the action, it POSTs new perception/result.
    Backend updates state/memory using the reported result.
    """
    agent_dir = f"data/agents/{agent_msg.agent_id}"
    agent = Agent(agent_dir)
    agent.update_perception(agent_msg.perception.model_dump())
    agent.update_agent_data(agent_msg.content)
    # Log memory event if relevant fields are present:
    if "event" in agent_msg.content and "salience" in agent_msg.content:
        agent.add_memory_event(
            timestamp=agent_msg.timestamp,
            location=str(agent_msg.content.get("location", "")),
            event=agent_msg.content["event"],
            salience=agent_msg.content["salience"]
        )
    agent.save()
    agent.save_memory()

