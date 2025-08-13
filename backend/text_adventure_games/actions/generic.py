"""
Generic action classes that delegate to object capabilities.

These actions replace the 20+ specific action classes with a flexible system
where objects define their own behavior through capability protocols.
"""

from .base import Action, ActionResult
from ....config.schema import (
    SetToStateAction as SetToStateSchema, StartUsingAction as StartUsingSchema,
    StopUsingAction as StopUsingSchema, TakeAction as TakeSchema, DropAction as DropSchema,
    PlaceAction as PlaceSchema, ConsumeAction as ConsumeSchema, ExamineAction as ExamineSchema,
    GoToAction as GoToSchema, LookAction as LookSchema
)
from backend.text_adventure_games.capabilities import (
    Activatable, Openable, Lockable, Usable, Container, Consumable, Examinable, Recipient
)
import re


def remove_item_safely(location, item, new_owner):
    """Safely remove an item from a location or container."""
    if hasattr(location, 'inventory') and item.name in location.inventory:
        del location.inventory[item.name]
    elif hasattr(location, 'items') and item.name in location.items:
        del location.items[item.name]


class GenericSetToStateAction(Action):
    """Generic action for changing object states (on/off, open/close, lock/unlock)"""
    
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
        """Generate applicable target objects based on their capabilities"""
        location = character.location
        if not location:
            return []
        
        combinations = []
        for item_name, item in location.items.items():
            # Check if object has state-changing capabilities
            if (isinstance(item, (Activatable, Openable, Lockable)) or
                hasattr(item, 'get_object_capabilities')):
                combinations.append({"target": item_name})
        return combinations
    
    def __init__(self, game, command: str):
        super().__init__(game)
        self.command = command.lower().strip()
        self.character = self.parser.get_character(command)
        
        # Parse the command to extract target and state
        self.target = None
        self.target_name = ""
        self.state = ""
        
        # Simple command parsing
        if "turn on" in self.command or "switch on" in self.command:
            self.state = "on"
            pattern = r"(?:turn on|switch on)\s+(.+)"
        elif "turn off" in self.command or "switch off" in self.command:
            self.state = "off"
            pattern = r"(?:turn off|switch off)\s+(.+)"
        elif "open" in self.command:
            self.state = "open"
            pattern = r"open\s+(.+)"
        elif "close" in self.command:
            self.state = "close"
            pattern = r"close\s+(.+)"
        elif "lock" in self.command:
            self.state = "lock"
            pattern = r"lock\s+(.+)"
        elif "unlock" in self.command:
            self.state = "unlock"
            pattern = r"unlock\s+(.+)"
        else:
            return
        
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
        
        # Check if target has the required capability for this state
        if self.state in ["on", "off"]:
            if not isinstance(self.target, Activatable):
                self.parser.fail(f"The {self.target_name} cannot be turned on or off.")
                return False
        elif self.state in ["open", "close"]:
            if not isinstance(self.target, Openable):
                self.parser.fail(f"The {self.target_name} cannot be opened or closed.")
                return False
        elif self.state in ["lock", "unlock"]:
            if not isinstance(self.target, Lockable):
                self.parser.fail(f"The {self.target_name} cannot be locked or unlocked.")
                return False
        
        return True
    
    def apply_effects(self):
        try:
            # Delegate to the object's capability method
            result = None
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
            
            if result is None:
                raise ValueError(f"Unknown state: {self.state}")
            
            # Convert capability ActionResult to game ActionResult
            narration = self.parser.ok(result.description)
            schema = ActionResult(
                description=result.description,
                house_action=SetToStateSchema(action_type="set_to_state", target=self.target_name, state=self.state)
            )
            return narration, schema
            
        except Exception as e:
            error_msg = f"Failed to {self.state} the {self.target_name}: {str(e)}"
            narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)


