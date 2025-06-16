class_name AgentManager

extends Node

func _ready():
	for agent in get_children():
		if agent.has_signal("chat_message_sent"):
			agent.connect("chat_message_sent", self._on_agent_chat_message_sent)
			

func _on_agent_chat_message_sent(receiver_id: String, message: Dictionary) -> void:
	var receiver_agent = _find_agent_by_id(receiver_id)
	if receiver_agent and receiver_agent.has_method("on_receive_chat_message"):
		receiver_agent.on_receive_chat_message(message)
	else:
		push_error("Receiver agent with id '%s' not found or missing on_receive_chat_message." % receiver_id)

# Helper to find agent by id among children
func _find_agent_by_id(agent_id: String) -> Node:
	for child in get_children():
		if child.has_method("get_agent_id") and child.get_agent_id() == agent_id:
			return child
	return null

# Action handlers
func handle_move_action(agent_id: String, destination_tile: Vector2i) -> void:
	var agent = _find_agent_by_id(agent_id)
	if agent:
		agent.on_move_action_received(agent_id, destination_tile)
	else:
		push_error("Agent with id '%s' not found for move action." % agent_id)

func handle_chat_action(agent_id: String, message: Dictionary) -> void:
	var agent = _find_agent_by_id(agent_id)
	if agent:
		agent.on_chat_action_received(agent_id, message)
	else:
		push_error("Agent with id '%s' not found for chat action." % agent_id)

func handle_interact_action(agent_id: String, object: String, current_state: String, new_state: String) -> void:
	var agent = _find_agent_by_id(agent_id)
	if agent:
		agent.on_interact_action_received(agent_id, object, current_state, new_state)
	else:
		push_error("Agent with id '%s' not found for interact action." % agent_id)

func handle_perceive_action(agent_id: String) -> void:
	var agent = _find_agent_by_id(agent_id)
	if agent:
		agent.on_perceive_action_received(agent_id)
	else:
		push_error("Agent with id '%s' not found for perceive action." % agent_id)

# General get agent property function
func get_agent_property(agent_id: String, property_func: String) -> Variant:
	var agent = _find_agent_by_id(agent_id)
	if agent and agent.has_method(property_func):
		return agent.call(property_func)
	else:
		push_error("Agent with id '%s' not found or missing method '%s'." % [agent_id, property_func])
		return null

func get_agent_current_tile(agent_id: String) -> Array:
	return get_agent_property(agent_id, "get_current_tile")

func get_agent_destination_tile(agent_id: String) -> Array:
	return get_agent_property(agent_id, "get_destination_tile")

func get_agent_visible_objects(agent_id: String) -> Dictionary:
	return get_agent_property(agent_id, "get_visible_objects")

func get_agent_visible_agents(agent_id: String) -> Array:
	return get_agent_property(agent_id, "get_visible_agents")

func get_agent_chatable_agents(agent_id: String) -> Array:
	return get_agent_property(agent_id, "get_chatable_agents")

func get_agent_heard_messages(agent_id: String) -> Array:
	return get_agent_property(agent_id, "get_heard_messages")

func get_agent_forwarded(agent_id: String) -> bool:
	return get_agent_property(agent_id, "get_forwarded")

func get_agent_in_progress(agent_id: String) -> bool:
	return get_agent_property(agent_id, "get_in_progress")
	
func get_agent_perception(agent_id: String) -> Dictionary:
	return get_agent_property(agent_id, "get_perception")

func get_agent_frontend_action(agent_id: String, action_type: String) -> Dictionary:
	var agent = _find_agent_by_id(agent_id)
	if agent:
		var res_action = {}
		match action_type:
			"move":
				res_action.action_type = "move"
				res_action.destination_tile = get_agent_destination_tile(agent_id)
			"chat":
				res_action.action_type = "chat"
				res_action.forwarded = get_agent_forwarded(agent_id)
			"interact":
				res_action.action_type = "interact"
			"perceive":
				res_action.action_type = "perceive"
		return res_action
	else:
		push_error("Agent with id '%s' not found or missing get_last_frontend_action." % agent_id)
		return {}
