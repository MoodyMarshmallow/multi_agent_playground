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
	for agent in agent_dictionary.values():
		agent.connect("reached_destination", Callable(self, "_on_agent_reached_destination"))
	pass

# Repopulate the agent_ids, agent_dictionary, and current_agent_id from children
func update_children_agents():
	agent_dictionary.clear()
	agent_ids.clear()
	for agent in get_children():
		if agent is BaseAgent:
			agent_dictionary[agent.name] = agent
			agent_ids.append(agent.name)
			agent.connect("reached_destination", Callable(self, "_on_agent_reached_destination"))
	if agent_ids.size() > 0:
		current_agent_id = agent_ids[0]

# The starting point for handling all agent actions
# Action is a dictionary with these fields
# agent_id: str
# action_type: Literal[
	# "take", "place", "place_on", "use",
	# "open", "close", "turn_on", "turn_off", "clean_item", "tidy_bed",
	# "go_to", "print_inventory"
# ]
# target: str
# recipient: Optional[str] = None  # Only for place_on
# move_to : Vector2

# Handle agent action, start navigation if move_to, otherwise handle immediately
func handle_agent_action(action: Dictionary):
	if action.has("move_to") and action.has("agent_id"):
		var agent_id = action["agent_id"]
		if agent_dictionary.has(agent_id):
			var agent: BaseAgent = agent_dictionary[agent_id]
			agent.start_navigation_action(action["move_to"], action)
		else:
			print("AgentManager: No agent found with id:", agent_id)
	else:
		_handle_post_navigation_action(action)

# Called when an agent reaches its destination
func _on_agent_reached_destination(action: Dictionary):
	_handle_post_navigation_action(action)

# Handle the rest of the action after navigation
func _handle_post_navigation_action(action: Dictionary):
	if not action.has("agent_id"):
		print("AgentManager: Action missing agent_id:", action)
		return
	var agent_id = action["agent_id"]
	if not agent_dictionary.has(agent_id):
		print("AgentManager: No agent found with id:", agent_id)
		return
	var agent: BaseAgent = agent_dictionary[agent_id]
	var action_type = action.get("action_type", "")
	var target = action.get("target", "")
	if action_type == "take":
		agent.add_to_inventory(target)
	elif action_type in ["place", "place_on", "use"]:
		agent.remove_from_inventory(target)
	elif action_type == "print_inventory":
		agent.print_inventory()

# Adds an item to the specified agent's inventory
func add_agent_inventory_item(agent_id: String, item: String) -> void:
	if agent_dictionary.has(agent_id):
		agent_dictionary[agent_id].add_to_inventory(item)
	else:
		print("AgentManager: No agent found with id:", agent_id)

# Removes an item from the specified agent's inventory
func remove_agent_inventory_item(agent_id: String, item: String) -> void:
	if agent_dictionary.has(agent_id):
		agent_dictionary[agent_id].remove_from_inventory(item)
	else:
		print("AgentManager: No agent found with id:", agent_id)

# Prints the specified agent's inventory
func print_agent_inventory(agent_id: String) -> void:
	if agent_dictionary.has(agent_id):
		agent_dictionary[agent_id].print_inventory()
	else:
		print("AgentManager: No agent found with id:", agent_id)

# Gets the specified agent's inventory data structure
func get_agent_inventory(agent_id: String) -> Array[String]:
	if agent_dictionary.has(agent_id):
		return agent_dictionary[agent_id].get_inventory()
	else:
		print("AgentManager: No agent found with id:", agent_id)
		return []

# Gets the global position of the specified agent
func get_agent_location(agent_id: String) -> Vector2:
	if agent_dictionary.has(agent_id):
		return agent_dictionary[agent_id].global_position
	else:
		return Vector2(-INF, -INF)