class GenericStartUsingAction(Action):
    """Generic action for starting to use objects (beds, TVs, etc.)"""
    
    ACTION_NAME = "start_using"
    ACTION_DESCRIPTION = "Start using an object"
    COMMAND_PATTERNS = [
        "use {target}"
    ]
    
    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS
    
    @classmethod
    def get_applicable_combinations(cls, character, parser):
        """Generate applicable usable objects"""
        location = character.location
        if not location:
            return []
        
        combinations = []
        for item_name, item in location.items.items():
            if isinstance(item, Usable):
                combinations.append({"target": item_name})
        return combinations
    
    def __init__(self, game, command: str):
        super().__init__(game)
        self.command = command.lower().strip()
        self.character = self.parser.get_character(command)
        
        # Parse target from command
        self.target = None
        self.target_name = ""
        
        patterns = [r"use\s+(.+)", r"sleep on\s+(.+)", r"watch\s+(.+)", r"sit on\s+(.+)", 
                   r"play\s+(.+)", r"take bath in\s+(.+)"]
        for pattern in patterns:
            match = re.search(pattern, self.command)
            if match:
                self.target_name = match.group(1).strip()
                break
        
        # Find the target
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
            schema = ActionResult(
                description=result.description,
                house_action=StartUsingSchema(action_type="start_using", target=self.target_name)
            )
            return narration, schema
            
        except Exception as e:
            error_msg = f"Failed to use the {self.target_name}: {str(e)}"
            narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)


class GenericStopUsingAction(Action):
    """Generic action for stopping use of objects"""
    
    ACTION_NAME = "stop_using"
    ACTION_DESCRIPTION = "Stop using an object"
    COMMAND_PATTERNS = [
        "stop using {target}"
    ]
    
    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS
    
    @classmethod
    def get_applicable_combinations(cls, character, parser):
        """Generate objects character is currently using"""
        location = character.location
        if not location:
            return []
        
        combinations = []
        for item_name, item in location.items.items():
            if isinstance(item, Usable) and item.is_being_used_by(character):
                combinations.append({"target": item_name})
        return combinations
    
    def __init__(self, game, command: str):
        super().__init__(game)
        self.command = command.lower().strip()
        self.character = self.parser.get_character(command)
        
        # Parse target from command
        self.target = None
        self.target_name = ""
        
        patterns = [r"stop using\s+(.+)", r"get up from\s+(.+)", r"stop watching\s+(.+)",
                   r"get out of\s+(.+)", r"stop playing\s+(.+)"]
        for pattern in patterns:
            match = re.search(pattern, self.command)
            if match:
                self.target_name = match.group(1).strip()
                break
        
        # Find the target
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
            schema = ActionResult(
                description=result.description,
                house_action=StopUsingSchema(action_type="stop_using", target=self.target_name)
            )
            return narration, schema
            
        except Exception as e:
            error_msg = f"Failed to stop using the {self.target_name}: {str(e)}"
            narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)


