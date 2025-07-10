extends Node2D

signal action(action : Dictionary)
	# Action is a dictionary with these fields
	# action_id: str (For all debug agent actions this id will be DebugAgent)
		# For debug actions that don't affect an agent this will simply be Debug
	# action_type: Literal[
		# "take", "place", "place_on", "use",
		# "open", "close", "turn_on", "turn_off", "clean_item", "tidy_bed"
	# ]
	# target: str
	# recipient: Optional[str] = None  # Only for place_on
	

# Parses any input submitted through the debugging input line edit object (displayed at the bottom 
# of the game screen)
func _on_debugging_input_submitted(text: String) -> void:
	print("Received debuggin input: ", text)
	_parse_action(text)

# Matches strings of the types: 
# take {object}, place {object}, place {object} on {object}, use {object}, 
# open {object}, close {object}, turn_on {object}, turn_off {object}, 
# clean {object}, tidy bed, and emit the corresponding signal. the {object} 
# should always be the target field, and in the case of place it should be 
# place {target} on {recipient}. Also for tidy bed it will have action 
# type tidy_bed and target bed

func _parse_action(text: String):
	var regex = RegEx.new()
	var result

	# place {target} on {recipient}
	regex.compile("^place\\s+(\\w+)\\s+on\\s+(\\w+)$")
	result = regex.search(text.strip_edges())
	if result:
		emit_signal("action", {
			"agent_id": "DebugAgent",
			"action_type": "place_on",
			"target": result.get_string(1),
			"recipient": result.get_string(2)
		})
		return

	# take {object}
	regex.compile("^take\\s+(\\w+)$")
	result = regex.search(text.strip_edges())
	if result:
		emit_signal("action", {
			"agent_id": "DebugAgent",
			"action_type": "take",
			"target": result.get_string(1)
		})
		return

	# place {object}
	regex.compile("^place\\s+(\\w+)$")
	result = regex.search(text.strip_edges())
	if result:
		emit_signal("action", {
			"agent_id": "DebugAgent",
			"action_type": "place",
			"target": result.get_string(1)
		})
		return

	# use {object}
	regex.compile("^use\\s+(\\w+)$")
	result = regex.search(text.strip_edges())
	if result:
		emit_signal("action", {
			"agent_id": "DebugAgent",
			"action_type": "use",
			"target": result.get_string(1)
		})
		return

	# open {object}
	regex.compile("^open\\s+(\\w+)$")
	result = regex.search(text.strip_edges())
	if result:
		emit_signal("action", {
			"agent_id": "DebugAgent",
			"action_type": "open",
			"target": result.get_string(1)
		})
		return

	# close {object}
	regex.compile("^close\\s+(\\w+)$")
	result = regex.search(text.strip_edges())
	if result:
		emit_signal("action", {
			"agent_id": "DebugAgent",
			"action_type": "close",
			"target": result.get_string(1)
		})
		return

	# turn_on {object}
	regex.compile("^turn[_ ]on\\s+(\\w+)$")
	result = regex.search(text.strip_edges())
	if result:
		emit_signal("action", {
			"agent_id": "DebugAgent",
			"action_type": "turn_on",
			"target": result.get_string(1)
		})
		return

	# turn_off {object}
	regex.compile("^turn[_ ]off\\s+(\\w+)$")
	result = regex.search(text.strip_edges())
	if result:
		emit_signal("action", {
			"agent_id": "DebugAgent",
			"action_type": "turn_off",
			"target": result.get_string(1)
		})
		return

	# clean {object}
	regex.compile("^clean\\s+(\\w+)$")
	result = regex.search(text.strip_edges())
	if result:
		emit_signal("action", {
			"agent_id": "DebugAgent",
			"action_type": "clean_item",
			"target": result.get_string(1)
		})
		return

	# tidy bed
	regex.compile("^tidy\\s+bed$")
	result = regex.search(text.strip_edges())
	if result:
		emit_signal("action", {
			"agent_id": "DebugAgent",
			"action_type": "tidy_bed",
			"target": "bed"
		})
		return

	# If no match, print for debugging
	print("Unrecognized action command:", text)
