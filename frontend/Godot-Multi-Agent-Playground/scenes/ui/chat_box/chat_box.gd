class_name ChatBox
extends Control

@onready var messages_vbox: VBoxContainer = $ChatPanel/VBoxContainer/ChatScroll/MessagesVBoxContainer

# Preload the message scene
var message_scene = preload("res://scenes/ui/chat_box/message.tscn")

func send_message(text: String):
	# Instance the message scene
	var new_message = message_scene.instantiate()
	
	# Add it to the MessagesVBoxContainer
	messages_vbox.add_child(new_message)
	
	# Set the message text
	new_message.set_message(text)
	
	print("Sent message: ", text)

func send_message_with_sender_recipient(sender: String, recipient: String, message: String):
	# Format the message text
	var formatted_text = "{sender} -> {recipient}:\n{message}".format({
		"sender": sender,
		"recipient": recipient,
		"message": message
	})
	
	# Send the formatted message
	send_message(formatted_text)
