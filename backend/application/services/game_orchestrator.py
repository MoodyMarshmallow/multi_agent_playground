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

# Infrastructure imports (will be injected)
from ...text_adventure_games.games import Game
from ...agent.manager import AgentManager
from ...infrastructure.agents.kani_agent import KaniAgent, ManualAgent
from ...config.schema import AgentActionOutput


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
    
    def __init__(self):
        self._event_handlers = []
    
    def publish_action_event(self, action_schema: Dict[str, Any]) -> None:
        """Publish action event to registered handlers."""
        # Convert dict back to AgentActionOutput for compatibility
        if action_schema:
            try:
                # AgentActionOutput expects specific fields, construct from schema
                action_output = AgentActionOutput(
                    agent_id=action_schema.get('agent_id', ''),
                    action=action_schema.get('action', {}),
                    current_room=action_schema.get('current_room'),
                    description=action_schema.get('description'),
                    timestamp=action_schema.get('timestamp')
                )
                for handler in self._event_handlers:
                    handler(action_output)
            except Exception as e:
                logging.getLogger(__name__).error(f"Error publishing event: {e}")
    
    def add_event_handler(self, handler) -> None:
        """Add an event handler."""
        self._event_handlers.append(handler)


class GameOrchestrator:
    """
    Application service that orchestrates the multi-agent simulation.
    
    Coordinates domain services (SimulationEngine, TurnScheduler) with 
    infrastructure components (AgentManager, Game) to manage the complete
    game lifecycle and simulation flow.
    """
    
    def __init__(self, agent_config: Optional[Dict[str, str]] = None):
        self._logger = logging.getLogger(__name__)
        
        # Domain state
        self._game_state: Optional[GameState] = None
        self._agents: Dict[str, Agent] = {}
        
        # Domain services
        self._turn_scheduler = TurnScheduler()
        
        # Infrastructure components (will be initialized)
        self._game: Optional[Game] = None
        self._agent_manager: Optional[AgentManager] = None
        
        # Infrastructure adapters
        self._agent_executor: Optional[GameOrchestratorAgentExecutor] = None
        self._event_publisher = GameOrchestratorEventPublisher()
        self._simulation_engine: Optional[SimulationEngine] = None
        
        # Configuration
        self._agent_config = agent_config or {}
        
        # Objects registry for API compatibility
        self._objects_registry: Dict[str, Dict] = {}
    
    async def initialize(self) -> None:
        """Initialize the game world, agents, and all services."""
        try:
            # Create game state
            session_id = str(uuid.uuid4())
            self._game_state = GameState(session_id=session_id)
            
            # Build game world
            self._game = self._build_house_environment()
            
            # Initialize agent manager
            self._agent_manager = AgentManager(self._game)
            
            # Initialize infrastructure adapters
            self._agent_executor = GameOrchestratorAgentExecutor(self._agent_manager)
            
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
    
    def _build_house_environment(self) -> Game:
        """Create a house environment using the text adventure framework."""
        from ...text_adventure_games.house import build_house_game
        return build_house_game()
    
    async def _setup_agents(self) -> None:
        """Setup agents based on configuration."""
        try:
            # Define agent personas (extracted from GameLoop)
            agent_personas = {
                "alex_001": "I am Alex, a friendly and social person who loves to chat with others. I enjoy reading books and might want to explore the house. I'm curious about what others are doing and like to help when I can.",
                "alan_002": "I am Alan, a quiet and thoughtful person who likes to observe and think. I prefer to explore slowly and examine things carefully. I might be interested in food and practical items."
            }
            
            # Create domain entities and infrastructure strategies
            for agent_name, persona in agent_personas.items():
                # Create domain entity
                agent = Agent(
                    agent_id=agent_name,
                    character_name=agent_name,
                    persona=persona,
                    current_location=None,  # Will be set after world state query
                    is_active=True
                )
                self._agents[agent_name] = agent
                
                # Create infrastructure strategy
                agent_strategy = await self._create_agent_strategy(agent_name, persona)
                if agent_strategy and self._agent_manager:
                    self._agent_manager.register_agent_strategy(agent_name, agent_strategy)
                    
                    # Add to turn rotation (ensure game_state is not None)
                    if self._game_state:
                        self._turn_scheduler.add_agent_to_rotation(self._game_state, agent_name)
            
            self._logger.info(f"Set up {len(self._agents)} agents successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to setup agents: {e}")
            # Add agents to rotation even if strategy creation failed
            if self._game_state:
                for agent_name in ["alex_001", "alan_002"]:
                    self._turn_scheduler.add_agent_to_rotation(self._game_state, agent_name)
    
    async def _create_agent_strategy(self, character_name: str, persona: str):
        """Create either a manual or AI agent based on configuration."""
        agent_type = self._agent_config.get(character_name, "ai")  # Default to AI
        
        if agent_type == "manual":
            self._logger.info(f"Creating manual agent for {character_name}")
            return ManualAgent(character_name, persona)
        else:  # agent_type == "ai" or any other value
            try:
                self._logger.info(f"Creating AI agent for {character_name}")
                
                # Get initial world state by executing a look command for this character
                if self._game and character_name in self._game.characters:
                    character = self._game.characters[character_name]
                    initial_world_state = self._get_initial_world_state_for_agent(character)
                    return KaniAgent(character_name, persona, initial_world_state)
                else:
                    self._logger.warning(f"Character {character_name} not found, creating agent without initial state")
                    return KaniAgent(character_name, persona)
                    
            except Exception as e:
                self._logger.warning(f"Failed to create AI agent for {character_name}: {e}")
                self._logger.info(f"Falling back to manual agent for {character_name}")
                return ManualAgent(character_name, persona)
    
    def _get_initial_world_state_for_agent(self, character) -> str:
        """Get the initial world state for an agent by executing a look action."""
        from ...text_adventure_games.actions.generic import EnhancedLookAction
        
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
        """Add an event handler for action events."""
        self._event_publisher.add_event_handler(handler)
    
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
        
        # Reinitialize everything
        await self.initialize()