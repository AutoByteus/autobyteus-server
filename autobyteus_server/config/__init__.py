import os
import sys
from typing import Dict
from pathlib import Path
import yaml
from autobyteus_server.config.config_parser import ConfigParser, TOMLConfigParser, ENVConfigParser
from autobyteus.utils.singleton import SingletonMeta
from autobyteus_server.workspaces.workspace import Workspace

class Config(metaclass=SingletonMeta):
    """
    Config is a Singleton class that reads and stores configuration data
    from a file using a ConfigParser. The data can be accessed using the 'get' method.
    """
    @staticmethod
    def get_application_root():
        """Get the application root directory, works in both development and packaged mode"""
        if getattr(sys, 'frozen', False):
            return Path(sys._MEIPASS)
        return Path(__file__).parent.parent.parent

    def __init__(self, config_file: str = None, parser: ConfigParser = ENVConfigParser()):
        self.app_root = self.get_application_root()
        
        if not config_file:
            config_file = str(self.app_root / '.env')
        
        self.config_file = config_file
        self.parser = parser
        self.config_data = self._read_config_file(config_file, parser)
        self.workspaces: Dict[str, Workspace] = {}
        
        # Initialize application directories and paths
        self._initialize_application_directories()
        
        # Initialize SQLite path if needed
        self._init_sqlite_path()

    def _initialize_application_directories(self):
        """Initialize application directories and paths"""
        # Set up resources directory relative to app root
        self.resources_dir = self.app_root / 'resources'
        self.resources_dir.mkdir(exist_ok=True)
        
        # Define specific resource paths
        self.set('RESOURCES_DIR', str(self.resources_dir))
        self.set('PLANTUML_JAR_PATH', str(self.resources_dir / 'plantuml.jar'))

    def get_resource_path(self, resource_name: str) -> Path:
        """
        Get the path for a specific resource file.
        
        Args:
            resource_name (str): Name of the resource file
            
        Returns:
            Path: Full path to the resource file
        """
        return self.resources_dir / resource_name

    def ensure_resource_exists(self, resource_name: str) -> bool:
        """
        Check if a resource exists in the resources directory.
        
        Args:
            resource_name (str): Name of the resource file
            
        Returns:
            bool: True if resource exists, False otherwise
        """
        return (self.resources_dir / resource_name).exists()

    def _read_config_file(self, config_file: str, parser: ConfigParser) -> dict:
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file '{config_file}' not found.")
        try:
            return parser.parse(config_file)
        except Exception as e:
            raise ValueError(f"Error reading configuration file '{config_file}': {e}")

    def _init_sqlite_path(self):
        """Initialize SQLite database path if using SQLite."""
        if self.get('DB_TYPE') == 'sqlite':
            db_path = self._get_sqlite_path()
            self.set('DB_NAME', db_path)

    def _get_sqlite_path(self) -> str:
        """Get the SQLite database file path"""
        # Create data directory relative to app root
        data_dir = self.app_root / 'data'
        data_dir.mkdir(exist_ok=True)
        
        env = self.get('APP_ENV', 'production')
        db_name = 'test.db' if env == 'test' else 'production.db'
        
        return str((data_dir / db_name).absolute())

    def get(self, key: str, default=None):
        return self.config_data.get(key, default)
    
    def set(self, key: str, value: str):
        self.config_data[key] = value
        os.environ[key] = value  # Set the environment variable
        # Update the .env file
        self.parser.update(self.config_file, key, value)
    
    def set_llm_api_key(self, provider: str, api_key: str):
        """
        Set the API key for a specific LLM provider.
        
        Args:
            provider (str): The LLM provider name (e.g., 'OPENAI', 'ANTHROPIC')
            api_key (str): The API key value
        """
        key_name = f"{provider}_API_KEY"
        self.set(key_name, api_key)
    
    def get_llm_api_key(self, provider: str) -> str:
        """
        Get the API key for a specific LLM provider.
        
        Args:
            provider (str): The LLM provider name (e.g., 'OPENAI', 'ANTHROPIC')
            
        Returns:
            str: The API key value for the provider
        """
        key_name = f"{provider}_API_KEY"
        return self.get(key_name)
    
    def add_workspace(self, workspace_name: str, workspace: Workspace):
        """
        Adds a new workspace to the global config.
        Args:
            workspace_name (str): The name or identifier of the workspace.
            workspace (Workspace): The workspace to add.
        """
        self.workspaces[workspace_name] = workspace

config = Config()
