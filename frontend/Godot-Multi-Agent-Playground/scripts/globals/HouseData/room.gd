class_name Room
extends Resource

var corners: Corners = Corners.new()
var adjacent_rooms: Array[String] = []
var objects: Dictionary = {}
var interactable_objects: Dictionary = {}
var idle_positions: Dictionary = {}
var occupied_positions: Dictionary = {}

func _init():
	pass

# Example usage:
# var bedroom = Room.new()
# bedroom.corners.ul = Vector2i(10, 10)
# bedroom.adjacent_rooms.append("dining_room")
