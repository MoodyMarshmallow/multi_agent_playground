extends NodeState

@export var player: Player
@export var animated_sprite_2d: AnimatedSprite2D
@export var speed: int = 50
@onready var navigation_agent_2d: NavigationAgent2D = $"../../NavigationAgent2D"
@onready var collision_shape_2d: CollisionShape2D = $"../../CollisionShape2D"
@onready var http_controller: Node = $"../../AgentController"

# Stuck detection variables
var stuck_timer: float = 0.0
var stuck_threshold: float = 3.0 
var last_position: Vector2 = Vector2.ZERO
var stuck_distance_threshold: float = 0.1

func on_process(_delta : float):
	pass


func on_physics_process(delta : float):
	var direction: Vector2 = GameInputEvents.movement_input()
	var move_direction: Vector2 = GameInputEvents.movement_input()
	if direction == Vector2.ZERO and navigation_agent_2d and not navigation_agent_2d.is_navigation_finished():
		var collider_pos = collision_shape_2d.global_position
		move_direction = (navigation_agent_2d.get_next_path_position() - collider_pos).normalized()
		
		var directions = {
			Vector2.UP: Vector2.UP,
			Vector2.DOWN: Vector2.DOWN,
			Vector2.LEFT: Vector2.LEFT,
			Vector2.RIGHT: Vector2.RIGHT
		}
		var max_dot = -INF
		var chosen_direction = Vector2.ZERO
		for dir in directions:
			var dot = move_direction.dot(dir)
			if dot > max_dot:
				max_dot = dot
				chosen_direction = dir
		direction = chosen_direction
		
		# Stuck detection
		var current_position = collider_pos
		var distance_moved = current_position.distance_to(last_position)
		
		if distance_moved < stuck_distance_threshold:
			stuck_timer += delta
			if stuck_timer >= stuck_threshold:
				print("Player stuck for too long, transitioning to Idle")
				transition.emit("Idle")
				return
		else:
			stuck_timer = 0.0
		
		last_position = current_position
		
	if direction == Vector2.UP:
		animated_sprite_2d.play("walk_back")
	elif direction == Vector2.RIGHT:
		animated_sprite_2d.play("walk_right")
	elif direction == Vector2.DOWN:
		animated_sprite_2d.play("walk_front")
	elif direction == Vector2.LEFT:
		animated_sprite_2d.play("walk_left")
	
	if direction != Vector2.ZERO:
		player.player_direction = direction
	
	player.velocity = move_direction * speed
	player.move_and_slide()

func on_next_transitions() -> void:
	var manual_input = GameInputEvents.movement_input()
	
	if manual_input == Vector2.ZERO:
		var is_navigating = navigation_agent_2d and not navigation_agent_2d.is_navigation_finished()
		if is_navigating:
			# Only stay in walking if we're still navigating and not at target
			var distance_to_target = player.global_position.distance_to(navigation_agent_2d.target_position)
			if distance_to_target < 10.0:
				_complete_movement()
				transition.emit("Idle")
		else:
			# No navigation happening and no manual input = go to idle
			_complete_movement()
			transition.emit("Idle")

func _complete_movement() -> void:
	if http_controller:
		http_controller.notify_action_completed()

func on_enter():
	stuck_timer = 0.0
	last_position = collision_shape_2d.global_position if collision_shape_2d else Vector2.ZERO

func on_exit():
	animated_sprite_2d.stop()
	stuck_timer = 0.0
