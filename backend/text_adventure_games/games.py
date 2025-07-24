from .things import Location, Character
from . import parsing

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
    """

    def __init__(
        self,
        start_at: Location,
        player: Character,
        characters=None,
        custom_actions=None,
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

        # NOTE: Custom actions are no longer added to parser - using pattern-based discovery only

        # Visit each location and add any blocks found to parser
        seen_before = {}
        for name, location in self.locations.items():
            if len(location.blocks) > 0 and name not in seen_before:
                for b in location.blocks:
                    self.parser.add_block(b)
                    seen_before[name] = True

        self._last_action_result = None
        self._last_action_agent_id = None


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
        if character.name not in self.characters:
            raise ValueError(f"Character {character.name} not in game")
        
        self.active_agents.add(character.name)
        if character.name not in self.turn_order:
            self.turn_order.append(character.name)

    def add_event(self, event_type: str, data: dict):
        """
        Add an event to the queue for frontend consumption.
        
        Args:
            event_type: Type of event (e.g., 'move', 'get', 'drop')
            data: Event-specific data
        """
        self.event_id_counter += 1
        event = {
            'id': self.event_id_counter,
            'type': event_type,
            'timestamp': self.event_id_counter,  # Simple turn counter
            'data': data
        }
        self.event_queue.append(event)

    def get_events_since(self, last_event_id: int) -> list[dict]:
        """
        Get all events after the given ID.
        
        Args:
            last_event_id: ID of last processed event
            
        Returns:
            List of new events
        """
        return [e for e in self.event_queue if e['id'] > last_event_id]

    def get_world_state_for_agent(self, agent: Character) -> dict:
        """
        Get the observable world state for an agent.
        
        Returns:
            Dict containing location info, inventory, and available actions
        """
        location = agent.location
        if location is not None:
            state = {
                'agent_name': agent.name,
                'location': {
                    'name': location.name,
                    'description': location.description
                },
                'inventory': list(agent.inventory.keys()),
                'visible_items': [
                    {'name': item.name, 'description': item.description}
                    for item in location.items.values()
                ],
                'visible_characters': [
                    {'name': char.name, 'description': char.description}
                    for char in location.characters.values()
                    if char.name != agent.name
                ],
                'available_exits': list(location.connections.keys()),
                'available_actions': self.parser.get_available_actions(agent)
            }
            return state
        else:
            raise ValueError(f"Agent {agent.name} location is None.")

    def describe(self) -> str:
        """
        Describe the current game state by first describing the current
        location, then listing any exits, and then describing any objects
        in the current location.
        """
        description = self.describe_current_location() + "\n"
        description += self.describe_exits() + "\n"
        description += self.describe_items() + "\n"
        description += self.describe_characters() + "\n"
        # self.parser.ok(description)
        return description

    def describe_current_location(self) -> str:
        """
        Describe the current location by printing its description field.
        """
        if self.player.location is not None:
            return self.player.location.description
        else:
            raise ValueError(f"Player {self.player.name} location is None.")

    def describe_exits(self) -> str:
        """
        List the directions that the player can take to exit from the current
        location.
        """
        if self.player.location is not None:
            exits = []
            for direction in self.player.location.connections.keys():
                location = self.player.location.connections[direction]
                exits.append(direction.capitalize() + " to " + location.name)
            description = ""
            if len(exits) > 0:
                description = "Exits:\n"
                for exit in exits:
                    description += exit + "\n"
            return description
        else:
            raise ValueError(f"Player {self.player.name} location is None.")

    def describe_items(self) -> str:
        """
        Describe what items are in the current location.
        """
        if self.player.location is not None:
            description = ""
            if len(self.player.location.items) > 0:
                description = "You see:"
                for item_name in self.player.location.items:
                    item = self.player.location.items[item_name]
                    description += "\n * " + item.description
                    if self.give_hints:
                        description += "\n   You can:"
                        special_commands = item.get_command_hints()
                        for cmd in special_commands:
                            description += "\n\t" + cmd
            return description
        else:
            raise ValueError(f"Player {self.player.name} location is None.")

    def describe_characters(self) -> str:
        """
        Describe what characters are in the current location.
        """
        if self.player.location is not None:
            description = ""
            if len(self.player.location.characters) > 1:
                description = "Characters:"
                for character_name in self.player.location.characters:
                    if character_name == self.player.name:
                        continue
                    character = self.player.location.characters[character_name]
                    description += "\n * " + character.description
            return description
        else:
            raise ValueError(f"Player {self.player.name} location is None.")



    def get_schema(self) -> AgentActionOutput:
        """
        Export the last action as an AgentActionOutput schema object.
        The description is narrative and user-friendly for the GUI chat, while the reason in NoOpAction remains technical.
        """
        if not self._last_action_result or not self._last_action_agent_id:
            raise RuntimeError("No action has been taken yet.")
        agent = self.characters.get(self._last_action_agent_id)
        current_room = agent.location.name if agent and agent.location else None
        # Compose a technical, GUI-friendly description
        # 1. Always include the action type and affected object (if any)
        action_type = getattr(self._last_action_result.house_action, 'action_type', 'noop')
        affected_object = self._last_action_result.object_id
        # 2. For NoOp, treat as non-fatal error with informative feedback
        if action_type == 'noop':
            # Get the actual reason from the action result
            action_reason = getattr(self._last_action_result.house_action, 'reason', 'Unknown command or invalid action')
            
            # Create error-focused description for agents
            description = f"ACTION FAILED: {action_reason}"
            
            # Add current context to help agent understand their situation
            if agent and agent.location:
                visible_items = [item.name for item in agent.location.items.values()]
                visible_characters = [char.name for char in agent.location.characters.values() if char.name != agent.name]
                available_exits = list(agent.location.connections.keys())
                
                context_lines = [f"You are currently in {current_room}."]
                if visible_items:
                    context_lines.append(f"Available items: {', '.join(visible_items)}")
                if visible_characters:
                    context_lines.append(f"Other characters: {', '.join(visible_characters)}")
                if available_exits:
                    context_lines.append(f"Available exits: {', '.join(available_exits)}")
                
                description += f" {' '.join(context_lines)}"
            
            reason = action_reason
        else:
            # For real actions, use the action result's description (assumed user-facing)
            description = self._last_action_result.description
            reason = None
        # Context for frontend (not in main description)
        visible_items = []
        visible_characters = []
        available_exits = []
        if agent and agent.location:
            visible_items = [item.name for item in agent.location.items.values()]
            visible_characters = [char.name for char in agent.location.characters.values() if char.name != agent.name]
            available_exits = list(agent.location.connections.keys())
        # Patch the NoOpAction reason if needed
        action_obj = self._last_action_result.house_action
        if action_type == 'noop' and hasattr(action_obj, 'reason'):
            action_obj.reason = reason
        return AgentActionOutput(
            agent_id=self._last_action_agent_id,
            action=action_obj,
            timestamp=datetime.now().isoformat(),
            current_room=current_room,
            description=description
        )
