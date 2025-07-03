# File: interact_action.gd
extends Action
class_name InteractAction

var object: String
var state: String
var new_state: String

func _init(_agent_id: String, _object: String, _state: String, _new_state: String):
	super._init("interact", _agent_id)
	object = _object
	state = _state
	new_state = _new_state
