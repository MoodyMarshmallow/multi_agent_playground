extends Camera2D

@export var camera_speed := 200.0  # Pixels per second

const MIN_ZOOM = 0.5
const MAX_ZOOM = 3.0
const ZOOM_STEP = 0.1

# Store the default camera position and zoom
var default_position: Vector2
var default_zoom: float = 1.0  # 1.0 is the default Godot zoom

func _ready() -> void:
	default_position = position
	zoom = Vector2(default_zoom, default_zoom)

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

	if input_vector != Vector2.ZERO:
		position += input_vector.normalized() * camera_speed * delta

	var current_zoom = zoom.x  # zoom is a Vector2, x and y should stay equal

	if Input.is_action_just_pressed("zoom_in"):
		current_zoom = min(MAX_ZOOM, current_zoom + ZOOM_STEP)
		zoom = Vector2(current_zoom, current_zoom)
	elif Input.is_action_just_pressed("zoom_out"):
		current_zoom = max(MIN_ZOOM, current_zoom - ZOOM_STEP)
		zoom = Vector2(current_zoom, current_zoom)
		
	# Reset camera to default position and zoom
	if Input.is_action_just_pressed("camera_reset"):
		position = default_position
		zoom = Vector2(default_zoom, default_zoom)
