from agents.agent import Agent
from actions.perceive import perceive
from actions.act import act

def handle_frontend_message(agent_dir, message):
    """
    Loads agent and memory from local files, processes perception/action, returns action.
    Args:
        agent_dir (str): path to the agent's directory.
        message (dict): frontend message (should contain "perception").
    Returns:
        dict: action (for frontend)
    """
    # 1. Load agent and memory
    agent = Agent(agent_dir)

    # 2. Update perception (can be a tool in future)
    agent.update_perception(message.get("perception", {}))
    agent_state = agent.to_state_dict()
    
    # === KANI LLM INTEGRATION PLACEHOLDER ===
    # Here is where you would call Kani LLM to perform planning or tool selection.
    # Example:
    # kani_result = call_kani_llm(agent_state, message)
    # thought = kani_result["thought"]
    # action = kani_result["action"]

    # 3. LLM 'think' (planning step)
    if agent_state["daily_req"]:
        thought = {"goal": agent_state["daily_req"][0]}
    else:
        thought = {"goal": None}

    # 4. Act (can be a tool in future)
    action = act(agent_state, thought)
    return action

# Example usage/testing
if __name__ == "__main__":
    agent_dir = "data/alex"
    msg = {
        "perception": {
            "visible_objects": {"bed": {"state": "unmade"}, "light switch": {"state": "off"}},
            "visible_agents": ["Maeve Jenson"]
        }
    }
    print(handle_frontend_message(agent_dir, msg))
