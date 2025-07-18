class InteractiveObject:
    """
    Base class for all interactive objects in the house simulation.
    """
    def __init__(self, object_id, object_type, state):
        self.object_id = object_id
        self.object_type = object_type
        self.state = state
        self.allowed_states = []
        
    def can_transition(self, new_state):
        """
        Checks if a new state transition is valid and not redundant.
        """
        return new_state in self.allowed_states and new_state != self.state

    def transition(self, new_state):
        """
        Performs the state transition if valid.
        """
        if self.can_transition(new_state):
            self.state = new_state
            return True
        return False

    def to_dict(self):
        """
        Returns a dictionary representation for serialization.
        """
        return {
            "id": self.object_id,
            "type": self.object_type,
            "state": self.state
        }

# ----------------------------------------
# Subclasses for Specific Object Types
# ----------------------------------------

class Door(InteractiveObject):
    """
    Example items: bedroom door, front door, closet door.
    States: open, closed, locked.
    """
    def __init__(self, object_id, state="closed"):
        super().__init__(object_id, "door", state)
        self.allowed_states = ["open", "closed", "locked"]
        self.is_locked = (state == "locked")

class Container(InteractiveObject):
    """
    Example items: box, cabinet, drawer, fridge, oven, washing machine.
    States: open, closed.
    """
    def __init__(self, object_id, state="closed"):
        super().__init__(object_id, "container", state)
        self.allowed_states = ["open", "closed"]
        self.contents = []  # Items inside the container

class Appliance(InteractiveObject):
    """
    Example items: TV, radio, microwave, dishwasher, washing machine, fan.
    States: on, off, broken.
    """
    def __init__(self, object_id, state="off"):
        super().__init__(object_id, "appliance", state)
        self.allowed_states = ["on", "off", "broken"]

class Switch(InteractiveObject):
    """
    Example items: wall switch, remote control button, push button.
    States: on, off, pressed, released.
    """
    def __init__(self, object_id, state="off"):
        super().__init__(object_id, "switch", state)
        self.allowed_states = ["on", "off", "pressed", "released"]

class Light(InteractiveObject):
    """
    Example items: lamp, ceiling light, LED strip.
    States: on, off, broken.
    """
    def __init__(self, object_id, state="off"):
        super().__init__(object_id, "light", state)
        self.allowed_states = ["on", "off", "broken"]

class Window(InteractiveObject):
    """
    Example items: living room window, bathroom window.
    States: open, closed, locked.
    """
    def __init__(self, object_id, state="closed"):
        super().__init__(object_id, "window", state)
        self.allowed_states = ["open", "closed", "locked"]
        self.is_locked = (state == "locked")

class Furniture(InteractiveObject):
    """
    Example items: bed, chair, couch, table, desk.
    States: vacant, occupied (optional, or N/A for non-interactive).
    """
    def __init__(self, object_id, state="vacant"):
        super().__init__(object_id, "furniture", state)
        self.allowed_states = ["vacant", "occupied"]

class Consumable(InteractiveObject):
    """
    Example items: food (apple, bread), drink (water, coffee), battery.
    States: whole, used, empty.
    """
    def __init__(self, object_id, state="whole"):
        super().__init__(object_id, "consumable", state)
        self.allowed_states = ["whole", "used", "empty"]

class Plant(InteractiveObject):
    """
    Example items: houseplant, garden flower.
    States: healthy, wilted, dead, watered.
    """
    def __init__(self, object_id, state="healthy"):
        super().__init__(object_id, "plant", state)
        self.allowed_states = ["healthy", "wilted", "dead", "watered"]

class Book(InteractiveObject):
    """
    Example items: novel, textbook, magazine.
    States: open, closed.
    """
    def __init__(self, object_id, state="closed"):
        super().__init__(object_id, "book", state)
        self.allowed_states = ["open", "closed"]

class Key(InteractiveObject):
    """
    Example items: front door key, safe key.
    States: unused, used.
    """
    def __init__(self, object_id, state="unused"):
        super().__init__(object_id, "key", state)
        self.allowed_states = ["unused", "used"]
