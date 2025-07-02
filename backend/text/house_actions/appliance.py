from text.text_adventure_games.actions import base

class TurnOnSink(base.Action):
    """Turn on the bathroom sink."""
    ACTION_NAME = "turn on sink"
    ACTION_DESCRIPTION = "Turn on the bathroom sink."
    ACTION_ALIASES = []

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.sink = self.parser.match_item("sink", self.parser.get_items_in_scope(self.character))

    def check_preconditions(self):
        return self.sink is not None and not self.sink.get_property("is_on")

    def apply_effects(self):
        self.sink.set_property("is_on", True)
        self.parser.ok("You turn on the sink. Water flows out.")


class TurnOffSink(base.Action):
    """Turn off the bathroom sink."""
    ACTION_NAME = "turn off sink"
    ACTION_DESCRIPTION = "Turn off the bathroom sink."
    ACTION_ALIASES = []

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.sink = self.parser.match_item("sink", self.parser.get_items_in_scope(self.character))

    def check_preconditions(self):
        return self.sink is not None and self.sink.get_property("is_on")

    def apply_effects(self):
        self.sink.set_property("is_on", False)
        self.parser.ok("You turn off the sink.")


class FillCup(base.Action):
    """Fill a cup with water from the sink. Uses the game.containers registry for the cup."""
    ACTION_NAME = "fill cup"
    ACTION_DESCRIPTION = "Fill a cup with water from the sink."
    ACTION_ALIASES = []

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.sink = self.parser.match_item("sink", self.parser.get_items_in_scope(self.character))
        # Use the cup from the sink's inventory via the containers registry
        containers = getattr(game, "containers", {})
        sink = containers.get("sink")
        if sink and hasattr(sink, "inventory"):
            self.cup = sink.inventory.get("cup")
        else:
            self.cup = None

    def check_preconditions(self):
        return self.sink is not None and self.sink.get_property("is_on") and self.cup is not None

    def apply_effects(self):
        self.character.add_to_inventory(self.cup)
        self.parser.ok("You fill the cup with water and take it.")


class FillBathtub(base.Action):
    """Fill the bathtub with water."""
    ACTION_NAME = "fill bathtub"
    ACTION_DESCRIPTION = "Fill the bathtub with water."
    ACTION_ALIASES = []

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.bathtub = self.parser.match_item("bathtub", self.parser.get_items_in_scope(self.character))

    def check_preconditions(self):
        return self.bathtub is not None and self.bathtub.get_property("volume") < 10

    def apply_effects(self):
        self.bathtub.set_property("volume", 10)
        self.parser.ok("You fill the bathtub with water.")


class UseWashingMachine(base.Action):
    """Use the washing machine."""
    ACTION_NAME = "use washing machine"
    ACTION_DESCRIPTION = "Use the washing machine."
    ACTION_ALIASES = []

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.machine = self.parser.match_item("washing machine", self.parser.get_items_in_scope(self.character))

    def check_preconditions(self):
        return self.machine is not None and self.character.location.name == "Laundry Room"

    def apply_effects(self):
        self.parser.ok("You start the washing machine. It hums quietly.") 