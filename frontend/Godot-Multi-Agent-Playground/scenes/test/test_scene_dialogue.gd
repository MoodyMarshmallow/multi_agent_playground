extends Node2D

@onready var balloon := $GameScreen/GameDialogueBalloon

func _ready():
	balloon.show_line("show line", "Bob")
