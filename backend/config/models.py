"""
Configuration Models
===================

Pydantic models for validating YAML configuration files.
These models ensure type safety and provide validation for
LLM engine configs, agent configs, and prompt templates.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
import os


class EngineConfig(BaseModel):
    """Configuration for an LLM engine (OpenAI, Anthropic, etc.)."""
    api_key_env: str = Field(..., description="Environment variable name for API key")
    model: str = Field(..., description="Model identifier")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(default=None, ge=1, description="Maximum tokens to generate")
    timeout: int = Field(default=30, ge=1, description="Request timeout in seconds")
    retry_attempts: int = Field(default=3, ge=0, description="Number of retry attempts")
    
    def get_api_key(self) -> Optional[str]:
        """Get the API key from environment variable."""
        return os.getenv(self.api_key_env)


class LLMConfig(BaseModel):
    """Top-level LLM configuration containing multiple engines."""
    engines: Dict[str, EngineConfig] = Field(..., description="Available engines")
    default_engine: str = Field(..., description="Default engine to use")
    
    def get_engine(self, engine_name: Optional[str] = None) -> EngineConfig:
        """Get engine config, falling back to default if not specified."""
        name = engine_name or self.default_engine
        if name not in self.engines:
            raise ValueError(f"Engine '{name}' not found in configuration")
        return self.engines[name]


class AgentConfig(BaseModel):
    """Configuration for an individual agent."""
    name: str = Field(..., description="Display name of the agent")
    persona: str = Field(..., description="Agent personality and behavior description")
    engine: Optional[str] = Field(default=None, description="Override engine for this agent")
    model: Optional[str] = Field(default=None, description="Override model for this agent")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0, description="Override temperature")
    max_tokens: Optional[int] = Field(default=None, ge=1, description="Override max tokens")
    prompt_template: Optional[str] = Field(default=None, description="Custom prompt template name")


class DefaultAgentConfig(BaseModel):
    """Default configuration applied to all agents."""
    engine: str = Field(default="openai", description="Default engine")
    model: str = Field(default="gpt-4o-mini", description="Default model")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Default temperature")
    max_tokens: Optional[int] = Field(default=None, ge=1, description="Default max tokens")
    prompt_template: str = Field(default="default_agent_prompt", description="Default prompt template")


class AgentsConfig(BaseModel):
    """Configuration for all agents."""
    agents: Dict[str, AgentConfig] = Field(..., description="Individual agent configurations")
    default_agent_config: DefaultAgentConfig = Field(default_factory=DefaultAgentConfig, description="Default settings")
    
    def get_agent_config(self, agent_id: str) -> AgentConfig:
        """Get agent config, raising error if not found."""
        if agent_id not in self.agents:
            raise ValueError(f"Agent '{agent_id}' not found in configuration")
        return self.agents[agent_id]
    
    def get_effective_config(self, agent_id: str) -> Dict[str, Any]:
        """Get the effective configuration for an agent (merged with defaults)."""
        agent_config = self.get_agent_config(agent_id)
        defaults = self.default_agent_config
        
        return {
            "name": agent_config.name,
            "persona": agent_config.persona,
            "engine": agent_config.engine or defaults.engine,
            "model": agent_config.model or defaults.model,
            "temperature": agent_config.temperature if agent_config.temperature is not None else defaults.temperature,
            "max_tokens": agent_config.max_tokens if agent_config.max_tokens is not None else defaults.max_tokens,
            "prompt_template": agent_config.prompt_template or defaults.prompt_template,
        }


class PromptTemplate(BaseModel):
    """Individual prompt template with content."""
    content: str = Field(..., description="Template content with {variable} placeholders")
    description: Optional[str] = Field(default=None, description="Description of this template's purpose")


class PromptComposition(BaseModel):
    """Composition of multiple templates into a complete prompt."""
    templates: List[str] = Field(..., description="List of template names to combine")
    separator: str = Field(default="\n\n", description="Separator between templates")
    description: Optional[str] = Field(default=None, description="Description of this composition")


class PromptsConfig(BaseModel):
    """Configuration for prompt templates and compositions."""
    templates: Dict[str, PromptTemplate] = Field(..., description="Available prompt templates")
    compositions: Dict[str, PromptComposition] = Field(..., description="Template compositions")
    
    def get_template(self, template_name: str) -> PromptTemplate:
        """Get a prompt template by name."""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found in configuration")
        return self.templates[template_name]
    
    def get_composition(self, composition_name: str) -> PromptComposition:
        """Get a prompt composition by name."""
        if composition_name not in self.compositions:
            raise ValueError(f"Composition '{composition_name}' not found in configuration")
        return self.compositions[composition_name]
    
    def build_prompt(self, composition_name: str, variables: Dict[str, str]) -> str:
        """Build a complete prompt from a composition with variable substitution."""
        composition = self.get_composition(composition_name)
        
        # Combine all templates in the composition
        template_parts = []
        for template_name in composition.templates:
            template = self.get_template(template_name)
            # Substitute variables in the template content
            content = template.content.format(**variables)
            template_parts.append(content)
        
        # Join with the specified separator
        return composition.separator.join(template_parts)


class DefaultsConfig(BaseModel):
    """Default values and fallbacks for the configuration system."""
    llm_defaults: Dict[str, Any] = Field(default_factory=dict, description="Default LLM settings")
    agent_defaults: Dict[str, Any] = Field(default_factory=dict, description="Default agent settings")
    prompt_defaults: Dict[str, Any] = Field(default_factory=dict, description="Default prompt settings")
    system_defaults: Dict[str, Any] = Field(default_factory=dict, description="System-wide defaults")