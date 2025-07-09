class_name InteractableComponent
extends Node2D

signal interactable_activated
signal interactable_deactivated


func _on_interact_activate(body: Node2D) -> void:
	interactable_activated.emit()

func _on_interact_deactivate(body: Node2D) -> void:
	interactable_deactivated.emit()
