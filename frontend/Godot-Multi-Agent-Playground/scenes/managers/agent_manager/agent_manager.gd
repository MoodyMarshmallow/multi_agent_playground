class_name AgentManager
extends Node2D


# - Variables ---
var current_agent_id : String
var agent_dictionary : Dictionary = {} # Dictionary[String, BaseAgent]
var agent_ids : Array[String] = []

# Action Queue
var action_queue: Array[Action] = []

# Populate the agent_ids, agent_dictionary, and current_agent_id from children
func _ready():
	update_children_agents()
	pass

# Repopulate the agent_ids, agent_dictionary, and current_agent_id from children
func update_children_agents():
	agent_dictionary.clear()
	agent_ids.clear()
	for agent in get_children():
		if agent is BaseAgent:
			agent_dictionary[agent.name] = agent
			agent_ids.append(agent.name)
	if agent_ids.size() > 0:
		current_agent_id = agent_ids[0]

# The starting point for handling all agent actions
# Action is a dictionary with these fields
# agent_id: str
# action_type: Literal[
	# "take", "place", "place_on", "use",
	# "open", "close", "turn_on", "turn_off", "clean_item", "tidy_bed",
	# "go_to"
# ]
# target: str
# recipient: Optional[str] = None  # Only for place_on
# move_to : Vector2

func handle_agent_action(action: Dictionary):
	if action.has("move_to") and action.has("agent_id"):
		var agent_id = action["agent_id"]
		if agent_dictionary.has(agent_id):
			var agent: BaseAgent = agent_dictionary[agent_id]
			agent.navigate_to(action["move_to"])
		else:
			print("AgentManager: No agent found with id:", agent_id)
	else:
		print("AgentManager: Action missing move_to or agent_id:", action)
