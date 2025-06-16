extends Node

# Configuration
const BACKEND_URL = "http://localhost:8000"
const POLL_INTERVAL = 5.0

# State tracking
var _poll_timer: Timer
var _current_actions = []
var _is_processing_actions: bool = false
var _pending_confirmations = []

# References to children
@onready var agent_manager: AgentManager = $AgentManager

# List of agent IDs to poll (could be made dynamic)
var agent_ids := ["alex_001", "alan_002"]

func _ready():
	# Create and setup timer
	_poll_timer = Timer.new()
	_poll_timer.wait_time = POLL_INTERVAL
	_poll_timer.one_shot = false
	_poll_timer.timeout.connect(_on_poll_timer_timeout)
	add_child(_poll_timer)
	_poll_timer.start()

func _on_poll_timer_timeout():
	if not _is_processing_actions:
		_is_processing_actions = true
		_request_next_actions()

func _request_next_actions():
	var http_request = HTTPRequest.new()
	add_child(http_request)
	http_request.request_completed.connect(_on_plan_request_completed)
	
	# Build the request body dynamically for each agent
	var request_body = []
	for agent_id in agent_ids:
		request_body.append({
			"agent_id": agent_id,
			"perception": agent_manager.get_agent_perception(agent_id)
		})
	print("\nList[AgentPlanRequest] = ", request_body)
	var headers = ["Content-Type: application/json"]
	var error = http_request.request(
		BACKEND_URL + "/agent_act/plan",
		headers,
		HTTPClient.METHOD_POST,
		JSON.stringify(request_body)
	)
	
	if error != OK:
		push_error("An error occurred in the HTTP request.")

func _on_plan_request_completed(result, response_code, headers, body):
	if result != HTTPRequest.RESULT_SUCCESS:
		push_error("HTTP request failed with code: " + str(response_code))
		return
		
	var json = JSON.new()
	var error = json.parse(body.get_string_from_utf8())
	if error != OK:
		push_error("JSON Parse Error: " + json.get_error_message())
		return
	var response = json.get_data()
	_current_actions = []
	for item in response:
		_current_actions.append(item as Dictionary)
	print("\nList[AgentActionOutput] = ", _current_actions)

	_process_all_actions()

func _process_all_actions():
	if _current_actions.is_empty():
		_is_processing_actions = false
		return
		
	_is_processing_actions = true
	_pending_confirmations.clear()
	
	# Process all actions first
	for action in _current_actions:
		_process_single_action(action)
	
	# After all actions are processed, send confirmations
	_send_pending_confirmations()

func _process_single_action(action: Dictionary):
	match action.action.action_type:
		"move":
			var dest_tile = Vector2i(action.action.destination_tile[0], action.action.destination_tile[1])
			agent_manager.handle_move_action(action.agent_id, dest_tile)
		"chat":
			agent_manager.handle_chat_action(action.agent_id, action.action.message)
		"interact":
			agent_manager.handle_interact_action(
				action.agent_id,
				action.action.object,
				action.action.current_state,
				action.action.new_state
			)
		"perceive":
			agent_manager.handle_perceive_action(action.agent_id)
		_:
			push_error("Unknown action type: " + action.action.action_type)
	
	# Add to pending confirmations
	_pending_confirmations.append(action)

func _send_pending_confirmations():
	if _pending_confirmations.is_empty():
		_is_processing_actions = false
		return
		
	var http_request = HTTPRequest.new()
	add_child(http_request)
	http_request.request_completed.connect(_on_confirm_request_completed)
	
	# Create confirmation bodies for all pending actions
	var confirm_bodies = []
	for action in _pending_confirmations:
		confirm_bodies.append({
			"agent_id": action.agent_id,
			"action": agent_manager.get_agent_frontend_action(action.agent_id, action.action.action_type),
			"in_progress": agent_manager.get_agent_in_progress(action.agent_id), # TODO: Get actual progress status
			"perception": agent_manager.get_agent_perception(action.agent_id)
		})
	
	var headers = ["Content-Type: application/json"]
	print("\nList[AgentActionInput] = ", confirm_bodies)
	var error = http_request.request(
		BACKEND_URL + "/agent_act/confirm",
		headers,
		HTTPClient.METHOD_POST,
		JSON.stringify(confirm_bodies)
	)
	
	if error != OK:
		push_error("An error occurred in the HTTP request.")

func _on_confirm_request_completed(result, response_code, headers, body):
	if result != HTTPRequest.RESULT_SUCCESS:
		push_error("HTTP request failed with code: " + str(response_code))
		return
	
	# Clear pending confirmations and mark processing as complete
	_pending_confirmations.clear()
	_is_processing_actions = false
