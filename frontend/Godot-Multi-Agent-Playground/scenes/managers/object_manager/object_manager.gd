class_name ObjectManager
extends Node

var rooms : Dictionary = {} # snake_case_name -> Node2D
var objects : Dictionary = {} # snake_case_name -> Node2D

# Populate the lists of rooms and objects with the respective objects
func _ready():
	update_children_objects()

# Repopulate the rooms and objects dictionaries from the scene tree
func update_children_objects():
	rooms.clear()
	objects.clear()
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
	if action.has("move_to"):
		# Wait for post-navigation callback
		return
	_do_object_action(action)

func handle_post_navigation_object_action(action: Dictionary):
	_do_object_action(action)

func _do_object_action(action: Dictionary) -> void:
	var action_type = action.get("action_type", "")
	var target = action.get("target", "")
	var place_location = action.get("place_location", null)
	var obj = get_object_by_name(target)
	if obj == null:
		return
	if action_type == "take":
		if obj.has_method("take_object"):
			obj.take_object()
		else:
			print("ObjectManager: Object does not have take_object method:", target)
	elif action_type == "use":
		if obj.has_method("use"):
			obj.use()
		else:
			print("ObjectManager: Object does not have use method:", target)
	elif action_type in ["place", "place_on"]:
		if obj.has_method("place_object_at") and place_location != null:
			obj.place_object_at(place_location)
		else:
			print("ObjectManager: Object does not have place_object_at method or place_location missing:", target)
	elif action_type in ["open", "close"]:
		var interactive_targets = ["toy_bin", "oven", "fridge", "medicine_cabinet", "bathroom_door", "entry_door"]
		if to_snake_case(target) in interactive_targets:
			var component = obj.get_node_or_null("InteractableComponent")
			if component:
				if action_type == "open":
					component.interactable_activated.emit()
				elif action_type == "close":
					component.interactable_deactivated.emit()
			else:
				print("ObjectManager: No InteractableComponent found on object:", target)
	elif action_type in ["turn_on", "turn_off"]:
		var interactive_targets = ["coffee_maker", "faucet", "bathtub"]
		if to_snake_case(target) in interactive_targets:
			var component = obj.get_node_or_null("InteractableComponent")
			if component:
				if action_type == "turn_on":
					component.interactable_activated.emit()
				elif action_type == "turn_off":
					component.interactable_deactivated.emit()
			else:
				print("ObjectManager: No InteractableComponent found on object:", target)

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
