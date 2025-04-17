import os
import sys
from typing import Dict
from pathlib import Path
import logging
import platform
from dotenv import load_dotenv, dotenv_values, set_key
from autobyteus_server.workspaces.workspace import Workspace
from autobyteus_server.config.logging import WindowsLoggingConfigurator, UnixLoggingConfigurator

logger = logging.getLogger(__name__)

class AppConfigError(Exception):
    """Base exception for all AppConfig-related errors."""
    pass

class AppConfig:
    """
    AppConfig class that reads and stores configuration data from a .env file.
    
    All configuration-related functionality is centralized in this class, including:
    - Path and directory management
    - Environment detection
    - Configuration loading via dotenv
    - Environment validation
    
    The initialize() method always loads environment variables and configures logging.
    """
    def __init__(self):
        """
        Initialize basic components of AppConfig.
        This performs minimal initialization to establish the app_root_dir and data_dir.
        Call initialize() to complete the initialization.
        """
        # Detect platform
        self._is_windows = platform.system() == 'Windows'
        print(f"Platform detection: Windows={self._is_windows}")
        
        # Initialize the app root directory using the non-packaged logic
        self.app_root_dir = self._get_app_root_dir()
        print(f"App root directory: {self.app_root_dir}")
        
        # Initialize the data directory - by default, it's the same as app_root_dir
        self.data_dir = self.app_root_dir
        print(f"Data directory: {self.data_dir}")
        
        # Create platform-specific logging configurator
        if self._is_windows:
            self.logging_configurator = WindowsLoggingConfigurator(self)
        else:
            self.logging_configurator = UnixLoggingConfigurator(self)
        
        # Defer determining the config file until initialization
        self.config_file = None
        
        # Initialize empty configuration data
        self.config_data = {}
        
        # Initialize empty workspaces
        self.workspaces: Dict[str, Workspace] = {}
        
        # Flag to track if initialize has been called
        self._initialized = False

    def initialize(self):
        """
        Complete the initialization of AppConfig.
        This method always loads environment variables and configures logging.
        
        Raises:
            AppConfigError: If any error occurs during initialization.
        """
        if self._initialized:
            print("initialize() called more than once. Ignoring.")
            return
        
        # Ensure we have a valid config file
        if not self.config_file or not os.path.exists(self.config_file):
            try:
                self.config_file = str(self.get_config_file_path())
                print(f"Config file path: {self.config_file}")
            except FileNotFoundError as e:
                error_msg = f"Configuration file not found: {e}"
                print(f"ERROR: {error_msg}")
                raise AppConfigError(error_msg) from e
        
        # Load environment variables and configuration data
        self._load_config_data()
        
        # Initialize SQLite path if needed
        if self.get('DB_TYPE', 'sqlite') == 'sqlite':
            try:
                self._init_sqlite_path()
            except Exception as e:
                error_msg = f"Failed to initialize SQLite path: {e}"
                print(f"ERROR: {error_msg}")
                raise AppConfigError(error_msg) from e
        
        # Configure logging unconditionally
        try:
            self._configure_logger()
        except Exception as e:
            error_msg = f"Failed to configure logging: {e}"
            print(f"ERROR: {error_msg}")
            raise AppConfigError(error_msg) from e
        
        # Mark as initialized
        self._initialized = True
        
        # Logging summary without mode-specific information
        logger.info("=" * 60)
        logger.info(f"APP ROOT DIRECTORY: {self.get_app_root_dir()}")
        logger.info(f"APP DATA DIRECTORY: {self.get_app_data_dir()}")
        logger.info(f"DB DIRECTORY: {self.get_db_dir()}")
        logger.info(f"LOGS DIRECTORY: {self.get_logs_dir()}")
        logger.info(f"DOWNLOAD DIRECTORY: {self.get_download_dir()}")
        logger.info("=" * 60)
        
        logger.info("AppConfig initialization completed successfully")

    def _load_config_data(self):
        """
        Load environment variables and configuration data from the .env file.
        
        Raises:
            AppConfigError: If loading the environment or parsing the configuration fails.
        """
        # Load environment variables from the config file
        try:
            self._load_environment()
        except Exception as e:
            error_msg = f"Failed to load environment variables: {e}"
            print(f"ERROR: {error_msg}")
            raise AppConfigError(error_msg) from e
        
        # Load configuration data into a local dictionary
        try:
            self.config_data = dotenv_values(self.config_file)
        except Exception as e:
            error_msg = f"Failed to parse configuration file: {e}"
            print(f"ERROR: {error_msg}")
            raise AppConfigError(error_msg) from e

    def _get_app_root_dir(self) -> Path:
        """Get the application root directory."""
        current_file = Path(__file__).resolve()
        return current_file.parent.parent.parent

    def _init_sqlite_path(self):
        """Initialize SQLite database path if using SQLite."""
        db_path = self._get_sqlite_path()
        self.set('DB_NAME', db_path)

    def _get_sqlite_path(self) -> str:
        """Get the SQLite database file path."""
        db_dir = self.get_db_dir()
        env = self.get('APP_ENV', 'production')
        db_name = 'test.db' if env == 'test' else 'production.db'
        return str((db_dir / db_name).absolute())

    def _configure_logger(self):
        """Configure logging using the logging configuration file."""
        print("=== Starting logging configuration ===")
        
        app_root = self.get_app_root_dir()
        config_path = app_root / 'logging_config.ini'
        print(f"Looking for logging config at: {config_path}")
        
        if not os.path.exists(config_path):
            print(f"Logging config not found, using basic configuration")
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            return
        
        logs_dir = self.get_logs_dir()
        
        # Use the platform-specific logging configurator
        success = self.logging_configurator.configure_logging(config_path, logs_dir)
        
        if not success:
            raise AppConfigError("Failed to configure logging")

    def _load_environment(self):
        """
        Load environment variables from the .env file.
        
        Raises:
            Exception: If environment variables cannot be loaded.
        """
        env_path = self.get_config_file_path()
        print(f"Loading environment from: {env_path}")
        if not load_dotenv(dotenv_path=env_path):
            error_msg = f"Failed to load environment variables from {env_path}"
            print(f"ERROR: {error_msg}")
            raise Exception(error_msg)
        os.environ.setdefault('LOG_LEVEL', 'INFO')
        print("Environment variables loaded successfully")

    # Public API methods

    def get_app_root_dir(self) -> Path:
        """Get the application root directory."""
        return self.app_root_dir

    def get_app_data_dir(self) -> Path:
        """Get the application data directory."""
        return self.data_dir

    def get_config_file_path(self) -> Path:        
        config_path = self.data_dir / '.env'
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        return config_path

    def get_db_dir(self) -> Path:
        db_dir = self.data_dir / 'db'
        db_dir.mkdir(exist_ok=True)
        return db_dir

    def get_logs_dir(self) -> Path:
        logs_dir = self.data_dir / 'logs'
        logs_dir.mkdir(exist_ok=True)
        return logs_dir

    def get_download_dir(self) -> Path:
        download_dir = self.data_dir / 'download'
        download_dir.mkdir(exist_ok=True)
        return download_dir

    def load_environment(self) -> bool:
        """
        DEPRECATED: Use initialize() instead.
        Load environment variables from the .env file.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        print("load_environment() is deprecated. Use initialize() instead.")
        try:
            self._load_environment()
            return True
        except Exception as e:
            print(f"Failed to load environment: {e}")
            return False

    def set_custom_app_data_dir(self, path: str) -> None:
        """
        Set a custom app data directory.
        This should be called before initialize().
        
        Args:
            path (str): The path to the custom app data directory.
        
        Raises:
            AppConfigError: If the directory does not exist, is not a directory, or if called after initialization.
        """
        if self._initialized:
            raise AppConfigError("Cannot set custom app data directory after initialize() has been called.")
        
        data_dir = Path(path)
        if not data_dir.exists():
            raise AppConfigError(f"Data directory does not exist: {data_dir}")
        if not data_dir.is_dir():
            raise AppConfigError(f"Path is not a directory: {data_dir}")
        
        self.data_dir = data_dir
        print(f"Custom app data directory set to: {self.data_dir}")
        
        try:
            self.config_file = str(self.get_config_file_path())
            print(f"Updated config file path to {self.config_file}")
        except FileNotFoundError as e:
            print(f"Config file not found in new data directory: {e}")
            self.config_file = None

    # Configuration access methods

    def get(self, key: str, default=None):
        """Get a configuration value by key."""
        return self.config_data.get(key, default)

    def set(self, key: str, value: str):
        """Set a configuration value by key."""
        self.config_data[key] = value
        os.environ[key] = value
        if self.config_file:
            try:
                set_key(self.config_file, key, value)
            except Exception as e:
                print(f"Could not update config file {self.config_file}: {e}. Changes will only be valid for the current session.")

    def set_llm_api_key(self, provider: str, api_key: str):
        """
        Set the API key for a specific LLM provider.
        
        Args:
            provider (str): The LLM provider name (e.g., 'OPENAI', 'ANTHROPIC')
            api_key (str): The API key value
        """
        self.set(f"{provider}_API_KEY", api_key)

    def get_llm_api_key(self, provider: str) -> str:
        """
        Get the API key for a specific LLM provider.
        
        Args:
            provider (str): The LLM provider name (e.g., 'OPENAI', 'ANTHROPIC')
        
        Returns:
            str: The API key value for the provider
        """
        return self.get(f"{provider}_API_KEY")

    def add_workspace(self, workspace_name: str, workspace: Workspace):
        """
        Adds a new workspace to the global config.
        
        Args:
            workspace_name (str): The name or identifier of the workspace.
            workspace (Workspace): The workspace to add.
        """
        self.workspaces[workspace_name] = workspace

    def is_initialized(self) -> bool:
        """
        Check if the AppConfig has been fully initialized.
        
        Returns:
            bool: True if initialized, False otherwise.
        """
        return self._initialized
