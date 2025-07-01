from text.text_adventure_games.actions import base


def match_first_item(parser, names, items_in_scope):
    for name in names:
        item = parser.match_item(name, items_in_scope)
        if item:
            return item
    return None


class OpenCloseItem(base.Action):
    """Open an openable item (drawer, cabinet, fridge, door)."""
    ACTION_NAME = "open"
    ACTION_DESCRIPTION = "Open an openable item."
    ACTION_ALIASES = ["open drawer", "open cabinet", "open fridge", "open door"]

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.target = match_first_item(
            self.parser,
            ["drawer", "cabinet", "fridge", "entry door"],
            self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self):
        return self.target is not None and not self.target.get_property("is_open")

    def apply_effects(self):
        self.target.set_property("is_open", True)
        self.parser.ok(f"You open the {self.target.name}.")


class CloseItem(base.Action):
    """Close a closable item (drawer, cabinet, fridge, door)."""
    ACTION_NAME = "close"
    ACTION_DESCRIPTION = "Close a closable item."
    ACTION_ALIASES = ["close drawer", "close cabinet", "close fridge", "close door"]

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.target = match_first_item(
            self.parser,
            ["drawer", "cabinet", "fridge", "entry door"],
            self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self):
        return self.target is not None and self.target.get_property("is_open")

    def apply_effects(self):
        self.target.set_property("is_open", False)
        self.parser.ok(f"You close the {self.target.name}.")


class TakeFromContainer(base.Action):
    """Take an item from a container (drawer, cabinet, fridge, bathtub). Uses a registry on the game object."""
    ACTION_NAME = "take"
    ACTION_DESCRIPTION = "Take an item from a container (drawer, cabinet, fridge, bathtub)."
    ACTION_ALIASES = [
        "take note", "take bandage", "take apple", "take sandwich",
        "take water bottle", "take rubber ducky"
    ]

    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.target = None
        self.container = None
        # Use a registry pattern: game.containers should be a dict of name:object
        containers = getattr(game, "containers", {})
        for container in containers.values():
            if hasattr(container, 'inventory'):
                for item in container.inventory.values():
                    if item.name in command:
                        self.target = item
                        self.container = container
                        break

    def check_preconditions(self):
        return (
            self.target is not None and self.container is not None and
            self.container.get_property("is_open", True)
            if hasattr(self.container, 'get_property') else True
        )

    def apply_effects(self):
        if self.target is None:
            self.parser.fail("There is nothing to take from a container matching your command.")
            return
        self.character.add_to_inventory(self.target)
        del self.container.inventory[self.target.name]
        self.parser.ok(f"You take the {self.target.name} from the {self.container.name}.") 