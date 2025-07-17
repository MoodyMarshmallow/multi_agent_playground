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

func _input(event):
	if event.is_action_pressed("display_instructions"):
		_print_instructions()
		return
	if event.is_action_pressed("toggle_print_http_requests"):
		print_http_responses = !print_http_responses
		var status = "ON" if print_http_responses else "OFF"
		print("[toggle_print_http_requests] HTTP response printing is now ", status)
		return
	# These are placeholders for future functionality
	if event.is_action_pressed("toggle_automatic_polling"):
		print("[toggle_automatic_polling] (E) pressed - no functionality yet.")
		return
	if event.is_action_pressed("play_next_action_in_queue"):
		print("[play_next_action_in_queue] (R) pressed - no functionality yet.")
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

func _print_instructions():
	print("--- Controls ---")
	print("i: Display instructions")
	print("1: http_next")
	print("2: http_states")
	print("3: http_objects")
	print("4: http_world_state")
	print("5: http_events")
	print("6: http_reset")
	print("7: http_status")
	print("P: toggle_print_http_requests (toggle HTTP response printing)")
	print("E: toggle_automatic_polling (no functionality yet)")
	print("R: play_next_action_in_queue (no functionality yet)")
