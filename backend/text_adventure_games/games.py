from .things import Location, Character
from . import parsing
from .state.world_state import WorldStateManager
from .state.character_manager import CharacterManager
from .state.descriptions import DescriptionManager
from .events.event_manager import EventManager
from .events.schema_export import SchemaExporter

from ..config.schema import AgentActionOutput
from datetime import datetime


class Game:
    """
    The Game class keeps track of the state of the world, and describes what
    the player sees as they move through different locations.

    Internally, we use a graph of Location objects and Item objects, which can
    be at a Location or in the player's inventory.  Each locations has a set of
    exits which are the directions that a player can move to get to an
    adjacent location. The player can move from one location to another
    location by typing a command like "Go North".
    
    Architecture:
    The Game class now uses a modular manager system instead of monolithic methods:
    - world_state_manager: Handles world state queries and building
    - description_manager: Manages location and object descriptions  
    - event_manager: Manages event queue for frontend communication
    - schema_exporter: Converts actions to API schema format
    - agent_manager: Manages agent turn order and registration
    
    Use managers directly instead of wrapper methods for better performance and clarity.
    """

    def __init__(
        self,
        start_at: Location,
        player: Character,
        characters=None,
    ):
        self.start_at = start_at
        self.player = player

        # Print the special commands associated with items in the game (helpful
        # for debugging and for novice players).
        self.give_hints = True

        # Records history of commands, states, and descriptions
        self.game_history = []

        self.game_over = False
        self.game_over_description = None

        # NEW: Event queue for frontend
        self.event_queue = []
        self.event_id_counter = 0

        # NEW: Track which characters are active agents
        self.active_agents = set()
        self.active_agents.add(player.name)
        
        # NEW: Track whose turn it is
        self.current_agent_index = 0
        self.turn_order = []

        # Add player to game and put them on starting point
        self.characters = {}
        self.add_character(player)
        self.start_at.add_character(player)
        self.start_at.has_been_visited = True

        # Add NPCs to game
        if characters:
            for c in characters:
                if isinstance(c, Character):
                    self.add_character(c)
                else:
                    err_msg = f"ERROR: invalid character ({c})"
                    raise Exception(err_msg)

        # Look up table for locations
        def location_map(location, acc):
            acc[location.name] = location
            for _, connection in location.connections.items():
                if connection.name not in acc:
                    acc = location_map(connection, acc)
            return acc

        self.locations = location_map(self.start_at, {})

        # Parser
        self.parser = parsing.Parser(self)

        self._last_action_result = None
        self._last_action_agent_id = None
        self._last_executed_action = None  # Track the last executed action instance

        # NEW: Initialize modular managers
        self.world_state_manager = WorldStateManager(self)
        self.agent_manager = CharacterManager(self)
        self.description_manager = DescriptionManager(self)
        self.event_manager = EventManager(self)
        self.schema_exporter = SchemaExporter(self)


    def is_won(self) -> bool:
        """
        A conditional check intended for subclasses to use for defining the
        game's winning conditions.
        """
        return False

    def is_game_over(self) -> bool:
        """
        A conditional check that determines if the game is over. By default it
        checks if the player has died or won.
        """
        # Something has set the game over state
        if self.game_over:
            return True
        # The player has died
        if self.player.get_property("is_dead"):
            self.game_over_description = "You have died. THE END"
            return True
        # Has the game has been won?
        return self.is_won()

    def add_character(self, character: Character):
        """
        Puts characters in the game
        """
        self.characters[character.name] = character

    def register_agent(self, character: Character):
        """
        Mark a character as an active agent who can take turns.
        
        Args:
            character: The Character to make an active agent
        """
        # Delegate to the new agent manager while maintaining backward compatibility
        self.agent_manager.register_agent(character)
        
        # Update legacy attributes for backward compatibility
        self.active_agents = self.agent_manager.active_agents
        self.turn_order = self.agent_manager.turn_order

    def add_event(self, event_type: str, data: dict):
        """
        Add an event to the queue for frontend consumption.
        
        Args:
            event_type: Type of event (e.g., 'move', 'get', 'drop')
            data: Event-specific data
        """
        # Delegate to the new event manager while maintaining backward compatibility
        self.event_manager.add_event(event_type, data)
        
        # Update legacy attributes for backward compatibility
        self.event_queue = self.event_manager.event_queue
        self.event_id_counter = self.event_manager.event_id_counter



