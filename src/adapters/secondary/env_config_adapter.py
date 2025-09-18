"""Environment configuration adapter implementation."""

from core.domain.configuration import AppConfig
from ports.configuration import ConfigurationPort


class EnvConfigAdapter(ConfigurationPort):
    """Implementation of configuration management using environment variables."""

    def load_config(self) -> AppConfig:
        """Load application configuration from environment variables.

        Returns:
            AppConfig instance.

        Raises:
            ValueError: If configuration is invalid.
        """
        return AppConfig.from_env()
