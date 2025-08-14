# Domain actions - pure business logic without external schema dependencies
from .base_action import Action, ActionResult
from typing import Dict, Any, Optional
from dataclasses import dataclass


# Domain data structures - no external dependencies
@dataclass
class ActionData:
    """Pure domain data structure for action results."""
    action_type: str
    description: str
    success: bool = True
    target: Optional[str] = None
    location: Optional[str] = None
    agent_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
from ..services.world_state_formatter import format_world_state
from ..entities import Location
from ..entities.item import Item
from ..entities import Character
from ..value_objects.capabilities import (
    Activatable, Openable, Lockable, Usable, Container, Consumable, Examinable, Recipient
)

import re


def remove_item_safely(location, item, new_owner):
    if hasattr(location, 'inventory') and item.name in location.inventory:
        del location.inventory[item.name]
    elif hasattr(location, 'items') and item.name in location.items:
        del location.items[item.name]


class GenericSetToStateAction(Action):
    ACTION_NAME = "set_to_state"
    ACTION_DESCRIPTION = "Change an object's state"
    COMMAND_PATTERNS = [
        "switch on {target}", "switch off {target}",
        "open {target}", "close {target}", 
        "lock {target}", "unlock {target}"
    ]

    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS

    @classmethod
    def get_applicable_combinations(cls, character, parser):
        location = character.location
        if not location:
            return []
        combinations = []
        for item_name, item in location.items.items():
            if (isinstance(item, (Activatable, Openable, Lockable)) or hasattr(item, 'get_object_capabilities')):
                combinations.append({"target": item_name})
        return combinations

    def __init__(self, game, command: str):
        super().__init__(game)
        self.command = command.lower().strip()
        self.character = self.parser.get_character(command)
        self.target = None
        self.target_name = ""
        self.state = ""
        if "turn on" in self.command or "switch on" in self.command:
            self.state = "on"; pattern = r"(?:turn on|switch on)\s+(.+)"
        elif "turn off" in self.command or "switch off" in self.command:
            self.state = "off"; pattern = r"(?:turn off|switch off)\s+(.+)"
        elif "open" in self.command:
            self.state = "open"; pattern = r"open\s+(.+)"
        elif "close" in self.command:
            self.state = "close"; pattern = r"close\s+(.+)"
        elif "lock" in self.command:
            self.state = "lock"; pattern = r"lock\s+(.+)"
        elif "unlock" in self.command:
            self.state = "unlock"; pattern = r"unlock\s+(.+)"
        else:
            pattern = None
        if pattern:
            match = re.search(pattern, self.command)
            if match:
                self.target_name = match.group(1).strip()
                location = self.character.location
                if location and self.target_name in location.items:
                    self.target = location.items[self.target_name]

    def check_preconditions(self) -> bool:
        if not self.target:
            self.parser.fail(f"You don't see a {self.target_name} here.")
            return False
        if self.state in ["on", "off"] and not isinstance(self.target, Activatable):
            self.parser.fail(f"The {self.target_name} cannot be turned on or off.")
            return False
        if self.state in ["open", "close"] and not isinstance(self.target, Openable):
            self.parser.fail(f"The {self.target_name} cannot be opened or closed.")
            return False
        if self.state in ["lock", "unlock"] and not isinstance(self.target, Lockable):
            self.parser.fail(f"The {self.target_name} cannot be locked or unlocked.")
            return False
        return True

    def apply_effects(self):
        try:
            if self.target is None:
                raise ValueError("Target object is None")
            if self.state == "on":
                result = self.target.activate()
            elif self.state == "off":
                result = self.target.deactivate()
            elif self.state == "open":
                result = self.target.open()
            elif self.state == "close":
                result = self.target.close()
            elif self.state == "lock":
                result = self.target.lock()
            elif self.state == "unlock":
                result = self.target.unlock()
            else:
                raise ValueError(f"Unknown state: {self.state}")
            narration = self.parser.ok(result.description)
            schema = ActionResult(
                description=result.description,
                house_action=ActionData(action_type="set_to_state", description=result.description, target=self.target_name, metadata={"state": self.state})
            )
            return narration, schema
        except Exception as e:
            error_msg = f"Failed to {self.state} the {self.target_name}: {str(e)}"
            narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)


