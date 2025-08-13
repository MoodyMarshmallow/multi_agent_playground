"""
Engine Factory - Multi-Engine Support for Kani Agents
=====================================================
Factory for creating different LLM engines (OpenAI, Anthropic, HuggingFace, etc.)
based on configuration. Provides a unified interface for engine creation.
"""

import logging
from typing import Any, Dict, Optional
from ...application.config.agent_config import ModelConfig

logger = logging.getLogger(__name__)


class EngineCreationError(Exception):
    """Exception raised when engine creation fails."""
    pass


class EngineFactory:
    """
    Factory for creating Kani-compatible LLM engines from configuration.
    
    Supports multiple providers with graceful fallback mechanisms.
    """
    
    def __init__(self):
        self._supported_providers = {
            "openai": self._create_openai_engine,
            "anthropic": self._create_anthropic_engine,
        }
        # Note: HuggingFace support can be added later when import path is confirmed
        
    def create_engine(self, model_config: ModelConfig) -> Any:
        """
        Create a Kani engine from model configuration.
        
        Args:
            model_config: Model configuration containing provider and settings
            
        Returns:
            Kani-compatible engine instance
            
        Raises:
            EngineCreationError: If engine creation fails
        """
        provider = model_config.provider
        
        if provider not in self._supported_providers:
            raise EngineCreationError(f"Unsupported provider: {provider}")
        
        try:
            engine_creator = self._supported_providers[provider]
            engine = engine_creator(model_config)
            logger.info(f"Successfully created {provider} engine with model {model_config.model_name}")
            return engine
            
        except Exception as e:
            error_msg = f"Failed to create {provider} engine: {e}"
            logger.error(error_msg)
            raise EngineCreationError(error_msg) from e
    
    def _create_openai_engine(self, config: ModelConfig) -> Any:
        """Create OpenAI engine."""
        try:
            from kani.engines.openai import OpenAIEngine
        except ImportError as e:
            raise EngineCreationError("OpenAI engine not available. Install with: pip install kani[openai]") from e
        
        api_key = config.get_api_key()
        if not api_key:
            raise EngineCreationError("OpenAI API key is required")
        
        # Build engine parameters with proper types
        engine_params: Dict[str, Any] = {
            "api_key": api_key,
            "model": config.model_name,
        }
        
        # Add optional parameters with proper types
        if config.temperature is not None:
            engine_params["temperature"] = float(config.temperature)
        if config.max_tokens is not None:
            engine_params["max_tokens"] = int(config.max_tokens)
        if config.timeout is not None:
            engine_params["timeout"] = int(config.timeout)
            
        # Add any extra parameters (these should be validated by caller)
        for key, value in config.extra_params.items():
            engine_params[key] = value
        
        return OpenAIEngine(**engine_params)
    
    def _create_anthropic_engine(self, config: ModelConfig) -> Any:
        """Create Anthropic engine."""
        try:
            from kani.engines.anthropic import AnthropicEngine
        except ImportError as e:
            raise EngineCreationError("Anthropic engine not available. Install with: pip install kani[anthropic]") from e
        
        api_key = config.get_api_key()
        if not api_key:
            raise EngineCreationError("Anthropic API key is required")
        
        # Build engine parameters with proper types
        engine_params: Dict[str, Any] = {
            "api_key": api_key,
            "model": config.model_name,
        }
        
        # Add optional parameters with proper types
        if config.temperature is not None:
            engine_params["temperature"] = float(config.temperature)
        if config.max_tokens is not None:
            engine_params["max_tokens"] = int(config.max_tokens)
        if config.timeout is not None:
            engine_params["timeout"] = int(config.timeout)
            
        # Add any extra parameters (these should be validated by caller)
        for key, value in config.extra_params.items():
            engine_params[key] = value
        
        return AnthropicEngine(**engine_params)
    
    # Note: HuggingFace engine support can be added here when import path is confirmed
    
    def get_supported_providers(self) -> list[str]:
        """Get list of supported provider names."""
        return list(self._supported_providers.keys())
    
    def is_provider_supported(self, provider: str) -> bool:
        """Check if a provider is supported."""
        return provider in self._supported_providers
    
    def validate_config(self, config: ModelConfig) -> tuple[bool, Optional[str]]:
        """
        Validate a model configuration without creating the engine.
        
        Args:
            config: Model configuration to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check provider support
            if not self.is_provider_supported(config.provider):
                return False, f"Unsupported provider: {config.provider}"
            
            # Check API key availability
            if config.provider in ["openai", "anthropic"]:
                api_key = config.get_api_key()
                if not api_key:
                    return False, f"API key required for {config.provider}"
            
            # Check required fields
            if not config.model_name:
                return False, "Model name is required"
            
            return True, None
            
        except Exception as e:
            return False, str(e)


class EngineManager:
    """
    Manager for engine instances with caching and lifecycle management.
    """
    
    def __init__(self):
        self._factory = EngineFactory()
        self._engine_cache: Dict[str, Any] = {}
    
    def get_engine(self, config: ModelConfig, cache_key: Optional[str] = None) -> Any:
        """
        Get or create an engine with optional caching.
        
        Args:
            config: Model configuration
            cache_key: Optional key for caching engine instances
            
        Returns:
            Kani-compatible engine instance
        """
        if cache_key and cache_key in self._engine_cache:
            logger.debug(f"Using cached engine for key: {cache_key}")
            return self._engine_cache[cache_key]
        
        engine = self._factory.create_engine(config)
        
        if cache_key:
            self._engine_cache[cache_key] = engine
            logger.debug(f"Cached engine with key: {cache_key}")
        
        return engine
    
    def clear_cache(self) -> None:
        """Clear all cached engines."""
        self._engine_cache.clear()
        logger.info("Engine cache cleared")
    
    def get_cached_engines(self) -> Dict[str, Any]:
        """Get dictionary of all cached engines."""
        return self._engine_cache.copy()


# Global engine manager instance
engine_manager = EngineManager()


def create_engine_from_config(config: ModelConfig, cache_key: Optional[str] = None) -> Any:
    """
    Convenience function to create an engine from configuration.
    
    Args:
        config: Model configuration
        cache_key: Optional caching key
        
    Returns:
        Kani-compatible engine instance
    """
    return engine_manager.get_engine(config, cache_key)