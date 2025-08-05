from backend.text_adventure_games.actions import base

class WatchTV(base.Action):
    """Watch TV in the living room."""
    ACTION_NAME = "watch tv"
    ACTION_DESCRIPTION = "Watch TV in the living room."
    ACTION_ALIASES = []

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.tv = self.parser.match_item("tv", self.parser.get_items_in_scope(self.character))

    def check_preconditions(self):
        return self.tv is not None and self.character.location.name == "Living Room"

    def apply_effects(self):
        self.parser.ok("You watch a fun show on TV and relax.")


class PlayPool(base.Action):
    """Play pool in the game room."""
    ACTION_NAME = "play pool"
    ACTION_DESCRIPTION = "Play pool in the game room."
    ACTION_ALIASES = []

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.pool_table = self.parser.match_item("pool table", self.parser.get_items_in_scope(self.character))

    def check_preconditions(self):
        return self.pool_table is not None and self.character.location.name == "Game Room"

    def apply_effects(self):
        self.parser.ok("You play a quick game of pool. Nice shot!")


class TakeBath(base.Action):
    """Take a bath in the bathroom."""
    ACTION_NAME = "take bath"
    ACTION_DESCRIPTION = "Take a bath in the bathroom."
    ACTION_ALIASES = []

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.bathtub = self.parser.match_item("bathtub", self.parser.get_items_in_scope(self.character))

    def check_preconditions(self):
        return self.bathtub is not None and self.character.location.name == "Bathroom"

    def apply_effects(self):
        self.parser.ok("You take a relaxing bath. You feel refreshed.")


class UseComputer(base.Action):
    """Use the computer in the bedroom."""
    ACTION_NAME = "use computer"
    ACTION_DESCRIPTION = "Use the computer in the bedroom."
    ACTION_ALIASES = []

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.computer = self.parser.match_item("computer", self.parser.get_items_in_scope(self.character))

    def check_preconditions(self):
        return self.computer is not None and self.character.location.name == "Bedroom"

    def apply_effects(self):
        self.parser.ok("You use the computer to check your messages and browse the web.") 