extends Node2D

signal take_object

func take():
	emit_signal("take_object")
