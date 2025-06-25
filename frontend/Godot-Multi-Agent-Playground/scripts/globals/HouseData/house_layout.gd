class_name House_Layout

enum Rooms {
	none,
	bedroom,
	bathroom,
	kitchen,
	entry_room,
	dining_room,
	living_room,
	laundry_room,
	game_room
}

# Global variables
var upper_left_corner = Vector2i(0, 0)
var bedroom: Room = Room.new()
var bathroom: Room = Room.new()
var kitchen: Room = Room.new()
var entry_room: Room = Room.new()
var dining_room: Room = Room.new()
var living_room: Room = Room.new()
var laundry_room: Room = Room.new()
var game_room: Room = Room.new()

# Initialize the room data
func _static():
	_set_up_rooms()

func _set_up_rooms():
	_set_up_bedroom()
	_set_up_bathroom()
	_set_up_kitchen()
	_set_up_entry_room()
	_set_up_dining_room()
	_set_up_living_room()
	_set_up_laundry_room()
	_set_up_game_room()

func _set_up_bedroom():
	bedroom.corners.ul = Vector2i(0, 0)
	bedroom.corners.ur = Vector2i(18, 0)
	bedroom.corners.dl = Vector2i(0, 8)
	bedroom.corners.dr = Vector2i(18, 8)
	bedroom.adjacent_rooms = ["laundry_room", "dining_room"]
	bedroom.objects = {
		"nightstand" : null,
		"plush" : null, 
		"robot" : null, 
		"bed" : null, 
		"desk" : null, 
		"carpet" : null, 
		"mirror" : null, 
		"blocks" : null, 
		"crib" : null, 
		"tv" : null, 
		"chest" : null, 
		"toy_cars" : null, 
		"cubbies" : null, 
		"transformer" : null, 
		"rug" : null, 
		"book" : null, 
		"plant" : null, 
		"dresser" : null, 
		"skateboard" : null, 
	}
	var chest : InteractableObject = InteractableObject.new()
	chest.name = "chest"
	chest.tile = Vector2i(7, 2)
	chest.states = {
		"open" : null,
		"closed" : null
	}
	chest.current_state = "closed"
	bedroom.interactable_objects = {
		"chest" : chest
	}
	
	bedroom.idle_positions = {}
	bedroom.occupied_positions = {}

func _set_up_bathroom():
	bathroom.corners.ul = Vector2i(19, 2)
	bathroom.corners.ur = Vector2i(30, 2)
	bathroom.corners.dl = Vector2i(19, 5)
	bathroom.corners.dr = Vector2i(30, 5)
	bathroom.adjacent_rooms = ["game_room"]
	bathroom.objects = {
		"sink" : null,
		"bathtub" : null,
		"cabinet" : null,
	}
	
	var sink : InteractableObject = InteractableObject.new()
	sink.name = "sink"
	sink.tile = Vector2i(20, 2)
	sink.states = {
		"on" : null,
		"off" : null
	}
	sink.current_state = "off"
	
	var bathtub : InteractableObject = InteractableObject.new()
	bathtub.name = "bathtub"
	bathtub.tile = Vector2i(24, 2)
	bathtub.states = {
		"full" : null,
		"empty" : null
	}
	bathtub.current_state = "empty"
	
	var cabinet : InteractableObject = InteractableObject.new()
	cabinet.name = "cabinet"
	cabinet.tile = Vector2i(28, 2)
	cabinet.states = {
		"open" : null,
		"closed" : null
	}
	cabinet.current_state = "closed"
	
	bathroom.interactable_objects = {
		"sink" : sink,
		"bathtub" : bathtub,
		"cabinet" : cabinet,
	}
	bathroom.idle_positions = {}
	bathroom.occupied_positions = {}

