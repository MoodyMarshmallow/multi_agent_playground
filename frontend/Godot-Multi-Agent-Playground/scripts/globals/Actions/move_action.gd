extends Action
class_name MoveAction

var destination_tile: Vector2i

func _init(_agent_id: String, _destination_tile: Vector2i):
	super._init("move", _agent_id)
	destination_tile = _destination_tile
