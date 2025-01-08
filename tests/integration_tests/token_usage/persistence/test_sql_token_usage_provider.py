
import pytest
from autobyteus_server.token_usage.provider.sql_persistence_provider import SqlPersistenceProvider
from autobyteus_server.token_usage.domain.token_usage_record import TokenUsageRecord
from datetime import datetime
import uuid

@pytest.fixture
def sql_persistence_provider():
    """Provides the singleton SqlPersistenceProvider instance for testing."""
    return SqlPersistenceProvider()

def test_create_token_usage_record(sql_persistence_provider):
    """
    Test creating a new token usage record in a SQL-based database.
    """
    conversation_id = "sql_test_conversation_id"
    conversation_type = "WORKFLOW"
    role = "assistant"
    token_count = 50
    cost = 0.002

    record = sql_persistence_provider.create_token_usage_record(
        conversation_id=conversation_id,
        conversation_type=conversation_type,
        role=role,
        token_count=token_count,
        cost=cost
    )

    assert isinstance(record, TokenUsageRecord)
    assert record.conversation_id == conversation_id
    assert record.conversation_type == conversation_type
    assert record.role == role
    assert record.token_count == token_count
    assert record.cost == cost
    assert isinstance(record.created_at, datetime)
    if record.token_usage_record_id:
        assert uuid.UUID(record.token_usage_record_id)  # Validate UUID format
    else:
        pytest.fail("token_usage_record_id should not be None after creation")
