"""Environment-based configuration management."""

from typing import Optional
from pydantic_settings import BaseSettings


class ClaudeApiSettings(BaseSettings):
    """Configuration for Anthropic Claude API."""
    
    # Required settings (made optional for testing)
    anthropic_api_key: Optional[str] = None
    
    # Model configuration
    model_name: str = "claude-sonnet-4-20250514"
    enable_thinking: bool = True
    max_tokens: int = 2000
    
    # API configuration
    api_timeout: int = 30
    max_retries: int = 3
    base_backoff_delay: float = 1.0  # seconds
    max_backoff_delay: float = 60.0  # seconds
    
    model_config = {
        "env_file": ".env",
        "env_prefix": "CLAUDE_"
    }


# Global settings instance
settings = ClaudeApiSettings()