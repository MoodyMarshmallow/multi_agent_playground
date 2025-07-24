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
	var recipient = action.get("recipient", null)
	var place_location = action.get("place_location", null)
	var state = action.get("state", null)
	var obj = get_object_by_name(target)
	if obj == null:
		if target != "" and target not in rooms.keys():
			print("[ObjectManager] Could not find object with name: ", target)
		return
	if action_type == "take":
		if obj.has_method("take_object"):
			obj.take_object()
		else:
			print("ObjectManager: Object does not have take_object method:", target)
	elif action_type == "drop":
		if obj.has_method("place_object_at") and place_location != null:
			obj.place_object_at(place_location)
		else:
			print("ObjectManager: Object does not have place_object_at method in order to drop or place_location missing:", target)
	elif action_type == "examine":
		if obj.has_method("examine_object"):
			obj.examine_object()
		else:
			print("ObjectManager: Object does not have examine_object method:", target)
	elif action_type == "place":
		if obj.has_method("place_object_at") and place_location != null:
			obj.place_object_at(place_location)
		else:
			print("ObjectManager: Object does not have place_object_at method or place_location missing:", target)
	elif action_type == "consume":
		if obj.has_method("consume_object"):
			obj.consume_object()
		elif obj.has_method("use"):
			obj.use()
		else:
			print("ObjectManager: Object does not have consume_object or use method:", target)
	elif action_type == "set_to_state":
		if obj.has_method("set_to_state"):
			obj.set_to_state(state)
		else:
			# Fallback: emit signals for known objects/states
			var interactive_targets = ["fridge", "oven", "medicine_cabinet", "toy_bin", "bathroom_door", "entry_door", "coffee_maker", "faucet", "bathtub"]
			if to_snake_case(target) in interactive_targets:
				var component = obj.get_node_or_null("InteractableComponent")
				if component:
					if state in ["open", "on"]:
						component.interactable_activated.emit()
					elif state in ["closed", "off"]:
						component.interactable_deactivated.emit()
				else:
					print("ObjectManager: No InteractableComponent found on object:", target)
	elif action_type == "start_using":
		if obj.has_method("start_using"):
			obj.start_using()
		else:
			print("ObjectManager: Object does not have start_using method:", target)
	elif action_type == "stop_using":
		if obj.has_method("stop_using"):
			obj.stop_using()
		else:
			print("ObjectManager: Object does not have stop_using method:", target)
	elif action_type == "look":
		print("Look action received. (No-op)")
	elif action_type == "go_to":
		pass # Navigation only

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
	var obj = objects.get(key, null)
	if obj == null or not is_instance_valid(obj):
		# Clean dictionary
		objects.erase(key)
		return null
	return obj

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

func remove_object_by_name(object_name: String) -> void:
	var key = to_snake_case(object_name)
	objects.erase(key)
