class_name TextInputManager
extends Node2D

signal action(action : Dictionary)
#	Action is a dictionary with these fields
#	action_id: str (For all debug agent actions this id will by default by DebugAgent. Can be changed with text input agent_id: {agent_id})
#		For debug actions that don't affect an agent this will simply be Debug
#	action_type: Literal[look, go_to, take, 
#		drop, examine, place, consume, 
#		set_to_state, start_using, stop_using
# 	]
# 	target: str (Not for look action)
# 	recipient: Optional[str] = None  # Only for place_on
# 	state: (for setting objects to a new state)

# Parses any input submitted through the debugging input line edit object (displayed at the bottom 
# of the game screen)
func _on_debugging_input_submitted(text: String) -> void:
	_parse_action(text)

# Matches strings of the types: 
# take {object}, place {object}, place {object} on {object}, use {object}, 
# open {object}, close {object}, turn_on {object}, turn_off {object}, 
# clean {object}, tidy bed, and emit the corresponding signal. the {object} 
# should always be the target field, and in the case of place it should be 
# place {target} on {recipient}. Also for tidy bed it will have action 
# type tidy_bed and target bed. For go_to {room} the target will be the room to 
# go to instead of an object

var current_agent_id: String = "DebugAgent"

func _parse_action(text: String):
	var regex = RegEx.new()
	var result

	# agent_id: {agent_id}
	regex.compile("^agent_id:\\s*(\\w+)$")
	result = regex.search(text.strip_edges())
	if result:
		current_agent_id = result.get_string(1)
		print("[TextInputManager] Set current_agent_id to: ", current_agent_id)
		return

	# place {item} on/in {object}
	regex.compile("^place\\s+(\\w+)\\s+(on|in)\\s+(\\w+)$")
	result = regex.search(text.strip_edges())
	if result:
		var target = _to_snake_case(result.get_string(1))
		var recipient = _to_snake_case(result.get_string(3))
		emit_signal("action", {
			"agent_id": current_agent_id,
			"action_type": "place",
			"target": target,
			"recipient": recipient,
			"description": "debugging place action"
		})
		return

	# take {item}
	regex.compile("^take\\s+(\\w+)$")
	result = regex.search(text.strip_edges())
	if result:
		emit_signal("action", {
			"agent_id": current_agent_id,
			"action_type": "take",
			"target": _to_snake_case(result.get_string(1)),
			"description": "debugging take action"
		})
		return

	# drop {item}
	regex.compile("^drop\\s+(\\w+)$")
	result = regex.search(text.strip_edges())
	if result:
		emit_signal("action", {
			"agent_id": current_agent_id,
			"action_type": "drop",
			"target": _to_snake_case(result.get_string(1)),
			"description": "debugging drop action"
		})
		return

	# examine {item}
	regex.compile("^examine\\s+(\\w+)$")
	result = regex.search(text.strip_edges())
	if result:
		emit_signal("action", {
			"agent_id": current_agent_id,
			"action_type": "examine",
			"target": _to_snake_case(result.get_string(1)),
			"description": "debugging examine action"
		})
		return

	# consume {item}
	regex.compile("^consume\\s+(\\w+)$")
	result = regex.search(text.strip_edges())
	if result:
		emit_signal("action", {
			"agent_id": current_agent_id,
			"action_type": "consume",
			"target": _to_snake_case(result.get_string(1)),
			"description": "debugging consume action"
		})
		return

	# set {object} to {state}
	regex.compile("^set\\s+(\\w+)\\s+to\\s+(\\w+)$")
	result = regex.search(text.strip_edges())
	if result:
		emit_signal("action", {
			"agent_id": current_agent_id,
			"action_type": "set_to_state",
			"target": _to_snake_case(result.get_string(1)),
			"state": _to_snake_case(result.get_string(2)),
			"description": "debugging set_to_state action"
		})
		return

	# start_using {object}
	regex.compile("^start_using\\s+(\\w+)$")
	result = regex.search(text.strip_edges())
	if result:
		emit_signal("action", {
			"agent_id": current_agent_id,
			"action_type": "start_using",
			"target": _to_snake_case(result.get_string(1)),
			"description": "debugging start_using action"
		})
		return

	# stop_using {object}
	regex.compile("^stop_using\\s+(\\w+)$")
	result = regex.search(text.strip_edges())
	if result:
		emit_signal("action", {
			"agent_id": current_agent_id,
			"action_type": "stop_using",
			"target": _to_snake_case(result.get_string(1)),
			"description": "debugging stop_using action"
		})
		return

	# go_to {room} or g {room}
	regex.compile("^(go_to|g)\\s+(\\w+)$")
	result = regex.search(text.strip_edges())
	if result:
		var target = _to_snake_case(result.get_string(2))
		emit_signal("action", {
			"agent_id": current_agent_id,
			"action_type": "go_to",
			"target": target,
			"description": "debugging go_to action"
		})
		return

	# look
	regex.compile("^look$")
	result = regex.search(text.strip_edges())
	if result:
		emit_signal("action", {
			"agent_id": current_agent_id,
			"action_type": "look",
			"description": "debugging look action"
		})
		return

	# print_inventory
	regex.compile("^print_inventory$")
	result = regex.search(text.strip_edges())
	if result:
		emit_signal("action", {
			"agent_id": current_agent_id,
			"action_type": "print_inventory",
			"description": "debugging print_inventory action"
		})
		return

	# chat: {sender} -> {recipient}: {message}
	regex.compile("^(\\w+)\\s*->\\s*(\\w+)\\s*:\\s*(.+)$")
	result = regex.search(text.strip_edges())
	if result:
		var sender = result.get_string(1)
		var recipient = result.get_string(2)
		var message = result.get_string(3).strip_edges()
		emit_signal("action", {
			"action_type": "chat",
			"sender": sender,
			"recipient": recipient,
			"message": message,
			"description": "chat message from " + sender + " to " + recipient
		})
		return

	# If no match, print for debugging
	print("Unrecognized action command:", text)

func _to_snake_case(s: String) -> String:
	return s.strip_edges().to_lower().replace(" ", "_")
