extends Node2D

@onready var debugging_input: LineEdit = $UIManager/DebuggingInput
@onready var ui_manager: CanvasLayer = $UIManager

@onready var http_manager: HttpManager = $HttpManager
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

func on_object_action_received(action: Dictionary):
	# If the action is 'place', set place_location to the agent's location
	if action.has("action_type") and action["action_type"] == "place":
		if action.has("agent_id"):
			action["place_location"] = agent_manager.get_agent_location(action["agent_id"])
	# If the action is 'place_on', set place_location to the recipient object's location
	elif action.has("action_type") and action["action_type"] == "place_on":
		if action.has("recipient"):
			action["place_location"] = object_manager.get_object_location(action["recipient"])
	object_manager.handle_object_action(action)
	pass

# set move_to field based on action and forward the action to the action_manager
func on_agent_action_received(action: Dictionary):
	var move_to: Vector2 = Vector2(-INF, -INF)
	print("received agent action: ", action)
	# If the action has a recipient, use its location
	if action.has("recipient") and action["recipient"] != null:
		move_to = object_manager.get_object_location(action["recipient"])
	# Otherwise, use the target's location
	elif action.has("target") and action["target"] != null:
		move_to = object_manager.get_object_location(action["target"])
		if action.has("action_type") and action["action_type"] == "go_to":
			move_to = object_manager.get_location(action["target"])

	# Add the move_to field to the action dictionary
	if move_to != Vector2(-INF, -INF):
		action["move_to"] = move_to

	# Call handle_agent_action in the action manager
	agent_manager.handle_agent_action(action)
