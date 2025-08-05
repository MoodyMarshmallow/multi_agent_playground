# File: chat_action.gd
extends Action
class_name ChatAction

var sender: String
var receiver: String
var message: String
var timestamp: String

func _init(_agent_id: String, _sender: String, _receiver: String, _message: String, _timestamp: String):
	super._init("chat", _agent_id)
	sender = _sender
	receiver = _receiver
	message = _message
	timestamp = _timestamp
