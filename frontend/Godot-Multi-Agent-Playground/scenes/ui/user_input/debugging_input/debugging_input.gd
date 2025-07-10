extends LineEdit

signal debugging_input_submitted(text: String)

var active := false

func _ready():
	process_mode = Node.PROCESS_MODE_ALWAYS
	connect("text_submitted", Callable(self, "_on_text_submitted"))
	release_focus()
	set_process_unhandled_key_input(true)
	connect("focus_entered", Callable(self, "_on_focus_entered"))
	connect("focus_exited", Callable(self, "_on_focus_exited"))

func _key_input(event):
	if not has_focus():
		return
	accept_event()
	if event.is_action_pressed("ui_accept"):
		pass
	elif event.is_action_pressed("ui_cancel") or (event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE):
		text = ""
		release_focus()

func _on_text_submitted(submitted_text: String) -> void:
	emit_signal("debugging_input_submitted", submitted_text)
	parse_input(submitted_text)
	text = ""
	release_focus()

func parse_input(input_text: String) -> void:
	pass

func _on_focus_entered():
	active = true
	get_tree().paused = true

func _on_focus_exited():
	active = false
	get_tree().paused = false