class GenericStartUsingAction(Action):
    ACTION_NAME = "start_using"
    ACTION_DESCRIPTION = "Start using an object"
    COMMAND_PATTERNS = ["use {target}"]

    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS

    @classmethod
    def get_applicable_combinations(cls, character, parser):
        location = character.location
        if not location:
            return []
        return [{"target": name} for name, item in location.items.items() if isinstance(item, Usable)]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.command = command.lower().strip()
        self.character = self.parser.get_character(command)
        self.target = None
        self.target_name = ""
        for pattern in [r"use\s+(.+)", r"sleep on\s+(.+)", r"watch\s+(.+)", r"sit on\s+(.+)", r"play\s+(.+)", r"take bath in\s+(.+)"]:
            match = re.search(pattern, self.command)
            if match:
                self.target_name = match.group(1).strip(); break
        if self.target_name:
            location = self.character.location
            if location and self.target_name in location.items:
                self.target = location.items[self.target_name]

    def check_preconditions(self) -> bool:
        if not self.target:
            self.parser.fail(f"You don't see a {self.target_name} here.")
            return False
        if not isinstance(self.target, Usable):
            self.parser.fail(f"You can't use the {self.target_name}.")
            return False
        return True

    def apply_effects(self):
        try:
            if self.target is None:
                raise ValueError("Target object is None")
            result = self.target.start_using(self.character)
            narration = self.parser.ok(result.description)
            schema = ActionResult(description=result.description, house_action=ActionData(action_type="start_using", description=result.description, target=self.target_name))
            return narration, schema
        except Exception as e:
            error_msg = f"Failed to use the {self.target_name}: {str(e)}"
            narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)


class GenericStopUsingAction(Action):
    ACTION_NAME = "stop_using"
    ACTION_DESCRIPTION = "Stop using an object"
    COMMAND_PATTERNS = ["stop using {target}"]

    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS

    @classmethod
    def get_applicable_combinations(cls, character, parser):
        location = character.location
        if not location:
            return []
        return [{"target": name} for name, item in location.items.items() if isinstance(item, Usable) and item.is_being_used_by(character)]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.command = command.lower().strip(); self.character = self.parser.get_character(command)
        self.target = None; self.target_name = ""
        for pattern in [r"stop using\s+(.+)", r"get up from\s+(.+)", r"stop watching\s+(.+)", r"get out of\s+(.+)", r"stop playing\s+(.+)"]:
            match = re.search(pattern, self.command)
            if match:
                self.target_name = match.group(1).strip(); break
        if self.target_name:
            location = self.character.location
            if location and self.target_name in location.items:
                self.target = location.items[self.target_name]

    def check_preconditions(self) -> bool:
        if not self.target:
            self.parser.fail(f"You don't see a {self.target_name} here.")
            return False
        if not isinstance(self.target, Usable):
            self.parser.fail(f"You can't use the {self.target_name}.")
            return False
        if not self.target.is_being_used_by(self.character):
            self.parser.fail(f"You're not using the {self.target_name}.")
            return False
        return True

    def apply_effects(self):
        try:
            if self.target is None:
                raise ValueError("Target object is None")
            result = self.target.stop_using(self.character)
            narration = self.parser.ok(result.description)
            schema = ActionResult(description=result.description, house_action=ActionData(action_type="stop_using", description=result.description, target=self.target_name))
            return narration, schema
        except Exception as e:
            error_msg = f"Failed to stop using the {self.target_name}: {str(e)}"
            narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)


