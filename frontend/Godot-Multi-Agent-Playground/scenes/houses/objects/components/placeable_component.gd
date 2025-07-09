extends Node2D

signal place_object

func place():
	emit_signal("place_object")
