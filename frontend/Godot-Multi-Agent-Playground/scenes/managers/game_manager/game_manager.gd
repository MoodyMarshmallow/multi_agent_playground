extends Node2D

@onready var debugging_input: LineEdit = $UIManager/DebuggingInput
@onready var ui_manager: CanvasLayer = $UIManager

@onready var http_manager: HTTPManager = $HttpManager
@onready var text_input_manager: TextInputManager = $TextInputManager
@onready var action_manager: ActionManager = $ActionManager

@onready var object_manager: ObjectManager = $ObjectManager
@onready var agent_manager: AgentManager = $AgentManager
@onready var debug_player: DebugPlayer = $DebugPlayer

func _ready():
	debugging_input.connect("debugging_input_submitted", Callable(text_input_manager, "_on_debugging_input_submitted"))
	text_input_manager.connect("action", Callable(action_manager, "_on_action_received"))
	
	action_manager.connect("object_action", Callable(self, "on_object_action_received"))
	action_manager.connect("agent_action", Callable(self, "on_agent_action_received"))
	action_manager.connect("general_action", Callable(self, "on_general_action_received"))

	agent_manager.connect("agent_action_completed", Callable(self, "_on_agent_action_completed"))

func on_general_action_received(action: Dictionary):
	# Set place_location for place actions
	if action.has("action_type") and action["action_type"] == "place":
		if action.has("recipient"):
			action["place_location"] = object_manager.get_object_location(action["recipient"])
	if action.has("action_type") and action["action_type"] == "drop" and action.has("agent_id"):
		action["place_location"] = agent_manager.get_agent_location(action["agent_id"])
		
	# Set move_to for navigation and object actions
	var move_to: Vector2 = Vector2(-INF, -INF)
	if action["action_type"] in ["go_to", "set_to_state", "start_using", "stop_using", "examine", "consume", "place", "take"]:
		if action.has("target") and action["target"] != null:
			move_to = object_manager.get_location(action["target"])
			if action.has("recipient") and action["recipient"] != null:
				move_to = object_manager.get_location(action["recipient"])
	if move_to != Vector2(-INF, -INF):
		action["move_to"] = move_to

	agent_manager.handle_agent_action(action)
	object_manager.handle_object_action(action)

func _on_agent_action_completed(agent_id: String, action: Dictionary):
	object_manager.handle_post_navigation_object_action(action)

# Manage all inputs:
