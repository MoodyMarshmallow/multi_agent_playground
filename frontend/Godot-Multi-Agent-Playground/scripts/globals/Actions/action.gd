extends RefCounted
class_name Action

var action_type: String
var agent_id: String

func _init(_action_type: String, _agent_id: String):
	action_type = _action_type
	agent_id = _agent_id
