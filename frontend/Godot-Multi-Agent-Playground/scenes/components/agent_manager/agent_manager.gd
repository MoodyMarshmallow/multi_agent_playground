class_name AgentManager

extends Node

# --- Constants ---
var TILE_SIZE : float = 16
var CHATTABLE_RADIUS : float = 4
var INTERACTABLE_RADIUS : float = 4

# - Variables ---
var current_agent_id : String
var agent_dictionary : Dictionary = {}
var agent_ids : Array = []

# Action Queue
var action_queue: Array[Action] = []

# Agent Scene
const agent_scene = preload("res://scenes/characters/agents/agent.tscn")

# Dynamically instantiate agents from summaries
func instantiate_agents(agent_summaries: Array) -> void:
	# Remove existing agents
	for agent in agent_dictionary.values():
		agent.queue_free()
	agent_dictionary.clear()
	agent_ids.clear()

	for summary in agent_summaries:
		var agent = agent_scene.instantiate()
		agent.agent_id = summary.agent_id
		
		# Set initial position
		var initial_position: Vector2
		if summary.has("curr_tile") and summary.curr_tile != null:
			initial_position = Vector2(summary.curr_tile[0], summary.curr_tile[1]) * TILE_SIZE
		else:
			initial_position = Vector2.ZERO
		
		# Check if position is inside a collider and find safe position if needed
		var safe_position = find_safe_position(initial_position)
		agent.position = safe_position
			
		# Set other properties as needed (e.g., name, occupation)
		if summary.has("first_name"): agent.first_name = summary.first_name
		if summary.has("last_name"): agent.last_name = summary.last_name
		if summary.has("age"): agent.age = summary.age
		if summary.has("occupation"): agent.occupation = summary.occupation
		if summary.has("currently"): agent.currently = summary.currently
		add_child(agent)
		agent_dictionary[agent.agent_id] = agent
		agent_ids.append(agent.agent_id)
		if agent.has_signal("chat_message_sent"):
			agent.connect("chat_message_sent", self._on_agent_chat_message_sent)
	# Set current_agent_id to first if available
	if agent_ids.size() > 0:
		current_agent_id = agent_ids[0]

# Find a safe position that's not inside a collider
func find_safe_position(initial_position: Vector2) -> Vector2:
	# Get the world 2D from the current scene
	var current_scene = get_tree().current_scene
	if not current_scene:
		print("Warning: No current scene found, using initial position")
		return initial_position
	
	var space_state = current_scene.get_world_2d().direct_space_state
	var query = PhysicsPointQueryParameters2D.new()
	query.position = initial_position
	query.collision_mask = 1  # Adjust collision mask as needed
	
	# Add a safety margin to prevent collider overlap
	var safety_margin = TILE_SIZE * 0.5  # Half a tile for safety
	
	# Check initial position with safety margin
	var result = space_state.intersect_point(query)
	if result.is_empty():
		# Double-check with a small area around the position
		var area_query = PhysicsShapeQueryParameters2D.new()
		var circle_shape = CircleShape2D.new()
		circle_shape.radius = safety_margin
		area_query.shape = circle_shape
		area_query.transform = Transform2D(0, initial_position)
		area_query.collision_mask = 1
		
		var area_result = space_state.intersect_shape(area_query)
		if area_result.is_empty():
			return initial_position
	
	# Try positions in a spiral pattern around the initial position
	var radius = TILE_SIZE + safety_margin
	var angle = 0
	var max_attempts = 30  # Increased attempts for better coverage
	
	for i in range(max_attempts):
		var test_position = initial_position + Vector2(cos(angle), sin(angle)) * radius
		
		# Check point collision
		query.position = test_position
		result = space_state.intersect_point(query)
		
		if result.is_empty():
			# Double-check with area collision
			var area_query = PhysicsShapeQueryParameters2D.new()
			var circle_shape = CircleShape2D.new()
			circle_shape.radius = safety_margin
			area_query.shape = circle_shape
			area_query.transform = Transform2D(0, test_position)
			area_query.collision_mask = 1
			
			var area_result = space_state.intersect_shape(area_query)
			if area_result.is_empty():
				return test_position
		
		angle += PI / 6  # 30 degrees for more precise search
		if i % 12 == 11:  # Every 12 attempts, increase radius
			radius += TILE_SIZE
	
	# If all attempts fail, return a fallback position
	print("Warning: Could not find safe position for agent, using fallback")
	return Vector2(100, 100)  # Fallback position

func iterate_selected_agent():
	var ids = agent_dictionary.keys()
	var current_index = ids.find(current_agent_id)
	var next_index = (current_index + 1) % ids.size()
	current_agent_id = ids[next_index]
	print("CURRENTLY SELECTED AGENT: ", current_agent_id)

func toggle_navigation_paths():
	for agent in agent_dictionary.values():
		if agent is Agent:
			agent.navigation_agent_2d.debug_enabled = not agent.navigation_agent_2d.debug_enabled

func _on_agent_chat_message_sent(receiver_id: String, message: Dictionary) -> void:
	var receiver_agent = _find_agent_by_id(receiver_id)
	if receiver_agent and receiver_agent.has_method("on_receive_chat_message"):
		receiver_agent.on_receive_chat_message(message)
	else:
		push_error("Receiver agent with id '%s' not found or missing on_receive_chat_message." % receiver_id)

# Helper to find agent by id among children
func _find_agent_by_id(agent_id: String) -> Node:
	return agent_dictionary.get(agent_id, null)

func change_emoji(agent_id: String, emoji: String) -> void:
	var agent = _find_agent_by_id(agent_id)
	if agent:
		agent.on_emoji_received(agent_id, emoji)
	else:
		push_error("Agent with id '%s' not found for move action." % agent_id)
	
# Action handlers
func handle_move_action(agent_id: String, destination_tile: Vector2i) -> void:
	action_queue.append(MoveAction.new(agent_id, destination_tile))
	var agent = _find_agent_by_id(agent_id)
	if agent:
		agent.on_move_action_received(agent_id, destination_tile)
	else:
		push_error("Agent with id '%s' not found for move action." % agent_id)

func handle_chat_action(agent_id: String, message: Dictionary) -> void:
	action_queue.append(ChatAction.new(agent_id, message.sender, message.receiver, message.message, message.timestamp))
	var agent = _find_agent_by_id(agent_id)
	if agent:
		agent.on_chat_action_received(agent_id, message)
	else:
		push_error("Agent with id '%s' not found for chat action." % agent_id)

func handle_interact_action(agent_id: String, object: String, current_state: String, new_state: String) -> void:
	action_queue.append(InteractAction.new(agent_id, object, current_state, new_state))
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

func get_agent_chattable_agents(agent_id: String) -> Array:
	return get_agent_property(agent_id, "get_chattable_agents")

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

func set_chattable_agents_for(requesting_agent: Agent):
	var nearby_agents : Array[String] = []
	for agent in agent_dictionary.values():
		if agent == requesting_agent or agent is not Agent:
			continue
		if agent.global_position.distance_to(requesting_agent.global_position) < TILE_SIZE * CHATTABLE_RADIUS:
			nearby_agents.append(agent.agent_id)
	requesting_agent.chattable_agents = nearby_agents
