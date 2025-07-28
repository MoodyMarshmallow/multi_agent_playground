class_name Inventory
extends Control

@onready var vbox_container: VBoxContainer = $InventoryPanel/ScrollContainer/VBoxContainer

# Dictionary to track existing inventory panels by agent_id
var inventory_panels: Dictionary = {}

# Preload the inventory panel scene
var inventory_panel_scene = preload("res://scenes/ui/inventory/inventory_panel.tscn")

func instantiate_inventory_panel(agent_id: String, text: String):
	# Check if panel already exists for this agent
	if agent_id in inventory_panels:
		print("Inventory panel for agent ", agent_id, " already exists!")
		return
	
	# Instance the inventory panel scene
	var new_panel = inventory_panel_scene.instantiate()
	
	# Add it to the VBoxContainer
	vbox_container.add_child(new_panel)
	
	# Set the agent_id and text
	new_panel.set_agent_id(agent_id)
	new_panel.set_text(text)
	
	# Store reference to the panel
	inventory_panels[agent_id] = new_panel

func update_inventory_panel(agent_id: String, text: String):
	# Check if panel exists for this agent
	if agent_id in inventory_panels:
		var panel = inventory_panels[agent_id]
		panel.set_text(text)
	else:
		print("No inventory panel found for agent: ", agent_id, ". Creating new one...")
		instantiate_inventory_panel(agent_id, text)

func destroy_inventory_panel(agent_id: String):
	# Check if panel exists for this agent
	if agent_id in inventory_panels:
		var panel = inventory_panels[agent_id]
		
		# Remove from parent
		if panel.get_parent():
			panel.get_parent().remove_child(panel)
		
		# Call destroy method on the panel itself
		panel.destroy()
		
		# Remove from dictionary
		inventory_panels.erase(agent_id)
	else:
		print("No inventory panel found for agent: ", agent_id)