func _set_up_kitchen():
	kitchen.corners.ul = Vector2i(0, 10)
	kitchen.corners.ur = Vector2i(11, 10)
	kitchen.corners.dl = Vector2i(0, 14)
	kitchen.corners.dr = Vector2i(11, 14)
	kitchen.adjacent_rooms = ["dining_room", "entry_room"]
	kitchen.objects = {
		"fridge" : null,
		"oven" : null,
		"coffee" : null,
	}
	
	var fridge : InteractableObject = InteractableObject.new()
	fridge.name = "fridge"
	fridge.tile = Vector2i(0, 10)
	fridge.states = {
		"open" : null,
		"closed" : null
	}
	fridge.current_state = "closed"
	
	var oven : InteractableObject = InteractableObject.new()
	oven.name = "oven"
	oven.tile = Vector2i(5, 10)
	oven.states = {
		"open" : null,
		"closed" : null
	}
	oven.current_state = "closed"
	
	var coffee : InteractableObject = InteractableObject.new()
	coffee.name = "coffee"
	coffee.tile = Vector2i(8, 10)
	coffee.states = {
		"on" : null,
		"off" : null
	}
	coffee.current_state = "off"
	
	kitchen.interactable_objects = {
		"fridge" : fridge,
		"oven" : oven,
		"coffee" : coffee,
	}
	kitchen.idle_positions = {}
	kitchen.occupied_positions = {}

func _set_up_entry_room():
	entry_room.corners.ul = Vector2i(3, 19)
	entry_room.corners.ur = Vector2i(9, 19)
	entry_room.corners.dl = Vector2i(3, 22)
	entry_room.corners.dr = Vector2i(9, 22)
	entry_room.adjacent_rooms = ["kitchen"]
	entry_room.objects = {
		"" : null,
	}
	entry_room.interactable_objects = {
		"" : null,
	}
	entry_room.idle_positions = {}
	entry_room.occupied_positions = {}

func _set_up_dining_room():
	dining_room.corners.ul = Vector2i(12, 10)
	dining_room.corners.ur = Vector2i(18, 10)
	dining_room.corners.dl = Vector2i(12, 19)
	dining_room.corners.dr = Vector2i(18, 19)
	dining_room.adjacent_rooms = ["kitchen", "bedroom", "living_room"]
	dining_room.objects = {
		"" : null,
	}
	dining_room.interactable_objects = {
		"" : null,
	}
	dining_room.idle_positions = {}
	dining_room.occupied_positions = {}

func _set_up_living_room():
	living_room.corners.ul = Vector2i(18, 13)
	living_room.corners.ur = Vector2i(25, 13)
	living_room.corners.dl = Vector2i(18, 19)
	living_room.corners.dr = Vector2i(25, 19)
	living_room.adjacent_rooms = ["dining_room", "game_room"]
	living_room.objects = {
		"" : null,
	}
	living_room.interactable_objects = {
		"" : null,
	}
	living_room.idle_positions = {}
	living_room.occupied_positions = {}

func _set_up_laundry_room():
	laundry_room.corners.ul = Vector2i(19, 7)
	laundry_room.corners.ur = Vector2i(24, 7)
	laundry_room.corners.dl = Vector2i(19, 11)
	laundry_room.corners.dr = Vector2i(24, 11)
	laundry_room.adjacent_rooms = ["bathroom", "game_room"]
	laundry_room.objects = {
		"" : null,
	}
	laundry_room.interactable_objects = {
		"" : null,
	}
	laundry_room.idle_positions = {}
	laundry_room.occupied_positions = {}

func _set_up_game_room():
	game_room.corners.ul = Vector2i(25, 7)
	game_room.corners.ur = Vector2i(30, 7)
	game_room.corners.dl = Vector2i(25, 19)
	game_room.corners.dr = Vector2i(30, 19)
	game_room.adjacent_rooms = ["bathroom", "living_room"]
	game_room.objects = {
		"" : null,
	}
	game_room.interactable_objects = {
		"" : null,
	}
	game_room.idle_positions = {}
	game_room.occupied_positions = {}
