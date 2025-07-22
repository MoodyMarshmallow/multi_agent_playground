class_name BaseObject
extends Node2D

@export var start_visible: bool = true

func _ready():
	visible = start_visible

# Hides the object (e.g., when taken)
func take_object() -> void:
	visible = false

# Places the object at a given position and makes it visible
func place_object_at(pos: Vector2) -> void:
	global_position = pos
	visible = true

# Destroys the object (e.g., when used)
func consume() -> void:
	queue_free()
	
func use() -> void:
	queue_free()

func examine_object() -> void:
	print("Examining ", self.name.to_lower())
