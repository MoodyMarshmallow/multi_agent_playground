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
    ACTION_DESCRIPTION = "Sleep in a bed."
    ACTION_ALIASES = ["nap", "rest"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.bed = self.parser.match_item(
            "bed", self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        """
        Preconditions:
        * There must be a bed here.
        * The bed must be clean.
        """
        if not self.was_matched(self.bed, "There's no bed here."):
            return False
        if not self.bed.get_property("is_clean", True):
            return self.parser.fail("The bed is too dirty to sleep in.")
        return True

    def apply_effects(self):
        """
        Effects:
        * The character sleeps in the bed.
        """
        return self.parser.ok(f"{self.character.name} sleeps peacefully in the bed.")


class MakeBed(base.Action):
    ACTION_NAME = "make bed"
    ACTION_DESCRIPTION = "Make the bed."
    ACTION_ALIASES = ["tidy bed", "straighten bed"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.bed = self.parser.match_item(
            "bed", self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        """
        Preconditions:
        * There must be a bed here.
        * The bed must not already be made.
        """
        if not self.was_matched(self.bed, "There's no bed here."):
            return False
        if self.bed.get_property("is_made", False):
            return self.parser.fail("The bed is already made.")
        return True

    def apply_effects(self):
        """
        Effects:
        * The bed is now made.
        """
        self.bed.set_property("is_made", True)
        return self.parser.ok(f"{self.character.name} makes the bed neatly.")


class CleanBed(base.Action):
    ACTION_NAME = "clean bed"
    ACTION_DESCRIPTION = "Clean the bed."
    ACTION_ALIASES = ["wash bed", "sanitize bed", "freshen bed"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.bed = self.parser.match_item(
            "bed", self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        """
        Preconditions:
        * There must be a bed here.
        * The bed must not already be clean.
        """
        if not self.was_matched(self.bed, "There's no bed here."):
            return False
        if self.bed.get_property("is_clean", True):
            return self.parser.fail("The bed is already clean.")
        return True

    def apply_effects(self):
        """
        Effects:
        * The bed is now clean.
        """
        self.bed.set_property("is_clean", True)
        return self.parser.ok(f"{self.character.name} cleans the bed thoroughly.")


class ChangeQuilt(base.Action):
    ACTION_NAME = "change quilt"
    ACTION_DESCRIPTION = "Change the quilt on the bed."
    ACTION_ALIASES = ["replace quilt", "swap quilt", "change blanket"]
    ALLOWED_COLORS = ["red", "blue", "green", "yellow", "white", "black"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.bed = self.parser.match_item(
            "bed", self.parser.get_items_in_scope(self.character)
        )
        self.new_quilt = None
        for color in self.ALLOWED_COLORS:
            if color in command:
                self.new_quilt = color
                break

    def check_preconditions(self) -> bool:
        """
        Preconditions:
        * There must be a bed here.
        * The bed must not be gettable.
        * A color must be specified for the new quilt.
        * The new quilt color must be different from the current one (if specified).
        """
        if not self.was_matched(self.bed, "There's no bed here."):
            return False
        if self.bed.get_property("gettable", False):
            return self.parser.fail("The bed cannot be picked up or moved.")
        if not self.new_quilt:
            return self.parser.fail(
                "Please specify a color for the new quilt (e.g., 'change quilt to yellow')."
            )
        if self.bed.get_property("quilt_color") == self.new_quilt:
            return self.parser.fail(f"The quilt is already {self.new_quilt}.")
        return True

    def apply_effects(self):
        """
        Effects:
        * The quilt color is changed (if specified).
        """
        self.bed.set_property("quilt_color", self.new_quilt)
        return self.parser.ok(f"{self.character.name} changes the quilt to {self.new_quilt}.")


class ExamineBed(base.Action):
    ACTION_NAME = "examine bed"
    ACTION_DESCRIPTION = "Examine the bed and its state."
    ACTION_ALIASES = ["look at bed", "x bed"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.bed = self.parser.match_item(
            "bed", self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        if not self.was_matched(self.bed, "There's no bed here."):
            return False
        return True

    def apply_effects(self):
        desc = self.bed.description
        cleanliness = self.bed.get_property("cleanliness", None)
        quilt_color = self.bed.get_property("quilt_color", None)
        is_made = self.bed.get_property("is_made", False)
        is_clean = self.bed.get_property("is_clean", True)
        details = []
        if cleanliness is not None:
            details.append(f"Cleanliness: {cleanliness}")
        if quilt_color:
            details.append(f"Quilt color: {quilt_color}")
        details.append(f"Made: {'yes' if is_made else 'no'}")
        details.append(f"Clean: {'yes' if is_clean else 'no'}")
        full_desc = desc
        if details:
            full_desc += "\n" + "\n".join(details)
        return self.parser.ok(full_desc) 