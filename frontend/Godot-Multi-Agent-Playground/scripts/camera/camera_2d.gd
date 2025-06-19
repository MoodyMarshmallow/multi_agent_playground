extends Camera2D

@export var camera_speed := 200.0  # Pixels per second

func _process(delta: float) -> void:
	var input_vector := Vector2.ZERO

	if Input.is_action_pressed("camera_up"):
		input_vector.y -= 1
	if Input.is_action_pressed("camera_down"):
		input_vector.y += 1
	if Input.is_action_pressed("camera_left"):
		input_vector.x -= 1
	if Input.is_action_pressed("camera_right"):
		input_vector.x += 1

	position += input_vector.normalized() * camera_speed * delta
