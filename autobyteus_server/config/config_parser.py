"""
This module provides a set of classes for parsing different types of configuration files.
It includes an abstract base class ConfigParser and concrete implementations for
YAML, TOML, and .env file formats.
"""

from abc import ABC, abstractmethod
import yaml  # For parsing YAML files
import toml  # For parsing TOML files
import os  # For file path operations
from dotenv import dotenv_values  # For parsing .env files


class ConfigParser(ABC):
    """
    ConfigParser is an abstract base class for configuration file parsers.
    
    This class defines a common interface for all configuration parsers,
    ensuring that all concrete implementations have a `parse` method.
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


class YAMLConfigParser(ConfigParser):
    """
    YAMLConfigParser is a class that parses YAML configuration files.

    This class implements the ConfigParser interface for YAML files.
    """

    def parse(self, config_file: str) -> dict:
        """
        Parse a YAML configuration file.

        Args:
            config_file (str): The path to the YAML configuration file.

        Returns:
            dict: A dictionary containing the parsed YAML configuration.
        """
        with open(config_file, "r") as file:
            # Use safe_load to prevent arbitrary code execution
            return yaml.safe_load(file)


class TOMLConfigParser(ConfigParser):
    """
    TOMLConfigParser is a class that parses TOML configuration files.

    This class implements the ConfigParser interface for TOML files.
    """

    def parse(self, config_file: str) -> dict:
        """
        Parse a TOML configuration file.

        Args:
            config_file (str): The path to the TOML configuration file.

        Returns:
            dict: A dictionary containing the parsed TOML configuration.
        """
        with open(config_file, "r") as file:
            return toml.load(file)


class ENVConfigParser(ConfigParser):
    """
    ENVConfigParser is a class that parses .env configuration files.

    This class implements the ConfigParser interface for .env files.
    """

    def parse(self, config_file: str) -> dict:
        """
        Parse a .env configuration file.

        Args:
            config_file (str): The path to the .env configuration file.

        Returns:
            dict: A dictionary containing the parsed .env configuration.

        Raises:
            FileNotFoundError: If the specified configuration file does not exist.
        """
        # Check if the file exists before attempting to parse it
        if not os.path.isfile(config_file):
            raise FileNotFoundError(f"Configuration file '{config_file}' not found.")
        
        # Use dotenv_values to parse the .env file
        return dotenv_values(config_file)