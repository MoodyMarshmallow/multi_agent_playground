extends NodeState

@export var player: Player
@export var animated_sprite_2d: AnimatedSprite2D
@onready var navigation_agent_2d: NavigationAgent2D = $"../../NavigationAgent2D"

func on_process(_delta : float):
	pass

var clicked_position: Vector2 = Vector2.ZERO
var navigating: bool = false

func on_physics_process(_delta : float) -> void:
	if player.player_direction == Vector2.UP:
		animated_sprite_2d.play("idle_back")
	elif player.player_direction == Vector2.RIGHT:
		animated_sprite_2d.play("idle_right")
	elif player.player_direction == Vector2.DOWN:
		animated_sprite_2d.play("idle_front")
	elif player.player_direction == Vector2.LEFT:
		animated_sprite_2d.play("idle_left")
	else:
		animated_sprite_2d.play("idle_front")

func on_next_transitions() -> void:
	GameInputEvents.movement_input()
	if (Input.is_action_just_pressed("right_click")):
		clicked_position = get_viewport().get_mouse_position()
		if navigation_agent_2d:
			navigation_agent_2d.set_target_position(clicked_position)
			var next_path_position = navigation_agent_2d.get_next_path_position()
			navigating = true
			
			# Wait a frame for navigation to calculate, then check if reachable
			await get_tree().process_frame
			
			if navigation_agent_2d.is_target_reachable():
				print("navigating")
				transition.emit("Walk")
			else:
				print("Target not reachable!")
				# goto closest point instead
				var closest_point = NavigationServer2D.map_get_closest_point(navigation_agent_2d.get_navigation_map(), clicked_position)
				navigation_agent_2d.set_target_position(closest_point)
				print("Navigating to closest reachable point")
				transition.emit("Walk")
			
	if GameInputEvents.is_movement_input():
		transition.emit("Walk")
	
	if player.current_tool == DataTypes.Tools.AxeWood && GameInputEvents.use_tool():
		transition.emit("Chopping")
	
	if player.current_tool == DataTypes.Tools.TillGround && GameInputEvents.use_tool():
		transition.emit("Tilling")
	
	if player.current_tool == DataTypes.Tools.WaterCrops && GameInputEvents.use_tool():
		transition.emit("Watering")

func on_enter():
	pass


func on_exit():
	animated_sprite_2d.stop()
