"""Game simulation domain service.

Handles world initialization, agent turn execution,
world state queries, and event management.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from ..text_adventure_games.games import Game
from ..text_adventure_games.house import build_house_game
from ..agent.manager import AgentManager
from ..agent.agent_strategies import KaniAgent, ManualAgent
from ..config.schema import AgentActionOutput
from ...log_config import log_game_event

logger = logging.getLogger(__name__)


class GameSimulation:
    """Pure game simulation logic without scheduling."""

    def __init__(self, agent_config: Optional[Dict[str, str]] = None):
        self.game: Optional[Game] = None
        self.agent_manager: Optional[AgentManager] = None
        self.agent_config = agent_config or {}

        self.event_queue: List[AgentActionOutput] = []
        self.event_id_counter = 0
        self.turn_counter = 0
        self.max_turns_per_session = 1000

        self.objects_registry: Dict[str, Dict] = {}
        self.last_served_event_index = 0

    async def initialize(self):
        """Initialize the game world and agents."""
        self.game = self._build_house_environment()
        self.agent_manager = AgentManager(self.game)
        await self._setup_agents()
        self._initialize_objects_registry()
        self.event_queue.clear()
        self.event_id_counter = 0
        self.turn_counter = 0
        self.last_served_event_index = 0
        logger.info("Game simulation initialized successfully")

    async def run_turn(self):
        """Execute a single agent turn."""
        if self.turn_counter >= self.max_turns_per_session:
            logger.warning("Max turns reached")
            return
        if not self.agent_manager:
            logger.error("Agent manager not initialized")
            return

        agent = self.agent_manager.get_next_agent()
        if agent:
            action_schema, action_ended_turn = await self.agent_manager.execute_agent_turn(agent)
            if action_schema:
                turn_status = "ended turn" if action_ended_turn else "continued turn"
                log_game_event(
                    "turn_end",
                    {
                        "agent": agent.name,
                        "turn": self.turn_counter,
                        "action": getattr(action_schema.action, "action_type", "unknown"),
                        "status": turn_status,
                    },
                )
                self._add_action_event(action_schema)
            if action_ended_turn:
                self.agent_manager.advance_turn()
                self.turn_counter += 1

    def set_agent_config(self, agent_config: Dict[str, str]):
        self.agent_config = agent_config

    def get_agent_config(self) -> Dict[str, str]:
        return self.agent_config.copy()

    def _build_house_environment(self) -> Game:
        return build_house_game()

    async def _setup_agents(self):
        try:
            agent_personas = {
                "alex_001": "I am Alex, a friendly and social person who loves to chat with others. I enjoy reading books and might want to explore the house. I'm curious about what others are doing and like to help when I can.",
                "alan_002": "I am Alan, a quiet and thoughtful person who likes to observe and think. I prefer to explore slowly and examine things carefully. I might be interested in food and practical items.",
            }
            for agent_name, persona in agent_personas.items():
                strategy = self._create_agent_strategy(agent_name, persona)
                if strategy and self.agent_manager:
                    self.agent_manager.register_agent_strategy(agent_name, strategy)
            logger.info("Agents set up successfully")
        except Exception as e:  # pragma: no cover - setup errors shouldn't crash
            import traceback
            logger.warning(f"Could not set up agents: {e}")
            traceback.print_exc()
            if self.agent_manager:
                self.agent_manager.active_agents.extend(["alex_001", "alan_002"])

    def _create_agent_strategy(self, character_name: str, persona: str):
        agent_type = self.agent_config.get(character_name, "ai")
        if agent_type == "manual":
            logger.info(f"Creating manual agent for {character_name}")
            return ManualAgent(character_name, persona)
        try:
            logger.info(f"Creating AI agent for {character_name}")
            if self.game and character_name in self.game.characters:
                character = self.game.characters[character_name]
                initial_world_state = self._get_initial_world_state_for_agent(character)
                return KaniAgent(character_name, persona, initial_world_state)
            logger.warning(f"Character {character_name} not found, creating agent without initial state")
            return KaniAgent(character_name, persona)
        except Exception as e:  # pragma: no cover - fallback path
            logger.warning(f"Failed to create AI agent for {character_name}: {e}")
            return ManualAgent(character_name, persona)

    def _get_initial_world_state_for_agent(self, character) -> str:
        from ..text_adventure_games.actions.generic import EnhancedLookAction

        look_action = EnhancedLookAction(self.game, "look")
        look_action.character = character
        try:
            _, schema = look_action.apply_effects()
            return schema.description if schema and schema.description else "You are in an unknown location."
        except Exception as e:  # pragma: no cover - defensive
            logger.error(f"Error getting initial world state for {character.name}: {e}")
            return "You are in an unknown location. Use 'look' to see your surroundings."

    def _initialize_objects_registry(self):
        self.objects_registry = {}
        if not self.game:
            return
        for location_name, location in self.game.locations.items():
            for item_name, item in location.items.items():
                self.objects_registry[item_name] = {
                    "name": item_name,
                    "description": item.description,
                    "location": location_name,
                    "state": "default",
                    "gettable": item.get_property("gettable") if item.get_property("gettable") is not None else True,
                }

    # --- World state queries ---
    def get_world_state(self) -> Dict[str, Any]:
        if not self.game or not self.agent_manager:
            return {"status": "not_initialized"}
        return {
            "agents": self.get_all_agent_states(),
            "objects": self.get_all_objects(),
            "locations": self.get_all_location_states(),
            "game_status": self.get_game_status(),
        }

    def get_all_agent_states(self) -> Dict[str, Dict]:
        if not self.game:
            return {}
        return {aid: self.get_agent_state(aid) for aid in self.game.characters.keys()}

    def get_all_location_states(self) -> Dict[str, Dict]:
        if not self.game:
            return {}
        states = {}
        for loc_name, location in self.game.locations.items():
            states[loc_name] = {
                "name": loc_name,
                "description": location.description,
                "items": list(location.items.keys()),
                "characters": list(location.characters.keys()),
                "connections": {d: l.name for d, l in location.connections.items()},
            }
        return states

    def _add_action_event(self, action_output: AgentActionOutput):
        self.event_id_counter += 1
        self._print_action_output(action_output)
        self.event_queue.append(action_output)

    def _print_action_output(self, action_output: AgentActionOutput):
        is_noop = action_output.action.action_type == "noop"
        if is_noop:
            error_details = [
                f"Agent: {action_output.agent_id}",
                f"Location: {action_output.current_room or 'Unknown'}",
                "Error Type: Invalid Action (noop)",
            ]
            action_fields = self._get_action_fields(action_output.action)
            if action_fields:
                for field_name, field_value in action_fields.items():
                    if field_value is not None:
                        error_details.append(f"{field_name.title()}: {field_value}")
            error_details.append(f"Timestamp: {action_output.timestamp}")
            if action_output.description:
                error_details.append(f"Error Details: {action_output.description}")
            logger.warning("ACTION ERROR - " + " | ".join(error_details))
        else:
            success_details = [
                f"Agent: {action_output.agent_id}",
                f"Location: {action_output.current_room or 'Unknown'}",
                f"Action: {action_output.action.action_type}",
            ]
            action_fields = self._get_action_fields(action_output.action)
            if action_fields:
                for field_name, field_value in action_fields.items():
                    if field_value is not None:
                        success_details.append(f"{field_name.title()}: {field_value}")
            success_details.append(f"Timestamp: {action_output.timestamp}")
            if action_output.description:
                success_details.append(f"Result: {action_output.description}")
            logger.info("ACTION EXECUTED - " + " | ".join(success_details))

    def _get_action_fields(self, action) -> dict:
        fields = {}
        if hasattr(action, "__fields__"):
            for field_name in action.__fields__:
                if field_name != "action_type":
                    fields[field_name] = getattr(action, field_name, None)
        elif hasattr(action, "model_fields"):
            for field_name in action.model_fields:
                if field_name != "action_type":
                    fields[field_name] = getattr(action, field_name, None)
        else:
            for field_name, field_value in action.__dict__.items():
                if not field_name.startswith("_") and field_name != "action_type":
                    fields[field_name] = field_value
        return fields

    def _get_current_timestamp(self) -> str:
        return datetime.now().isoformat()

    def get_events_since(self, last_timestamp: str) -> List[AgentActionOutput]:
        if not last_timestamp:
            return self.event_queue
        return [e for e in self.event_queue if e.timestamp and e.timestamp > last_timestamp]

    def get_unserved_events(self) -> List[AgentActionOutput]:
        unserved = self.event_queue[self.last_served_event_index:]
        self.last_served_event_index = len(self.event_queue)
        return unserved

    def get_agent_state(self, agent_id: str) -> Dict:
        if not self.game:
            raise RuntimeError("Game not initialized")
        character = self.game.characters.get(agent_id)
        if not character:
            raise KeyError(f"Agent {agent_id} not found")
        return {
            "agent_id": agent_id,
            "location": character.location.name if character.location else None,
            "inventory": list(character.inventory.keys()),
            "properties": character.properties,
        }

    def get_all_objects(self) -> List[Dict]:
        return list(self.objects_registry.values())

    async def reset(self):
        await self.initialize()

    def get_game_status(self) -> Dict:
        if not self.game or not self.agent_manager:
            return {"status": "not_initialized"}
        return {
            "status": "running",
            "turn_counter": self.turn_counter,
            "active_agents": len(self.agent_manager.active_agents),
            "total_events": len(self.event_queue),
            "locations": len(self.game.locations),
            "characters": len(self.game.characters),
        }
