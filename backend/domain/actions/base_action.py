from typing import Optional, Any, List
from ..entities import Thing, Character, Item, Location
from config.schema import NoOpAction, LookAction

class ActionResult:
    def __init__(self, description: str, house_action: Optional[Any] = None, object_id: Optional[str] = None):
        if house_action is None:
            house_action = NoOpAction(action_type="noop", reason=description)
        self.description = description
        self.house_action = house_action
        self.object_id = object_id


class Action:
    """
    Base action class with precondition/effect interface and turn management.
    """

    ACTION_NAME: str
    ACTION_DESCRIPTION: str
    ACTION_ALIASES: List[str]
    COMMAND_PATTERNS: List[str]
    ends_turn: bool = True

    def __init__(self, game):
        self.game = game
        self.parser = game.parser

    def check_preconditions(self) -> bool:
        return False

    def apply_effects(self):
        narration = self.parser.ok("no effect")
        schema = ActionResult(description="no effect")
        return narration, schema

    def __call__(self):
        if self.check_preconditions():
            result = self.apply_effects()
            if not (isinstance(result, tuple) and len(result) == 2):
                narration = str(result)
                schema = ActionResult(description=narration)
                result = (narration, schema)
            self.game._last_action_result = result[1]
            return result
        else:
            narration = self.parser.last_error_message or "Action could not be performed."
            schema = ActionResult(description=narration)
            self.game._last_action_result = schema
            return narration, schema

    # Common preconditions and helpers
    def at(self, thing: Thing, location: Location, describe_error: bool = True) -> bool:
        if not location.here(thing):
            message = f"{thing.name.capitalize()} is not at {location.name}"
            if describe_error:
                self.parser.fail(message)
            return False
        return True

    def has_connection(self, location: Location, direction: str, describe_error: bool = True) -> bool:
        if direction not in location.connections:
            message = f"{location.name.capitalize()} does not have an exit '{direction}'"
            if describe_error:
                self.parser.fail(message)
            return False
        return True

    def is_blocked(self, location: Location, direction: str, describe_error: bool = True) -> bool:
        if location.is_blocked(direction):
            message = location.get_block_description(direction)
            if describe_error:
                self.parser.fail(message)
            return True
        return False

    def property_equals(self, thing: Thing, property_name: str, property_value: str, error_message: Optional[str] = None, display_message_upon: bool = False, describe_error: bool = True) -> bool:
        if thing.get_property(property_name) != property_value:
            if not display_message_upon:
                if not error_message:
                    error_message = f"{thing.name.capitalize()}'s {property_name} is not {property_value}"
                if describe_error:
                    self.parser.fail(error_message)
            return False
        else:
            if display_message_upon:
                if not error_message:
                    error_message = f"{thing.name.capitalize()}'s {property_name} is {property_value}"
                if describe_error:
                    self.parser.fail(error_message)
            return True

    def has_property(self, thing: Thing, property_name: str, error_message: Optional[str] = None, display_message_upon: bool = False, describe_error: bool = True) -> bool:
        if not thing.get_property(property_name):
            if not display_message_upon:
                if not error_message:
                    error_message = f"{thing.name.capitalize()} {property_name} is False"
                if describe_error:
                    self.parser.fail(error_message)
            return False
        else:
            if display_message_upon:
                if not error_message:
                    error_message = f"{thing.name.capitalize()} {property_name} is True"
                if describe_error:
                    self.parser.fail(error_message)
            return True

    def loc_has_item(self, location: Location, item: Item, describe_error: bool = True) -> bool:
        if item.name in location.items:
            return True
        message = f"{location.name} does not have {item.name}"
        if describe_error:
            self.parser.fail(message)
        return False

    def is_in_inventory(self, character: Character, item: Item, describe_error: bool = True) -> bool:
        if not character.is_in_inventory(item):
            message = f"{character.name.capitalize()} does not have {item.name}"
            if describe_error:
                self.parser.fail(message)
            return False
        return True

    def was_matched(self, thing: Thing, error_message: Optional[str] = None, describe_error: bool = True) -> bool:
        if thing is None:
            if not error_message:
                error_message = "Something was not matched by the self.parser."
            if describe_error:
                self.parser.fail(error_message)
            return False
        return True

    @classmethod
    def get_applicable_combinations(cls, character, parser):
        return []

    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS or []
