"""
Agent Configuration Models
==========================
Pydantic models for validating and managing agent configurations from YAML files.
These models support multi-engine agent strategies with flexible configuration.
"""

from typing import Dict, Any, Optional, List, Literal
from pydantic import BaseModel, Field, validator
import os


class ModelConfig(BaseModel):
    """
    Configuration for LLM model and engine settings.
    
    Supports multiple providers (OpenAI, Anthropic, HuggingFace, etc.)
    with provider-specific configuration options.
    """
    provider: Literal["openai", "anthropic", "custom"] = Field(
        ..., 
        description="LLM provider type"
    )
    model_name: str = Field(
        ..., 
        description="Specific model name (e.g., 'gpt-4o-mini', 'claude-3-haiku')"
    )
    api_key_env: Optional[str] = Field(
        None,
        description="Environment variable name containing the API key"
    )
    api_key: Optional[str] = Field(
        None,
        description="Direct API key (not recommended for production)"
    )
    temperature: float = Field(
        0.7, 
        ge=0.0, 
        le=2.0, 
        description="Sampling temperature for model responses"
    )
    max_tokens: Optional[int] = Field(
        None, 
        ge=1, 
        description="Maximum tokens in model response"
    )
    timeout: int = Field(
        30, 
        ge=1, 
        description="Request timeout in seconds"
    )
    # Provider-specific settings
    extra_params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Provider-specific additional parameters"
    )
    
    @validator('api_key_env')
    def validate_api_key_env(cls, v, values):
        """Validate that API key is available either directly or via environment."""
        if v and not values.get('api_key'):
            # Check if environment variable exists
            if not os.getenv(v):
                raise ValueError(f"Environment variable {v} not found")
        elif not v and not values.get('api_key'):
            # Default API key environment variables
            provider = values.get('provider')
            if provider == 'openai':
                default_env = 'OPENAI_API_KEY'
            elif provider == 'anthropic':
                default_env = 'ANTHROPIC_API_KEY'
            else:
                raise ValueError(f"API key required for provider {provider}")
            
            if not os.getenv(default_env):
                raise ValueError(f"API key required: set {default_env} environment variable or provide api_key")
            return default_env
        return v
    
    def get_api_key(self) -> str:
        """Get the API key from environment or direct configuration."""
        if self.api_key:
            return self.api_key
        elif self.api_key_env:
            return os.getenv(self.api_key_env) or ""
        else:
            # Use default environment variables
            if self.provider == 'openai':
                return os.getenv('OPENAI_API_KEY', "")
            elif self.provider == 'anthropic':
                return os.getenv('ANTHROPIC_API_KEY', "")
            return ""


class AgentConfig(BaseModel):
    """
    Configuration for a single agent in the multi-agent simulation.
    
    Defines the agent's identity, strategy type, model configuration,
    and behavioral parameters.
    """
    # Agent Identity
    agent_id: str = Field(
        ..., 
        description="Unique identifier for the agent"
    )
    character_name: Optional[str] = Field(
        None,
        description="Character name in the game (defaults to agent_id)"
    )
    
    # Strategy Configuration
    strategy_type: Literal["kani", "manual", "custom"] = Field(
        "kani",
        description="Type of agent strategy to use"
    )
    
    # Agent Behavior
    persona: str = Field(
        ...,
        description="Agent's personality and behavioral description"
    )
    initial_location: Optional[str] = Field(
        None,
        description="Starting location for the agent"
    )
    
    # Model Configuration (only for LLM-based agents)
    llm_config: Optional[ModelConfig] = Field(
        None,
        description="LLM configuration for kani-based agents"
    )
    
    # Agent-specific Settings
    max_recent_actions: int = Field(
        5,
        ge=1,
        description="Number of recent actions to remember for context"
    )
    is_active: bool = Field(
        True,
        description="Whether the agent participates in turns"
    )
    
    # Custom Strategy Settings
    custom_strategy_class: Optional[str] = Field(
        None,
        description="Full class path for custom strategy implementations"
    )
    custom_params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional parameters for custom strategies"
    )
    
    @validator('character_name', always=True)
    def set_character_name(cls, v, values):
        """Set character_name to agent_id if not provided."""
        return v or values.get('agent_id')
    
    @validator('llm_config')
    def validate_llm_config_for_strategy(cls, v, values):
        """Ensure llm_config is provided for kani-based agents."""
        strategy_type = values.get('strategy_type')
        if strategy_type == 'kani' and not v:
            raise ValueError("llm_config is required for kani strategy type")
        return v


class AgentSystemConfig(BaseModel):
    """
    Complete configuration for the agent system.
    
    Contains all agent definitions and system-level settings.
    """
    agents: Dict[str, AgentConfig] = Field(
        ...,
        description="Dictionary of agent configurations by agent_id"
    )
    
    # System Settings
    default_strategy: Literal["kani", "manual"] = Field(
        "kani",
        description="Default strategy type for agents"
    )
    fallback_to_manual: bool = Field(
        True,
        description="Whether to fallback to manual agents if LLM creation fails"
    )
    max_initialization_retries: int = Field(
        3,
        ge=1,
        description="Maximum retries for agent initialization"
    )
    
    @validator('agents')
    def validate_unique_character_names(cls, v):
        """Ensure all character names are unique."""
        character_names = []
        for agent_config in v.values():
            char_name = agent_config.character_name
            if char_name in character_names:
                raise ValueError(f"Duplicate character name: {char_name}")
            character_names.append(char_name)
        return v


class AgentConfigDefaults:
    """
    Default configurations for common agent setups.
    """
    
    @staticmethod
    def openai_gpt4_mini() -> ModelConfig:
        """Default OpenAI GPT-4o-mini configuration."""
        return ModelConfig(
            provider="openai",
            model_name="gpt-4o-mini",
            api_key_env="OPENAI_API_KEY",
            api_key=None,
            temperature=0.7,
            max_tokens=None,
            timeout=30,
            extra_params={}
        )
    
    @staticmethod
    def anthropic_haiku() -> ModelConfig:
        """Default Anthropic Claude-3-haiku configuration."""
        return ModelConfig(
            provider="anthropic",
            model_name="claude-3-haiku-20240307",
            api_key_env="ANTHROPIC_API_KEY",
            api_key=None,
            temperature=0.7,
            max_tokens=None,
            timeout=30,
            extra_params={}
        )
    
    @staticmethod
    def friendly_agent(agent_id: str) -> AgentConfig:
        """Template for a friendly, social agent."""
        return AgentConfig(
            agent_id=agent_id,
            character_name=agent_id,
            strategy_type="kani",
            persona="I am a friendly and social person who loves to chat with others. "
                   "I enjoy reading books and might want to explore the house. "
                   "I'm curious about what others are doing and like to help when I can.",
            initial_location=None,
            llm_config=AgentConfigDefaults.openai_gpt4_mini(),
            max_recent_actions=5,
            is_active=True,
            custom_strategy_class=None,
            custom_params={}
        )
    
    @staticmethod
    def thoughtful_agent(agent_id: str) -> AgentConfig:
        """Template for a quiet, thoughtful agent."""
        return AgentConfig(
            agent_id=agent_id,
            character_name=agent_id,
            strategy_type="kani",
            persona="I am a quiet and thoughtful person who likes to observe and think. "
                   "I prefer to explore slowly and examine things carefully. "
                   "I might be interested in food and practical items.",
            initial_location=None,
            llm_config=AgentConfigDefaults.openai_gpt4_mini(),
            max_recent_actions=5,
            is_active=True,
            custom_strategy_class=None,
            custom_params={}
        )