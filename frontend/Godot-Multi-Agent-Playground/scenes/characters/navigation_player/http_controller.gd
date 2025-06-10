extends Node

# HTTP Client for API communication
var http_request: HTTPRequest
@export var agent_id: String = "alex_001"
@export var update_interval: float = 5.0  # Seconds between updates
@export var base_url: String = "http://localhost:8000"
@export var default_navigation_x : float = 5.0
@export var default_navigation_y : float = 5.0

var is_action_in_progress: bool = false
var current_action: Dictionary = {}
var current_request_type: String = ""  # "plan" or "confirm"


signal new_destination(coordinates: Vector2)
signal update_position(tile_position: Vector2)

func _ready() -> void:
	# Create and setup HTTP request node
	http_request = HTTPRequest.new()
	add_child(http_request)
	http_request.request_completed.connect(_on_request_completed)
	
	# Start the planning cycle
	#request_next_action()

func request_next_action() -> void:
	print("In request next action")
	if is_action_in_progress:
		print("already have action in progress")
		return
		
	var perception_data = {
		"self_state": _get_current_state(),
		"visible_objects": _get_visible_objects(),
		"visible_agents": _get_visible_agents(),
		"timestamp": Time.get_datetime_string_from_system(),
		"current_tile": _get_current_tile()
	}
	print("perception data: ", perception_data)
	# Make the planning request
	var url = base_url + "/agent_act/plan"
	var query = "?agent_id=" + agent_id
	var headers = PackedStringArray(["Content-Type: application/json"])
	var json = JSON.stringify(perception_data)
	print("making http request")
	current_request_type = "plan"
	var error = http_request.request(url + query, headers, HTTPClient.METHOD_POST, json)
	if error != OK:
		print("Failed to request next action")
		# Retry after a delay
		#await get_tree().create_timer(1.0).timeout
		#request_next_action()

func _get_default_plan_response() -> Dictionary:
	print("running default_plan")
	return {
	"agent_id": "agent_1",
	"action_type": "move",
	"content": {
		"destination_coordinates": [default_navigation_x, default_navigation_y]
	},
	"emoji": "",
	"current_tile": "",
	"current_location": ""
}


func _confirm_action(action_type: String, content: Dictionary) -> void:
	print("confirming action")
	
	var confirmation_data = {
		"agent_id": agent_id,
		"timestamp": Time.get_datetime_string_from_system(),
		"action_type": action_type,
		"content": content,
		"perception": {
			"self_state": _get_current_state(),
			"visible_objects": _get_visible_objects(),
			"visible_agents": _get_visible_agents(),
			"current_time": Time.get_datetime_string_from_system(),
			"current_tile": _get_current_tile()
		},
	}
	print("confirmation data: ", confirmation_data)
	
	# Make the confirmation request
	var url = base_url + "/agent_act/confirm"
	var headers = PackedStringArray(["Content-Type: application/json"])
	var json = JSON.stringify(confirmation_data)
	
	current_request_type = "confirm"
	is_action_in_progress = false
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, json)
	if error != OK:
		print("Failed to confirm action. Backend failed with error: ", error)

func _on_request_completed(result: int, response_code: int, headers: PackedStringArray, body: PackedByteArray) -> void:
	print("request completed")
	if result != HTTPRequest.RESULT_SUCCESS:
		print("HTTP Request failed")
		if current_request_type == "plan":
			_handle_plan_response(_get_default_plan_response())
		return
		
	if response_code != 200:
		print("Received response code: " + str(response_code))
		if current_request_type == "plan":
			_handle_plan_response(_get_default_plan_response())
		return
		
	var json = JSON.parse_string(body.get_string_from_utf8())
	if json == null:
		print("JSON Parse Error")
		return
	
	# Check which endpoint responded based on the URL
	var url = String(headers[headers.find("X-Request-URL")] if headers.find("X-Request-URL") >= 0 else "")
	
	if current_request_type == "plan":
		_handle_plan_response(json)
	elif current_request_type == "confirm":
		_handle_confirm_response(json)
	else:
		print("ELSINGALL")
		_handle_plan_response(json)

func _handle_plan_response(response: Dictionary) -> void:
	is_action_in_progress = true
	current_action = response
	print(response)
	match response.action_type:
		"move":
			print("action type move")
			if "destination_coordinates" in response.content:
				print("found destination_coordinates")
				var coords = response.content.destination_coordinates
				new_destination.emit(Vector2(coords[0], coords[1]))
		"interact":
			# complete immediately for now
			_action_completed()
		"perceive":
			_action_completed()
		_:
			print("Unknown action type: " + response.action_type)
			_action_completed()

func _handle_confirm_response(_response: Dictionary) -> void:
	is_action_in_progress = false
	current_action = {}
	# Request the next action after a short delay
	#await get_tree().create_timer(update_interval).timeout
	#request_next_action()

# Called by the navigation system when an action is completed
func notify_action_completed() -> void:
	print("http_controller notified that action was completed")
	if current_action.is_empty():
		return
	
	_confirm_action(current_action.action_type, current_action.content)

# Helper functions to gather perception data
func _get_current_state() -> String:
	var parent = get_parent()
	if parent and parent.has_method("get_current_state"):
		return parent.get_current_state()
	return "idle"

func _get_visible_objects() -> Dictionary:
	var parent = get_parent()
	if parent and parent.has_method("get_visible_objects"):
		return parent.get_visible_objects()
	return {}

func _get_visible_agents() -> Array:
	var parent = get_parent()
	if parent and parent.has_method("get_visible_agents"):
		return parent.get_visible_agents()
	return []
	
func _get_current_tile() -> Array:
	var parent = get_parent()
	if parent and parent.has_method("get_visible_agents"):
		return [parent.get_current_tile().x, parent.get_current_tile().y]
	return [0, 0]

func _action_completed() -> void:
	notify_action_completed()
