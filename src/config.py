"""
Configuration settings for the MCP server.
"""

from typing import Dict, Any

class Config:
    """
    Configuration class for the MCP server.
    """

    def __init__(self):
        """
        Initialize the configuration.
        """
        self._config = {
            "bridge": {
                "type": "mock",  # Default to mock bridge
                "config": {}
            },
            # Other configuration settings
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key.
            default: Default value if key is not found.

        Returns:
            Any: Configuration value.
        """
        keys = key.split(".")
        value = self._config
        for k in keys:
            if k not in value:
                return default
            value = value[k]
        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key.
            value: Configuration value.
        """
        keys = key.split(".")
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value