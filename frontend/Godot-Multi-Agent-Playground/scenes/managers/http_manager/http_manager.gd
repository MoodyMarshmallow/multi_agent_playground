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
signal play_next_action

var automatic_polling := false
var automatic_playing := false
@onready var polling_timer: Timer = Timer.new()
@onready var play_timer: Timer = Timer.new()

@onready var action_manager: ActionManager = get_node("../ActionManager")

func _ready() -> void:
	print("Press i to view controls")
	_print_instructions()
	polling_timer.wait_time = 5.0
	polling_timer.one_shot = false
	polling_timer.autostart = false
	add_child(polling_timer)
	polling_timer.timeout.connect(_on_polling_timer_timeout)

	play_timer.wait_time = 4.0
	play_timer.one_shot = false
	play_timer.autostart = false
	add_child(play_timer)
	play_timer.timeout.connect(_on_play_timer_timeout)

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
		automatic_polling = !automatic_polling
		if automatic_polling:
			polling_timer.start()
			print("[toggle_automatic_polling] Automatic polling is now ON")
		else:
			polling_timer.stop()
			print("[toggle_automatic_polling] Automatic polling is now OFF")
		return
	if event.is_action_pressed("toggle_automatic_playing"):
		automatic_playing = !automatic_playing
		if automatic_playing:
			play_timer.start()
			print("[toggle_automatic_playing] Automatic play is now ON")
		else:
			play_timer.stop()
			print("[toggle_automatic_playing] Automatic play is now OFF")
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
				if action_dict.has("target"):
					action_dict["target"] = _to_snake_case(action_dict["target"])
				if action_dict.has("recipient"):
					action_dict["recipient"] = _to_snake_case(action_dict["recipient"])
				action_dicts.append(action_dict)
			action_manager.add_actions_from_http(action_dicts)

func _on_polling_timer_timeout():
	_http_request(input_to_route["http_next"], "http_next")

func _on_play_timer_timeout():
	emit_signal("play_next_action")

func _to_snake_case(s: String) -> String:
	return s.strip_edges().to_lower().replace(" ", "_")

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
	print("E: toggle_automatic_polling")
	print("F: toggle_automatic_playing")
	print("R: play_next_action_in_queue (MUST PRESS FOR AGENT TO TAKE NEXT ACTION IF NOT ON AUTOMATIC PLAYING)")