class GenericTakeAction(Action):
    ACTION_NAME = "take"
    ACTION_DESCRIPTION = "Take an item"
    COMMAND_PATTERNS = ["take {target}"]

    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS

    @classmethod
    def get_applicable_combinations(cls, character, parser):
        location = character.location
        if not location:
            return []
        combinations = []
        for item_name, item in location.items.items():
            if item.get_property("gettable", False):
                combinations.append({"target": item_name})
        return combinations

    def __init__(self, game, command: str):
        super().__init__(game)
        self.command = command.lower().strip()
        self.character = self.parser.get_character(command)
        self.target = None
        self.target_name = ""
        for pattern in [r"take\s+(.+)", r"get\s+(.+)", r"pick up\s+(.+)", r"grab\s+(.+)"]:
            match = re.search(pattern, self.command)
            if match:
                self.target_name = match.group(1).strip(); break
        if self.target_name:
            location = self.character.location
            if location:
                if self.target_name in location.items:
                    self.target = location.items[self.target_name]
                else:
                    for item in location.items.values():
                        if hasattr(item, 'inventory') and self.target_name in item.inventory:
                            self.target = item.inventory[self.target_name]
                            break

    def check_preconditions(self) -> bool:
        if not self.target:
            self.parser.fail(f"You don't see a {self.target_name} here.")
            return False
        if not self.target.get_property("gettable", False):
            self.parser.fail(f"You can't take the {self.target_name}.")
            return False
        return True

    def apply_effects(self):
        try:
            if self.target is not None and self.target.location is not None:
                remove_item_safely(self.target.location, self.target, self.character)
            self.character.add_to_inventory(self.target)
            narration = self.parser.ok(f"You take the {self.target_name}.")
            schema = ActionResult(description=f"You take the {self.target_name}.", house_action=ActionData(action_type="take", description=f"You take the {self.target_name}.", target=self.target_name))
            return narration, schema
        except Exception as e:
            error_msg = f"Failed to take the {self.target_name}: {str(e)}"
            narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)


class GenericDropAction(Action):
    ACTION_NAME = "drop"
    ACTION_DESCRIPTION = "Drop an item"
    COMMAND_PATTERNS = ["drop {target}"]

    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS

    @classmethod
    def get_applicable_combinations(cls, character, parser):
        return [{"target": item_name} for item_name in character.inventory]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.command = command.lower().strip(); self.character = self.parser.get_character(command)
        self.target = None; self.target_name = ""
        for pattern in [r"drop\s+(.+)", r"put down\s+(.+)", r"leave\s+(.+)"]:
            match = re.search(pattern, self.command)
            if match:
                self.target_name = match.group(1).strip(); break
        if self.target_name and self.target_name in self.character.inventory:
            self.target = self.character.inventory[self.target_name]

    def check_preconditions(self) -> bool:
        if not self.target:
            self.parser.fail(f"You don't have a {self.target_name}.")
            return False
        return True

    def apply_effects(self):
        try:
            location = self.character.location
            self.character.remove_from_inventory(self.target)
            location.add_item(self.target)
            narration = self.parser.ok(f"You drop the {self.target_name}.")
            schema = ActionResult(description=f"You drop the {self.target_name}.", house_action=ActionData(action_type="drop", description=f"You drop the {self.target_name}.", target=self.target_name))
            return narration, schema
        except Exception as e:
            error_msg = f"Failed to drop the {self.target_name}: {str(e)}"
            narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)


