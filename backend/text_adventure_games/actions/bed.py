from backend.text_adventure_games.actions import base
from backend.text_adventure_games.things import Item


def get_bed_legend():
    """
    Returns a legend string for interacting with the bed.
    """
    return (
        "Bed interaction legend:\n"
        "  sleep: Sleep in the bed.\n"
        "  make bed: Make the bed.\n"
        "  clean bed: Clean the bed.\n"
        "  change quilt to <color>: Change the quilt to a specified color.\n"
        "  (colors: red, blue, green, yellow, white, black)\n"
    )

class Sleep(base.Action):
    ACTION_NAME = "sleep"
    ACTION_DESCRIPTION = "Sleep in the bed."
    ACTION_ALIASES = ["nap"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.bed = self.parser.match_item("bed", self.parser.get_items_in_scope(self.character))

    def check_preconditions(self) -> bool:
        if not self.was_matched(self.bed, "There's no bed here."):
            return False
        if not self.bed.get_property("is_sleepable", False):
            self.parser.fail("You can't sleep on that.")
            return False
        return True

    def apply_effects(self):
        return self.parser.ok(f"{self.character.name} sleeps peacefully in the bed.")


class MakeBed(base.Action):
    ACTION_NAME = "make bed"
    ACTION_DESCRIPTION = "Make the bed."
    ACTION_ALIASES = ["tidy bed"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.bed = self.parser.match_item("bed", self.parser.get_items_in_scope(self.character))

    def check_preconditions(self) -> bool:
        if not self.was_matched(self.bed, "There's no bed here."):
            return False
        if self.bed.get_property("is_made", False):
            self.parser.fail("The bed is already made.")
            return False
        return True

    def apply_effects(self):
        self.bed.set_property("is_made", True)
        return self.parser.ok("You make the bed. It looks tidy now.")


class CleanBed(base.Action):
    ACTION_NAME = "clean bed"
    ACTION_DESCRIPTION = "Clean the bed."
    ACTION_ALIASES = ["wash bed"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.bed = self.parser.match_item("bed", self.parser.get_items_in_scope(self.character))

    def check_preconditions(self) -> bool:
        if not self.was_matched(self.bed, "There's no bed here."):
            return False
        cleanliness = self.bed.get_property("cleanliness", 100)
        if cleanliness >= 100:
            self.parser.fail("The bed is already clean.")
            return False
        return True

    def apply_effects(self):
        self.bed.set_property("cleanliness", 100)
        return self.parser.ok("You clean the bed. It's spotless now.")


class ChangeQuilt(base.Action):
    ACTION_NAME = "change quilt"
    ACTION_DESCRIPTION = "Change the quilt color on the bed."
    ACTION_ALIASES = ["replace quilt", "swap quilt", "change blanket"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.bed = self.parser.match_item("bed", self.parser.get_items_in_scope(self.character))
        # Use parser.split_command to extract color after 'to'
        before, after = self.parser.split_command(command, "to")
        self.new_quilt = after.strip() if after else None

    def check_preconditions(self) -> bool:
        if not self.was_matched(self.bed, "There's no bed here."):
            return False
        if not self.new_quilt:
            self.parser.fail("You must specify a color for the new quilt using 'change quilt to <color>'.")
            return False
        current_color = self.bed.get_property("quilt_color")
        if current_color and self.new_quilt == current_color:
            self.parser.fail(f"The quilt is already {self.new_quilt}.")
            return False
        return True

    def apply_effects(self):
        self.bed.set_property("quilt_color", self.new_quilt)
        return self.parser.ok(f"You change the quilt to {self.new_quilt}.")


class ExamineBed(base.Action):
    ACTION_NAME = "examine bed"
    ACTION_DESCRIPTION = "Examine the bed and see its state and hints."
    ACTION_ALIASES = ["look at bed", "x bed"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.bed = self.parser.match_item("bed", self.parser.get_items_in_scope(self.character))

    def check_preconditions(self) -> bool:
        if not self.was_matched(self.bed, "There's no bed here."):
            return False
        return True

    def apply_effects(self):
        desc = self.bed.examine_text or self.bed.description
        state = []
        if self.bed.get_property("is_made"):
            state.append("The bed is made.")
        else:
            state.append("The bed is unmade.")
        quilt = self.bed.get_property("quilt_color")
        if quilt:
            state.append(f"The quilt is {quilt}.")
        clean = self.bed.get_property("cleanliness")
        if clean is not None:
            state.append(f"Cleanliness: {clean}/100.")
        # Item hints
        hints = self.bed.get_command_hints()
        if hints:
            state.append("Hints: " + ", ".join(hints))
        return self.parser.ok(desc + "\n" + "\n".join(state)) 