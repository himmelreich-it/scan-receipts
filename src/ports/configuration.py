"""Configuration port."""

from abc import ABC, abstractmethod

from core.domain.configuration import AppConfig


class ConfigurationPort(ABC):
    """Interface for configuration management."""

    @abstractmethod
    def load_config(self) -> AppConfig:
        """Load application configuration.

        Returns:
            AppConfig instance.

        Raises:
            ValueError: If configuration is invalid.
        """
        pass
