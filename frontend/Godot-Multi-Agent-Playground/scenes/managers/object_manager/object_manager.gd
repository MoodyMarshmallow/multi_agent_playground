class_name ObjectManager
extends Node

var rooms : Dictionary = {} # snake_case_name -> Node2D
var objects : Dictionary = {} # snake_case_name -> Node2D

# Populate the lists of rooms and objects with the respective objects
func _ready():
	# Clear lists in case of re-initialization
	rooms.clear()
	objects.clear()
	# Add all direct children (rooms) to the rooms array
	for room in get_children():
		if room is Node2D:
			var room_key = to_snake_case(room.name)
			rooms[room_key] = room
			# Add all children of the room (objects) to the objects array
			for obj in room.get_children():
				if obj is Node2D:
					var obj_key = to_snake_case(obj.name)
					objects[obj_key] = obj

# The starting point for handling all object actions
func handle_object_action(action: Dictionary) -> void:
	pass

# No need for _normalize_name anymore!

func to_snake_case(name: String) -> String:
	var snake = ""
	for i in name.length():
		var c = name[i]
		if c == c.to_upper() and c != c.to_lower() and i > 0:
			snake += "_"
		snake += c.to_lower()
	return snake

# Returns a Node2D corresponding to the room with the provided room_name
func get_room_by_name(room_name: String) -> Node2D:
	var key = to_snake_case(room_name)
	return rooms.get(key, null)

# Returns a Node2D corresponding to the object with the provided object_name
func get_object_by_name(object_name: String) -> Node2D:
	var key = to_snake_case(object_name)
	return objects.get(key, null)

# Returns the global position of a room (usually around the center of the room)
func get_room_location(room: String) -> Vector2:
	print("getting room location")
	var room_node = get_room_by_name(room)
	if room_node:
		print("room location is: ", room_node.global_position)
		return room_node.global_position
	print("defaulting to 0, 0 room location")
	return Vector2(-INF, -INF)
# Returns the global position of an object (usually around the center of the object's sprite)
func get_object_location(object: String) -> Vector2:
	var obj_node = get_object_by_name(object)
	if obj_node:
		return obj_node.global_position
	return Vector2(-INF, -INF)

# Returns the global position of a room or object, given its name
func get_location(name: String) -> Vector2:
	var obj_node = get_object_by_name(name)
	if obj_node:
		return obj_node.global_position
	var room_node = get_room_by_name(name)
	if room_node:
		return room_node.global_position
	return Vector2(-INF, -INF)
