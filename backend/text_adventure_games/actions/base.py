from ..things import Thing, Character, Item, Location
from ...config.schema import NoOpAction, LookAction
from typing import Optional, Any, List

class ActionResult:
    def __init__(self, description: str, house_action: Optional[Any] = None, object_id: Optional[str] = None):
        if house_action is None:
            house_action = NoOpAction(action_type="noop", reason=description)
        self.description = description
        self.house_action = house_action
        self.object_id = object_id

class Action:
    """
    In the game, rather than allowing players to do anything, we have a
    specific set of Actions that can do.  The Action class that checks
    preconditions (the set of conditions that must be true in order for the
    action to have), and applies the effects of the action by updatin the state
    of the world.

    Different actions have different arguments, so we subclass Action to create
    new actions.

    Every action must implement two functions:
      * check_preconditions()
      * apply_effects()
    """

    ACTION_NAME: str
    ACTION_DESCRIPTION: str
    ACTION_ALIASES: List[str]
    COMMAND_PATTERNS: List[str]  # New: defines what commands this action can handle
    
    # Turn management - whether this action ends the agent's turn
    ends_turn: bool = True  # Default: all actions end turns for backward compatibility

    def __init__(self, game):
        self.game = game
        self.parser = game.parser

    def check_preconditions(self) -> bool:
        """
        Called before apply_effects to ensure the state for applying the
        action is valid
        """
        return False

    def apply_effects(self):
        """
        This method applies the action and changes the state of the game.
        Returns a (narration, schema) tuple.
        """
        narration = self.parser.ok("no effect")
        schema = ActionResult(description="no effect")
        return narration, schema

    def __call__(self):
        if self.check_preconditions():
            result = self.apply_effects()
            # If result is not a tuple, wrap it
            if not (isinstance(result, tuple) and len(result) == 2):
                narration = str(result)
                schema = ActionResult(description=narration)
                result = (narration, schema)
            # Store last action result in the game for schema export
            if hasattr(self.game, '_last_action_result'):
                self.game._last_action_result = result[1]
            else:
                self.game._last_action_result = result[1]
            return result
        else:
            # On precondition failure, return last error message as narration and schema
            narration = self.parser.last_error_message or "Action could not be performed."
            schema = ActionResult(description=narration)
            if hasattr(self.game, '_last_action_result'):
                self.game._last_action_result = schema
            else:
                self.game._last_action_result = schema
            return narration, schema


    ###
    # Preconditions - these functions are common preconditions.
    # They handle the error messages sent to the parser.
    ###

    def at(self, thing: Thing, location: Location, describe_error: bool = True) -> bool:
        """
        Checks if the thing is at the location.
        """
        # The character must be at the location
        if not location.here(thing):
            message = "{name} is not at {loc}".format(
                name=thing.name.capitalize(), loc=location.name
            )
            if describe_error:
                self.parser.fail(message)
            return False
        else:
            return True

    def has_connection(
        self, location: Location, direction: str, describe_error: bool = True
    ) -> bool:
        """
        Checks if the location has an exit in this direction.
        """
        if direction not in location.connections:  # JD logical change
            m = "{location_name} does not have an exit '{direction}'"
            message = m.format(
                location_name=location.name.capitalize(), direction=direction
            )
            if describe_error:
                self.parser.fail(message)
            return False
        else:
            return True

    def is_blocked(
        self, location: Location, direction: str, describe_error: bool = True
    ) -> bool:
        """
        Checks if the location blocked in this direction.
        """
        if location.is_blocked(direction):
            message = location.get_block_description(direction)
            if describe_error:
                self.parser.fail(message)
            return True
        else:
            return False

    def property_equals(
        self,
        thing: Thing,
        property_name: str,
        property_value: str,
        error_message: Optional[str] = None,
        display_message_upon: bool = False,
        describe_error: bool = True,
    ) -> bool:
        """
        Checks whether the thing has the specified property.
        """
        if thing.get_property(property_name) != property_value:
            if display_message_upon is False:
                if not error_message:
                    error_message = "{name}'s {property_name} is not {value}".format(
                        name=thing.name.capitalize(),
                        property_name=property_name,
                        value=property_value,
                    )
                if describe_error:
                    self.parser.fail(error_message)
            return False
        else:
            if display_message_upon is True:
                if not error_message:
                    error_message = "{name}'s {property_name} is {value}".format(
                        name=thing.name.capitalize(),
                        property_name=property_name,
                        value=property_value,
                    )
                if describe_error:
                    self.parser.fail(error_message)
            return True

    def has_property(
        self,
        thing: Thing,
        property_name: str,
        error_message: Optional[str] = None,
        display_message_upon: bool = False,
        describe_error: bool = True,
    ) -> bool:
        """
        Checks whether the thing has the specified property.
        """
        if not thing.get_property(property_name):
            if display_message_upon is False:
                if not error_message:
                    error_message = "{name} {property_name} is False".format(
                        name=thing.name.capitalize(), property_name=property_name
                    )
                if describe_error:
                    self.parser.fail(error_message)
            return False
        else:
            if display_message_upon is True:
                if not error_message:
                    error_message = "{name} {property_name} is True".format(
                        name=thing.name.capitalize(), property_name=property_name
                    )
                if describe_error:
                    self.parser.fail(error_message)
            return True

    def loc_has_item(
        self, location: Location, item: Item, describe_error: bool = True
    ) -> bool:
        """
        Checks to see if the location has the item.  Similar funcality to at, but
        checks for items that have multiple locations like doors.
        """
        if item.name in location.items:
            return True
        else:
            message = "{loc} does not have {item}".format(
                loc=location.name, item=item.name
            )
            if describe_error:
                self.parser.fail(message)
            return False

    def is_in_inventory(
        self, character: Character, item: Item, describe_error: bool = True
    ) -> bool:
        """
        Checks if the character has this item in their inventory.
        """
        if not character.is_in_inventory(item):
            message = "{name} does not have {item_name}".format(
                name=character.name.capitalize(), item_name=item.name
            )
            if describe_error:
                self.parser.fail(message)
            return False
        else:
            return True

    def was_matched(
        self,
        thing: Thing,
        error_message: Optional[str] = None,
        describe_error: bool = True,
    ) -> bool:
        """
        Checks to see if the thing was matched by the self.parser.
        """
        if thing is None:
            if not error_message:
                message = "Something was not matched by the self.parser."
            if describe_error:
                self.parser.fail(error_message)
            return False
        else:
            return True

    @classmethod
    def get_applicable_combinations(cls, character, parser):
        """
        Return all valid item/object combinations that this action could apply to.
        
        Args:
            character: The character who would perform the action
            parser: The game parser for accessing items in scope
            
        Yields:
            dict: Variable substitutions for command patterns (e.g., {"item": "apple"})
        """
        # Default implementation - subclasses should override for complex actions
        return []

    @classmethod
    def get_command_patterns(cls):
        """
        Return the command patterns this action can handle.
        
        Returns:
            list[str]: Command patterns with placeholders like "get {item}"
        """
        return cls.COMMAND_PATTERNS or []

    # === Helper methods for common action discovery patterns ===
    
    @classmethod
    def _get_all_items_in_scope(cls, character, parser):
        """Yield all items visible to character."""
        for item_name, item in parser.get_items_in_scope(character).items():
            yield {"item": item_name}

    @classmethod  
    def _get_items_with_property(cls, character, parser, property_name, default_value=False):
        """Yield items that have a specific property."""
        for item_name, item in parser.get_items_in_scope(character).items():
            if item.get_property(property_name, default_value):
                yield {"item": item_name}

    @classmethod
    def _get_location_items(cls, character):
        """Yield items in character's current location only."""
        for item_name, item in character.location.items.items():
            yield {"item": item_name}

    @classmethod
    def _get_inventory_items(cls, character):
        """Yield items in character's inventory."""
        for item_name, item in character.inventory.items():
            yield {"item": item_name}

    @classmethod
    def _get_other_characters(cls, character):
        """Yield other characters in the same location."""
        for char_name, char in character.location.characters.items():
            if char_name != character.name:
                yield {"character": char_name}

    @classmethod
    def _get_combinations(cls, character, parser, **param_specs):
        """
        General combination generator for N parameters.
        
        Args:
            character: Acting character
            parser: Game parser
            **param_specs: Parameter specifications, e.g.:
                item={"source": "inventory", "filter": lambda x: x.get_property("is_food")},
                character={"source": "location_characters", "exclude_self": True}
        
        Yields:
            dict: Parameter combinations like {"item": "apple", "character": "bob"}
        """
        from itertools import product
        
        # Collect all parameter values for each parameter
        param_values = {}
        
        for param_name, spec in param_specs.items():
            source = spec.get("source", "")
            param_filter = spec.get("filter", None)
            exclude_self = spec.get("exclude_self", False)
            
            values = []
            
            if source == "inventory":
                for item_name, item in character.inventory.items():
                    if not param_filter or param_filter(item):
                        values.append(item_name)
            elif source == "location_items":
                for item_name, item in character.location.items.items():
                    if not param_filter or param_filter(item):
                        values.append(item_name)
            elif source == "all_items_in_scope":
                for item_name, item in parser.get_items_in_scope(character).items():
                    if not param_filter or param_filter(item):
                        values.append(item_name)
            elif source == "location_characters":
                for char_name, char in character.location.characters.items():
                    if exclude_self and char_name == character.name:
                        continue
                    if not param_filter or param_filter(char):
                        values.append(char_name)
            elif source == "connected_locations":
                for direction, location in character.location.connections.items():
                    if not param_filter or param_filter(location):
                        values.append(location.name)
            
            param_values[param_name] = values
        
        # Generate all combinations using itertools.product
        if param_values:
            param_names = list(param_values.keys())
            value_lists = [param_values[name] for name in param_names]
            
            for combination in product(*value_lists):
                yield dict(zip(param_names, combination))


