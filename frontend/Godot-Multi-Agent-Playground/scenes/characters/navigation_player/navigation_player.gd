class_name NavigationPlayer
extends Player

@onready var navigation_agent_2d: NavigationAgent2D = $NavigationAgent2D
@onready var agent_controller: Node = $AgentController

var target_position: Vector2 = Vector2.ZERO
var is_moving: bool = false
var visible_objects: Dictionary = {}

const TILE_SIZE : float = 16
const VISIBILITY_RANGE: int = 3

func _ready():
	# Enable debug visualization
	navigation_agent_2d.debug_enabled = true
	navigation_agent_2d.debug_use_custom = true
	navigation_agent_2d.debug_path_custom_color = Color.RED
	navigation_agent_2d.debug_path_custom_point_size = 8.0
	navigation_agent_2d.debug_path_custom_line_width = 3.0

	# Make the agent follow the path more precisely
	navigation_agent_2d.path_desired_distance = 10.0  # Default is usually 20.0
	navigation_agent_2d.target_desired_distance = 10.0  # Default is usually 10.0
	navigation_agent_2d.path_max_distance = 15.0
	navigation_agent_2d.simplify_path = false
	
	# Get reference to the HTTP controller and connect signals
	var controller = get_node("../AgentController")
	if controller:
		controller.new_destination.connect(_on_new_destination)
		controller.update_position.connect(_on_update_position)
	
	target_position = position

func _physics_process(_delta: float) -> void:
	update_visible_objects()

func update_visible_objects() -> void:
	var current_pos = Vector2i(position.x / TILE_SIZE, position.y / TILE_SIZE)
	var new_visible_objects: Dictionary = {}
	
	# Check all tiles in a square around the player
	for x in range(current_pos.x - VISIBILITY_RANGE, current_pos.x + VISIBILITY_RANGE + 1):
		for y in range(current_pos.y - VISIBILITY_RANGE, current_pos.y + VISIBILITY_RANGE + 1):
			var check_pos = Vector2i(x, y)
			if check_pos.distance_to(current_pos) <= VISIBILITY_RANGE:
				# account for house offset
				var object = HouseLayout.get_object_at_position(check_pos - Vector2i(16, 3))
				if not object.is_empty():
					new_visible_objects[object.name] = {
						"name": object.name,
						"room": object.data.room,
						"position": check_pos,
						"description": HouseLayout.get_object_description(object.name)
					}
	visible_objects = new_visible_objects

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("request_next_action"):
		request_next_action()
	if event.is_action_pressed("debug"):
		print_visible_objects()

func request_next_action() -> void:
	if agent_controller:
		agent_controller.request_next_action()

func _on_new_destination(coordinates):
	# Handle new destination coordinates
	# coordinates will be an array [x, y]
	target_position = coordinates * TILE_SIZE
	is_moving = true

func _on_update_position(tile_position):
	# Handle absolute position updates
	# tile_position will be an array [x, y]
	position = tile_position * TILE_SIZE
	target_position = position
	is_moving = false 

# TODO
func get_current_state() -> String:
	if $StateMachine:
		return $StateMachine.current_node_state_name
	return "idle"

func get_visible_objects() -> Dictionary:
	return visible_objects

func get_visible_agents() -> Array:
	return [] 

# Debug function to print visible objects
func print_visible_objects() -> void:
	print("Currently visible objects:")
	for obj_name in visible_objects:
		var obj = visible_objects[obj_name]
		print("%s in %s at position: %s" % [obj.name, obj.room, obj.position]) 

func clear_visible_objects() -> void:
	visible_objects.clear()
