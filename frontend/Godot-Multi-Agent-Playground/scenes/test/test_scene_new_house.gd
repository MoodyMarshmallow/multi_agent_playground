extends Node2D

@onready var debugging_input: LineEdit = $Camera2D/DebuggingInput
@onready var debug_player: DebugPlayer = $DebugPlayer

func _ready():
	debugging_input.connect("debugging_input_submitted", Callable(debug_player, "_on_debugging_input_submitted"))
