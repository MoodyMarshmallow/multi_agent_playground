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
    ACTION_ALIASES = ["nap", "take nap"]

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
        if self.bed.get_property("cleanliness", 100) < 100:
            self.parser.fail("The bed is too dirty to sleep in.")
            return False
        return True

    def apply_effects(self):
        # Bed becomes unmade
        self.bed.set_property("is_made", False)
        # Increment player's sleep count
        sleep_count = self.character.get_property("sleep_count", 0) + 1
        self.character.set_property("sleep_count", sleep_count)
        # Every 3rd sleep, bed becomes unclean
        bed_became_unclean = False
        if sleep_count % 3 == 0:
            self.bed.set_property("cleanliness", 50)  # or another value < 100
            bed_became_unclean = True
        # Increase player's health, capped at 100
        health = self.character.get_property("health", 70)
        health = min(100, health + 10)
        self.character.set_property("health", health)
        # Build message
        msg = f"{self.character.name} sleeps peacefully in the bed. Health: {health}/100. Bed is now unmade."
        if bed_became_unclean:
            msg += " The bed is getting dirty."
        return self.parser.ok(msg)


class MakeBed(base.Action):
    ACTION_NAME = "make bed"
    ACTION_DESCRIPTION = "Make the bed."
    ACTION_ALIASES = ["tidy"]

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
    ACTION_ALIASES = ["wash"]

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
    ACTION_ALIASES = ["replace", "swap"]

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
        # Check if player has the quilt item
        inventory = getattr(self.character, 'inventory', {})
        quilt_item_name = f"{self.new_quilt} quilt"
        if quilt_item_name not in inventory:
            self.parser.fail(f"You don't have a {self.new_quilt} quilt.")
            return False
        current_color = self.bed.get_property("quilt_color")
        if current_color and self.new_quilt == current_color:
            self.parser.fail(f"The quilt is already {self.new_quilt}.")
            return False
        return True

    def apply_effects(self):
        # Remove the new quilt from inventory
        quilt_item_name = f"{self.new_quilt} quilt"
        new_quilt_item = self.character.inventory[quilt_item_name]
        del self.character.inventory[quilt_item_name]
        # Optionally, return the old quilt to the closet if present in the room
        current_color = self.bed.get_property("quilt_color")
        old_quilt_item = None
        if current_color:
            old_quilt_item_name = f"{current_color} quilt"
            old_quilt_item = Item(old_quilt_item_name, f"a {current_color} quilt", f"A soft, {current_color} quilt for the bed.")
            old_quilt_item.set_property("quilt_color", current_color)
            # Try to find a closet in the room
            location = getattr(self.character, 'location', None)
            closet = None
            if location and hasattr(location, 'inventory'):
                closet = location.inventory.get("closet")
            if closet:
                closet.add_item(old_quilt_item)
        # Set the bed's quilt color
        self.bed.set_property("quilt_color", self.new_quilt)
        return self.parser.ok(f"You change the quilt to {self.new_quilt}.")


class ExamineBed(base.Action):
    ACTION_NAME = "examine bed"
    ACTION_DESCRIPTION = "Examine the bed and see its state and hints."
    ACTION_ALIASES = ["inspect", "look over"]

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