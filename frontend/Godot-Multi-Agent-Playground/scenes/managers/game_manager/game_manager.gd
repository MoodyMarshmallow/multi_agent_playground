extends Node2D

@onready var ui_manager: CanvasLayer = $UIManager
@onready var debugging_input: LineEdit = $UIManager/DebuggingInput
@onready var inventory: Inventory = $UIManager/Inventory
@onready var chat_box: ChatBox = $UIManager/ChatBox

@onready var http_manager: HTTPManager = $HttpManager
@onready var text_input_manager: TextInputManager = $TextInputManager
@onready var action_manager: ActionManager = $ActionManager

@onready var object_manager: ObjectManager = $NavigationRegionD/ObjectManager
@onready var agent_manager: AgentManager = $AgentManager

func _ready():
	debugging_input.connect("debugging_input_submitted", Callable(text_input_manager, "_on_debugging_input_submitted"))
	text_input_manager.connect("action", Callable(action_manager, "_on_action_received"))
	
	action_manager.connect("object_action", Callable(self, "on_object_action_received"))
	action_manager.connect("agent_action", Callable(self, "on_agent_action_received"))
	action_manager.connect("general_action", Callable(self, "on_general_action_received"))

	http_manager.connect("play_next_action", Callable(self, "_on_play_next_action"))

	agent_manager.connect("agent_action_completed", Callable(self, "_on_agent_action_completed"))
	
	# Initialize inventory panels for all agents (except DebugAgent)
	_initialize_agent_inventories()

func _initialize_agent_inventories():
	# Wait one frame to ensure all nodes are ready
	await get_tree().process_frame
	
	# Get all agents from the agent manager
	var agents = agent_manager.get_children()
	
	for agent in agents:
		# Skip DebugAgent
		if agent.name == "DebugAgent" or "debug" in agent.name.to_lower():
			continue
		
		# Create inventory panel for this agent
		inventory.instantiate_inventory_panel(agent.agent_id, "empty")
		
		# Connect the agent's inventory changed signal
		agent.connect("inventory_changed", Callable(self, "_on_agent_inventory_changed"))

func _on_agent_inventory_changed(agent_id: String, inventory_text: String):
	# Update the inventory UI for this agent
	inventory.update_inventory_panel(agent_id, inventory_text)

func on_general_action_received(action: Dictionary):
	# Handle chat actions
	if action.has("action_type") and action["action_type"] == "chat":
		if action.has("sender") and action.has("recipient") and action.has("message"):
			chat_box.send_message_with_sender_recipient(
				action["sender"], 
				action["recipient"], 
				action["message"]
			)
		return
	
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

func _on_play_next_action():
	action_manager.play_next_action_in_queue()
