from backend.text_adventure_games.actions import base
from backend.text_adventure_games.things.containers import Container
from backend.config import schema

def match_container_in_scope(parser, command, character):
    items_in_scope = parser.get_items_in_scope(character)
    for item in items_in_scope.values():
        if getattr(item, 'get_property', None) and item.get_property("is_container", False):
            if item.name in command:
                return item
    return None

def match_item_in_container(container, command):
    for item in container.inventory.values():
        if item.name in command:
            return item
    return None

class OpenContainer(base.Action):
    ACTION_NAME = "open"
    ACTION_DESCRIPTION = "Open a container."
    ACTION_ALIASES = ["unseal", "unlock"]

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.container = match_container_in_scope(self.parser, command, self.character)

    def check_preconditions(self):
        if not self.container:
            self.parser.fail("You don't see any container to open.")
            return False
        if not self.container.get_property("is_openable", False):
            self.parser.fail(f"The {self.container.name} can't be opened.")
            return False
        if self.container.get_property("is_open", False):
            self.parser.fail(f"The {self.container.name} is already open.")
            return False
        if self.container.get_property("is_locked", False):
            self.parser.fail(f"The {self.container.name} is locked.")
            return False
        return True

    def apply_effects(self):
        self.container.set_property("is_open", True)
        items = self.container.list_items()
        if not items:
            narration = self.parser.ok(f"You open the {self.container.name}.\nThe {self.container.name} is empty.")
        else:
            narration = self.parser.ok(f"You open the {self.container.name}.\nInside the {self.container.name} you see:")
            for item in items:
                narration += f"\n * {item.description}"
        house_action = schema.OpenItemAction(action_type="open_item", target=self.container.name)
        schema_result = base.ActionResult(description=f"Opened {self.container.name}.", house_action=house_action, object_id=self.container.name)
        return narration, schema_result

class CloseContainer(base.Action):
    ACTION_NAME = "close"
    ACTION_DESCRIPTION = "Close a container."
    ACTION_ALIASES = ["seal", "shut"]

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.container = match_container_in_scope(self.parser, command, self.character)

    def check_preconditions(self):
        if not self.container:
            self.parser.fail("You don't see any container to close.")
            return False
        if not self.container.get_property("is_openable", False):
            self.parser.fail(f"The {self.container.name} can't be closed.")
            return False
        if not self.container.get_property("is_open", False):
            self.parser.fail(f"The {self.container.name} is already closed.")
            return False
        return True

    def apply_effects(self):
        self.container.set_property("is_open", False)
        narration = self.parser.ok(f"You close the {self.container.name}.")
        house_action = schema.CloseItemAction(action_type="close_item", target=self.container.name)
        schema_result = base.ActionResult(description=f"Closed {self.container.name}.", house_action=house_action, object_id=self.container.name)
        return narration, schema_result

class TakeFromContainer(base.Action):
    ACTION_NAME = "take"
    ACTION_DESCRIPTION = "Take an item from a container."
    ACTION_ALIASES = ["retrieve", "fetch", "get"]

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.container = match_container_in_scope(self.parser, command, self.character)
        self.target = match_item_in_container(self.container, command) if self.container else None

    def check_preconditions(self):
        if not self.container or not self.target:
            self.parser.fail("There is nothing to take from a container matching your command.")
            return False
        if not self.container.get_property("is_container", False):
            self.parser.fail(f"The {self.container.name} is not a container.")
            return False
        if self.container.get_property("is_openable", False) and not self.container.get_property("is_open", True):
            self.parser.fail(f"The {self.container.name} is closed.")
            return False
        return True

    def apply_effects(self):
        self.character.add_to_inventory(self.target)
        self.container.remove_item(self.target)
        narration = self.parser.ok(f"You take the {self.target.name} from the {self.container.name}.")
        house_action = schema.TakeFromContainerAction(action_type="take_from_container", item=self.target.name, container=self.container.name)
        schema_result = base.ActionResult(description=f"Took {self.target.name} from {self.container.name}.", house_action=house_action, object_id=self.target.name)
        return narration, schema_result

class ViewContainer(base.Action):
    ACTION_NAME = "view container"
    ACTION_DESCRIPTION = "View the contents of a container if it is open."
    ACTION_ALIASES = ["view"]

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.container = match_container_in_scope(self.parser, command, self.character)

    def check_preconditions(self):
        if not self.container:
            self.parser.fail("You don't see any container to view.")
            return False
        if self.container.get_property("is_openable", False) and not self.container.get_property("is_open", False):
            self.parser.fail(f"The {self.container.name} is closed.")
            return False
        return True

    def apply_effects(self):
        items = self.container.list_items()
        if not items:
            narration = self.parser.ok(f"The {self.container.name} is empty.")
        else:
            narration = self.parser.ok(f"Inside the {self.container.name} you see:")
            for item in items:
                narration += f"\n * {item.description}"
        schema_result = base.ActionResult(description=f"Viewed contents of {self.container.name}.", house_action=None, object_id=self.container.name)
        return narration, schema_result

class PutInContainer(base.Action):
    ACTION_NAME = "put in"
    ACTION_DESCRIPTION = "Put an item from inventory into a container."
    ACTION_ALIASES = ["put", "place", "insert"]

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.container = match_container_in_scope(self.parser, command, self.character)
        self.target = self.parser.match_item(command, self.character.inventory)

    def check_preconditions(self):
        if not self.container or not self.target:
            self.parser.fail("There is nothing to put in a container matching your command.")
            return False
        if not self.container.get_property("is_container", False):
            self.parser.fail(f"The {self.container.name} is not a container.")
            return False
        if self.container.get_property("is_openable", False) and not self.container.get_property("is_open", True):
            self.parser.fail(f"The {self.container.name} is closed.")
            return False
        if not self.character.is_in_inventory(self.target):
            self.parser.fail(f"You don't have the {self.target.name}.")
            return False
        return True

    def apply_effects(self):
        self.character.remove_from_inventory(self.target)
        self.container.add_item(self.target)
        narration = self.parser.ok(f"You put the {self.target.name} in the {self.container.name}.")
        schema_result = base.ActionResult(description=f"Put {self.target.name} in {self.container.name}.", house_action=None, object_id=self.target.name)
        return narration, schema_result