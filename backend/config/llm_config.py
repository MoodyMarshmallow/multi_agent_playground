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