class GenericPlaceAction(Action):
    ACTION_NAME = "place"
    ACTION_DESCRIPTION = "Place an item in/on something or give to someone"
    COMMAND_PATTERNS = ["put {target} in {recipient}"]

    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS

    @classmethod
    def get_applicable_combinations(cls, character, parser):
        location = character.location
        if not location:
            return []
        combinations = []
        for item_name in character.inventory:
            for recipient_name, recipient in location.items.items():
                if isinstance(recipient, (Container, Recipient)):
                    combinations.append({"target": item_name, "recipient": recipient_name})
            for recipient_name, recipient in location.characters.items():
                if recipient != character and isinstance(recipient, Recipient):
                    combinations.append({"target": item_name, "recipient": recipient_name})
        return combinations

    def __init__(self, game, command: str):
        super().__init__(game)
        self.command = command.lower().strip(); self.character = self.parser.get_character(command)
        self.target = None; self.target_name = ""; self.recipient = None; self.recipient_name = ""
        for pattern in [r"put\s+(.+?)\s+in\s+(.+)", r"place\s+(.+?)\s+in\s+(.+)", r"give\s+(.+?)\s+to\s+(.+)", r"put\s+(.+?)\s+on\s+(.+)"]:
            match = re.search(pattern, self.command)
            if match:
                self.target_name = match.group(1).strip(); self.recipient_name = match.group(2).strip(); break
        if self.target_name and self.target_name in self.character.inventory:
            self.target = self.character.inventory[self.target_name]
        if self.recipient_name:
            location = self.character.location
            if location:
                if self.recipient_name in location.items:
                    self.recipient = location.items[self.recipient_name]
                elif self.recipient_name in location.characters:
                    self.recipient = location.characters[self.recipient_name]

    def check_preconditions(self) -> bool:
        if not self.target:
            self.parser.fail(f"You don't have a {self.target_name}.")
            return False
        if not self.recipient:
            self.parser.fail(f"You don't see a {self.recipient_name} here.")
            return False
        if not isinstance(self.recipient, (Container, Recipient)):
            self.parser.fail(f"You can't put things in/on the {self.recipient_name}.")
            return False
        return True

    def apply_effects(self):
        try:
            if self.recipient is None:
                raise ValueError("Recipient is None")
            if hasattr(self.recipient, 'place_item'):
                result = self.recipient.place_item(self.target, self.character)
            else:
                result = self.recipient.receive_item(self.target, self.character)
            narration = self.parser.ok(result.description)
            schema = ActionResult(description=result.description, house_action=ActionData(action_type="place", description=result.description, target=self.target_name, metadata={"recipient": self.recipient_name}))
            return narration, schema
        except Exception as e:
            error_msg = f"Failed to place the {self.target_name}: {str(e)}"
            narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)


class GenericConsumeAction(Action):
    ACTION_NAME = "consume"
    ACTION_DESCRIPTION = "Consume an item"
    COMMAND_PATTERNS = ["consume {target}"]

    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS

    @classmethod
    def get_applicable_combinations(cls, character, parser):
        return [{"target": item_name} for item_name, item in character.inventory.items() if isinstance(item, Consumable)]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.command = command.lower().strip(); self.character = self.parser.get_character(command)
        self.target = None; self.target_name = ""
        for pattern in [r"eat\s+(.+)", r"drink\s+(.+)", r"consume\s+(.+)"]:
            match = re.search(pattern, self.command)
            if match:
                self.target_name = match.group(1).strip(); break
        if self.target_name and self.target_name in self.character.inventory:
            self.target = self.character.inventory[self.target_name]

    def check_preconditions(self) -> bool:
        if not self.target:
            self.parser.fail(f"You don't have a {self.target_name}.")
            return False
        if not isinstance(self.target, Consumable):
            self.parser.fail(f"You can't consume the {self.target_name}.")
            return False
        return True

    def apply_effects(self):
        try:
            if self.target is None:
                raise ValueError("Target object is None")
            result = self.target.consume(self.character)
            narration = self.parser.ok(result.description)
            schema = ActionResult(description=result.description, house_action=ActionData(action_type="consume", description=result.description, target=self.target_name))
            return narration, schema
        except Exception as e:
            error_msg = f"Failed to consume the {self.target_name}: {str(e)}"
            narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)


