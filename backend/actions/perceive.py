def perceive(agent_state, perception):
    """
    Updates agent's perception in state. (Kani placeholder: this can be a tool)
    Args:
        agent_state (dict)
        perception (dict): World info seen by agent.
    Returns:
        dict: Updated agent state.
    """
    # === KANI TOOL PLACEHOLDER ===
    agent_state = agent_state.copy()
    agent_state["visible_objects"] = perception.get("visible_objects", {})
    agent_state["visible_agents"] = perception.get("visible_agents", [])
    return agent_state
