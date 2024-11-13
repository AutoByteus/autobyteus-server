import pytest
import logging
from pymongo import MongoClient
import os
from repository_mongodb import MongoConfig
from sqlalchemy.orm import sessionmaker
from repository_sqlalchemy.database_config import DatabaseConfig
from repository_sqlalchemy.session_management import get_engine
from repository_sqlalchemy import Base, transaction
from dotenv import load_dotenv
import sys

# Define the path for the SQLite test database
TEST_DB_DIR = os.path.join(os.path.dirname(__file__), 'data')
TEST_DB_PATH = os.path.join(TEST_DB_DIR, 'test.db')

def configure_logging():
    """Configure logging for tests"""
    # Clear any existing handlers
    root_logger = logging.getLogger()
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)
    
    # Always set to DEBUG level
    log_level = 'DEBUG'
    root_logger.setLevel(log_level)
    
    # Create console handler with DEBUG level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Log configuration completion
    logging.debug(f"Test logging configured with level: {log_level}")

# Configure logging before any tests run
configure_logging()

def ensure_test_db_directory():
    """Ensure the directory for test database exists"""
    try:
        os.makedirs(TEST_DB_DIR, exist_ok=True)
    except Exception as e:
        logging.error(f"Failed to create test database directory: {e}")
        raise

def remove_test_db():
    """Remove test database file if it exists"""
    try:
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
    except Exception as e:
        logging.warning(f"Could not remove test database: {e}")

# Load environment variables from .env.test
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env.test'), override=True)

@pytest.fixture(scope="session")
def db_config():
    # Ensure we start with a clean database file
    remove_test_db()
    # Ensure the directory exists
    ensure_test_db_directory()
    
    os.environ['DB_TYPE'] = 'sqlite'
    os.environ['DB_NAME'] = TEST_DB_PATH
    return DatabaseConfig('sqlite')

'''
@pytest.fixture(scope="session")
def db_config():
    os.environ['DB_TYPE'] = 'postgresql'
    os.environ['DB_NAME'] = 'postgres'  # Default database name
    os.environ['DB_USER'] = 'postgres'  # Default username
    os.environ['DB_PASSWORD'] = 'mysecretpassword'  # Password set in Docker run command
    os.environ['DB_HOST'] = 'localhost'
    os.environ['DB_PORT'] = '5432'  # Default PostgreSQL port
    return DatabaseConfig('postgresql')
'''

@pytest.fixture(scope="session")
def engine(db_config):
    return get_engine()

@pytest.fixture(scope="session", autouse=True)
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)
    # Clean up the database file after all tests
    remove_test_db()

@pytest.fixture(scope="function", autouse=True)
def clean_table_data():
    with transaction() as session:
        yield
        session.rollback()

@pytest.fixture(scope="session")
def mongo_config():
    os.environ['MONGO_HOST'] = os.getenv('MONGO_HOST', 'localhost')
    os.environ['MONGO_PORT'] = os.getenv('MONGO_PORT', '27017')
    os.environ['MONGO_USERNAME'] = os.getenv('MONGO_USERNAME', '')
    os.environ['MONGO_PASSWORD'] = os.getenv('MONGO_PASSWORD', '')
    os.environ['MONGO_DATABASE'] = os.getenv('MONGO_DATABASE', 'test_database')
    os.environ['MONGO_REPLICA_SET'] = os.getenv('MONGO_REPLICA_SET', 'rs0')
    return MongoConfig()

@pytest.fixture(scope="session")
def mongo_client(mongo_config):
    client = MongoClient(mongo_config.get_connection_uri())
    yield client
    client.close()

@pytest.fixture(scope="session")
def mongo_database(mongo_client, mongo_config):
    return mongo_client[mongo_config.database]