from .things import Location, Character
from . import parsing, actions, blocks

import json
import inspect
from collections import namedtuple
from backend.config.schema import AgentActionOutput
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

        # Add custom actions to parser
        if custom_actions:
            for ca in custom_actions:
                if inspect.isclass(ca) and issubclass(ca, actions.Action):
                    self.parser.add_action(ca)
                else:
                    err_msg = f"ERROR: invalid custom action ({ca})"
                    raise Exception(err_msg)

        # Visit each location and add any blocks found to parser
        seen_before = {}
        for name, location in self.locations.items():
            if len(location.blocks) > 0 and name not in seen_before:
                for b in location.blocks:
                    self.parser.add_block(b)
                    seen_before[name] = True

        self._last_action_result = None
        self._last_action_agent_id = None

    def game_loop(self):
        """
        A simple loop that starts the game, loops over commands from the user,
        and then stops if the game's state says the game is over.
        """
        narration, schema = self.parser.parse_command("look")
        print(narration)
        print(f"[DEBUG] Action schema: {schema}")

        while True:
            command = input("\n> ")
            narration, schema = self.parser.parse_command(command)
            print(narration)
            print(f"[DEBUG] Action schema: {schema}")
            if self.is_game_over():
                break

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
        return self.player.location.description

    def describe_exits(self) -> str:
        """
        List the directions that the player can take to exit from the current
        location.
        """
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

    def describe_items(self) -> str:
        """
        Describe what items are in the current location.
        """
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

    def describe_characters(self) -> str:
        """
        Describe what characters are in the current location.
        """
        description = ""

        if len(self.player.location.characters) > 1:
            description = "Characters:"
            for character_name in self.player.location.characters:
                if character_name == self.player.name:
                    continue
                character = self.player.location.characters[character_name]
                description += "\n * " + character.description
        return description

    def describe_inventory(self) -> str:
        """
        Describes the player's inventory.
        """
        if len(self.player.inventory) == 0:
            empty_inventory = "You don't have anything."
            self.ok(empty_inventory, [], "Describe the player's inventory.")
        else:
            # descriptions = []  # JD logical issue?
            inventory_description = "In your inventory, you have:\n"
            for item_name in self.player.inventory:
                item = self.player.inventory[item_name]
                d = "* {item} - {item_description}\n"
                inventory_description += d.format(
                    item=item_name, item_description=item.description
                )
            self.ok(inventory_description)

    # The methods below read and write a game to JSON
    def to_primitive(self):
        """
        Serialize a game to json.
        """
        data = {
            "player": self.player.name,
            "start_at": self.start_at.name,
            "game_history": self.game_history,  # TODO this is empty?
            "game_over": self.game_over,
            "game_over_description": self.game_over_description,
            "characters": [c.to_primitive() for c in self.characters.values()],
            "locations": [l.to_primitive() for l in self.locations.values()],
            "actions": sorted([a for a in self.parser.actions]),
        }
        return data

    @classmethod
    def default_actions(self):
        """
        Generates a dictionary of all actions packaged as part of this library
        """
        actions_found = {}
        for member in dir(actions):
            attr = getattr(actions, member)
            if inspect.isclass(attr) and issubclass(attr, actions.Action):
                # dont include base class
                if not attr == actions.Action:
                    actions_found[attr.action_name()] = attr
        return actions_found

    @classmethod
    def default_blocks(self):
        """
        Generates as dictionary of all blocks packaged as part of this library
        """
        blocks_found = {}
        for member in dir(blocks):
            attr = getattr(blocks, member)
            if inspect.isclass(attr) and issubclass(attr, blocks.Block):
                # dont include base class
                if not attr == blocks.Block:
                    # if this changes, also adjust _type in blocks.Block
                    blocks_found[attr.__name__] = attr
        return blocks_found

    @classmethod
    def from_primitive(cls, data, custom_actions=None, custom_blocks=None):
        """
        This complex method performs the huge job of converting a game from its
        primitive representation to fully formed python objects.

        There are three main parts to this method:

        1. Create skeletons for all characters and locations. Currently, items
           exist by being in a location or a character's inventory, and so this
           step also creates item skeletons. See the from_primitive methods for
           characters and locations for more.
        2. Replace fields in skeletons where an object's name exists with the
           actual objects. This step replaces fields where an object's name is
           stored instead of the actual object.
        3. Instantiate anything left that requires full object instances to
           work properly. Blocks require actual instances for everything.

        Once those steps are done, this method simply adds any remaining game
        fields to the game instance.
        """
        SkeletonContext = namedtuple(
            "SkeletonContext", ["characters", "locations", "items"]
        )

        # FIRST PASS

        characters = {
            c["name"]: Character.from_primitive(c) for c in data["characters"]
        }
        locations = {l["name"]: Location.from_primitive(l) for l in data["locations"]}
        items = {}
        context = SkeletonContext(characters, locations, items)

        # SECOND PASS

        # Characters
        for c in context.characters.values():
            # locations
            l = context.locations[c.location]
            c.location = l
            # inventory
            for item_name, item in c.inventory.items():
                if hasattr(item, "location") and item.location:
                    l_obj = context.locations[item.location]
                    item.location = l_obj
                elif hasattr(item, "owner") and item.owner:
                    c_obj = context.characters[item.owner]
                    item.owner = c_obj
                context.items[item_name] = item

        # Locations
        for l in context.locations.values():
            # characters
            for char_name, c in l.characters.items():
                c_obj = context.characters[char_name]
                l.characters[char_name] = c_obj
            # connections
            for dir_name, connection in l.connections.items():
                c_obj = context.locations[connection]
                l.connections[dir_name] = c_obj
            # items
            for item_name, item in l.items.items():
                if hasattr(item, "location") and item.location:
                    l_obj = context.locations[item.location]
                    item.location = l_obj
                elif hasattr(item, "owner") and item.owner:
                    c_obj = context.characters[item.owner]
                    item.owner = c_obj
                context.items[item_name] = item

        # THIRD PASS

        # Actions
        action_map = cls.default_actions()

        # Validate custom actions
        if custom_actions:
            for ca in custom_actions:
                if inspect.isclass(ca) and issubclass(ca, actions.Action):
                    action_map[ca.action_name()] = ca
                else:
                    err_msg = f"ERROR: invalid custom action ({ca})"
                    raise Exception(err_msg)

        # verify all commands from primitive data have an associated action
        action_names = list(action_map.keys())
        for action_name in data["actions"]:
            if action_name not in action_names:
                err_msg = "".join(
                    [
                        f"ERROR: unmapped action ({action_name}) found in ",
                        "primitive data",
                    ]
                )
                raise Exception(err_msg)

        # Blocks
        block_map = cls.default_blocks()

        # Validate custom blocks
        if custom_blocks:
            for cb in custom_blocks:
                if inspect.isclass(cb) and issubclass(cb, blocks.Block):
                    block_map[cb.__name__] = cb
                else:
                    err_msg = f"ERROR: invalid custom block ({cb})"
                    raise Exception(err_msg)

        # Instantiate all blocks for all locations
        for l in context.locations.values():
            for direction, block_data in l.blocks.items():
                # it is possible for two locations to have the same block, so
                # skip any that have already been instantiated
                if isinstance(block_data, blocks.Block):
                    continue
                cls_type = block_map[block_data["_type"]]
                del block_data["_type"]
                # we will copy the properties of relevant items before we
                # install the block, so we can restore them after
                prop_map = {}
                # replace thing names in primitive with thing instances
                for param_name, param in block_data.items():
                    if param in context.items:
                        param_instance = context.items[param]
                    elif param in context.locations:
                        param_instance = context.locations[param]
                    block_data[param_name] = param_instance
                    prop_map[param_name] = param_instance.properties.copy()
                instance = cls_type.from_primitive(block_data)
                # restore properties found in primitive data
                for param_name, param in block_data.items():
                    param.properties = prop_map[param_name]

        start_at = context.locations[data["start_at"]]
        player = context.characters[data["player"]]

        instance = cls(start_at, player, custom_actions=action_map.values())
        instance.game_history = data["game_history"]
        instance.game_over = data["game_over"]
        instance.game_over_description = data["game_over_description"]

        return instance

    def to_json(self):
        """
        Creates a JSON version of a game's primitive data.
        """
        data = self.to_primitive()
        data_json = json.dumps(data)
        return data_json

    @classmethod
    def from_json(cls, data_json, **kw):
        """
        Goes from JSON into actual game instances.
        """
        data = json.loads(data_json)
        instance = cls.from_primitive(data, **kw)
        return instance

    def save_game(self, filename):
        """
        Converts a game's state to JSON and then saves it to a file
        """
        save_data = self.to_json()
        with open(filename, 'w') as f:
            f.write(save_data)

    @classmethod
    def load_game(cls, filename, **kw):
        """
        Reads a file with a game's state stored as JSON and converts it to a
        game instance.
        """
        with open(filename, 'r') as f:
            save_data = f.read()
            return cls.from_json(save_data, **kw)

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
        # 2. For NoOp, always use a technical, non-narrative reason/description
        if action_type == 'noop':
            # Compose a presentable summary for the GUI chat
            room_desc = f"You are in the {current_room}." if current_room else ""
            visible_items = []
            visible_characters = []
            available_exits = []
            if agent and agent.location:
                visible_items = [item.name for item in agent.location.items.values()]
                visible_characters = [char.name for char in agent.location.characters.values() if char.name != agent.name]
                available_exits = list(agent.location.connections.keys())
            lines = [room_desc]
            if visible_items:
                lines.append(f"You see: {', '.join(visible_items)}.")
            if visible_characters:
                lines.append(f"{', '.join(visible_characters)} {'is' if len(visible_characters)==1 else 'are'} here.")
            if available_exits:
                lines.append(f"Exits are {', '.join(available_exits)}.")
            narrative_desc = " ".join([l for l in lines if l])
            description = narrative_desc.strip()
            reason = 'No backend state change for this command.'
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
            description=description,
            current_object=self._last_action_result.object_id
        )
