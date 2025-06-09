"""
Multi-Agent Playground - LLM Configuration
==========================================
Configuration settings for LLM integration including API keys and model parameters.
"""

import os
from pathlib import Path
from typing import Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Look for .env file in the project root (two levels up from this file)
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # python-dotenv not installed, skip loading .env file
    pass


class LLMConfig:
    """Configuration class for LLM settings."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: Optional[int] = None
    
    # Kani Configuration
    KANI_RETRY_ATTEMPTS: int = 3
    KANI_TIMEOUT: int = 30
    
    @classmethod
    def get_openai_api_key(cls) -> str:
        """
        Get OpenAI API key from environment or raise an error if not found.
        
        Returns:
            str: The OpenAI API key
            
        Raises:
            ValueError: If API key is not found
        """
        api_key = cls.OPENAI_API_KEY
        if not api_key:
            raise ValueError(
                "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
            )
        return api_key
    
    @classmethod
    def validate_config(cls) -> bool:
        """
        Validate that all required configuration is present.
        
        Returns:
            bool: True if configuration is valid
            
        Raises:
            ValueError: If required configuration is missing
        """
        try:
            cls.get_openai_api_key()
            return True
        except ValueError as e:
            raise ValueError(f"LLM configuration validation failed: {e}") 