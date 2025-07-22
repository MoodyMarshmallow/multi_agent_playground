class_name HTTPManager
extends Node

# Map input actions to backend routes
var input_to_route = {
	"http_next": "/agent_act/next",
	"http_states": "/agents/states",
	"http_objects": "/objects",
	"http_world_state": "/world_state",
	"http_events": "/game/events",
	"http_reset": "/game/reset",
	"http_status": "/game/status",
}

# Print HTTP responses by default
var print_http_responses := true

@onready var action_manager: ActionManager = get_node("../ActionManager")

func _ready() -> void:
	print("Press i to view controls")
	_print_instructions()

func _input(event):
	if event.is_action_pressed("display_instructions"):
		_print_instructions()
		return
	if event.is_action_pressed("toggle_print_http_requests"):
		print_http_responses = !print_http_responses
		var status = "ON" if print_http_responses else "OFF"
		print("[toggle_print_http_requests] HTTP response printing is now ", status)
		return
	if event.is_action_pressed("toggle_automatic_polling"):
		print("[toggle_automatic_polling] (E) pressed - no functionality yet.")
		return
	if event.is_action_pressed("play_next_action_in_queue"):
		action_manager.play_next_action_in_queue()
		return
	if event.is_action_pressed("print_action_queue"):
		action_manager.print_action_queue()
		return
	for action in input_to_route.keys():
		if event.is_action_pressed(action):
			_http_request(input_to_route[action], action)
			return

func _http_request(route: String, action_name: String):
	var http = HTTPRequest.new()
	add_child(http)
	http.request_completed.connect(_on_http_request_completed.bind(action_name, route))
	var err = http.request("http://localhost:8000" + route)
	if err != OK:
		print("[", action_name, "] HTTP request error: ", err)

func _on_http_request_completed(result, response_code, headers, body, action_name, route):
	if print_http_responses:
		print("[", action_name, "] Response from ", route, ": ", body.get_string_from_utf8())
	if action_name == "http_next":
		var actions = JSON.parse_string(body.get_string_from_utf8())
		if actions is Array:
			var action_dicts = []
			for action_output in actions:
				var action_dict = action_output["action"]
				action_dict["agent_id"] = action_output["agent_id"]
				action_dicts.append(action_dict)
			action_manager.add_actions_from_http(action_dicts)

func _print_instructions():
	print("--- Controls ---")
	print("i: Display instructions")
	print("arrow keys: Move camera")
	print("cmd +, cmd - : Zoom camera")
	print("shift - (_): Reset camera")
	print("1: http_next")
	print("2: http_states")
	print("3: http_objects")
	print("4: http_world_state")
	print("5: http_events")
	print("6: http_reset")
	print("7: http_status")
	print("Q: print_action_queue")
	print("P: toggle_print_http_requests")
	print("E: toggle_automatic_polling (automatic polling not set up yet because need to debug individual actions first)")
	print("R: play_next_action_in_queue (MUST PRESS FOR AGENT TO TAKE NEXT ACTION)")
