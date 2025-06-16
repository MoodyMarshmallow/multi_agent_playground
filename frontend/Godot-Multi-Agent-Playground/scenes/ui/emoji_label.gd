extends Node2D
@onready var label: Label = $Label

func set_emoji_from_backend(escape_str: String):
	var emoji_char = decode_unicode_escape(escape_str)
	label.text = emoji_char

func decode_unicode_escape(escape_str: String) -> String:
	var json = JSON.new()
	var parse_result = json.parse('"%s"' % escape_str)
	
	if parse_result == OK:
		return json.data
	else:
		print("Failed to parse unicode escape: ", escape_str)
		return escape_str
