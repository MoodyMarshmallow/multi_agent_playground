class_name DebugPlayer
extends CharacterBody2D

@onready var animated_sprite_2d: AnimatedSprite2D = $AnimatedSprite2D
@onready var navigation_agent_2d: NavigationAgent2D = $NavigationAgent2D

var speed: float = 50.0
var last_direction: String = "down"
var using_navigation := false

func _ready():
	# Enable debug visualization
	navigation_agent_2d.debug_enabled = true
	navigation_agent_2d.debug_use_custom = true
	navigation_agent_2d.debug_path_custom_color = Color.RED
	navigation_agent_2d.debug_path_custom_point_size = 8.0
	navigation_agent_2d.debug_path_custom_line_width = 3.0
	
	#Make the agent follow the path more precisely
	navigation_agent_2d.path_desired_distance = 3.0  # Default is usually 20.0
	navigation_agent_2d.target_desired_distance = 10.0  # Default is usually 10.0
	navigation_agent_2d.path_max_distance = 15.0
	navigation_agent_2d.simplify_path = false
	
func _physics_process(delta: float) -> void:
	if using_navigation:
		# NavigationAgent2D handles pathfinding
		if navigation_agent_2d.is_navigation_finished():
			using_navigation = false
			animated_sprite_2d.play("idle_" + last_direction)
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

func navigate_to(target_position: Vector2) -> void:
	var nav_map = navigation_agent_2d.get_navigation_map()
	if nav_map:
		var closest_point = NavigationServer2D.map_get_closest_point(nav_map, target_position)
		navigation_agent_2d.set_target_position(closest_point)
	else:
		navigation_agent_2d.set_target_position(target_position)
	using_navigation = true

func _on_debugging_input_submitted(text: String) -> void:
	var regex = RegEx.new()
	var result

	# Handle "go to {room}" or "g {room}"
	regex.compile("^(go to|g)\\s+(.+)$")
	result = regex.search(text.strip_edges())
	if result:
		var room_name = result.get_string(2).replace(" ", "_")
		var tile: Vector2i = HouseLayout.get_empty_position_in_room_by_name(room_name)
		if tile != null and tile != Vector2i(-1, -1):
			var world_pos = tile * 16
			navigate_to(world_pos)
			print("Navigating to ", room_name, "at tile ", tile, "world pos ", world_pos)
		else:
			print("No empty tile found in ", room_name)
		return  # Only handle one command at a time

	# Handle "interact with {object}" or "i {object}"
	regex.compile("^(interact with|i)\\s+(.+)$")
	result = regex.search(text.strip_edges())
	if result:
		var object_name = result.get_string(2).replace(" ", "_")
		var tile: Vector2i = HouseLayout.get_empty_position_by_object(object_name)
		if tile != null and tile != Vector2i(-1, -1):
			var world_pos = tile * 16
			navigate_to(world_pos)
			print("Navigating to ", object_name, "at tile ", tile, "world pos ", world_pos)
		else:
			print("No empty tile found by ", object_name)
		return

	print("Unrecognized command: ", text)
