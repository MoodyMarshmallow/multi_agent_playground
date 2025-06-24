# TimeManager.gd
extends Node

const TIME_SCALE := 60.0  # 60x faster than real time

var game_seconds_passed := 0.0  # in-game seconds

func _process(delta):
	game_seconds_passed += delta * TIME_SCALE

func get_formatted_time() -> String:
	var total_seconds := int(game_seconds_passed)
	var seconds := total_seconds % 60
	var minutes := (total_seconds / 60) % 60
	var hours := (total_seconds / 3600) % 24
	var days := (total_seconds / 86400) + 1  # day 1-based

	return "%02dT%02d:%02d:%02d" % [days, hours, minutes, seconds]
