"""
AgentStrategyLoader - Configuration-Driven Agent Creation
=========================================================
Loads agent configurations from YAML files and creates appropriate agent strategies
with multi-engine support. Handles fallback mechanisms and error recovery.
"""

import logging
import os
import yaml
from typing import Dict, List, Optional, Any, Protocol
from pathlib import Path

from .agent_config import AgentConfig, AgentSystemConfig, ModelConfig
from ...infrastructure.agents.engine_factory import EngineFactory, EngineCreationError, create_engine_from_config
from ...domain.entities.agent_strategy import AgentStrategy

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Exception raised when configuration loading or validation fails."""
    pass


class AgentCreationError(Exception):
    """Exception raised when agent creation fails."""
    pass


class ConfigLoader:
    """
    Loads and validates agent configurations from YAML files.
    """
    
    @staticmethod
    def load_from_file(config_path: str) -> AgentSystemConfig:
        """
        Load agent configuration from YAML file.
        
        Args:
            config_path: Path to YAML configuration file
            
        Returns:
            Validated agent system configuration
            
        Raises:
            ConfigurationError: If file loading or validation fails
        """
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                raise ConfigurationError(f"Configuration file not found: {config_path}")
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            if not config_data:
                raise ConfigurationError(f"Empty or invalid YAML file: {config_path}")
            
            # Validate configuration using Pydantic
            system_config = AgentSystemConfig(**config_data)
            logger.info(f"Loaded configuration for {len(system_config.agents)} agents from {config_path}")
            
            return system_config
            
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML syntax in {config_path}: {e}") from e
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration from {config_path}: {e}") from e
    
    @staticmethod
    def load_from_dict(config_data: Dict[str, Any]) -> AgentSystemConfig:
        """
        Load agent configuration from dictionary.
        
        Args:
            config_data: Dictionary containing configuration data
            
        Returns:
            Validated agent system configuration
            
        Raises:
            ConfigurationError: If validation fails
        """
        try:
            system_config = AgentSystemConfig(**config_data)
            logger.info(f"Loaded configuration for {len(system_config.agents)} agents from dictionary")
            return system_config
            
        except Exception as e:
            raise ConfigurationError(f"Failed to validate configuration: {e}") from e


class AgentStrategyLoader:
    """
    Factory for creating agent strategies from configuration.
    
    Coordinates configuration loading, engine creation, and agent instantiation
    with comprehensive error handling and fallback mechanisms.
    """
    
    def __init__(self, fallback_to_manual: bool = True):
        self.engine_factory = EngineFactory()
        self.fallback_to_manual = fallback_to_manual
        self._created_agents: Dict[str, AgentStrategy] = {}
        
    def load_agents_from_file(self, config_path: str) -> Dict[str, AgentStrategy]:
        """
        Load all agents from a YAML configuration file.
        
        Args:
            config_path: Path to YAML configuration file
            
        Returns:
            Dictionary mapping agent_id to created strategy instances
            
        Raises:
            ConfigurationError: If configuration loading fails
        """
        system_config = ConfigLoader.load_from_file(config_path)
        return self.create_agents_from_config(system_config)
    
    def load_agents_from_dict(self, config_data: Dict[str, Any]) -> Dict[str, AgentStrategy]:
        """
        Load all agents from configuration dictionary.
        
        Args:
            config_data: Configuration data dictionary
            
        Returns:
            Dictionary mapping agent_id to created strategy instances
        """
        system_config = ConfigLoader.load_from_dict(config_data)
        return self.create_agents_from_config(system_config)
    
    def create_agents_from_config(self, system_config: AgentSystemConfig) -> Dict[str, AgentStrategy]:
        """
        Create all agent strategies from system configuration.
        
        Args:
            system_config: Validated system configuration
            
        Returns:
            Dictionary mapping agent_id to created strategy instances
        """
        agents = {}
        
        for agent_id, agent_config in system_config.agents.items():
            try:
                agent_strategy = self.create_single_agent(agent_config, system_config)
                agents[agent_id] = agent_strategy
                self._created_agents[agent_id] = agent_strategy
                
                logger.info(f"Successfully created {agent_config.strategy_type} agent: {agent_id}")
                
            except Exception as e:
                logger.error(f"Failed to create agent {agent_id}: {e}")
                
                if self.fallback_to_manual:
                    try:
                        fallback_agent = self._create_manual_fallback(agent_config)
                        agents[agent_id] = fallback_agent
                        self._created_agents[agent_id] = fallback_agent
                        logger.warning(f"Created manual fallback agent for {agent_id}")
                    except Exception as fallback_error:
                        logger.error(f"Failed to create fallback agent for {agent_id}: {fallback_error}")
                        continue
                else:
                    # Re-raise original error if no fallback
                    raise AgentCreationError(f"Failed to create agent {agent_id}") from e
        
        logger.info(f"Created {len(agents)} agents successfully")
        return agents
    
    def create_single_agent(self, agent_config: AgentConfig, system_config: AgentSystemConfig) -> AgentStrategy:
        """
        Create a single agent strategy from configuration.
        
        Args:
            agent_config: Configuration for the specific agent
            system_config: System-wide configuration
            
        Returns:
            Created agent strategy instance
            
        Raises:
            AgentCreationError: If agent creation fails
        """
        if agent_config.strategy_type == "kani":
            return self._create_kani_agent(agent_config)
        elif agent_config.strategy_type == "manual":
            return self._create_manual_agent(agent_config)
        elif agent_config.strategy_type == "custom":
            return self._create_custom_agent(agent_config)
        else:
            raise AgentCreationError(f"Unsupported strategy type: {agent_config.strategy_type}")
    
    def _create_kani_agent(self, config: AgentConfig) -> AgentStrategy:
        """Create a Kani-based agent with configured engine."""
        if not config.llm_config:
            raise AgentCreationError(f"LLM configuration required for kani agent {config.agent_id}")
        
        # Import here to avoid circular dependencies
        from ...infrastructure.agents.kani_agent import KaniAgent
        
        # Create engine from configuration
        try:
            engine = create_engine_from_config(config.llm_config, cache_key=f"{config.agent_id}_engine")
        except EngineCreationError as e:
            raise AgentCreationError(f"Failed to create engine for agent {config.agent_id}: {e}") from e
        
        # Get initial world state (will be set by GameOrchestrator)
        initial_world_state = None
        
        # Create Kani agent with engine
        try:
            agent = KaniAgent(
                character_name=config.character_name or config.agent_id,
                persona=config.persona,
                initial_world_state=initial_world_state,
                engine=engine  # Pass engine directly
            )
            
            # Set additional configuration
            agent.max_recent_actions = config.max_recent_actions
            
            return agent
            
        except Exception as e:
            raise AgentCreationError(f"Failed to create KaniAgent for {config.agent_id}: {e}") from e
    
    def _create_manual_agent(self, config: AgentConfig) -> AgentStrategy:
        """Create a manual agent for debugging/testing."""
        from ...infrastructure.agents.kani_agent import ManualAgent
        
        try:
            return ManualAgent(
                character_name=config.character_name or config.agent_id,
                persona=config.persona
            )
        except Exception as e:
            raise AgentCreationError(f"Failed to create ManualAgent for {config.agent_id}: {e}") from e
    
    def _create_custom_agent(self, config: AgentConfig) -> AgentStrategy:
        """Create a custom agent strategy from class path."""
        if not config.custom_strategy_class:
            raise AgentCreationError(f"custom_strategy_class required for custom agent {config.agent_id}")
        
        try:
            # Import the custom class dynamically
            module_path, class_name = config.custom_strategy_class.rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            strategy_class = getattr(module, class_name)
            
            # Create instance with configuration
            return strategy_class(
                character_name=config.character_name,
                persona=config.persona,
                **config.custom_params
            )
            
        except Exception as e:
            raise AgentCreationError(f"Failed to create custom agent {config.agent_id}: {e}") from e
    
    def _create_manual_fallback(self, config: AgentConfig) -> AgentStrategy:
        """Create a manual agent as fallback when primary creation fails."""
        from ...infrastructure.agents.kani_agent import ManualAgent
        
        return ManualAgent(
            character_name=config.character_name or config.agent_id,
            persona=f"FALLBACK: {config.persona}"
        )
    
    def get_created_agents(self) -> Dict[str, AgentStrategy]:
        """Get dictionary of all successfully created agents."""
        return self._created_agents.copy()
    
    def get_supported_strategies(self) -> List[str]:
        """Get list of supported strategy types."""
        return ["kani", "manual", "custom"]
    
    def get_supported_providers(self) -> List[str]:
        """Get list of supported LLM providers."""
        return self.engine_factory.get_supported_providers()
    
    def validate_configuration(self, config_path: str) -> tuple[bool, List[str]]:
        """
        Validate a configuration file without creating agents.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        try:
            system_config = ConfigLoader.load_from_file(config_path)
            
            # Validate each agent configuration
            for agent_id, agent_config in system_config.agents.items():
                try:
                    # Validate LLM configuration for kani agents
                    if agent_config.strategy_type == "kani" and agent_config.llm_config:
                        is_valid, error_msg = self.engine_factory.validate_config(agent_config.llm_config)
                        if not is_valid:
                            errors.append(f"Agent {agent_id}: {error_msg}")
                    
                    # Validate custom strategy class path
                    if agent_config.strategy_type == "custom" and not agent_config.custom_strategy_class:
                        errors.append(f"Agent {agent_id}: custom_strategy_class required for custom agents")
                        
                except Exception as e:
                    errors.append(f"Agent {agent_id}: {e}")
            
        except ConfigurationError as e:
            errors.append(str(e))
        except Exception as e:
            errors.append(f"Unexpected validation error: {e}")
        
        return len(errors) == 0, errors


def create_loader(fallback_to_manual: bool = True) -> AgentStrategyLoader:
    """
    Convenience function to create an AgentStrategyLoader.
    
    Args:
        fallback_to_manual: Whether to create manual agents when LLM creation fails
        
    Returns:
        Configured AgentStrategyLoader instance
    """
    return AgentStrategyLoader(fallback_to_manual=fallback_to_manual)