import pytest
from repository_mongodb.transaction_management import transaction
from repository_mongodb.mongo_client import get_mongo_client, get_mongo_database

@pytest.fixture(scope="function")
def mongo_session():
    """
    Provides a MongoDB session for testing with automatic rollback.
    """
    with transaction() as session:
        yield session
        session.abort_transaction()
        session.end_session()