import os
import sys
import tempfile
import logging
import pytest
import platform
from pathlib import Path

from autobyteus_server.config.app_config import AppConfig, AppConfigError


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
            
            # Create a basic logging_config.ini file
            log_config = app_dir / 'logging_config.ini'
            with open(log_config, 'w') as f:
                f.write('''
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
class=logging.handlers.RotatingFileHandler
level=INFO
formatter=myFormatter
args=("%(log_file_path)s", "a", 10000000, 5)

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
        
        # Set custom app data directory to our temp directory
        config.set_custom_app_data_dir(str(temp_app_dir))
        
        # Verify data_dir is set correctly
        assert config.data_dir == temp_app_dir
        assert config.config_file == str(temp_app_dir / '.env')
        
        # Initialize the config
        config.initialize()
        
        # Verify initialization state
        assert config.is_initialized() is True
        assert 'APP_ENV' in config.config_data
        assert config.get('APP_ENV') == 'test'
        assert config.get('LOG_LEVEL') == 'DEBUG'
        
        # Check log file was created
        assert (temp_app_dir / 'logs' / 'app.log').exists()
        
        # Check API key access
        assert config.get_llm_api_key('OPENAI') == 'test-key'
        
        # Test setting a new value
        config.set('NEW_KEY', 'new-value')
        assert config.get('NEW_KEY') == 'new-value'
        
        # Verify it was also written to the .env file
        with open(temp_app_dir / '.env', 'r') as f:
            content = f.read()
            assert 'NEW_KEY=new-value' in content

    def test_windows_path_handling(self, temp_app_dir, monkeypatch):
        """Test Windows-specific path handling."""
        # Skip test if not on Windows and can't fully simulate Windows environment
        if platform.system() != 'Windows':
            pytest.skip("Windows-specific test")
        
        config = AppConfig()
        
        # Set custom app data directory
        config.set_custom_app_data_dir(str(temp_app_dir))
        
        # Initialize
        config.initialize()
        
        # Verify log file was created
        log_file = temp_app_dir / 'logs' / 'app.log'
        assert log_file.exists()
        
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

    def test_packaged_environment_validation(self, temp_app_dir, monkeypatch):
        """Test packaged environment validation."""
        config = AppConfig()
        
        # Mock packaged environment detection
        monkeypatch.setattr(config, 'is_packaged_environment', lambda: True)
        
        # Set custom app data directory
        config.set_custom_app_data_dir(str(temp_app_dir))
        
        # Add required directories for validation
        alembic_dir = temp_app_dir.parent / 'alembic'
        alembic_dir.mkdir()
        
        # Create alembic.ini file
        with open(temp_app_dir / 'alembic.ini', 'w') as f:
            f.write('[alembic]\nscript_location = alembic\n')
        
        try:
            # This should not exit because we have the required files
            config.validate_packaged_environment()
        except SystemExit:
            pytest.fail("validate_packaged_environment() exited unexpectedly")

    def test_initialization_failure(self, temp_app_dir):
        """Test handling of initialization failures."""
        # Remove the .env file to cause initialization to fail
        env_file = temp_app_dir / '.env'
        os.remove(env_file)
        
        config = AppConfig()
        config.set_custom_app_data_dir(str(temp_app_dir))
        
        # Initialization should fail with AppConfigError
        with pytest.raises(AppConfigError):
            config.initialize()
        
        # Config should not be marked as initialized
        assert config.is_initialized() is False

    def test_reinitialize(self, temp_app_dir):
        """Test calling initialize more than once."""
        config = AppConfig()
        config.set_custom_app_data_dir(str(temp_app_dir))
        
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
