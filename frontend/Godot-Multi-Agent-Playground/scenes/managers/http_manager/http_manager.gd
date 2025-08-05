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
	print("\n")
	print("recomended to press commands E, F, and P at startup to toggle automatic polling and playing, 
	and not print out all http request responses. Also make sure backend is running before polling.")
	print("\n")
	print("i: Display instructions")
	print("T: print text debugging instructions")
	print("D: print in depth instructions")

func _input(event):
	if event.is_action_pressed("display_instructions"):
		_print_instructions()
		return
	if event.is_action_pressed("display_text_debugging_instructions"):
		_print_text_debugging_instructions()
		return
	if event.is_action_pressed("display_in_depth_instructions"):
		_print_in_depth_instructions()
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
			print("[toggle_automatic_playing] Automatic playing is now ON")
		else:
			play_timer.stop()
			print("[toggle_automatic_playing] Automatic playing is now OFF")
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
	print("")
	print("--- Controls ---")
	print("i: Display instructions")
	print("T: print text debugging instructions")
	print("D: print in depth instructions")
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

func _print_text_debugging_instructions():
	print("")
	print("--- Text Commands ---")
	print("Type these commands in the text input field at the bottom left of the screen:")
	print()
	print("AGENT MANAGEMENT:")
	print("  agent_id: {agent_name}     - Set which agent performs actions")
	print("  Example: agent_id: alex_001")
	print()
	print("MOVEMENT:")
	print("  go_to {room} or go_to {object} - Move agent to a room/location")
	print("  g {room} or g {object}        - Short form of go_to")
	print("  Example: go_to kitchen")
	print()
	print("OBJECT INTERACTIONS:")
	print("  take {item}                - Pick up an item")
	print("  drop {item}                - Drop an item from inventory")
	print("  place {item} on {object}   - Place item on another object")
	print("  place {item} in {object}   - Place item inside another object")
	print("  examine {object}           - Examine an object for details")
	print("  consume {item}             - Consume/destroy an item")
	print("  Examples: take apple, place book on table")
	print()
	print("OBJECT STATES:")
	print("  set {object} to {state}    - Change object state")
	print("  start_using {object}       - Begin using an object")
	print("  stop_using {object}        - Stop using an object")
	print("  Examples: set fridge to open, start_using oven")
	print("  Note: Animations support open/closed for: fridge, oven, medicine_cabinet,")
	print("        toy_bin, entry_door, bathroom_door")
	print("        And on/off for: coffee_maker, bathtub, faucet")
	print()
	print("INFORMATION:")
	print("  look                       - Show what agent can see")
	print("  print_inventory            - Display agent's inventory")
	print()
	print("CHAT:")
	print("  {sender} -> {recipient}: {message}")
	print("  Example: alex_001 -> alan_002: Hi, how are you doing?")
	print()
	print("NOTES:")
	print("- Commands are flexible with spacing around operators")
	print("- Object/agent names are auto-converted to snake_case")
	print("- Most commands use the currently selected agent")
	print("- Chat messages don't require setting agent_id first")

func _print_in_depth_instructions():
	print("")
	print("")
	print("These commands can be inputted by typing the corresponding command into the")
	print("line edit box in the bottom left of the screen. Click on it to start typing")
	print("(note this will also pause all game events), press enter to complete the")
	print("command or escape to leave the line edit without issuing a command")
	_print_text_debugging_instructions()
	
	print("")
	print("These are the normal key based controls")
	print("--- Controls ---")
	print("i: Display instructions - just the key strokes and what they do")
	print("T: print text debugging instructions - just the text based debugging")
	print("   (things you can type into the bottom left line edit box)")
	print("D: print in depth instructions - the in-depth instructions you're reading now")
	
	print("Camera controls:")
	print("arrow keys: Move camera - move camera around to follow agents as they act")
	print("cmd +, cmd - : Zoom camera - zooms camera in and out")
	print("             (can distort pixels so be careful)")
	print("shift - (_): Reset camera - resets to the default view the camera started in")
	
	print("")
	print("These are the routes that our backend supports. Pressing these keys will")
	print("initiate a corresponding http request to the python FastAPI backend")
	print("1: http_next - The main route to be using. Fetches the agent actions that")
	print("              have been completed on the backend and adds them to the")
	print("              frontend's action queue (the actions won't actually be played")
	print("              on screen until the action queue processes them)")
	print("2: http_states - prints the states of the agents")
	print("3: http_objects - prints the states of the objects")
	print("4: http_world_state - prints the entire world state")
	print("5: http_events - debugging")
	print("6: http_reset - debugging")
	print("7: http_status - debugging")
	print("Q: print_action_queue - prints the frontend's action queue where it stores")
	print("                       actions it has received from the backend but hasn't")
	print("                       played yet")
	print("P: toggle_print_http_requests - toggles if the responses from the requests")
	print("                                to the http routes will be printed out or not")
	print("E: toggle_automatic_polling - toggles automatically sending a http_next")
	print("                              request to the backend every 5 seconds")
	print("F: toggle_automatic_playing - toggles automatically playing the next action")
	print("                              from the action queue if there is one every 4")
	print("                              seconds")
	print("R: play_next_action_in_queue - plays the next action from the action queue")
	print("                                in the frontend (MUST PRESS FOR AGENT TO TAKE")
	print("                                NEXT ACTION IF NOT ON AUTOMATIC PLAYING)")
	
	print("")
	print("recomended to press commands E, F, and P at startup to toggle automatic polling and playing, 
	and not print out all http request responses. Also make sure backend is running before polling.")
