class_name Agent

extends CharacterBody2D

signal chat_message_sent(receiver_id: String, message: Dictionary)

@onready var navigation_agent_2d: NavigationAgent2D = $NavigationAgent2D
@onready var animated_sprite_2d: AnimatedSprite2D = $AnimatedSprite2D

# Variables we will need to send to http manager:
@export var agent_id: String = "alex_001"
var current_tile: Vector2i = Vector2i(0, 0)
var visible_objects: Dictionary = {}
@export var visible_agents: Array[String] = []
var chatable_agents: Array = []
var heard_messages: Array = []
var timestamp: String = ""
var forwarded: bool = true
var in_progress: bool = false
var destination_tile: Vector2i = Vector2i(0, 0)

func _ready() -> void:
	pass

# --- Functions signalled from HTTP manager ---
func on_move_action_received(agent_id: String, destination_tile: Vector2i) -> void:
	if agent_id != self.agent_id:
		return
	print("Moving to tile: ", destination_tile)
	in_progress = true
	current_tile = destination_tile
	destination_tile = destination_tile
	in_progress = false

# Called when a chat action is received
func on_chat_action_received(agent_id: String, message: Dictionary) -> void:
	if agent_id != self.agent_id:
		return
	print("Sent chat message: ", message)
	in_progress = true
	chat_message_sent.emit(message.receiver, message)
	forwarded = true
	in_progress = false

func on_receive_chat_message(message: Dictionary) -> void:
	heard_messages.append(message)

# Called when an interact action is received
func on_interact_action_received(agent_id: String, object: String, current_state: String, new_state: String) -> void:
	if agent_id != self.agent_id:
		return
	print("Interacting with object: %s, from %s to %s" % [object, current_state, new_state])
	in_progress = true
	in_progress = false

# Called when a perceive action is received
func on_perceive_action_received(agent_id: String) -> void:
	if agent_id != self.agent_id:
		return
	print("Perceive action triggered")
	in_progress = true
	in_progress = false


# --- Getter functions for HTTP manager ---

func get_agent_id() -> String:
	return agent_id

func get_current_tile() -> Array:
	return [current_tile.x, current_tile.y]

func get_destination_tile() -> Array:
	return [destination_tile.x, destination_tile.y]

func get_visible_objects() -> Dictionary:
	return visible_objects

func get_visible_agents() -> Array:
	return visible_agents

func get_chatable_agents() -> Array:
	return chatable_agents

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
	return {
		"timestamp": timestamp,
		"current_tile": [current_tile.x, current_tile.y],
		"visible_objects": visible_objects,
		"visible_agents": visible_agents,
		"chatable_agents": chatable_agents,
		"heard_messages": old_heard_messages
	}
