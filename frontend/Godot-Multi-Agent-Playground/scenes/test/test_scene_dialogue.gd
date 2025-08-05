extends Node2D

@onready var balloon := $GameScreen/HBoxContainer/Dialogue
@onready var inventory_balloon := $GameScreen/HBoxContainer/Inventory

func _ready():
	balloon.show_line("show line", "Bob")
	inventory_balloon.show_line("show inventory line", "Inventory")
