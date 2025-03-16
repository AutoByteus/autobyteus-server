import os
import sys
from typing import Dict
from pathlib import Path
import logging
import platform
import tempfile
import shutil
from dotenv import load_dotenv, dotenv_values, set_key
from autobyteus_server.workspaces.workspace import Workspace

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
        # Cache for Nuitka detection
        self._is_nuitka = None
        
        # Detect platform
        self._is_windows = platform.system() == 'Windows'
        print(f"Platform detection: Windows={self._is_windows}")
        
        # Initialize the app root directory
        self.app_root_dir = self._get_app_root_dir()
        print(f"App root directory: {self.app_root_dir}")
        
        # Initialize the data directory - by default, it's the same as app_root_dir
        self.data_dir = self.app_root_dir
        print(f"Data directory: {self.data_dir}")
        
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
        
        # Final summary logging placed at the end of initialization
        logger.info("=" * 60)
        # Determine mode based on packaged environment flag
        if self.is_packaged_environment():
            logger.info("RUNNING IN PACKAGED MODE")
        else:
            logger.info("RUNNING IN DEVELOPMENT MODE")
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
        if self.is_packaged_environment():
            executable_path = Path(os.path.abspath(sys.argv[0])).resolve()
            return executable_path.parent
        
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

    def _create_modified_logging_config(self, log_file_path):
        """
        Create a modified logging configuration file with the log path hardcoded.
        This avoids issues with string interpolation of paths.
        
        Args:
            log_file_path (str): The log file path to hardcode
            
        Returns:
            str: Path to the temporary logging config file
        """
        print(f"Creating modified logging config with hardcoded path: {log_file_path}")
        
        app_root = self.get_app_root_dir()
        orig_config_path = app_root / 'logging_config.ini'
        
        if not os.path.exists(orig_config_path):
            print(f"Original logging config not found at {orig_config_path}")
            return None
        
        # Create a temporary file for the modified config
        fd, temp_path = tempfile.mkstemp(suffix='.ini', prefix='logging_config_')
        os.close(fd)
        
        # Since we're hardcoding paths, escape backslashes in the log file path for Python
        if self._is_windows:
            log_file_path = log_file_path.replace('\\', '\\\\')
        
        # Read the original config
        with open(orig_config_path, 'r') as file:
            content = file.read()
        
        # Replace the dynamic path with a hardcoded one
        # Example: args=("%(log_file_path)s", "midnight", 1, 1) -> args=("C:\\path\\to\\log.log", "midnight", 1, 1)
        modified_content = content.replace('args=("%(log_file_path)s"', f'args=("{log_file_path}"')
        
        # Write the modified config
        with open(temp_path, 'w') as file:
            file.write(modified_content)
        
        print(f"Created temporary config file at: {temp_path}")
        return temp_path

    def _configure_logger(self):
        """Configure logging using the logging configuration file."""
        import logging.config
        import sys
        
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
        print(f"Logs directory: {logs_dir}")
        
        # Create logs directory
        try:
            os.makedirs(str(logs_dir), exist_ok=True)
            print(f"Created/verified logs directory at: {logs_dir}")
        except Exception as dir_e:
            print(f"Error creating logs directory: {dir_e}")
        
        # Create log file path - simplest possible approach
        if self._is_windows:
            # On Windows, build path using os.path.join with string components
            logs_dir_str = str(logs_dir)
            log_file = os.path.join(logs_dir_str, "app.log")
            print(f"Windows log file path: {log_file}")
        else:
            # On other platforms, Path joining works fine
            log_file = str(logs_dir / 'app.log')
            print(f"Non-Windows log file path: {log_file}")
        
        # Try to directly test if we can write to the log file location
        try:
            with open(log_file, 'a') as test_file:
                test_file.write("Log file test\n")
            print(f"Successfully wrote to log file: {log_file}")
        except Exception as file_e:
            print(f"ERROR writing to log file: {file_e}")
            # Try a fallback location
            log_file = os.path.join(os.getcwd(), "autobyteus_app.log")
            print(f"Using fallback log file: {log_file}")
            try:
                with open(log_file, 'a') as test_file:
                    test_file.write("Log file test\n")
                print(f"Successfully wrote to fallback log file")
            except Exception as fallback_e:
                print(f"ERROR writing to fallback log file: {fallback_e}")
                # Console-only logging as last resort
                logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)]
                )
                print("Using console-only logging as last resort")
                return
        
        try:
            # Instead of using string interpolation, use a modified config with hardcoded path
            temp_config = self._create_modified_logging_config(log_file)
            
            if temp_config:
                print(f"Using modified logging config from: {temp_config}")
                logging.config.fileConfig(
                    temp_config,
                    disable_existing_loggers=False
                )
                # Clean up the temporary file
                try:
                    os.unlink(temp_config)
                except:
                    print(f"Note: Could not delete temporary config file: {temp_config}")
            else:
                # Fallback to simple configuration
                print("Using basic logging configuration")
                logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(log_file),
                        logging.StreamHandler(sys.stdout)
                    ]
                )
            
            print(f"Logging configured successfully with log file: {log_file}")
            logger.info(f"Logging started with file: {log_file}")
        except Exception as e:
            print(f"ERROR configuring logging: {e}")
            print("Using basic configuration as fallback")
            
            # Fallback to simple configuration
            try:
                logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(log_file),
                        logging.StreamHandler(sys.stdout)
                    ]
                )
            except Exception as fallback_e:
                print(f"ERROR with fallback logging: {fallback_e}")
                # Console-only as last resort
                logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)]
                )
            raise

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

    def is_nuitka_build(self) -> bool:
        """
        Detect if the application is running from a Nuitka build.
        
        Returns:
            bool: True if running from a Nuitka build, False otherwise.
        """
        if self._is_nuitka is not None:
            return self._is_nuitka
        
        executable_lower = sys.executable.lower()
        for pattern in ['onefile_', 'onefil']:
            if pattern in executable_lower:
                self._is_nuitka = True
                print(f"Detected Nuitka build from pattern '{pattern}' in executable: {sys.executable}")
                return True
        
        self._is_nuitka = False
        return False

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

    def is_packaged_environment(self) -> bool:
        """Check if running in a packaged environment."""
        return self.is_nuitka_build()

    def validate_packaged_environment(self):
        """
        Validate that all required files and directories exist in packaged mode.
        Exits the application if validation fails.
        """
        app_root_dir = self.get_app_root_dir()
        required_files = ['.env', 'logging_config.ini', 'alembic.ini']
        required_dirs = ['download', 'alembic']
        app_data_dir = self.get_app_data_dir()
        missing_files = [str(app_data_dir / f) for f in required_files if not (app_data_dir / f).exists()]
        missing_dirs = [str(app_root_dir / d) for d in required_dirs if not (app_root_dir / d).is_dir()]
        for d in ['logs', 'db']:
            if not (app_data_dir / d).is_dir():
                missing_dirs.append(str(app_data_dir / d))
        if missing_files or missing_dirs:
            logger.error("Missing required files or directories:")
            if missing_files:
                logger.error(f"Files: {', '.join(missing_files)}")
            if missing_dirs:
                logger.error(f"Directories: {', '.join(missing_dirs)}")
            sys.exit(1)

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
