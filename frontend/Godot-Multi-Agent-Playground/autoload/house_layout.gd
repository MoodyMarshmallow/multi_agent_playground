extends Node

var house_data: Dictionary = {}
var _object_locations: Dictionary = {}  # Cache for quick lookups

func _ready() -> void:
	load_house_data()
	_build_object_locations()

func load_house_data() -> void:
	var json_file = FileAccess.open("res://resources/house_layout.json", FileAccess.READ)
	if json_file:
		var json_text = json_file.get_as_text()
		json_file = null  # Close the file

		var result = JSON.parse_string(json_text)
		if result != null:
			house_data = result
		else:
			push_error("Failed to parse house layout JSON with parse_string.")
	else:
		push_error("Failed to load house layout file")



func _build_object_locations() -> void:
	# Flatten the hierarchy for easy lookups
	for floor_name in house_data.house:
		var floor_data = house_data.house[floor_name]
		for room_name in floor_data:
			var room_data = floor_data[room_name]
			_process_room(room_name, room_data)

func _process_room(room_name: String, room_data: Dictionary) -> void:
	for object_name in room_data:
		var object_data = room_data[object_name]
		if object_data is Dictionary:
			if "shape" in object_data:
				# Simple object
				_object_locations[object_name] = {
					"room": room_name,
					"shape": object_data.shape,
					"interact": object_data.get("interact", []),
					"description": object_data.get("description", "")
				}
			else:
				# Nested objects (like bookshelves)
				for sub_object_name in object_data:
					var sub_object = object_data[sub_object_name]
					if sub_object is Dictionary and "shape" in sub_object:
						_object_locations[sub_object_name] = {
							"room": room_name,
							"parent": object_name,
							"shape": sub_object.shape,
							"interact": sub_object.get("interact", []),
							"description": sub_object.get("description", "")
						}

# Public API

func get_object_at_position(pos: Vector2i) -> Dictionary:
	# Returns object data if found at position, empty dict if not
	for object_name in _object_locations:
		var object_data = _object_locations[object_name]
		for cell in object_data.shape:
			if cell[0] == pos.x and cell[1] == pos.y:
				return {
					"name": object_name,
					"data": object_data
				}
	return {}

func get_room_for_position(pos: Vector2i) -> String:
	var object = get_object_at_position(pos)
	if not object.is_empty():
		return object.data.room
	return ""

func get_interaction_points_for_object(object_name: String) -> Array:
	if object_name in _object_locations:
		return _object_locations[object_name].get("interact", [])
	return []

func get_object_shape(object_name: String) -> Array:
	if object_name in _object_locations:
		return _object_locations[object_name].shape
	return []

func get_object_description(object_name: String) -> String:
	if object_name in _object_locations:
		return _object_locations[object_name].get("description", "")
	return ""

func get_all_objects_in_room(room_name: String) -> Array:
	var objects = []
	for object_name in _object_locations:
		if _object_locations[object_name].room == room_name:
			objects.append(object_name)
	return objects
