"""Configuration management for the receipt scanner application.

DEPRECATED: This module is kept for backward compatibility.
Use core.domain.configuration instead.
"""

# Re-export from new location for backward compatibility
from core.domain.configuration import REQUIRED_ENV_VARS, AppConfig

__all__ = ["REQUIRED_ENV_VARS", "AppConfig"]