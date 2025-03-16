import os
import sys
import pytest
import tempfile
import logging.handlers
from pathlib import Path

@pytest.fixture
def mock_packaged_environment(monkeypatch):
    """Mock a packaged environment."""
    original_executable = sys.executable
    
    # Mock sys.executable to make it look like a Nuitka build
    monkeypatch.setattr(sys, 'executable', 'onefile_autobyteus_server')
    
    yield
    
    # Restore original sys.executable
    monkeypatch.setattr(sys, 'executable', original_executable)

@pytest.fixture
def full_app_environment():
    """Create a complete application environment structure for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        app_dir = Path(temp_dir)
        
        # Create required directories
        logs_dir = app_dir / 'logs'
        db_dir = app_dir / 'db'
        download_dir = app_dir / 'download'
        alembic_dir = app_dir / 'alembic'
        
        logs_dir.mkdir()
        db_dir.mkdir()
        download_dir.mkdir()
        alembic_dir.mkdir()
        
        # Create required files
        env_file = app_dir / '.env'
        logging_config = app_dir / 'logging_config.ini'
        alembic_ini = app_dir / 'alembic.ini'
        
        # Write content to .env
        with open(env_file, 'w') as f:
            f.write('APP_ENV=test\n')
            f.write('DB_TYPE=sqlite\n')
        
        # Write content to logging_config.ini - using raw string to prevent escape issues
        with open(logging_config, 'w') as f:
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
class=logging.FileHandler
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
        
        # Write content to alembic.ini
        with open(alembic_ini, 'w') as f:
            f.write('''
[alembic]
script_location = alembic
            ''')
        
        yield app_dir
