class_name ActionManager
extends Node2D

signal object_action(action : Dictionary)
signal agent_action(action : Dictionary)

# Parses an action and calls the corresponding functions in the 
# agent manager and object manager

# Action is a dictionary with these fields
# agent_id: str
# action_type: Literal[
	# "take", "place", "place_on", "use",
	# "open", "close", "turn_on", "turn_off", "clean_item", "tidy_bed",
	# "go_to"
# ]
# target: str
# recipient: Optional[str] = None  # Only for place_on

func _on_action_received(action: Dictionary):
	object_action.emit(action)
	agent_action.emit(action)
