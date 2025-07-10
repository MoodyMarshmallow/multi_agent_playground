extends Node2D

@onready var debugging_input: LineEdit = $UIManager/DebuggingInput
@onready var ui_manager: CanvasLayer = $UIManager

@onready var http_manager: Node = $HttpManager
@onready var text_input_manager: Node2D = $TextInputManager

@onready var object_manager: Node2D = $ObjectManager
@onready var agent_manager: AgentManager = $AgentManager
@onready var debug_player: DebugPlayer = $DebugPlayer

func _ready():
	debugging_input.connect("debugging_input_submitted", Callable(debug_player, "_on_debugging_input_submitted"))
	debugging_input.connect("debugging_input_submitted", Callable(text_input_manager, "_on_debugging_input_submitted"))
