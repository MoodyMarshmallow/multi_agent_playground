"""
Generic action classes that delegate to object capabilities.

These actions replace the 20+ specific action classes with a flexible system
where objects define their own behavior through capability protocols.
"""

from .base import Action, ActionResult
from ...config.schema import (
    SetToStateAction as SetToStateSchema, StartUsingAction as StartUsingSchema,
    StopUsingAction as StopUsingSchema, TakeAction as TakeSchema, DropAction as DropSchema,
    PlaceAction as PlaceSchema, ConsumeAction as ConsumeSchema, ExamineAction as ExamineSchema,
    GoToAction as GoToSchema, LookAction as LookSchema
)
from backend.text_adventure_games.capabilities import (
    Activatable, Openable, Lockable, Usable, Container, Consumable, Examinable, Recipient
)
import re


class GenericSetToStateAction(Action):
    """Generic action for changing object states (on/off, open/close, lock/unlock)"""
    
    ACTION_NAME = "set_to_state"
    ACTION_DESCRIPTION = "Change an object's state"
    COMMAND_PATTERNS = [
        "turn on {target}", "turn off {target}", "switch on {target}", "switch off {target}",
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
                hasattr(item, 'get_available_actions')):
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
        "use {target}", "sleep on {target}", "watch {target}", "sit on {target}",
        "play {target}", "take bath in {target}"
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
        "stop using {target}", "get up from {target}", "stop watching {target}",
        "get out of {target}", "stop playing {target}"
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
        "take {target}", "get {target}", "pick up {target}", "grab {target}"
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
            # Check if item can be taken
            if item.get_property("gettable", True):
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
        
        # Check if item can be taken
        if not self.target.get_property("gettable", True):
            self.parser.fail(f"You can't take the {self.target_name}.")
            return False
        
        return True
    
    def apply_effects(self):
        try:
            # Remove from current location/container
            if self.target is not None and self.target.location is not None:
                self.target.location.remove_item(self.target)
            
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
        "drop {target}", "put down {target}", "leave {target}"
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
        "put {target} in {recipient}", "place {target} in {recipient}",
        "give {target} to {recipient}", "put {target} on {recipient}"
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
        "eat {target}", "drink {target}", "consume {target}"
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
        "examine {target}", "look at {target}", "inspect {target}", "check {target}"
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
        "go {direction}", "move {direction}", "walk {direction}", "travel {direction}",
        "{direction}", "n", "s", "e", "w", "north", "south", "east", "west"
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
    ACTION_DESCRIPTION = "Look around the current location"
    ACTION_ALIASES = ["l", "describe"]
    COMMAND_PATTERNS = ["look", "describe", "l"]
    
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
            
            # Start with basic location description
            description_parts = [f"**{location.name}**", location.description]
            
            # Show connections
            if location.connections:
                exits = list(location.connections.keys())
                exits_text = "Exits: " + ", ".join(exits)
                description_parts.append(exits_text)
            
            # Show objects with their available capabilities
            if location.items:
                objects_text = "\n**Objects here:**"
                for item in location.items.values():
                    item_desc = f"• {item.name}"
                    
                    # Add simple capability hints
                    hints = []
                    if isinstance(item, Activatable):
                        if hasattr(item, 'is_active'):
                            hints.append("turn on/off" if not item.is_active() else "turn off")
                        else:
                            hints.append("turn on/off")
                    if isinstance(item, Openable):
                        if hasattr(item, 'is_open'):
                            hints.append("open" if not item.is_open() else "close")
                        else:
                            hints.append("open/close")
                    if isinstance(item, Usable):
                        hints.append("use")
                    if isinstance(item, Examinable):
                        hints.append("examine")
                    
                    if hints:
                        item_desc += f" [{', '.join(hints)}]"
                    
                    objects_text += f"\n  {item_desc}"
                description_parts.append(objects_text)
            
            # Show characters
            if location.characters:
                other_characters = [char for char in location.characters.values() if char != self.character]
                if other_characters:
                    chars_text = "\n**Characters here:**"
                    for char in other_characters:
                        char_desc = f"• {char.name} - {char.description}"
                        chars_text += f"\n  {char_desc}"
                    description_parts.append(chars_text)
            
            # Show inventory
            if self.character.inventory:
                inv_text = "\n**You are carrying:**"
                for item in self.character.inventory.values():
                    inv_text += f"\n  • {item.name}"
                description_parts.append(inv_text)
            
            full_description = "\n\n".join(description_parts)
            
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