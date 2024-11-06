"""
This module provides a set of classes for parsing different types of configuration files.
It includes an abstract base class ConfigParser and concrete implementations for
YAML, TOML, and .env file formats.
"""

from abc import ABC, abstractmethod
import yaml
import toml
import os
from dotenv import dotenv_values, set_key


class ConfigParser(ABC):
    """
    ConfigParser is an abstract base class for configuration file parsers.
    """

    @abstractmethod
    def parse(self, config_file: str) -> dict:
        """
        Parse the configuration file and return its contents as a dictionary.

        Args:
            config_file (str): The path to the configuration file.

        Returns:
            dict: A dictionary containing the parsed configuration.
        """
        pass

    @abstractmethod
    def update(self, config_file: str, key: str, value: str):
        """
        Update a value in the configuration file.

        Args:
            config_file (str): The path to the configuration file.
            key (str): The key to update.
            value (str): The new value.
        """
        pass


class YAMLConfigParser(ConfigParser):
    """YAMLConfigParser is a class that parses YAML configuration files."""

    def parse(self, config_file: str) -> dict:
        with open(config_file, "r") as file:
            return yaml.safe_load(file)

    def update(self, config_file: str, key: str, value: str):
        with open(config_file, "r") as file:
            config = yaml.safe_load(file) or {}
        
        config[key] = value
        
        with open(config_file, "w") as file:
            yaml.dump(config, file)


class TOMLConfigParser(ConfigParser):
    """TOMLConfigParser is a class that parses TOML configuration files."""

    def parse(self, config_file: str) -> dict:
        with open(config_file, "r") as file:
            return toml.load(file)

    def update(self, config_file: str, key: str, value: str):
        with open(config_file, "r") as file:
            config = toml.load(file)
        
        config[key] = value
        
        with open(config_file, "w") as file:
            toml.dump(config, file)


class ENVConfigParser(ConfigParser):
    """ENVConfigParser is a class that parses .env configuration files."""

    def parse(self, config_file: str) -> dict:
        if not os.path.isfile(config_file):
            raise FileNotFoundError(f"Configuration file '{config_file}' not found.")
        return dotenv_values(config_file)

    def update(self, config_file: str, key: str, value: str):
        """
        Update a value in the .env file.
        
        Args:
            config_file (str): The path to the .env file.
            key (str): The key to update.
            value (str): The new value.
        """
        set_key(config_file, key, value)