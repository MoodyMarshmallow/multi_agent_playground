class_name InventoryPanel
extends PanelContainer

var agent_id: String

@onready var agent_name_label: Label = $MarginContainer/VBoxContainer2/AgentNameLabel
@onready var agent_inventory_label: Label = $MarginContainer/VBoxContainer2/AgentInventoryLabel

func set_text(new_text: String):
	agent_inventory_label.text = new_text

func set_agent_id(new_agent_id: String):
	agent_name_label.text = new_agent_id