class GenericTakeAction(Action):
    """Generic action for picking up items"""
    
    ACTION_NAME = "take"
    ACTION_DESCRIPTION = "Take an item"
    COMMAND_PATTERNS = [
        "take {target}"
    ]
    
    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS
    
    @classmethod
    def get_applicable_combinations(cls, character, parser):
        """Generate applicable items that can be taken"""
        location = character.location
        if not location:
            return []
        
        combinations = []
        for item_name, item in location.items.items():
            # Check if item can be taken (default to False for safety)
            if item.get_property("gettable", False):
                combinations.append({"target": item_name})
        return combinations
    
    def __init__(self, game, command: str):
        super().__init__(game)
        self.command = command.lower().strip()
        self.character = self.parser.get_character(command)
        
        # Parse target from command
        self.target = None
        self.target_name = ""
        
        # Simple parsing for take commands
        patterns = [r"take\s+(.+)", r"get\s+(.+)", r"pick up\s+(.+)", r"grab\s+(.+)"]
        for pattern in patterns:
            match = re.search(pattern, self.command)
            if match:
                self.target_name = match.group(1).strip()
                break
        
        # Find the target
        if self.target_name:
            location = self.character.location
            if location:
                # Look for item in location
                if self.target_name in location.items:
                    self.target = location.items[self.target_name]
                else:
                    # Look in containers
                    for item in location.items.values():
                        if hasattr(item, 'inventory') and self.target_name in item.inventory:
                            self.target = item.inventory[self.target_name]
                            break
    
    def check_preconditions(self) -> bool:
        if not self.target:
            self.parser.fail(f"You don't see a {self.target_name} here.")
            return False
        
        # Check if item can be taken (default to False for safety)
        if not self.target.get_property("gettable", False):
            self.parser.fail(f"You can't take the {self.target_name}.")
            return False
        
        return True
    
    def apply_effects(self):
        try:
            # Remove from current location/container
            if self.target is not None and self.target.location is not None:
                remove_item_safely(self.target.location, self.target, self.character)
            
            # Add to character inventory
            self.character.add_to_inventory(self.target)
            
            narration = self.parser.ok(f"You take the {self.target_name}.")
            schema = ActionResult(
                description=f"You take the {self.target_name}.",
                house_action=TakeSchema(action_type="take", target=self.target_name)
            )
            return narration, schema
            
        except Exception as e:
            error_msg = f"Failed to take the {self.target_name}: {str(e)}"
            narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)


class GenericDropAction(Action):
    """Generic action for dropping items from inventory"""
    
    ACTION_NAME = "drop"
    ACTION_DESCRIPTION = "Drop an item"
    COMMAND_PATTERNS = [
        "drop {target}"
    ]
    
    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS
    
    @classmethod
    def get_applicable_combinations(cls, character, parser):
        """Generate items in character's inventory"""
        combinations = []
        for item_name in character.inventory:
            combinations.append({"target": item_name})
        return combinations
    
    def __init__(self, game, command: str):
        super().__init__(game)
        self.command = command.lower().strip()
        self.character = self.parser.get_character(command)
        
        # Parse target from command
        self.target = None
        self.target_name = ""
        
        patterns = [r"drop\s+(.+)", r"put down\s+(.+)", r"leave\s+(.+)"]
        for pattern in patterns:
            match = re.search(pattern, self.command)
            if match:
                self.target_name = match.group(1).strip()
                break
        
        # Find the target in inventory
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
            
            # Remove from inventory and add to current location
            self.character.remove_from_inventory(self.target)
            location.add_item(self.target)
            
            narration = self.parser.ok(f"You drop the {self.target_name}.")
            schema = ActionResult(
                description=f"You drop the {self.target_name}.",
                house_action=DropSchema(action_type="drop", target=self.target_name)
            )
            return narration, schema
            
        except Exception as e:
            error_msg = f"Failed to drop the {self.target_name}: {str(e)}"
            narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)


