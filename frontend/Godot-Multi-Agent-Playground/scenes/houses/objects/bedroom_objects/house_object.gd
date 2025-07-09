class_name HouseObject
extends Node2D


@onready var sprite_2d: Sprite2D = $Sprite2D
@onready var takeable: Node = $TakeableComponent
@onready var placeable: Node = $PlaceableComponent

func _ready():
	if takeable.has_signal("take_object"):
		takeable.connect("take_object", Callable(self, "_on_take_object"))
	if placeable.has_signal("place_object"):
		placeable.connect("place_object", Callable(self, "_on_place_object"))

func _on_take_object():
	sprite_2d.hide()

func _on_place_object():
	sprite_2d.show()

func move_to_world_position(new_position: Vector2) -> void:
	global_position = new_position

func set_sprite_size(width: float, height: float) -> void:
	if sprite_2d.texture:
		var tex_size = sprite_2d.texture.get_size()
		sprite_2d.scale = Vector2(width / tex_size.x, height / tex_size.y)

# Inventory suggestion
# In your inventory UI script
#func add_to_inventory(item_sprite: Sprite2D):
	#var icon = TextureRect.new()
	#icon.texture = item_sprite.texture
	#icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	#icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	#icon.size = Vector2(32, 32) # or whatever your slot size is
	#$InventorySlotContainer.add_child(icon)