class GenericExamineAction(Action):
    ACTION_NAME = "examine"
    ACTION_DESCRIPTION = "Examine something closely"
    COMMAND_PATTERNS = ["examine {target}"]

    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS

    @classmethod
    def get_applicable_combinations(cls, character, parser):
        location = character.location
        if not location:
            return []
        combinations = []
        for item_name in location.items:
            combinations.append({"target": item_name})
        for char_name, char in location.characters.items():
            if char != character:
                combinations.append({"target": char_name})
        for item_name in character.inventory:
            combinations.append({"target": item_name})
        return combinations

    def __init__(self, game, command: str):
        super().__init__(game)
        self.command = command.lower().strip(); self.character = self.parser.get_character(command)
        self.target = None; self.target_name = ""
        for pattern in [r"examine\s+(.+)", r"look at\s+(.+)", r"inspect\s+(.+)", r"check\s+(.+)"]:
            match = re.search(pattern, self.command)
            if match:
                self.target_name = match.group(1).strip(); break
        if self.target_name:
            location = self.character.location
            if location:
                if self.target_name in location.items:
                    self.target = location.items[self.target_name]
                elif self.target_name in location.characters:
                    self.target = location.characters[self.target_name]
                elif self.target_name in self.character.inventory:
                    self.target = self.character.inventory[self.target_name]

    def check_preconditions(self) -> bool:
        if not self.target:
            self.parser.fail(f"You don't see a {self.target_name} here.")
            return False
        return True

    def apply_effects(self):
        try:
            if self.target is None:
                return self.parser.fail(f"You don't see a {self.target_name} here.")
            if isinstance(self.target, Examinable):
                result = self.target.examine(self.character)
                description = result.description
            else:
                description = f"You examine the {self.target_name}. {getattr(self.target, 'description', 'Nothing special.')}"
            narration = self.parser.ok(description)
            schema = ActionResult(description=description, house_action=ActionData(action_type="examine", description=description, target=self.target_name))
            return narration, schema
        except Exception as e:
            error_msg = f"Failed to examine the {self.target_name}: {str(e)}"
            narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)


class MoveAction(Action):
    ACTION_NAME = "move"
    ACTION_DESCRIPTION = "Move in a direction"
    COMMAND_PATTERNS = ["go {direction}"]

    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS

    @classmethod
    def get_applicable_combinations(cls, character, parser):
        location = character.location
        if not location:
            return []
        return [{"direction": direction} for direction in location.connections.keys()]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.command = command.lower().strip(); self.character = self.parser.get_character(command)
        self.direction = None; self.target_location = None
        current_location = self.character.location
        if current_location:
            self.direction = self.parser.get_direction(command, current_location)
            if self.direction and self.direction in current_location.connections:
                self.target_location = current_location.connections[self.direction]

    def check_preconditions(self) -> bool:
        if not self.direction:
            self.parser.fail(f"No valid direction found in command '{self.command}'")
            return False
        if not self.target_location:
            self.parser.fail(f"You can't go {self.direction} from here.")
            return False
        current_location = self.character.location
        if current_location and current_location.is_blocked(self.direction):
            self.parser.fail(f"The way {self.direction} is blocked.")
            return False
        return True

    def apply_effects(self):
        try:
            old_location = self.character.location
            if old_location:
                old_location.remove_character(self.character)
            if self.target_location is not None:
                self.target_location.add_character(self.character)
                self.character.location = self.target_location
                location_name = self.target_location.name
            else:
                raise ValueError("Target location is None")
            narration = self.parser.ok(f"You go {self.direction} to the {location_name}.")
            schema = ActionResult(description=f"You go {self.direction} to the {location_name}.", house_action=ActionData(action_type="go_to", description=f"You go {self.direction} to the {location_name}.", target=location_name, location=location_name, metadata={"direction": self.direction}))
            return narration, schema
        except Exception as e:
            error_msg = f"Failed to go {self.direction}: {str(e)}"
            narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)


