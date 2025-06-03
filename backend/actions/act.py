def act(agent_state, thought):
    """
    Converts a goal into a concrete action for the frontend.(Kani placeholder: this can be a tool)
    Args:
        agent_state (dict)
        thought (dict): Output from plan(), e.g. {"goal": "Go to the kitchen"}
    Returns:
        dict: Action for frontend.
    """
    goal = thought.get("goal")
    if goal and "kitchen" in goal:
        return {
            "agent_id": agent_state.get("name", "agent"),
            "action_type": "move",
            "content": {"destination_coordinates": [51, 10]},
            "emoji": "🚶"
        }
    return {"action_type": "idle"}