class GenericPlaceAction(Action):
    """Generic action for placing items in containers or giving to characters"""
    
    ACTION_NAME = "place"
    ACTION_DESCRIPTION = "Place an item in/on something or give to someone"
    COMMAND_PATTERNS = [
        "put {target} in {recipient}"
    ]
    
    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS
    
    @classmethod
    def get_applicable_combinations(cls, character, parser):
        """Generate combinations of inventory items and recipients"""
        location = character.location
        if not location:
            return []
        
        combinations = []
        for item_name in character.inventory:
            # Find potential recipients (containers or characters)
            for recipient_name, recipient in location.items.items():
                if isinstance(recipient, (Container, Recipient)):
                    combinations.append({"target": item_name, "recipient": recipient_name})
            
            for recipient_name, recipient in location.characters.items():
                if recipient != character and isinstance(recipient, Recipient):
                    combinations.append({"target": item_name, "recipient": recipient_name})
        return combinations
    
    def __init__(self, game, command: str):
        super().__init__(game)
        self.command = command.lower().strip()
        self.character = self.parser.get_character(command)
        
        # Parse target and recipient from command
        self.target = None
        self.target_name = ""
        self.recipient = None
        self.recipient_name = ""
        
        patterns = [
            r"put\s+(.+?)\s+in\s+(.+)", r"place\s+(.+?)\s+in\s+(.+)",
            r"give\s+(.+?)\s+to\s+(.+)", r"put\s+(.+?)\s+on\s+(.+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, self.command)
            if match:
                self.target_name = match.group(1).strip()
                self.recipient_name = match.group(2).strip()
                break
        
        # Find target and recipient
        if self.target_name and self.target_name in self.character.inventory:
            self.target = self.character.inventory[self.target_name]
        
        if self.recipient_name:
            location = self.character.location
            if location:
                # Check for container/object recipients
                if self.recipient_name in location.items:
                    self.recipient = location.items[self.recipient_name]
                # Check for character recipients
                elif self.recipient_name in location.characters:
                    self.recipient = location.characters[self.recipient_name]
    
    def check_preconditions(self) -> bool:
        if not self.target:
            self.parser.fail(f"You don't have a {self.target_name}.")
            return False
        
        if not self.recipient:
            self.parser.fail(f"You don't see a {self.recipient_name} here.")
            return False
        
        # Check if recipient can receive items
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
            schema = ActionResult(
                description=result.description,
                house_action=PlaceSchema(action_type="place", target=self.target_name, recipient=self.recipient_name)
            )
            return narration, schema
            
        except Exception as e:
            error_msg = f"Failed to place the {self.target_name}: {str(e)}"
            narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)


class GenericConsumeAction(Action):
    """Generic action for consuming items (eating, drinking)"""
    
    ACTION_NAME = "consume"
    ACTION_DESCRIPTION = "Consume an item"
    COMMAND_PATTERNS = [
        "consume {target}"
    ]
    
    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS
    
    @classmethod
    def get_applicable_combinations(cls, character, parser):
        """Generate consumable items in inventory"""
        combinations = []
        for item_name, item in character.inventory.items():
            if isinstance(item, Consumable):
                combinations.append({"target": item_name})
        return combinations
    
    def __init__(self, game, command: str):
        super().__init__(game)
        self.command = command.lower().strip()
        self.character = self.parser.get_character(command)
        
        # Parse target from command
        self.target = None
        self.target_name = ""
        
        patterns = [r"eat\s+(.+)", r"drink\s+(.+)", r"consume\s+(.+)"]
        for pattern in patterns:
            match = re.search(pattern, self.command)
            if match:
                self.target_name = match.group(1).strip()
                break
        
        # Find the target in inventory
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
            schema = ActionResult(
                description=result.description,
                house_action=ConsumeSchema(action_type="consume", target=self.target_name)
            )
            return narration, schema
            
        except Exception as e:
            error_msg = f"Failed to consume the {self.target_name}: {str(e)}"
            narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)