class EnhancedLookAction(Action):
    ACTION_NAME = "look"
    ACTION_DESCRIPTION = "Refresh what you see around you"
    ACTION_ALIASES = ["l", "describe"]
    COMMAND_PATTERNS = ["look"]
    ends_turn = False

    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS

    @classmethod
    def get_applicable_combinations(cls, character, parser):
        return [{}]

    def __init__(self, game, command: str = ""):
        super().__init__(game)
        self.command = command
        self.character = self.parser.get_character(command) if command else game.player_character

    def check_preconditions(self) -> bool:
        return True

    def apply_effects(self):
        try:
            location = self.character.location
            if not location:
                narration = self.parser.fail("You are nowhere.")
                return narration, ActionResult(description="You are nowhere.")
            world_state = self.game.world_state_manager.get_world_state_for_agent(self.character)
            full_description = format_world_state(world_state)
            narration = self.parser.ok(full_description)
            schema = ActionResult(description=full_description, house_action=ActionData(action_type="look", description=full_description), object_id=location.name)
            return narration, schema
        except Exception as e:
            error_msg = f"Failed to look around: {str(e)}"
            narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)


class GenericChatRequestAction(Action):
    ACTION_NAME = "chat_request"
    ACTION_DESCRIPTION = "Send a chat request to another agent"
    COMMAND_PATTERNS = ["chat_request {recipient} {message}"]
    ends_turn = True

    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS

    @classmethod
    def get_applicable_combinations(cls, character, parser):
        location = character.location
        if not location:
            return []
        combinations = []
        for char_name, char in parser.game.characters.items():
            if char.location == location and char.name != character.name:
                combinations.append({"recipient": char_name})
        return combinations

    def __init__(self, game, command: str):
        super().__init__(game)
        self.command = command.strip(); self.character = self.parser.get_character(command)
        self.recipient = None; self.message = ""
        parts = command.split(' ', 2)
        if len(parts) >= 3 and parts[0].lower() == "chat_request":
            recipient_name = parts[1]; self.message = parts[2]
            if recipient_name in self.game.characters:
                self.recipient = self.game.characters[recipient_name]

    def check_preconditions(self) -> bool:
        if not self.recipient:
            self.parser.fail("You need to specify a valid recipient."); return False
        if not self.message:
            self.parser.fail("You need to provide a message explaining why you want to chat."); return False
        if self.recipient.location != self.character.location:
            self.parser.fail(f"{self.recipient.name} is not here."); return False
        return True

    def apply_effects(self):
        try:
            if not hasattr(self.game, 'agent_manager') or not hasattr(self.game.agent_manager, 'chat_manager'):
                raise ValueError("Chat system not available")
            if not self.recipient:
                raise ValueError("No recipient specified")
            chat_manager = self.game.agent_manager.chat_manager
            _ = chat_manager.send_chat_request(sender_id=self.character.name, recipient_id=self.recipient.name, message=self.message)
            description = f"You sent a chat request to {self.recipient.name}: '{self.message}'"
            narration = self.parser.ok(description)
            schema = ActionResult(description=description, house_action=ActionData(action_type="chat_request", description=description, metadata={"recipient": self.recipient.name, "message": self.message}))
            return narration, schema
        except Exception as e:
            error_msg = f"Failed to send chat request: {str(e)}"; narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)


