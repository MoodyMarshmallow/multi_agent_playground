extends NodeState

@export var player: Player
@export var animated_sprite_2d: AnimatedSprite2D
@export var speed: int = 50

func on_process(_delta : float):
	pass


func on_physics_process(_delta : float):
	var direction: Vector2 = GameInputEvents.movement_input()
	
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
	
	player.velocity = direction * speed
	player.move_and_slide()

func on_next_transitions() -> void:
	GameInputEvents.movement_input()
	
	if !GameInputEvents.is_movement_input():
		transition.emit("Idle")
	
func on_enter():
	pass


func on_exit():
	animated_sprite_2d.stop()
