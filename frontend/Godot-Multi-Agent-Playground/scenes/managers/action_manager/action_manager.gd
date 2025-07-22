class_name ActionManager
extends Node2D

signal object_action(action : Dictionary)
signal agent_action(action : Dictionary)
signal general_action(action: Dictionary)

var action_queue: Array = []

# Add actions from HTTPManager (expects a list of dictionaries with agent_id and action fields)
func add_actions_from_http(actions: Array) -> void:
	for action in actions:
		action_queue.append(action)

# Play the next action in the queue
func play_next_action_in_queue() -> void:
	if action_queue.size() > 0:
		var next_action = action_queue.pop_front()
		print("playing action: ", next_action)
		general_action.emit(next_action)
	else:
		print("[ActionManager] Action queue is empty.")

# Print the current action queue for debugging
func print_action_queue() -> void:
	print("[ActionManager] Current action queue:")
	for i in range(action_queue.size()):
		print(str(i) + ": ", action_queue[i])

# Parses an action and calls the corresponding functions in the 
# agent manager and object manager

# Action is a dictionary with these fields
# agent_id: str
# action_type: Literal[
	# "take", "place", "place_on", "use",
	# "open", "close", "turn_on", "turn_off", "clean_item", "tidy_bed",
	# "go_to"
# ]
# (Here are the updated action types)
# action_type: Literal[look, go_to, take, drop, examine, place, consume, set_to_state, start_using, stop_using]
# target: str (Not for look action)
# recipient: Optional[str] = None  # Only for place_on
# state: (for setting objects to a new state)

func _on_action_received(action: Dictionary):
	action_queue.append(action)
	#general_action.emit(action)
