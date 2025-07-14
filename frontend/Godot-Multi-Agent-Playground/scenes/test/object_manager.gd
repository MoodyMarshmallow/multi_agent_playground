extends Node

func take_object(object_name: String) -> void:
	for child in get_children():
		print(child.name)
		if child.name == object_name:
			if child.has_node("TakeableComponent"):
				var takeable = child.get_node("TakeableComponent")
				if takeable.has_method("take"):
					takeable.take()
					print("Took object:", object_name)
					return
	print("No takeable object found with name:", object_name)

func place_object(object_name: String) -> void:
	for child in get_children():
		if child.name == object_name and child.has_node("PlaceableComponent"):
			var placeable = child.get_node("PlaceableComponent")
			if placeable.has_method("place"):
				placeable.place()
				print("Placed object:", object_name)
				return
	print("No placeable object found with name:", object_name)
