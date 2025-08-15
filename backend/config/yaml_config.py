"""
YAML Configuration Manager
==========================

Central configuration manager that loads and validates YAML configuration files.
Provides type-safe access to LLM engines, agent configs, and prompt templates.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from functools import lru_cache

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Look for .env file in the project root
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        logging.getLogger(__name__).debug(f"Loaded .env file from: {env_path}")
except ImportError:
    # python-dotenv not installed, skip loading .env file
    pass

from .models import (
    LLMConfig, AgentsConfig, PromptsConfig, DefaultsConfig,
    EngineConfig, AgentConfig
)

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Central configuration manager for the multi-agent playground.
    
    Loads and validates YAML configuration files, provides type-safe
    access to configurations, and handles fallbacks.
    """
    
    def __init__(self, config_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Directory containing YAML config files. 
                       Defaults to the directory of this file.
        """
        if config_dir is None:
            config_dir = Path(__file__).parent
        
        self.config_dir = Path(config_dir)
        
        # Configuration caches
        self._llm_config: Optional[LLMConfig] = None
        self._agents_config: Optional[AgentsConfig] = None
        self._prompts_config: Optional[PromptsConfig] = None
        self._defaults_config: Optional[DefaultsConfig] = None
        
        logger.info(f"ConfigManager initialized with config_dir: {self.config_dir}")
    
    @property
    def llm_config(self) -> LLMConfig:
        """Get LLM configuration, loading if necessary."""
        if self._llm_config is None:
            self._llm_config = self._load_llm_config()
        return self._llm_config
    
    @property
    def agents_config(self) -> AgentsConfig:
        """Get agents configuration, loading if necessary."""
        if self._agents_config is None:
            self._agents_config = self._load_agents_config()
        return self._agents_config
    
    @property
    def prompts_config(self) -> PromptsConfig:
        """Get prompts configuration, loading if necessary."""
        if self._prompts_config is None:
            self._prompts_config = self._load_prompts_config()
        return self._prompts_config
    
    @property
    def defaults_config(self) -> DefaultsConfig:
        """Get defaults configuration, loading if necessary."""
        if self._defaults_config is None:
            self._defaults_config = self._load_defaults_config()
        return self._defaults_config
    
    def _load_yaml_file(self, filename: str) -> Dict[str, Any]:
        """Load and parse a YAML file."""
        file_path = self.config_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                logger.debug(f"Loaded YAML file: {file_path}")
                return data or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file {file_path}: {e}")
        except Exception as e:
            raise RuntimeError(f"Error reading file {file_path}: {e}")
    
    def _load_llm_config(self) -> LLMConfig:
        """Load and validate LLM configuration."""
        try:
            data = self._load_yaml_file("llm.yaml")
            config = LLMConfig(**data)
            logger.info("LLM configuration loaded successfully")
            return config
        except Exception as e:
            logger.error(f"Failed to load LLM config: {e}")
            raise
    
    def _load_agents_config(self) -> AgentsConfig:
        """Load and validate agents configuration."""
        try:
            data = self._load_yaml_file("agents.yaml")
            config = AgentsConfig(**data)
            logger.info("Agents configuration loaded successfully")
            return config
        except Exception as e:
            logger.error(f"Failed to load agents config: {e}")
            raise
    
    def _load_prompts_config(self) -> PromptsConfig:
        """Load and validate prompts configuration."""
        try:
            data = self._load_yaml_file("prompts.yaml")
            config = PromptsConfig(**data)
            logger.info("Prompts configuration loaded successfully")
            return config
        except Exception as e:
            logger.error(f"Failed to load prompts config: {e}")
            raise
    
    def _load_defaults_config(self) -> DefaultsConfig:
        """Load and validate defaults configuration."""
        try:
            data = self._load_yaml_file("defaults.yaml")
            config = DefaultsConfig(**data)
            logger.info("Defaults configuration loaded successfully")
            return config
        except Exception as e:
            logger.warning(f"Failed to load defaults config: {e}. Using empty defaults.")
            return DefaultsConfig()
    
    def get_engine_config(self, engine_name: Optional[str] = None) -> EngineConfig:
        """
        Get engine configuration.
        
        Args:
            engine_name: Name of the engine. If None, uses default engine.
            
        Returns:
            EngineConfig for the specified engine.
        """
        return self.llm_config.get_engine(engine_name)
    
    def get_agent_config(self, agent_id: str) -> AgentConfig:
        """
        Get configuration for a specific agent.
        
        Args:
            agent_id: ID of the agent.
            
        Returns:
            AgentConfig for the specified agent.
        """
        return self.agents_config.get_agent_config(agent_id)
    
    def get_effective_agent_config(self, agent_id: str) -> Dict[str, Any]:
        """
        Get the effective configuration for an agent (merged with defaults).
        
        Args:
            agent_id: ID of the agent.
            
        Returns:
            Dictionary with effective configuration.
        """
        return self.agents_config.get_effective_config(agent_id)
    
    def build_system_prompt(self, agent_id: str, variables: Optional[Dict[str, str]] = None) -> str:
        """
        Build a complete system prompt for an agent.
        
        Args:
            agent_id: ID of the agent.
            variables: Variables to substitute in the prompt template.
                      Automatically includes 'character_name' and 'persona'.
            
        Returns:
            Complete system prompt string.
        """
        try:
            # Get agent configuration
            agent_config = self.get_effective_agent_config(agent_id)
            
            # Prepare variables for template substitution
            prompt_variables = {
                'character_name': agent_config['name'],
                'persona': agent_config['persona'],
            }
            if variables:
                prompt_variables.update(variables)
            
            # Get the prompt template name
            template_name = agent_config.get('prompt_template', 'default_agent_prompt')
            
            # Build the prompt
            prompt = self.prompts_config.build_prompt(template_name, prompt_variables)
            logger.debug(f"Built system prompt for {agent_id} using template '{template_name}'")
            return prompt
            
        except Exception as e:
            logger.error(f"Failed to build system prompt for {agent_id}: {e}")
            raise
    
    def reload_configs(self):
        """Reload all configuration files from disk."""
        logger.info("Reloading all configurations")
        self._llm_config = None
        self._agents_config = None
        self._prompts_config = None
        self._defaults_config = None
    
    def validate_configs(self) -> bool:
        """
        Validate all configurations.
        
        Returns:
            True if all configurations are valid, False otherwise.
        """
        try:
            # Access all configs to trigger loading and validation
            _ = self.llm_config
            _ = self.agents_config
            _ = self.prompts_config
            _ = self.defaults_config
            logger.info("All configurations validated successfully")
            return True
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False


# Global config manager instance
_config_manager: Optional[ConfigManager] = None


@lru_cache(maxsize=1)
def get_config_manager() -> ConfigManager:
    """
    Get the global configuration manager instance.
    
    Returns:
        ConfigManager instance.
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def reload_global_config():
    """Reload the global configuration manager."""
    global _config_manager
    if _config_manager is not None:
        _config_manager.reload_configs()
    # Clear the LRU cache
    get_config_manager.cache_clear()
    _config_manager = None