class ActionSequence(Action):
    """
    A container action that handles multiple commands entered as a single
    string of comma separated actions.

    Example: get pole, go out, south, catch fish with pole
    """
    ACTION_NAME = "sequence"
    ACTION_DESCRIPTION = "Complete a sequence of actions specified in a list"

    def __init__(
        self,
        game,
        command: str,
    ):
        super().__init__(game)
        self.command = command

    def check_preconditions(self) -> bool:
        return True

    def apply_effects(self):
        responses = []
        for cmd in self.command.split(","):
            cmd = cmd.strip()
            responses.append(self.parser.parse_command(cmd))
        narration = "; ".join(str(r[0]) for r in responses)
        schema = ActionResult(description="Sequence of actions executed.")
        return narration, schema


class Quit(Action):
    ACTION_NAME = "quit"
    ACTION_DESCRIPTION = "Quit the game"
    ACTION_ALIASES = ["q"]
    COMMAND_PATTERNS = ["quit"]

    def __init__(
        self,
        game,
        command: str,
    ):
        super().__init__(game)
        self.command = command

    def check_preconditions(self) -> bool:
        return True

    def apply_effects(self):
        if not self.game.game_over:
            self.game.game_over = True
            if not self.game.game_over_description:
                self.game.game_over_description = "The End"
            narration = self.parser.ok(self.game.game_over_description)
            schema = ActionResult(description="Game ended.")
            return narration, schema
        narration = self.parser.fail("Game already ended.")
        schema = ActionResult(description="Game already ended.")
        return narration, schema


class Look(Action):
    ACTION_NAME = "describe"
    ACTION_DESCRIPTION = "Describe the current location"
    ACTION_ALIASES = ["look", "l"]
    COMMAND_PATTERNS = ["describe", "look"]

    def __init__(
        self,
        game,
        command: str,
    ):
        super().__init__(game)
        self.command = command

    def check_preconditions(self) -> bool:
        return True

    def apply_effects(self):
        # Get basic location description
        base_description = self.game.description_manager.describe_full_location()
        
        # Get available actions from parser
        available_actions = self.parser.get_available_actions(self.game.player)
        
        # Create enhanced description with available actions
        enhanced_description = base_description
        if available_actions:
            enhanced_description += "\n\nAvailable actions:"
            for action in available_actions:
                enhanced_description += f"\n• {action['command']}: {action['description']}"
        
        narration = self.parser.ok(enhanced_description)
        look_action = LookAction(action_type="look")
        schema = ActionResult(
            description="Described current location.",
            house_action=look_action,
            object_id=self.game.player.location.name if self.game.player.location else None
        )
        return narration, schema
