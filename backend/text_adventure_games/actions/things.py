from . import base
from ...config.schema import TakeAction, DropAction


class Get(base.Action):
    ACTION_NAME = "get"
    ACTION_DESCRIPTION = "Get something and add it to the inventory"
    ACTION_ALIASES = ["take"]
    COMMAND_PATTERNS = ["get {item}"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.location = self.character.location
        self.item = self.parser.match_item(command, self.location.items)

    def check_preconditions(self) -> bool:
        """
        Preconditions:
        * The item must be matched.
        * The character must be at the location
        * The item must be at the location
        * The item must be gettable
        """
        if not self.was_matched(self.item, "I don't see it."):
            message = "I don't see it."
            self.parser.fail(message)
            return False
        if not self.location.here(self.character):
            message = "{name} is not here.".format(name=self.character.name)
            self.parser.fail(message)
            return False
        if not self.location.here(self.item):
            message = "There is no {name} here.".format(name=self.item.name)
            self.parser.fail(message)
            return False
        if not self.item.get_property("gettable"):
            error_message = "{name} is not {property_name}.".format(
                name=self.item.name.capitalize(), property_name="gettable"
            )
            self.parser.fail(error_message)
            return False
        return True

    def apply_effects(self):
        """
        Get's an item from the location and adds it to the character's
        inventory, assuming preconditions are met.
        """
        self.location.remove_item(self.item)
        self.character.add_to_inventory(self.item)
        description = "{character_name} got the {item_name}.".format(
            character_name=self.character.name, item_name=self.item.name
        )
        narration = self.parser.ok(description)
        get_action = TakeAction(action_type="take", target=self.item.name)
        schema = base.ActionResult(
            description=f"Got {self.item.name}.",
            house_action=get_action,
            object_id=self.item.name
        )
        return narration, schema

    @classmethod
    def get_applicable_combinations(cls, character, parser):
        """Return items that could potentially be gotten."""
        return list(cls._get_location_items(character))


class Drop(base.Action):
    ACTION_NAME = "drop"
    ACTION_DESCRIPTION = "Drop something from the character's inventory"
    ACTION_ALIASES = ["toss", "get rid of"]
    COMMAND_PATTERNS = ["drop {item}"]

    def __init__(
        self,
        game,
        command: str,
    ):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.location = self.character.location
        self.item = self.parser.match_item(command, self.character.inventory)

    def check_preconditions(self) -> bool:
        """
        Preconditions:
        * The item must be in the character's inventory
        """
        if not self.was_matched(self.item, "I don't see it."):
            return False
        if not self.character.is_in_inventory(self.item):
            d = "{character_name} does not have the {item_name}."
            description = d.format(
                character_name=self.character.name, item_name=self.item.name
            )
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        """
        Drop removes an item from character's inventory and adds it to the
        current location, assuming preconditions are met
        """
        self.character.remove_from_inventory(self.item)
        self.item.location = self.location
        self.location.add_item(self.item)
        d = "{character_name} dropped the {item_name} in the {location}."
        description = d.format(
            character_name=self.character.name.capitalize(),
            item_name=self.item.name,
            location=self.location.name,
        )
        narration = self.parser.ok(description)
        drop_action = DropAction(action_type="drop", target=self.item.name)
        schema = base.ActionResult(
            description=f"Dropped {self.item.name}.",
            house_action=drop_action,
            object_id=self.item.name
        )
        return narration, schema

    @classmethod
    def get_applicable_combinations(cls, character, parser):
        """Return items that could potentially be dropped."""
        return list(cls._get_inventory_items(character))


class Inventory(base.Action):
    ACTION_NAME = "inventory"
    ACTION_DESCRIPTION = "Check the character's inventory"
    ACTION_ALIASES = ["i"]
    COMMAND_PATTERNS = ["inventory"]

    def __init__(
        self,
        game,
        command: str,
    ):
        super().__init__(game)
        self.character = self.parser.get_character(command)

    def check_preconditions(self) -> bool:
        if self.character is None:
            return False
        return True

    def apply_effects(self):
        if len(self.character.inventory) == 0:
            description = f"{self.character.name}'s inventory is empty."
            return self.parser.ok(description)
        else:
            description = "In your inventory, you have:\n"
            for item_name in self.character.inventory:
                item = self.character.inventory[item_name]
                description += f"* {item_name} - {item.description}\n"
                hints = item.get_command_hints() if hasattr(item, 'get_command_hints') else []
                for cmd in hints:
                    description += f"\t{cmd}\n"
            return self.parser.ok(description)


class Examine(base.Action):
    ACTION_NAME = "examine"
    ACTION_DESCRIPTION = "Examine an item"
    ACTION_ALIASES = ["look at", "x"]
    COMMAND_PATTERNS = ["examine {item}"]

    def __init__(
        self,
        game,
        command: str,
    ):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.matched_item = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        if self.character is None:
            return False
        return True

    def apply_effects(self):
        """The player wants to examine an item"""
        if self.matched_item:
            desc = self.matched_item.examine_text or self.matched_item.description
            description = f"* {desc}"
            hints = self.matched_item.get_command_hints() if hasattr(self.matched_item, 'get_command_hints') else []
            for cmd in hints:
                description += f"\n\t{cmd}"
            return self.parser.ok(description)
        else:
            return self.parser.ok("You don't see anything special.")

    @classmethod
    def get_applicable_combinations(cls, character, parser):
        """Return items that could potentially be examined."""
        return list(cls._get_all_items_in_scope(character, parser))


class Give(base.Action):
    ACTION_NAME = "give"
    ACTION_DESCRIPTION = "Give something to someone"
    ACTION_ALIASES = ["hand"]
    COMMAND_PATTERNS = ["give {item} to {character}"]

    def __init__(self, game, command: str):
        super().__init__(game)
        give_words = ["give", "hand"]
        command_before_word = ""
        command_after_word = command
        parts = None
        for word in give_words:
            if word in command:
                parts = command.split(word, 1)
                command_before_word = parts[0]
                command_after_word = parts[1]
                break
        self.giver = self.parser.get_character(command_before_word)
        self.recipient = self.parser.get_character(command_after_word)
        self.item = self.parser.match_item(command, self.giver.inventory)

    def check_preconditions(self) -> bool:
        """
        Preconditions:
        * The item must be in the giver's inventory
        * The character must be at the same location as the recipient
        """
        if not self.was_matched(self.item, "I don't see it."):
            return False
        if not self.giver.is_in_inventory(self.item):
            return False
        if not self.giver.location.here(self.recipient):
            return False
        return True

    def apply_effects(self):
        """
        Give removes an item from giver's inventory and adds it to the
        recipient's inventory. (Assumes that the preconditions are met.)
        """
        self.giver.remove_from_inventory(self.item)
        self.recipient.add_to_inventory(self.item)
        description = "{giver} gave the {item_name} to {recipient}".format(
            giver=self.giver.name.capitalize(),
            item_name=self.item.name,
            recipient=self.recipient.name.capitalize(),
        )
        narration = self.parser.ok(description)
        schema = base.ActionResult(description=description)
        return narration, schema

    @classmethod
    def get_applicable_combinations(cls, character, parser):
        """Return item and character combinations for giving."""
        return list(cls._get_combinations(
            character, parser,
            item={"source": "inventory"},
            recipient={"source": "location_characters", "exclude_self": True}
        ))


class Unlock_Door(base.Action):
    ACTION_NAME = "unlock door"
    ACTION_DESCRIPTION = "Unlock a door"

    def __init__(self, game, command):
        super().__init__(game)
        self.command = command
        self.character = self.parser.get_character(command)
        self.key = self.parser.match_item(
            "key", self.parser.get_items_in_scope(self.character)
        )
        self.door = self.parser.match_item(
            "door", self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        if self.door and self.door.get_property("is_locked") and self.key:
            return True
        else:
            return False

    def apply_effects(self):
        self.door.set_property("is_locked", False)
        narration = self.parser.ok("Door is unlocked")
        schema = base.ActionResult(description="Door is unlocked")
        return narration, schema
