extends RichTextLabel

func _ready() -> void:
	self.custom_minimum_size = Vector2(100, 100)

func _input(event):
	if event.is_action_pressed("toggle_emoji_visibility"):
		visible = not visible

func decode_unicode_escape(escape_str: String) -> String:
	var json = JSON.new()
	var result = json.parse('"%s"' % escape_str)
	if result == OK:
		return json.get_data()
	else:
		push_error("Failed to decode emoji: " + escape_str)
		return ""

func set_emoji_from_backend(escape_str: String):
	var emoji_char = decode_unicode_escape(escape_str)
	text = emoji_char