class GenericExamineAction(Action):
    """Generic action for examining objects and items"""
    
    ACTION_NAME = "examine"
    ACTION_DESCRIPTION = "Examine something closely"
    COMMAND_PATTERNS = [
        "examine {target}"
    ]
    
    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS
    
    @classmethod
    def get_applicable_combinations(cls, character, parser):
        """Generate all examinable objects"""
        location = character.location
        if not location:
            return []
        
        combinations = []
        # Location items
        for item_name in location.items:
            combinations.append({"target": item_name})
        
        # Characters
        for char_name, char in location.characters.items():
            if char != character:  # Don't examine yourself
                combinations.append({"target": char_name})
        
        # Inventory items
        for item_name in character.inventory:
            combinations.append({"target": item_name})
        return combinations
    
    def __init__(self, game, command: str):
        super().__init__(game)
        self.command = command.lower().strip()
        self.character = self.parser.get_character(command)
        
        # Parse target from command
        self.target = None
        self.target_name = ""
        
        patterns = [r"examine\s+(.+)", r"look at\s+(.+)", r"inspect\s+(.+)", r"check\s+(.+)"]
        for pattern in patterns:
            match = re.search(pattern, self.command)
            if match:
                self.target_name = match.group(1).strip()
                break
        
        # Find the target
        if self.target_name:
            location = self.character.location
            if location:
                # Check location items
                if self.target_name in location.items:
                    self.target = location.items[self.target_name]
                # Check characters
                elif self.target_name in location.characters:
                    self.target = location.characters[self.target_name]
                # Check inventory
                elif self.target_name in self.character.inventory:
                    self.target = self.character.inventory[self.target_name]
    
    def check_preconditions(self) -> bool:
        if not self.target:
            self.parser.fail(f"You don't see a {self.target_name} here.")
            return False
        
        return True
    
    def apply_effects(self):
        try:
            # Ensure target exists (should be guaranteed by preconditions)
            if self.target is None:
                return self.parser.fail(f"You don't see a {self.target_name} here.")
            
            # Use object's examine capability if available, otherwise basic description
            if isinstance(self.target, Examinable):
                result = self.target.examine(self.character)
                description = result.description
            else:
                description = f"You examine the {self.target_name}. {getattr(self.target, 'description', 'Nothing special.')}"
            
            narration = self.parser.ok(description)
            schema = ActionResult(
                description=description,
                house_action=ExamineSchema(action_type="examine", target=self.target_name)
            )
            return narration, schema
            
        except Exception as e:
            error_msg = f"Failed to examine the {self.target_name}: {str(e)}"
            narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)


class MoveAction(Action):
    """Direction-based movement action"""
    
    ACTION_NAME = "move"
    ACTION_DESCRIPTION = "Move in a direction"
    COMMAND_PATTERNS = [
        "go {direction}"
    ]
    
    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS
    
    @classmethod
    def get_applicable_combinations(cls, character, parser):
        """Generate available directions from current location"""
        location = character.location
        if not location:
            return []
        
        combinations = []
        for direction in location.connections.keys():
            combinations.append({"direction": direction})
        return combinations
    
    def __init__(self, game, command: str):
        super().__init__(game)
        self.command = command.lower().strip()
        self.character = self.parser.get_character(command)
        
        # Parse direction from command using existing parser logic
        self.direction = None
        self.target_location = None
        
        current_location = self.character.location
        if current_location:
            # Use the existing get_direction method from parser
            self.direction = self.parser.get_direction(command, current_location)
            # Look up the target location from the connections
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
            
            # Move character to new location
            if old_location:
                old_location.remove_character(self.character)
            
            if self.target_location is not None:
                self.target_location.add_character(self.character)
                self.character.location = self.target_location
                location_name = self.target_location.name
            else:
                raise ValueError("Target location is None")
            
            narration = self.parser.ok(f"You go {self.direction} to the {location_name}.")
            # IMPORTANT: Schema passes the room name (not direction) to frontend
            schema = ActionResult(
                description=f"You go {self.direction} to the {location_name}.",
                house_action=GoToSchema(action_type="go_to", target=location_name)
            )
            return narration, schema
            
        except Exception as e:
            error_msg = f"Failed to go {self.direction}: {str(e)}"
            narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)


