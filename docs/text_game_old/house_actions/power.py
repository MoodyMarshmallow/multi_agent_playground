from backend.text_adventure_games.actions import base

class TurnOnItem(base.Action):
    """Turn on a switchable item (lamp, oven, TV, computer, etc.)."""
    ACTION_NAME = "turn on"
    ACTION_DESCRIPTION = "Turn on a switchable item."
    ACTION_ALIASES = [
        "turn on lamp", "turn on oven", "turn on tv", "turn on computer", "turn on microwave", "turn on toaster",
        "turn on coffee maker", "turn on grill", "turn on arcade machine", "turn on flashlight", "turn on washer", "turn on dryer"
    ]

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.target = None
        for item in self.parser.get_items_in_scope(self.character):
            if (item.name in command or item.description.lower() in command.lower()) and item.get_property("is_switchable", False):
                self.target = item
                break

    def check_preconditions(self):
        if self.target is None:
            self.parser.fail("You don't see anything to turn on.")
            return False
        if not self.target.get_property("is_switchable", False):
            self.parser.fail(f"The {self.target.name} can't be turned on.")
            return False
        if self.target.get_property("is_on", False):
            self.parser.fail(f"The {self.target.name} is already on.")
            return False
        if self.target.get_property("is_powered", True) is False:
            self.parser.fail(f"The {self.target.name} has no power.")
            return False
        return True

    def apply_effects(self):
        self.target.set_property("is_on", True)
        self.parser.ok(f"You turn on the {self.target.name}.")

class TurnOffItem(base.Action):
    """Turn off a switchable item (lamp, oven, TV, computer, etc.)."""
    ACTION_NAME = "turn off"
    ACTION_DESCRIPTION = "Turn off a switchable item."
    ACTION_ALIASES = [
        "turn off lamp", "turn off oven", "turn off tv", "turn off computer", "turn off microwave", "turn off toaster",
        "turn off coffee maker", "turn off grill", "turn off arcade machine", "turn off flashlight", "turn off washer", "turn off dryer"
    ]

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.target = None
        for item in self.parser.get_items_in_scope(self.character):
            if (item.name in command or item.description.lower() in command.lower()) and item.get_property("is_switchable", False):
                self.target = item
                break

    def check_preconditions(self):
        if self.target is None:
            self.parser.fail("You don't see anything to turn off.")
            return False
        if not self.target.get_property("is_switchable", False):
            self.parser.fail(f"The {self.target.name} can't be turned off.")
            return False
        if not self.target.get_property("is_on", False):
            self.parser.fail(f"The {self.target.name} is already off.")
            return False
        return True

    def apply_effects(self):
        self.target.set_property("is_on", False)
        self.parser.ok(f"You turn off the {self.target.name}.")

class SetTemperature(base.Action):
    """Set the temperature of an item (oven, fridge, grill, thermostat)."""
    ACTION_NAME = "set temperature"
    ACTION_DESCRIPTION = "Set the temperature of an item."
    ACTION_ALIASES = [
        "set oven temperature", "set fridge temperature", "set grill temperature", "set thermostat temperature"
    ]

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.target = None
        self.value = None
        for item in self.parser.get_items_in_scope(self.character):
            if (item.name in command or item.description.lower() in command.lower()) and item.get_property("temperature") is not None:
                self.target = item
                break
        import re
        match = re.search(r"(\d+)", command)
        if match:
            self.value = int(match.group(1))

    def check_preconditions(self):
        if self.target is None:
            self.parser.fail("You don't see anything whose temperature you can set.")
            return False
        if self.value is None:
            self.parser.fail("You must specify a temperature value.")
            return False
        if not self.target.get_property("is_switchable", False) and self.target.get_property("temperature") is None:
            self.parser.fail(f"The {self.target.name} can't have its temperature set.")
            return False
        return True

    def apply_effects(self):
        self.target.set_property("temperature", self.value)
        self.parser.ok(f"You set the temperature of the {self.target.name} to {self.value}.")

class AdjustBrightness(base.Action):
    """Adjust the brightness of a lamp."""
    ACTION_NAME = "adjust brightness"
    ACTION_DESCRIPTION = "Adjust the brightness of a lamp."
    ACTION_ALIASES = ["adjust lamp brightness", "set lamp brightness"]

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.target = None
        self.value = None
        for item in self.parser.get_items_in_scope(self.character):
            if "lamp" in item.name and item.get_property("brightness") is not None:
                self.target = item
                break
        import re
        match = re.search(r"(\d+)", command)
        if match:
            self.value = int(match.group(1))

    def check_preconditions(self):
        if self.target is None:
            self.parser.fail("You don't see a lamp to adjust.")
            return False
        if self.value is None:
            self.parser.fail("You must specify a brightness value.")
            return False
        if not self.target.get_property("is_switchable", False) and self.target.get_property("brightness") is None:
            self.parser.fail(f"The {self.target.name} can't have its brightness adjusted.")
            return False
        return True

    def apply_effects(self):
        self.target.set_property("brightness", self.value)
        self.parser.ok(f"You set the brightness of the {self.target.name} to {self.value}.")

class AdjustVolume(base.Action):
    """Adjust the volume of a TV or alarm clock."""
    ACTION_NAME = "adjust volume"
    ACTION_DESCRIPTION = "Adjust the volume of a device."
    ACTION_ALIASES = ["adjust tv volume", "set tv volume", "adjust alarm clock volume", "set alarm clock volume"]

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.target = None
        self.value = None
        for item in self.parser.get_items_in_scope(self.character):
            if (item.name in command or item.description.lower() in command.lower()) and item.get_property("volume") is not None:
                self.target = item
                break
        import re
        match = re.search(r"(\d+)", command)
        if match:
            self.value = int(match.group(1))

    def check_preconditions(self):
        if self.target is None:
            self.parser.fail("You don't see anything whose volume you can adjust.")
            return False
        if self.value is None:
            self.parser.fail("You must specify a volume value.")
            return False
        if not self.target.get_property("is_switchable", False) and self.target.get_property("volume") is None:
            self.parser.fail(f"The {self.target.name} can't have its volume adjusted.")
            return False
        return True

    def apply_effects(self):
        self.target.set_property("volume", self.value)
        self.parser.ok(f"You set the volume of the {self.target.name} to {self.value}.") 