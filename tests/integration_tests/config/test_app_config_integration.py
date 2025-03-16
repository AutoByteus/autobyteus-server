import os
import sys
import tempfile
import logging
import pytest
import platform
from pathlib import Path
import tempfile
from unittest.mock import patch

from autobyteus_server.config.app_config import AppConfig, AppConfigError

# Mark all tests in this module to not use the transaction fixture
pytestmark = pytest.mark.skip_transaction

class TestAppConfigIntegration:
    """Integration tests for AppConfig class."""
    
    @pytest.fixture
    def temp_app_dir(self):
        """Create a temporary directory structure for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            app_dir = Path(temp_dir)
            
            # Create required directories
            logs_dir = app_dir / 'logs'
            db_dir = app_dir / 'db'
            download_dir = app_dir / 'download'
            
            logs_dir.mkdir()
            db_dir.mkdir()
            download_dir.mkdir()
            
            # Create a basic .env file
            env_file = app_dir / '.env'
            with open(env_file, 'w') as f:
                f.write('APP_ENV=test\n')
                f.write('DB_TYPE=sqlite\n')
                f.write('LOG_LEVEL=DEBUG\n')
                f.write('OPENAI_API_KEY=test-key\n')
            
            # Create a basic logging_config.ini file - using raw string to prevent escape sequence issues
            log_config = app_dir / 'logging_config.ini'
            with open(log_config, 'w') as f:
                f.write(r'''
[loggers]
keys=root

[handlers]
keys=fileHandler,consoleHandler

[formatters]
keys=myFormatter

[logger_root]
level=INFO
handlers=fileHandler,consoleHandler

[handler_fileHandler]
class=FileHandler
level=INFO
formatter=myFormatter
args=("%(log_file_path)s",)

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=myFormatter
args=(sys.stdout,)

[formatter_myFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
datefmt=
                ''')
            
            yield app_dir

    def test_initialize_full_cycle(self, temp_app_dir):
        """Test the full initialization cycle of AppConfig."""
        config = AppConfig()
        
        # Mock logging.config.fileConfig to avoid actual file operations
        with patch('logging.config.fileConfig'):
            # Set custom app data directory to our temp directory
            # Use os.path.normpath to handle Windows paths safely
            safe_path = os.path.normpath(str(temp_app_dir))
            config.set_custom_app_data_dir(safe_path)
            
            # Verify data_dir is set correctly
            assert config.data_dir == temp_app_dir
            assert os.path.normpath(config.config_file) == os.path.normpath(str(temp_app_dir / '.env'))
            
            # Initialize the config
            config.initialize()
            
            # Verify initialization state
            assert config.is_initialized() is True
            assert 'APP_ENV' in config.config_data
            assert config.get('APP_ENV') == 'test'
            assert config.get('LOG_LEVEL') == 'DEBUG'
            
            # Check API key access
            assert config.get_llm_api_key('OPENAI') == 'test-key'
            
            # Test setting a new value
            config.set('NEW_KEY', 'new-value')
            assert config.get('NEW_KEY') == 'new-value'
            
            # Verify it was also written to the .env file
            with open(temp_app_dir / '.env', 'r') as f:
                content = f.read()
                assert 'NEW_KEY=new-value' in content

    def test_windows_path_handling(self, temp_app_dir):
        """Test Windows-specific path handling."""
        # Skip test if not on Windows
        if platform.system() != 'Windows':
            pytest.skip("Windows-specific test")
        
        config = AppConfig()
        
        # Mock logging configuration to avoid actual file operations
        with patch('logging.config.fileConfig'):
            # Set custom app data directory using normalized path
            safe_path = os.path.normpath(str(temp_app_dir))
            config.set_custom_app_data_dir(safe_path)
            
            # Initialize
            config.initialize()
            
            # Test various path methods
            app_dir = config.get_app_root_dir()
            data_dir = config.get_app_data_dir()
            db_dir = config.get_db_dir()
            logs_dir = config.get_logs_dir()
            download_dir = config.get_download_dir()
            
            # All paths should exist
            assert app_dir.exists()
            assert data_dir.exists()
            assert db_dir.exists()
            assert logs_dir.exists()
            assert download_dir.exists()

    def test_packaged_environment_validation(self, temp_app_dir):
        """Test packaged environment validation."""
        config = AppConfig()
        
        # Set up a temp parent directory for alembic to avoid conflicts
        parent_dir = tempfile.mkdtemp(prefix='alembic_parent_')
        
        try:
            # Mock packaged environment detection
            with patch.object(config, 'is_packaged_environment', return_value=True):
                # Set custom app data directory using normalized path
                safe_path = os.path.normpath(str(temp_app_dir))
                config.set_custom_app_data_dir(safe_path)
                
                # Add required directories for validation
                alembic_dir = Path(parent_dir) / 'alembic'
                alembic_dir.mkdir(exist_ok=False)  # Will fail if directory already exists
                
                # Create alembic.ini file
                with open(temp_app_dir / 'alembic.ini', 'w') as f:
                    f.write('[alembic]\nscript_location = alembic\n')
                
                # Mock Path.parent to return our custom parent directory
                with patch.object(Path, 'parent', return_value=Path(parent_dir)):
                    # Mock sys.exit to prevent test from actually exiting
                    with patch('sys.exit') as mock_exit:
                        config.validate_packaged_environment()
                        
                        # It should not exit since we have all required files
                        mock_exit.assert_not_called()
        finally:
            # Clean up temp directory
            import shutil
            shutil.rmtree(parent_dir)

    def test_initialization_failure(self, temp_app_dir):
        """Test handling of initialization failures."""
        # Remove the .env file to cause initialization to fail
        env_file = temp_app_dir / '.env'
        os.remove(env_file)
        
        config = AppConfig()
        
        # Set custom app data directory using normalized path
        safe_path = os.path.normpath(str(temp_app_dir))
        
        # This should now fail since we removed the .env file
        with pytest.raises(AppConfigError):
            config.set_custom_app_data_dir(safe_path)
        
        # Config should not be marked as initialized
        assert config.is_initialized() is False

    def test_reinitialize(self, temp_app_dir):
        """Test calling initialize more than once."""
        config = AppConfig()
        
        # Mock logging configuration to avoid file operations
        with patch('logging.config.fileConfig'):
            # Set custom app data directory using normalized path
            safe_path = os.path.normpath(str(temp_app_dir))
            config.set_custom_app_data_dir(safe_path)
            
            # First initialization
            config.initialize()
            assert config.is_initialized() is True
            
            # Capture logs to verify warning
            with self.capture_logs() as captured:
                # Second initialization should log a warning
                config.initialize()
                assert any("initialize() called more than once" in record.message 
                        for record in captured.records)

    @pytest.fixture
    def capture_logs(self):
        """Fixture to capture log messages."""
        class LogCapture:
            def __init__(self):
                self.handler = logging.handlers.MemoryHandler(capacity=1024)
                self.records = []
                
                # Custom handler to store records
                self.handler.setLevel(logging.DEBUG)
                self.handler.setFormatter(logging.Formatter('%(message)s'))
                
            def __enter__(self):
                # Get logger and add handler
                logger = logging.getLogger('autobyteus_server.config.app_config')
                logger.addHandler(self.handler)
                return self
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                # Get all records and remove handler
                self.records = self.handler.buffer
                logger = logging.getLogger('autobyteus_server.config.app_config')
                logger.removeHandler(self.handler)
        
        return LogCapture