class EnhancedLookAction(Action):
    """Enhanced capability-aware look action that shows available object interactions"""
    
    ACTION_NAME = "look"
    ACTION_DESCRIPTION = "Refresh what you see around you"
    ACTION_ALIASES = ["l", "describe"]
    COMMAND_PATTERNS = ["look"]
    
    # Look actions are quick observations that don't end the agent's turn
    ends_turn = False
    
    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS
    
    @classmethod
    def get_applicable_combinations(cls, character, parser):
        """Look is always available"""
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
            
            # Get the world state exactly as the agent would receive it
            world_state = self.game.world_state_manager.get_world_state_for_agent(self.character)
            
            # Format it using the same method as agents receive
            full_description = self._format_world_state(world_state)
            
            narration = self.parser.ok(full_description)
            schema = ActionResult(
                description=full_description,
                house_action=LookSchema(action_type="look"),
                object_id=location.name
            )
            return narration, schema
            
        except Exception as e:
            error_msg = f"Failed to look around: {str(e)}"
            narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)
    
    def _format_world_state(self, state: dict) -> str:
        """Format world state into readable observation."""
        lines = []
        
        # Location
        location_info = state.get('location', {})
        lines.append(f"You are at: {location_info.get('name', 'Unknown Location')}")
        if location_info.get('description'):
            lines.append(location_info['description'])
        
        # Inventory
        inventory = state.get('inventory', [])
        if inventory:
            lines.append(f"\nYou are carrying: {', '.join(inventory)}")
        else:
            lines.append("\nYou are not carrying anything.")
        
        # Visible items
        visible_items = state.get('visible_items', [])
        if visible_items:
            lines.append("\nYou can see:")
            for item in visible_items:
                lines.append(f"  - {item.get('name', 'item')}: {item.get('description', 'an item')}")
        
        # Other characters
        visible_characters = state.get('visible_characters', [])
        if visible_characters:
            lines.append("\nOther characters here:")
            for char in visible_characters:
                char_line = f"  - {char.get('name', 'character')}: {char.get('description', 'a character')}"
                
                # Add chat availability indicator
                char_name = char.get('name')
                if char_name:
                    char_line += f" (You can chat with {char_name} using: chat_request {char_name} <your message>)"
                
                lines.append(char_line)
        
        # Available exits
        available_exits = state.get('available_exits', [])
        if available_exits:
            lines.append(f"\nAvailable exits: {', '.join(available_exits)}")
        
        # Available actions
        available_actions = state.get('available_actions', [])
        if available_actions:
            lines.append("\nAvailable actions:")
            for action in available_actions:
                lines.append(f"  - {action['command']}: {action.get('description', 'perform action')}")
        
        return '\n'.join(lines)


class GenericChatRequestAction(Action):
    """Send a chat request to another agent"""
    
    ACTION_NAME = "chat_request"
    ACTION_DESCRIPTION = "Send a chat request to another agent"
    COMMAND_PATTERNS = [
        "chat_request {recipient} {message}"
    ]
    ends_turn = True
    
    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS
    
    @classmethod
    def get_applicable_combinations(cls, character, parser):
        """Generate other characters in the same location"""
        location = character.location
        if not location:
            return []
        
        combinations = []
        # Find other characters in the room
        for char_name, char in parser.game.characters.items():
            if char.location == location and char.name != character.name:
                combinations.append({"recipient": char_name})
        return combinations
    
    def __init__(self, game, command: str):
        super().__init__(game)
        self.command = command.strip()
        self.character = self.parser.get_character(command)
        
        # Parse recipient and message from command
        self.recipient = None
        self.message = ""
        
        # Parse: chat_request <recipient> <message>
        parts = command.split(' ', 2)
        if len(parts) >= 3 and parts[0].lower() == "chat_request":
            recipient_name = parts[1]
            self.message = parts[2]
            
            # Find recipient character
            if recipient_name in self.game.characters:
                self.recipient = self.game.characters[recipient_name]
    
    def check_preconditions(self) -> bool:
        if not self.recipient:
            self.parser.fail("You need to specify a valid recipient.")
            return False
        
        if not self.message:
            self.parser.fail("You need to provide a message explaining why you want to chat.")
            return False
        
        # Check if recipient is in the same location
        if self.recipient.location != self.character.location:
            self.parser.fail(f"{self.recipient.name} is not here.")
            return False
        
        return True
    
    def apply_effects(self):
        try:
            # Access chat manager through game's agent manager
            if not hasattr(self.game, 'agent_manager') or not hasattr(self.game.agent_manager, 'chat_manager'):
                raise ValueError("Chat system not available")
            
            if not self.recipient:
                raise ValueError("No recipient specified")
            
            chat_manager = self.game.agent_manager.chat_manager
            
            # Send chat request
            request_id = chat_manager.send_chat_request(
                sender_id=self.character.name,
                recipient_id=self.recipient.name,
                message=self.message
            )
            
            description = f"You sent a chat request to {self.recipient.name}: '{self.message}'"
            narration = self.parser.ok(description)
            
            # Import ChatRequestAction schema
            from ....config.schema import ChatRequestAction as ChatRequestSchema
            
            schema = ActionResult(
                description=description,
                house_action=ChatRequestSchema(
                    action_type="chat_request",
                    recipient=self.recipient.name,
                    message=self.message
                )
            )
            return narration, schema
            
        except Exception as e:
            error_msg = f"Failed to send chat request: {str(e)}"
            narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)