class GenericChatResponseAction(Action):
    ACTION_NAME = "chat_response"
    ACTION_DESCRIPTION = "Accept or reject a chat request"
    COMMAND_PATTERNS = ["chat_response {request_id} {response}"]
    ends_turn = False

    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS

    @classmethod
    def get_applicable_combinations(cls, character, parser):
        if not hasattr(parser.game, 'agent_manager') or not hasattr(parser.game.agent_manager, 'chat_manager'):
            return []
        chat_manager = parser.game.agent_manager.chat_manager
        pending_requests = chat_manager.get_pending_requests(character.name)
        combinations = []
        for request in pending_requests:
            combinations.append({"request_id": request.request_id, "response": "accept"})
            combinations.append({"request_id": request.request_id, "response": "reject"})
        return combinations

    def __init__(self, game, command: str):
        super().__init__(game)
        self.command = command.strip(); self.character = self.parser.get_character(command)
        self.request_id = ""; self.accepted = False
        parts = command.split(' ', 2)
        if len(parts) >= 3 and parts[0].lower() == "chat_response":
            self.request_id = parts[1]; response = parts[2].lower(); self.accepted = response in ["accept", "yes", "true"]

    def check_preconditions(self) -> bool:
        if not self.request_id: self.parser.fail("You need to specify a request ID."); return False
        if not hasattr(self.game, 'agent_manager') or not hasattr(self.game.agent_manager, 'chat_manager'):
            self.parser.fail("Chat system not available."); return False
        chat_manager = self.game.agent_manager.chat_manager
        request = chat_manager.get_request_by_id(self.request_id)
        if not request:
            self.parser.fail(f"No chat request found with ID: {self.request_id}"); return False
        if request.recipient_id != self.character.name:
            self.parser.fail("You can only respond to your own chat requests."); return False
        return True

    def apply_effects(self):
        try:
            chat_manager = self.game.agent_manager.chat_manager
            request = chat_manager.respond_to_request(agent_id=self.character.name, request_id=self.request_id, accepted=self.accepted)
            if not request: raise ValueError("Failed to respond to chat request")
            description = f"You {'accepted' if self.accepted else 'rejected'} the chat request from {request.sender_id}."
            narration = self.parser.ok(description)
            schema = ActionResult(description=description, house_action=ActionData(action_type="chat_response", description=description, metadata={"request_id": self.request_id, "accepted": self.accepted}))
            return narration, schema
        except Exception as e:
            error_msg = f"Failed to respond to chat request: {str(e)}"; narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)


class GenericChatAction(Action):
    ACTION_NAME = "chat"
    ACTION_DESCRIPTION = "Send a chat message to another agent"
    COMMAND_PATTERNS = ["chat {recipient} {message}"]
    ends_turn = True

    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS

    @classmethod
    def get_applicable_combinations(cls, character, parser):
        if not hasattr(parser.game, 'agent_manager') or not hasattr(parser.game.agent_manager, 'chat_manager'):
            return []
        chat_manager = parser.game.agent_manager.chat_manager
        partner = chat_manager.get_conversation_partner(character.name)
        if partner:
            return [{"recipient": partner}]
        return []

    def __init__(self, game, command: str):
        super().__init__(game)
        self.command = command.strip(); self.character = self.parser.get_character(command)
        self.recipient = None; self.message = ""
        parts = command.split(' ', 2)
        if len(parts) >= 3 and parts[0].lower() == "chat":
            recipient_name = parts[1]; self.message = parts[2]
            if recipient_name in self.game.characters:
                self.recipient = self.game.characters[recipient_name]

    def check_preconditions(self) -> bool:
        if not self.recipient:
            self.parser.fail("You need to specify a valid recipient."); return False
        if not self.message:
            self.parser.fail("You need to provide a message."); return False
        if self.recipient.location != self.character.location:
            self.parser.fail(f"{self.recipient.name} is not here."); return False
        if not hasattr(self.game, 'agent_manager') or not hasattr(self.game.agent_manager, 'chat_manager'):
            self.parser.fail("Chat system not available."); return False
        chat_manager = self.game.agent_manager.chat_manager
        partner = chat_manager.get_conversation_partner(self.character.name)
        if not partner:
            self.parser.fail("You need to have an accepted chat request before sending messages."); return False
        if partner != self.recipient.name:
            self.parser.fail(f"You can only chat with {partner} right now."); return False
        return True

    def apply_effects(self):
        try:
            if not self.recipient: raise ValueError("No recipient specified")
            chat_manager = self.game.agent_manager.chat_manager
            chat_manager.end_conversation(self.character.name)
            description = f"You sent a message to {self.recipient.name}: '{self.message}'"
            narration = self.parser.ok(description)
            schema = ActionResult(description=description, house_action=ActionData(action_type="chat", description=description, metadata={"sender": self.character.name, "recipient": self.recipient.name, "message": self.message}))
            return narration, schema
        except Exception as e:
            error_msg = f"Failed to send chat message: {str(e)}"; narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)
