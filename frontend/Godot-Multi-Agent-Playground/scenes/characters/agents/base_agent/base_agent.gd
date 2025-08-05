class_name BaseAgent
extends CharacterBody2D

@onready var animated_sprite_2d: AnimatedSprite2D = $AnimatedSprite2D
@onready var navigation_agent_2d: NavigationAgent2D = $NavigationAgent2D
@onready var collision_shape_2d: CollisionShape2D = $CollisionShape2D
@onready var object_manager: ObjectManager = $"../../NavigationRegionD/ObjectManager"

@export var agent_id: String = ""
var speed: float = 50.0
var last_direction: String = "down"
var using_navigation := false
var inventory: Array[String] = []
var inventory_objects: Array = []

signal reached_destination(action: Dictionary)
signal inventory_changed(agent_id: String, inventory_text: String)

var pending_action: Dictionary = {}

func _ready():
	# Enable debug visualization
	#navigation_agent_2d.debug_enabled = true
	#navigation_agent_2d.debug_use_custom = true
	#navigation_agent_2d.debug_path_custom_color = Color.RED
	#navigation_agent_2d.debug_path_custom_point_size = 8.0
	#navigation_agent_2d.debug_path_custom_line_width = 3.0
	
	#Make the agent follow the path more precisely
	navigation_agent_2d.path_desired_distance = 3.0  # Default is usually 20.0
	navigation_agent_2d.target_desired_distance = 10.0  # Default is usually 10.0
	navigation_agent_2d.path_max_distance = 5.0 # was 15.0
	navigation_agent_2d.simplify_path = false

# Supports using_navigation and szxc movement keys
func _physics_process(delta: float) -> void:
	if using_navigation:
		# NavigationAgent2D handles pathfinding
		if navigation_agent_2d.is_navigation_finished():
			using_navigation = false
			# Enhanced facing logic: prefer up, then left/right, then down
			if pending_action.has("move_to"):
				var target_pos = pending_action["move_to"]
				var direction_vec = target_pos - global_position
				var dx = direction_vec.x
				var dy = direction_vec.y
				# Prefer up if the target is above, unless it's much more to the left/right
				if dy < 0 and abs(dy) > 0.01 * abs(dx):
					last_direction = "up"
				elif abs(dx) > abs(dy):
					last_direction = "right" if dx > 0 else "left"
				elif dy > 0:
					last_direction = "down"
				else:
					last_direction = "up"
				animated_sprite_2d.play("idle_" + last_direction)
			if pending_action.size() > 0:
				emit_signal("reached_destination", pending_action)
				pending_action = {}
			return

		var next_path_pos = navigation_agent_2d.get_next_path_position()
		var direction = (next_path_pos - global_position)
		if direction.length() > 1.0:
			velocity = direction.normalized() * speed
			# Update animation direction
			if abs(velocity.x) > abs(velocity.y):
				last_direction = "right" if velocity.x > 0 else "left"
			else:
				last_direction = "down" if velocity.y > 0 else "up"
			animated_sprite_2d.play("walk_" + last_direction)
		else:
			velocity = Vector2.ZERO
			navigation_agent_2d.advance_to_next_path_position()
	else:
		velocity = Vector2.ZERO
		# Manual movement input
		if Input.is_action_pressed("walk_up"):
			velocity.y -= 1
			last_direction = "up"
		elif Input.is_action_pressed("walk_down"):
			velocity.y += 1
			last_direction = "down"

		if Input.is_action_pressed("walk_left"):
			velocity.x -= 1
			last_direction = "left"
		elif Input.is_action_pressed("walk_right"):
			velocity.x += 1
			last_direction = "right"

		# Normalize and apply speed
		if velocity != Vector2.ZERO:
			velocity = velocity.normalized() * speed
			animated_sprite_2d.play("walk_" + last_direction)
		else:
			animated_sprite_2d.play("idle_" + last_direction)
	move_and_slide()

	# Update inventory object positions to follow the agent
	for obj in inventory_objects:
		if obj:
			obj.global_position = global_position

# Set navigation using global position
func navigate_to(target_position: Vector2) -> void:
	var nav_map = navigation_agent_2d.get_navigation_map()
	if nav_map:
		var closest_point = NavigationServer2D.map_get_closest_point(nav_map, target_position)
		navigation_agent_2d.set_target_position(closest_point)
	else:
		navigation_agent_2d.set_target_position(target_position)
	using_navigation = true

# Call this to start a navigation action and store the action
func start_navigation_action(target_position: Vector2, action: Dictionary) -> void:
	pending_action = action
	navigate_to(target_position)

# Helper to convert a string to snake_case
func to_snake_case(name: String) -> String:
	var snake = ""
	for i in name.length():
		var c = name[i]
		if c == c.to_upper() and c != c.to_lower() and i > 0:
			snake += "_"
		snake += c.to_lower()
	# Replace spaces with underscores
	snake = snake.replace(" ", "_")
	return snake

# Adds an item to the inventory by name (standardized to snake_case)
func add_to_inventory(item: String) -> void:
	print("adding to inventory, ", item)
	var key = to_snake_case(item)
	# Only add if the object exists in the object manager
	if object_manager:
		var obj = object_manager.get_object_by_name(item)
		if obj and is_instance_valid(obj):
			if key not in inventory:
				inventory.append(key)
				if obj not in inventory_objects:
					inventory_objects.append(obj)
					obj.global_position = global_position
					obj.visible = false # Optionally hide the object
				_emit_inventory_changed()
		else:
			print("[BaseAgent] Tried to add invalid or non-existent item to inventory: ", item)

# Removes an item from the inventory by name (standardized to snake_case)
func remove_from_inventory(item: String) -> void:
	var key = to_snake_case(item)
	if key in inventory:
		inventory.erase(key)
		# Remove the object reference from inventory_objects
		if object_manager:
			var obj = object_manager.get_object_by_name(item)
			if obj and obj in inventory_objects:
				inventory_objects.erase(obj)
		_emit_inventory_changed()

# Helper function to emit inventory changed signal
func _emit_inventory_changed():
	var inventory_text = "empty"
	if inventory.size() > 0:
		inventory_text = "\n".join(inventory).replace("_", " ")
	emit_signal("inventory_changed", agent_id, inventory_text)

# Prints the inventory in the specified format (underscores replaced by spaces)
func print_inventory() -> void:
	print(agent_id + "'s inventory:")
	for item in inventory:
		print(item.replace("_", " "))

# Returns the inventory data structure
func get_inventory() -> Array[String]:
	return inventory