class GenericChatResponseAction(Action):
    """Accept or reject a chat request"""
    
    ACTION_NAME = "chat_response"
    ACTION_DESCRIPTION = "Accept or reject a chat request"
    COMMAND_PATTERNS = [
        "chat_response {request_id} {response}"
    ]
    ends_turn = False  # This action does not end the turn
    
    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS
    
    @classmethod
    def get_applicable_combinations(cls, character, parser):
        """Generate pending chat requests for this character"""
        if not hasattr(parser.game, 'agent_manager') or not hasattr(parser.game.agent_manager, 'chat_manager'):
            return []
        
        chat_manager = parser.game.agent_manager.chat_manager
        pending_requests = chat_manager.get_pending_requests(character.name)
        
        combinations = []
        for request in pending_requests:
            combinations.append({
                "request_id": request.request_id,
                "response": "accept"
            })
            combinations.append({
                "request_id": request.request_id,
                "response": "reject"
            })
        return combinations
    
    def __init__(self, game, command: str):
        super().__init__(game)
        self.command = command.strip()
        self.character = self.parser.get_character(command)
        
        # Parse request_id and response from command
        self.request_id = ""
        self.accepted = False
        
        # Parse: chat_response <request_id> <accept/reject>
        parts = command.split(' ', 2)
        if len(parts) >= 3 and parts[0].lower() == "chat_response":
            self.request_id = parts[1]
            response = parts[2].lower()
            self.accepted = response in ["accept", "yes", "true"]
    
    def check_preconditions(self) -> bool:
        if not self.request_id:
            self.parser.fail("You need to specify a request ID.")
            return False
        
        # Check if chat manager exists
        if not hasattr(self.game, 'agent_manager') or not hasattr(self.game.agent_manager, 'chat_manager'):
            self.parser.fail("Chat system not available.")
            return False
        
        # Check if the request exists
        chat_manager = self.game.agent_manager.chat_manager
        request = chat_manager.get_request_by_id(self.request_id)
        if not request:
            self.parser.fail(f"No chat request found with ID: {self.request_id}")
            return False
        
        # Check if this agent is the recipient
        if request.recipient_id != self.character.name:
            self.parser.fail("You can only respond to your own chat requests.")
            return False
        
        return True
    
    def apply_effects(self):
        try:
            chat_manager = self.game.agent_manager.chat_manager
            
            # Respond to the request
            request = chat_manager.respond_to_request(
                agent_id=self.character.name,
                request_id=self.request_id,
                accepted=self.accepted
            )
            
            if not request:
                raise ValueError("Failed to respond to chat request")
            
            if self.accepted:
                description = f"You accepted the chat request from {request.sender_id}."
            else:
                description = f"You rejected the chat request from {request.sender_id}."
            
            narration = self.parser.ok(description)
            
            # Import ChatResponseAction schema
            from ....config.schema import ChatResponseAction as ChatResponseSchema
            
            schema = ActionResult(
                description=description,
                house_action=ChatResponseSchema(
                    action_type="chat_response",
                    request_id=self.request_id,
                    accepted=self.accepted
                )
            )
            return narration, schema
            
        except Exception as e:
            error_msg = f"Failed to respond to chat request: {str(e)}"
            narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)


