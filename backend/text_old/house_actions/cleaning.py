from backend.text_adventure_games.actions import base

class CleanItem(base.Action):
    """Clean an item (bed, sink, table, plate, couch, garden tools, etc.)."""
    ACTION_NAME = "clean"
    ACTION_DESCRIPTION = "Clean an item to restore its cleanliness."
    ACTION_ALIASES = [
        "clean bed", "clean sink", "clean table", "clean plate", "clean couch", "clean garden tools",
        "clean bathtub", "clean oven", "clean fridge", "clean cabinets", "clean trash can", "clean lamp",
        "clean bookshelf", "clean game table", "clean grill", "clean mailbox", "clean laundry basket",
        "clean shower", "clean medicine cabinet", "clean toilet", "clean chair", "clean dining table",
        "clean board game", "clean remote control", "clean computer", "clean phone", "clean flashlight"
    ]

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        # Try to match any item in scope that matches the command
        self.target = None
        for item in self.parser.get_items_in_scope(self.character):
            if item.name in command or item.description.lower() in command.lower():
                self.target = item
                break

    def check_preconditions(self):
        if self.target is None:
            self.parser.fail("You don't see anything to clean.")
            return False
        if not self.target.get_property("is_cleanable", False):
            self.parser.fail(f"You can't clean the {self.target.name}.")
            return False
        cleanliness = self.target.get_property("cleanliness")
        if cleanliness is not None and cleanliness >= 100:
            self.parser.fail(f"The {self.target.name} is already clean.")
            return False
        if self.target.get_property("is_clean", False):
            self.parser.fail(f"The {self.target.name} is already clean.")
            return False
        return True

    def apply_effects(self):
        if self.target.get_property("cleanliness") is not None:
            self.target.set_property("cleanliness", 100)
        self.target.set_property("is_clean", True)
        self.parser.ok(f"You clean the {self.target.name}. It looks spotless now.") 