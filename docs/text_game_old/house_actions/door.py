from backend.text_adventure_games.actions import base
from backend.text_adventure_games.blocks.base import Block

class UnlockDoor(base.Action):
    """Unlock the entry door with a key."""
    ACTION_NAME = "unlock door"
    ACTION_DESCRIPTION = "Unlock the entry door with a key."
    ACTION_ALIASES = []

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.door = self.parser.match_item("entry door", self.parser.get_items_in_scope(self.character))
        self.key = self.parser.match_item("key", self.character.inventory.values())

    def check_preconditions(self):
        if self.door is None:
            self.parser.fail("You don't see a door to unlock.")
            return False
        if not self.door.get_property("is_locked", False):
            self.parser.fail("The door is already unlocked.")
            return False
        if self.key is None:
            self.parser.fail("You don't have the key to unlock the door.")
            return False
        return True

    def apply_effects(self):
        self.door.set_property("is_locked", False)
        self.parser.ok("You unlock the entry door with the key.")


class LockDoor(base.Action):
    """Lock the entry door with a key."""
    ACTION_NAME = "lock door"
    ACTION_DESCRIPTION = "Lock the entry door with a key."
    ACTION_ALIASES = []

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.door = self.parser.match_item("entry door", self.parser.get_items_in_scope(self.character))
        self.key = self.parser.match_item("key", self.character.inventory.values())

    def check_preconditions(self):
        if self.door is None:
            self.parser.fail("You don't see a door to lock.")
            return False
        if self.door.get_property("is_locked", False):
            self.parser.fail("The door is already locked.")
            return False
        if self.key is None:
            self.parser.fail("You don't have the key to lock the door.")
            return False
        return True

    def apply_effects(self):
        self.door.set_property("is_locked", True)
        self.parser.ok("You lock the entry door with the key.")


class EntryDoorBlock(Block):
    """Block movement if the entry door is closed or locked."""
    def __init__(self, door):
        super().__init__(name="Entry Door Block", description="The entry door is closed or locked.")
        self.door = door

    def is_blocked(self) -> bool:
        # Block if the door is not open or is locked
        return not self.door.get_property("is_open", False) or self.door.get_property("is_locked", False) 