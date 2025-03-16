import os
import sys
import platform
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from autobyteus_server.config.app_config import AppConfig, AppConfigError


class TestAppConfig:
    """Test the AppConfig class functionality."""

    def test_init(self):
        """Test the initialization of AppConfig."""
        config = AppConfig()
        
        assert config._is_nuitka is None
        assert config._is_windows == (platform.system() == 'Windows')
        assert isinstance(config.app_root_dir, Path)
        assert config.data_dir == config.app_root_dir
        assert config.config_file is None
        assert config.config_data == {}
        assert config.workspaces == {}
        assert config._initialized is False

    @patch('autobyteus_server.config.app_config.load_dotenv')
    @patch('autobyteus_server.config.app_config.dotenv_values')
    @patch('pathlib.Path.exists')
    def test_load_config_data(self, mock_exists, mock_dotenv_values, mock_load_dotenv):
        """Test loading configuration data."""
        mock_exists.return_value = True
        mock_load_dotenv.return_value = True
        mock_dotenv_values.return_value = {'KEY': 'VALUE'}
        
        config = AppConfig()
        config.config_file = 'dummy.env'
        
        # Call the method being tested
        config._load_config_data()
        
        # Verify expected calls
        mock_load_dotenv.assert_called_once()
        mock_dotenv_values.assert_called_once_with('dummy.env')
        
        # Verify result
        assert config.config_data == {'KEY': 'VALUE'}

    @patch('autobyteus_server.config.app_config.load_dotenv')
    def test_load_environment_success(self, mock_load_dotenv):
        """Test successful environment loading."""
        mock_load_dotenv.return_value = True
        
        config = AppConfig()
        with patch.object(config, 'get_config_file_path', return_value=Path('dummy.env')):
            config._load_environment()
        
        # Environment default should be set
        assert os.environ.get('LOG_LEVEL') == 'INFO'

    @patch('autobyteus_server.config.app_config.load_dotenv')
    def test_load_environment_failure(self, mock_load_dotenv):
        """Test failed environment loading."""
        mock_load_dotenv.return_value = False
        
        config = AppConfig()
        with patch.object(config, 'get_config_file_path', return_value=Path('dummy.env')):
            with pytest.raises(Exception) as exc_info:
                config._load_environment()
            
            assert "Failed to load environment variables" in str(exc_info.value)

    @patch('autobyteus_server.config.app_config.logging.config.fileConfig')
    @patch('os.path.exists')
    def test_configure_logger_success(self, mock_exists, mock_fileconfig):
        """Test successful logger configuration."""
        mock_exists.return_value = True
        
        config = AppConfig()
        with patch.object(config, 'get_app_root_dir', return_value=Path('/app')):
            with patch.object(config, 'get_logs_dir', return_value=Path('/app/logs')):
                config._configure_logger()
        
        # Verify fileConfig was called
        mock_fileconfig.assert_called_once()

    @patch('os.path.exists')
    def test_configure_logger_no_config_file(self, mock_exists):
        """Test logger configuration when config file doesn't exist."""
        mock_exists.return_value = False
        
        config = AppConfig()
        with patch.object(config, 'get_app_root_dir', return_value=Path('/app')):
            with patch('logging.basicConfig') as mock_basic_config:
                config._configure_logger()
        
        # Verify basic config was used as fallback
        mock_basic_config.assert_called_once()

    @patch('os.path.exists')
    @patch('autobyteus_server.config.app_config.logging.config.fileConfig')
    def test_configure_logger_error(self, mock_fileconfig, mock_exists):
        """Test error handling in logger configuration."""
        mock_exists.return_value = True
        mock_fileconfig.side_effect = Exception("Config error")
        
        config = AppConfig()
        with patch.object(config, 'get_app_root_dir', return_value=Path('/app')):
            with patch.object(config, 'get_logs_dir', return_value=Path('/app/logs')):
                with patch('logging.basicConfig') as mock_basic_config:
                    with patch('os.makedirs') as mock_makedirs:
                        with pytest.raises(Exception):
                            config._configure_logger()
        
        # Verify directory creation was attempted
        mock_makedirs.assert_called_once()
        # Verify basic config was used as fallback
        mock_basic_config.assert_called_once()

    def test_safe_path_string_non_windows(self):
        """Test safe path string conversion on non-Windows platforms."""
        config = AppConfig()
        config._is_windows = False
        
        path = Path("/app/logs/test.log")
        result = config._safe_path_string(path)
        
        assert result == str(path)

    @patch('os.path.normpath')
    def test_safe_path_string_windows(self, mock_normpath):
        """Test safe path string conversion on Windows platforms."""
        mock_normpath.return_value = "E:\\app\\logs\\test.log"
        
        config = AppConfig()
        config._is_windows = True
        
        path = Path("E:/app/logs/test.log")
        result = config._safe_path_string(path)
        
        mock_normpath.assert_called_once_with(str(path))
        assert result == "E:\\app\\logs\\test.log"

    @patch('sys.executable', 'onefile_executable')
    def test_is_nuitka_build_true(self):
        """Test Nuitka build detection when true."""
        config = AppConfig()
        
        assert config.is_nuitka_build() is True
        # Test caching
        assert config._is_nuitka is True
        assert config.is_nuitka_build() is True

    @patch('sys.executable', 'regular_executable')
    def test_is_nuitka_build_false(self):
        """Test Nuitka build detection when false."""
        config = AppConfig()
        
        assert config.is_nuitka_build() is False
        # Test caching
        assert config._is_nuitka is False
        assert config.is_nuitka_build() is False

    def test_get_app_root_dir_packaged(self):
        """Test getting app root directory in packaged environment."""
        config = AppConfig()
        
        with patch.object(config, 'is_packaged_environment', return_value=True):
            with patch('os.path.abspath', return_value='/app/executable'):
                with patch('pathlib.Path.resolve', return_value=Path('/app/executable')):
                    result = config._get_app_root_dir()
        
        assert result == Path('/app')

    def test_get_app_root_dir_development(self):
        """Test getting app root directory in development environment."""
        config = AppConfig()
        
        with patch.object(config, 'is_packaged_environment', return_value=False):
            with patch('pathlib.Path.resolve', return_value=Path('/code/autobyteus-server/autobyteus_server/config/app_config.py')):
                result = config._get_app_root_dir()
        
        assert result == Path('/code/autobyteus-server')

    def test_get_config_file_path(self):
        """Test getting config file path."""
        config = AppConfig()
        config.data_dir = Path('/app')
        
        with patch('pathlib.Path.exists', return_value=True):
            result = config.get_config_file_path()
        
        assert result == Path('/app/.env')

    def test_get_config_file_path_not_found(self):
        """Test getting config file path when file not found."""
        config = AppConfig()
        config.data_dir = Path('/app')
        
        with patch('pathlib.Path.exists', return_value=False):
            with pytest.raises(FileNotFoundError):
                config.get_config_file_path()

    def test_set_custom_app_data_dir(self):
        """Test setting custom app data directory."""
        config = AppConfig()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create .env file
            env_path = Path(temp_dir) / '.env'
            with open(env_path, 'w') as f:
                f.write('TEST=VALUE')
            
            # Set custom app data dir
            config.set_custom_app_data_dir(temp_dir)
            
            assert config.data_dir == Path(temp_dir)
            assert config.config_file == str(env_path)

    def test_set_custom_app_data_dir_after_init(self):
        """Test setting custom app data directory after initialization."""
        config = AppConfig()
        config._initialized = True
        
        with pytest.raises(AppConfigError):
            config.set_custom_app_data_dir('/app')

    def test_set_custom_app_data_dir_not_exists(self):
        """Test setting custom app data directory when directory doesn't exist."""
        config = AppConfig()
        
        with pytest.raises(AppConfigError):
            config.set_custom_app_data_dir('/nonexistent/directory')

    def test_get(self):
        """Test getting configuration value."""
        config = AppConfig()
        config.config_data = {'KEY': 'VALUE'}
        
        assert config.get('KEY') == 'VALUE'
        assert config.get('NONEXISTENT') is None
        assert config.get('NONEXISTENT', 'DEFAULT') == 'DEFAULT'

    @patch('autobyteus_server.config.app_config.set_key')
    def test_set(self, mock_set_key):
        """Test setting configuration value."""
        config = AppConfig()
        config.config_file = 'dummy.env'
        
        config.set('KEY', 'VALUE')
        
        assert config.config_data['KEY'] == 'VALUE'
        assert os.environ['KEY'] == 'VALUE'
        mock_set_key.assert_called_once_with('dummy.env', 'KEY', 'VALUE')

    @patch('autobyteus_server.config.app_config.set_key')
    def test_set_no_config_file(self, mock_set_key):
        """Test setting configuration value without config file."""
        config = AppConfig()
        config.config_file = None
        
        config.set('KEY', 'VALUE')
        
        assert config.config_data['KEY'] == 'VALUE'
        assert os.environ['KEY'] == 'VALUE'
        mock_set_key.assert_not_called()

    @patch('autobyteus_server.config.app_config.set_key')
    def test_set_error(self, mock_set_key):
        """Test error handling when setting configuration value."""
        config = AppConfig()
        config.config_file = 'dummy.env'
        mock_set_key.side_effect = Exception("Error updating config")
        
        config.set('KEY', 'VALUE')
        
        assert config.config_data['KEY'] == 'VALUE'
        assert os.environ['KEY'] == 'VALUE'
        mock_set_key.assert_called_once()

    def test_llm_api_key(self):
        """Test setting and getting LLM API keys."""
        config = AppConfig()
        
        with patch.object(config, 'set') as mock_set:
            config.set_llm_api_key('OPENAI', 'api-key-123')
            mock_set.assert_called_once_with('OPENAI_API_KEY', 'api-key-123')
        
        with patch.object(config, 'get', return_value='api-key-123') as mock_get:
            result = config.get_llm_api_key('OPENAI')
            mock_get.assert_called_once_with('OPENAI_API_KEY')
            assert result == 'api-key-123'

    def test_add_workspace(self):
        """Test adding a workspace."""
        config = AppConfig()
        workspace = MagicMock()
        
        config.add_workspace('test_workspace', workspace)
        
        assert config.workspaces['test_workspace'] == workspace

    def test_is_initialized(self):
        """Test checking if AppConfig is initialized."""
        config = AppConfig()
        
        assert config.is_initialized() is False
        
        config._initialized = True
        assert config.is_initialized() is True
