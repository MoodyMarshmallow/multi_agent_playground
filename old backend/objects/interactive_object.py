class InteractiveObject:
    """
    Base class for all interactive objects in the house simulation.
    """
    def __init__(self, object_id, object_type, state, location):
        self.object_id = object_id
        self.object_type = object_type
        self.state = state
        self.location = location
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
    def __init__(self, object_id, state="closed", location=None):
        super().__init__(object_id, "door", state, location)
        self.allowed_states = ["open", "closed", "locked"]

class Container(InteractiveObject):  # For fridge, cabinet
    def __init__(self, object_id, state="closed", location=None):
        super().__init__(object_id, "container", state, location)
        self.allowed_states = ["open", "closed"]
        self.contents = []

class Appliance(InteractiveObject):  # For bathtub, sink
    def __init__(self, object_id, state="off", location=None):
        super().__init__(object_id, "appliance", state, location)
        self.allowed_states = ["on", "off"]

class SteamObject(InteractiveObject):  # For coffee cup
    def __init__(self, object_id, state="still", location=None):
        super().__init__(object_id, "steam", state, location)
        self.allowed_states = ["still", "rising"]
