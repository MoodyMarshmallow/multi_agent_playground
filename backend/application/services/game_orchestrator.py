"""
GameOrchestrator Application Service
====================================
Main coordinator for the multi-agent simulation, bridging domain services
with infrastructure components.

This application service orchestrates the game lifecycle, coordinates
domain services with infrastructure, and manages the overall simulation flow.
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

# Domain imports
from ...domain.entities.agent import Agent
from ...domain.entities.game_state import GameState
from ...domain.services.simulation_engine import SimulationEngine, AgentExecutor, ActionEventPublisher
from ...domain.services.turn_scheduler import TurnScheduler
from ...domain.events.event_bus import EventBus
from ...domain.events.domain_event import AgentActionEvent

# Infrastructure imports (will be injected)
from ...infrastructure.game.game_engine import Game
from ...domain.actions.interaction_actions import EnhancedLookAction
from ...agent.manager import AgentManager
from ...infrastructure.agents.kani_agent import KaniAgent, ManualAgent
from ...infrastructure.events.async_event_bus import AsyncEventBus

# Phase 4: Configuration and strategy loading
from ..config.agent_strategy_loader import AgentStrategyLoader, ConfigurationError, AgentCreationError

# Phase 5: World building configuration
from ..config.world_builder import WorldBuilder, WorldBuildingError


class GameOrchestratorAgentExecutor(AgentExecutor):
    """Infrastructure implementation of AgentExecutor for SimulationEngine."""
    
    def __init__(self, agent_manager: AgentManager):
        self._agent_manager = agent_manager
    
    async def execute_agent_turn(self, agent: Agent, action_result: str) -> Tuple[Dict[str, Any], bool]:
        """Execute agent turn through AgentManager infrastructure."""
        # Find the corresponding character in the game
        if agent.character_name not in self._agent_manager.game.characters:
            raise ValueError(f"Character {agent.character_name} not found in game")
        
        character = self._agent_manager.game.characters[agent.character_name]
        
        # Store the action result for this agent (AgentManager reads this internally)
        if action_result:
            self._agent_manager.previous_action_results[agent.character_name] = action_result
        
        # Execute through AgentManager (only takes character parameter)
        action_schema, action_ended_turn = await self._agent_manager.execute_agent_turn(character)
        
        # Convert to dictionary format expected by domain service
        schema_dict = action_schema.dict() if action_schema else {}
        
        return schema_dict, action_ended_turn


class GameOrchestratorEventPublisher(ActionEventPublisher):
    """Infrastructure implementation of ActionEventPublisher for SimulationEngine."""
    
    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
        self._logger = logging.getLogger(__name__)
    
    def publish_action_event(self, action_schema: Dict[str, Any]) -> None:
        """Publish action event through the event bus."""
        if action_schema:
            try:
                # Convert action_schema to AgentActionEvent
                agent_action_event = AgentActionEvent.from_agent_action_output(action_schema)
                
                # Publish through event bus (async operation, but we'll handle it in a task)
                asyncio.create_task(self._event_bus.publish(agent_action_event))
                
                self._logger.debug(f"Published agent action event: {agent_action_event.event_id}")
                
            except Exception as e:
                self._logger.error(f"Error publishing event: {e}")
    
    def add_event_handler(self, handler) -> None:
        """Legacy method for backward compatibility - now unused."""
        self._logger.warning("add_event_handler called but is no longer used with event bus")


class GameOrchestrator:
    """
    Application service that orchestrates the multi-agent simulation.
    
    Coordinates domain services (SimulationEngine, TurnScheduler) with 
    infrastructure components (AgentManager, Game) to manage the complete
    game lifecycle and simulation flow.
    """
    
    def __init__(self, config_file_path: str, world_config_path: Optional[str] = None):
        self._logger = logging.getLogger(__name__)
        
        # Validate required configuration
        if not config_file_path:
            raise ValueError("config_file_path is required. Agent configuration must be loaded from YAML file.")
        
        # Domain state
        self._game_state: Optional[GameState] = None
        self._agents: Dict[str, Agent] = {}
        
        # Domain services
        self._turn_scheduler = TurnScheduler()
        
        # Infrastructure components (will be initialized)
        self._game: Optional[Game] = None
        self._agent_manager: Optional[AgentManager] = None
        self._event_bus: Optional[EventBus] = None
        
        # Infrastructure adapters
        self._agent_executor: Optional[GameOrchestratorAgentExecutor] = None
        self._event_publisher: Optional[GameOrchestratorEventPublisher] = None
        self._simulation_engine: Optional[SimulationEngine] = None
        
        # Configuration
        self._config_file_path = config_file_path
        
        # Phase 5: World configuration
        self._world_config_path = world_config_path or "config/worlds/house.yaml"
        self._world_builder = WorldBuilder()
        
        # Objects registry for API compatibility
        self._objects_registry: Dict[str, Dict] = {}
    
    async def initialize(self) -> None:
        """Initialize the game world, agents, and all services."""
        try:
            # Create game state
            session_id = str(uuid.uuid4())
            self._game_state = GameState(session_id=session_id)
            
            # Initialize event bus
            self._event_bus = AsyncEventBus()
            await self._event_bus.start()
            
            # Build game world from configuration
            self._game = self._build_world_from_config()
            if not self._game:
                raise RuntimeError("Failed to build game world")
            
            # Initialize agent manager
            self._agent_manager = AgentManager(self._game)
            
            # Initialize infrastructure adapters
            self._agent_executor = GameOrchestratorAgentExecutor(self._agent_manager)
            self._event_publisher = GameOrchestratorEventPublisher(self._event_bus)
            
            # Initialize simulation engine with adapters
            self._simulation_engine = SimulationEngine(
                agent_executor=self._agent_executor,
                event_publisher=self._event_publisher
            )
            
            # Setup agents
            await self._setup_agents()
            
            # Initialize objects registry
            self._initialize_objects_registry()
            
            # Start game state
            self._game_state.start_game()
            
            self._logger.info("Game orchestrator initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize game orchestrator: {e}")
            raise
    
    def _build_world_from_config(self) -> Game:
        """Create a world environment from YAML configuration."""
        import os
        
        # Use absolute path to ensure it works regardless of working directory
        if not os.path.isabs(self._world_config_path):
            # Navigate to project root (from backend/application/services/ -> ../../.. -> project_root)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            world_config_path = os.path.join(project_root, self._world_config_path)
        else:
            world_config_path = self._world_config_path
        
        try:
            # Build world from YAML configuration
            game = self._world_builder.build_world_from_file(world_config_path)
            self._logger.info(f"Successfully built world from configuration: {world_config_path}")
            return game
            
        except WorldBuildingError as e:
            self._logger.error(f"World building failed: {e}")
            raise RuntimeError(f"Failed to build world from configuration: {e}") from e
        except Exception as e:
            self._logger.error(f"Unexpected error during world building: {e}")
            raise RuntimeError(f"Failed to build world from configuration: {e}") from e
    
    async def _setup_agents(self) -> None:
        """Setup agents from YAML configuration file."""
        try:
            # Phase 4: Always use YAML configuration
            await self._setup_agents_from_config()
                
        except Exception as e:
            self._logger.error(f"Failed to setup agents from configuration: {e}")
            raise RuntimeError(f"Agent setup failed. Ensure {self._config_file_path} is valid and accessible.") from e
    
    async def _setup_agents_from_config(self) -> None:
        """Setup agents from YAML configuration file (Phase 4)."""
        if not self._config_file_path:
            raise ConfigurationError("Config file path not provided")
        
        self._logger.info(f"Loading agents from configuration file: {self._config_file_path}")
        
        # Create strategy loader
        strategy_loader = AgentStrategyLoader(fallback_to_manual=True)
        
        try:
            # Load agents from YAML configuration
            agent_strategies = strategy_loader.load_agents_from_file(self._config_file_path)
            
            # Process each loaded agent
            for agent_id, agent_strategy in agent_strategies.items():
                # Create domain entity
                agent = Agent(
                    agent_id=agent_id,
                    character_name=agent_strategy.character_name,
                    persona=getattr(agent_strategy, 'persona', f'Agent {agent_id}'),
                    current_location=None,  # Will be set after world state query
                    is_active=True
                )
                self._agents[agent_id] = agent
                
                # Register strategy with agent manager
                if self._agent_manager:
                    self._agent_manager.register_agent_strategy(agent_id, agent_strategy)
                    
                    # Add to turn rotation
                    if self._game_state:
                        self._turn_scheduler.add_agent_to_rotation(self._game_state, agent_id)
                
                self._logger.info(f"Successfully configured agent: {agent_id}")
            
            self._logger.info(f"Set up {len(self._agents)} agents from configuration file")
            
        except (ConfigurationError, AgentCreationError) as e:
            self._logger.error(f"Failed to load agents from config: {e}")
            raise
    
    
    def _get_initial_world_state_for_agent(self, character) -> str:
        """Get the initial world state for an agent by executing a look action."""
        
        # Create and execute a look action for this character
        look_action = EnhancedLookAction(self._game, "look")
        look_action.character = character
        
        # Execute the look action to get formatted world state
        try:
            narration, schema = look_action.apply_effects()
            # Return the description which contains the formatted world state
            return schema.description if schema and schema.description else "You are in an unknown location."
        except Exception as e:
            self._logger.error(f"Error getting initial world state for {character.name}: {e}")
            return "You are in an unknown location. Use 'look' to see your surroundings."
    
    def _initialize_objects_registry(self):
        """Initialize the objects registry for frontend communication."""
        self._objects_registry = {}
        
        if not self._game:
            return
            
        for location_name, location in self._game.locations.items():
            for item_name, item in location.items.items():
                self._objects_registry[item_name] = {
                    "name": item_name,
                    "description": item.description,
                    "location": location_name,
                    "state": "default",
                    "gettable": item.get_property("gettable") if item.get_property("gettable") is not None else True
                }
    
    async def execute_next_turn(self) -> Tuple[Optional[Dict[str, Any]], bool]:
        """Execute the next simulation turn."""
        if not self._game_state or not self._simulation_engine:
            raise RuntimeError("Game orchestrator not initialized")
        
        if not self._turn_scheduler.should_continue_simulation(self._game_state):
            return None, False
        
        # Get current agent
        agent_id = self._turn_scheduler.get_current_agent_id(self._game_state)
        if not agent_id or agent_id not in self._agents:
            return None, False
        
        agent = self._agents[agent_id]
        
        # Get previous action result for this agent
        previous_result = self._agent_manager.previous_action_results.get(agent_id) if self._agent_manager else None
        
        # Execute simulation turn
        action_schema, action_ended_turn = await self._simulation_engine.execute_simulation_turn(
            self._game_state, agent, previous_result
        )
        
        # Advance turn if needed
        if self._turn_scheduler.should_advance_turn(action_ended_turn, self._game_state):
            self._turn_scheduler.advance_to_next_agent(self._game_state)
        
        return action_schema, action_ended_turn
    
    def add_event_handler(self, handler) -> None:
        """Add an event handler for action events (legacy compatibility)."""
        if self._event_publisher:
            self._event_publisher.add_event_handler(handler)
        else:
            self._logger.warning("Cannot add event handler: event publisher not initialized")
    
    # Public API methods for compatibility with GameLoop
    
    def get_game_state_entity(self) -> Optional[GameState]:
        """Get the domain game state entity."""
        return self._game_state
    
    def get_agent_entities(self) -> Dict[str, Agent]:
        """Get the domain agent entities."""
        return self._agents.copy()
    
    def get_infrastructure_game(self) -> Optional[Game]:
        """Get the infrastructure game object."""
        return self._game
    
    def get_agent_manager(self) -> Optional[AgentManager]:
        """Get the infrastructure agent manager."""
        return self._agent_manager
    
    def get_event_bus(self) -> Optional[EventBus]:
        """Get the event bus instance."""
        return self._event_bus
    
    def get_objects_registry(self) -> Dict[str, Dict]:
        """Get the objects registry."""
        return self._objects_registry.copy()
    
    def get_turn_statistics(self) -> Dict[str, Any]:
        """Get turn statistics from the scheduler."""
        if not self._game_state:
            return {}
        return self._turn_scheduler.get_turn_statistics(self._game_state)
    
    def get_simulation_statistics(self) -> Dict[str, Any]:
        """Get simulation statistics from the engine."""
        if not self._simulation_engine:
            return {}
        return self._simulation_engine.get_simulation_statistics()
    
    async def reset(self) -> None:
        """Reset the entire simulation."""
        if self._simulation_engine:
            self._simulation_engine.clear_history()
        
        if self._game_state:
            self._turn_scheduler.reset_turn_state(self._game_state)
            self._game_state.stop_game()
        
        # Clear agent manager state
        if self._agent_manager:
            self._agent_manager.previous_action_results.clear()
        
        # Clear event bus
        if self._event_bus:
            await self._event_bus.clear_events()
            await self._event_bus.stop()
        
        # Reinitialize everything
        await self.initialize()