class GenericChatAction(Action):
    """Send a chat message to another agent (only after accepting a chat request)"""
    
    ACTION_NAME = "chat"
    ACTION_DESCRIPTION = "Send a chat message to another agent"
    COMMAND_PATTERNS = [
        "chat {recipient} {message}"
    ]
    ends_turn = True  # Sending a message ends the turn
    
    @classmethod
    def get_command_patterns(cls):
        return cls.COMMAND_PATTERNS
    
    @classmethod
    def get_applicable_combinations(cls, character, parser):
        """Generate other characters this agent can chat with (in active conversation)"""
        if not hasattr(parser.game, 'agent_manager') or not hasattr(parser.game.agent_manager, 'chat_manager'):
            return []
        
        chat_manager = parser.game.agent_manager.chat_manager
        
        # Only allow chatting with conversation partner
        conversation_partner = chat_manager.get_conversation_partner(character.name)
        if conversation_partner:
            return [{"recipient": conversation_partner}]
        
        return []
    
    def __init__(self, game, command: str):
        super().__init__(game)
        self.command = command.strip()
        self.character = self.parser.get_character(command)
        
        # Parse recipient and message from command
        self.recipient = None
        self.message = ""
        
        # Parse: chat <recipient> <message>
        parts = command.split(' ', 2)
        if len(parts) >= 3 and parts[0].lower() == "chat":
            recipient_name = parts[1]
            self.message = parts[2]
            
            # Find recipient character
            if recipient_name in self.game.characters:
                self.recipient = self.game.characters[recipient_name]
    
    def check_preconditions(self) -> bool:
        if not self.recipient:
            self.parser.fail("You need to specify a valid recipient.")
            return False
        
        if not self.message:
            self.parser.fail("You need to provide a message.")
            return False
        
        # Check if recipient is in the same location
        if self.recipient.location != self.character.location:
            self.parser.fail(f"{self.recipient.name} is not here.")
            return False
        
        # Check if there's an active conversation
        if not hasattr(self.game, 'agent_manager') or not hasattr(self.game.agent_manager, 'chat_manager'):
            self.parser.fail("Chat system not available.")
            return False
        
        chat_manager = self.game.agent_manager.chat_manager
        conversation_partner = chat_manager.get_conversation_partner(self.character.name)
        
        if not conversation_partner:
            self.parser.fail("You need to have an accepted chat request before sending messages.")
            return False
        
        if conversation_partner != self.recipient.name:
            self.parser.fail(f"You can only chat with {conversation_partner} right now.")
            return False
        
        return True
    
    def apply_effects(self):
        try:
            if not self.recipient:
                raise ValueError("No recipient specified")
            
            chat_manager = self.game.agent_manager.chat_manager
            
            # End the conversation after sending message
            chat_manager.end_conversation(self.character.name)
            
            description = f"You sent a message to {self.recipient.name}: '{self.message}'"
            narration = self.parser.ok(description)
            
            # Import ChatAction schema
            from ....config.schema import ChatAction as ChatSchema
            
            # Create ChatAction for frontend consumption
            schema = ActionResult(
                description=description,
                house_action=ChatSchema(
                    action_type="chat",
                    sender=self.character.name,
                    recipient=self.recipient.name,
                    message=self.message
                )
            )
            
            # This ChatAction will be sent to the frontend event queue
            return narration, schema
            
        except Exception as e:
            error_msg = f"Failed to send chat message: {str(e)}"
            narration = self.parser.fail(error_msg)
            return narration, ActionResult(description=error_msg)