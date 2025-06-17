class_name Agent

extends CharacterBody2D

signal chat_message_sent(receiver_id: String, message: Dictionary)

@onready var animated_sprite_2d: AnimatedSprite2D = $AnimatedSprite2D
@onready var agent_manager: AgentManager = get_parent()

# Variables we will need to send to http manager:
@export var agent_id: String = "alex_001"
var current_tile: Vector2i = Vector2i(0, 0)
var visible_objects: Dictionary = {}
@export var visible_agents: Array[String] = []
@export var HouseUpperLeftTile : Vector2i = Vector2i(0, 0)
@export var chattable_agents: Array[String] = []
var heard_messages: Array = []
var timestamp: String = ""
var forwarded: bool = true
var in_progress: bool = false
var destination_tile: Vector2i = Vector2i(0, 0)

# --- Navigation Variables ---
@onready var navigation_agent_2d: NavigationAgent2D = $NavigationAgent2D
var speed = 50.0

# --- State Machine ---
@onready var state_machine: StateMachine = $StateMachine
@onready var idle: State = $StateMachine/Idle
@onready var walk: State = $StateMachine/Walk


func _ready() -> void:
	# Enable debug visualization
	navigation_agent_2d.debug_enabled = true
	navigation_agent_2d.debug_use_custom = true
	navigation_agent_2d.debug_path_custom_color = Color.RED
	navigation_agent_2d.debug_path_custom_point_size = 8.0
	navigation_agent_2d.debug_path_custom_line_width = 3.0

	# Make the agent follow the path more precisely
	navigation_agent_2d.path_desired_distance = 10.0  # Default is usually 20.0
	navigation_agent_2d.target_desired_distance = 10.0  # Default is usually 10.0
	navigation_agent_2d.path_max_distance = 15.0
	navigation_agent_2d.simplify_path = false
	
	current_tile = position_to_tile(position)
	destination_tile = current_tile

# --- FSM Functions ---

func position_to_tile(pos: Vector2) -> Vector2i:
	# Assumes pos is in pixels
	var tile_x = int(floor(pos.x / 16))
	var tile_y = int(floor(pos.y / 16))
	return Vector2i(tile_x, tile_y)

func tile_to_position(tile: Vector2i) -> Vector2:
	# Assumes pos is in pixels
	var pos_x = int((tile.x + 0.5) * 16)
	var pos_y = int((tile.y + 0.5) * 16)
	return Vector2(pos_x, pos_y)

# --- Functions signalled from HTTP manager ---
func on_move_action_received(agent_id: String, destination_tile: Vector2i) -> void:
	if agent_id != self.agent_id:
		return
	in_progress = true
	destination_tile = destination_tile + HouseUpperLeftTile
	var destination_pos = Vector2(destination_tile.x * 16 + 8, destination_tile.y * 16 + 8)

	# Snap to navigation region
	var safe_destination = NavigationServer2D.map_get_closest_point(navigation_agent_2d.get_navigation_map(), destination_pos)
	var safe_destination_tile = position_to_tile(safe_destination)
	navigation_agent_2d.set_target_position(safe_destination)
	state_machine.on_child_transition(state_machine.current_state, "Walk")
	current_tile = destination_tile
	
	navigation_agent_2d.set_target_position(destination_pos)
	state_machine.on_child_transition(state_machine.current_state, "Walk")
	in_progress = false

# Called when a chat action is received
func on_chat_action_received(agent_id: String, message: Dictionary) -> void:
	if agent_id != self.agent_id:
		return
	navigation_agent_2d.set_target_position(position)
	in_progress = true
	state_machine.on_child_transition(state_machine.current_state, "Idle")
	chat_message_sent.emit(message.receiver, message)
	forwarded = true
	in_progress = false

func on_receive_chat_message(message: Dictionary) -> void:
	heard_messages.append(message)

# Called when an interact action is received
func on_interact_action_received(agent_id: String, object: String, current_state: String, new_state: String) -> void:
	if agent_id != self.agent_id:
		return
	navigation_agent_2d.set_target_position(position)
	print("Interacting with object: %s, from %s to %s" % [object, current_state, new_state])
	in_progress = true
	state_machine.on_child_transition(state_machine.current_state, "Idle")
	in_progress = false

# Called when a perceive action is received
func on_perceive_action_received(agent_id: String) -> void:
	if agent_id != self.agent_id:
		return
	navigation_agent_2d.set_target_position(position)
	print("Perceive action triggered")
	in_progress = true
	state_machine.on_child_transition(state_machine.current_state, "Idle")
	in_progress = false

# --- Update functions for tracked variables ---

func set_chattable_agents():
	agent_manager.set_chattable_agents_for(self)


func set_interactable_objects() -> void:
	pass

# --- Getter functions for HTTP manager ---

func get_agent_id() -> String:
	return agent_id

func get_current_tile() -> Array:
	current_tile = tile_to_position(position)
	return [current_tile.x, current_tile.y]

func get_destination_tile() -> Array:
	return [destination_tile.x, destination_tile.y]

func get_visible_objects() -> Dictionary:
	return visible_objects

func get_visible_agents() -> Array:
	return visible_agents

func get_chattable_agents() -> Array:
	set_chattable_agents()
	return chattable_agents

func get_heard_messages() -> Array:
	return heard_messages

func get_timestamp() -> String:
	return timestamp

func get_forwarded() -> bool:
	return forwarded

func get_in_progress() -> bool:
	return in_progress

# Return the full perception dictionary
func get_perception() -> Dictionary:
	# clear heard_messages
	var old_heard_messages = heard_messages
	heard_messages = []
	# update chattable agents
	set_chattable_agents()
	return {
		"timestamp": timestamp,
		"current_tile": [current_tile.x, current_tile.y],
		"visible_objects": visible_objects,
		"visible_agents": visible_agents,
		"chattable_agents": chattable_agents,
		"heard_messages": old_heard_messages
	}

func _physics_process(delta: float) -> void:
	var navigation_agent_2d = $NavigationAgent2D
	if navigation_agent_2d.is_navigation_finished():
		in_progress = false
		state_machine.on_child_transition(state_machine.current_state, "Idle")
		return
	# Get the next point to move toward
	var next_point = navigation_agent_2d.get_next_path_position()
	var direction = (next_point - position).normalized()
	# Move the agent
	position += direction * speed * delta
	current_tile = position_to_tile(position)
	pass

# updates the agent's perception variable such as visible_objects, visible_agents, chattable_agents, and current_tile
func _update_perception() -> void:
	pass
