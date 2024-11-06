import pytest
from repository_sqlalchemy.transaction_management import transaction

@pytest.fixture(scope="function", autouse=True)
def transaction_rollback():
    """
    Provides a MongoDB session for testing with automatic rollback.
    """
    with transaction() as session:
        yield session
        session.rollback()