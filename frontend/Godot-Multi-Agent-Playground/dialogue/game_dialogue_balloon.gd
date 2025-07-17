extends BaseGameDialogueBalloon

@onready var emotes_panel: Panel = $Balloon/Panel/Dialogue/HBoxContainer/EmotesPanel

#showing dialogue is the show_line function under base_game_dialogue.gd

func start(dialogue_resource: DialogueResource, title: String, extra_game_states: Array = []) -> void:
	super.start(dialogue_resource, title, extra_game_states)
	emotes_panel.play_emote("idle_bob")
	
func next(next_id: String) -> void:
	super.next(next_id)
	emotes_panel.play_emote("idle_bob")
