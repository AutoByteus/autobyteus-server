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

# Load environment variables from .env.test
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env.test'), override=True)

@pytest.fixture(scope="session")
def db_config():
    os.environ['DB_TYPE'] = os.getenv('DB_TYPE', 'sqlite')
    os.environ['DB_NAME'] = os.getenv('DB_NAME', ':memory:')
    os.environ['DB_USER'] = os.getenv('DB_USER', 'postgres')
    os.environ['DB_PASSWORD'] = os.getenv('DB_PASSWORD', 'mysecretpassword')
    os.environ['DB_HOST'] = os.getenv('DB_HOST', 'localhost')
    os.environ['DB_PORT'] = os.getenv('DB_PORT', '5432')
    return DatabaseConfig(os.environ['DB_TYPE'])

@pytest.fixture(scope="session")
def engine(db_config):
    return get_engine()

@pytest.fixture(scope="session", autouse=True)
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

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