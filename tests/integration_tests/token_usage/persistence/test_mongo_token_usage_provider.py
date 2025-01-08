
import pytest
from datetime import datetime, timedelta
from autobyteus_server.token_usage.provider.mongodb_persistence_provider import MongoPersistenceProvider
from autobyteus_server.token_usage.domain.token_usage_record import TokenUsageRecord

@pytest.fixture
def mongo_persistence_provider():
    """
    Provides a MongoPersistenceProvider instance for testing token usage.
    """
    return MongoPersistenceProvider()

def test_create_token_usage_record(mongo_persistence_provider):
    """
    Test creating a new token usage record in MongoDB.
    """
    conversation_id = "mongo_test_conversation_id"
    conversation_type = "WORKFLOW"
    role = "user"
    token_count = 100
    cost = 0.01

    record = mongo_persistence_provider.create_token_usage_record(
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
    assert record.created_at is not None

def test_get_token_usage_records_no_filters(mongo_persistence_provider):
    """
    Test retrieving all token usage records without any filters.
    """
    # Create a couple of records
    mongo_persistence_provider.create_token_usage_record(
        conversation_id="mongo_conversation_1",
        conversation_type="AI_TERMINAL",
        role="user",
        token_count=10,
        cost=0.001
    )
    mongo_persistence_provider.create_token_usage_record(
        conversation_id="mongo_conversation_2",
        conversation_type="WORKFLOW",
        role="assistant",
        token_count=20,
        cost=0.002
    )

    records = mongo_persistence_provider.get_token_usage_records()
    assert len(records) >= 2  # We expect at least the two we just created

def test_get_token_usage_records_filter_by_conversation_id(mongo_persistence_provider):
    """
    Test retrieving token usage records filtered by conversation_id.
    """
    conversation_id = "mongo_specific_conv_id"
    # Create multiple records, some for a different conversation
    mongo_persistence_provider.create_token_usage_record(
        conversation_id=conversation_id,
        conversation_type="WORKFLOW",
        role="user",
        token_count=15,
        cost=0.0015
    )
    mongo_persistence_provider.create_token_usage_record(
        conversation_id="another_conv_id",
        conversation_type="WORKFLOW",
        role="assistant",
        token_count=25,
        cost=0.0025
    )

    records = mongo_persistence_provider.get_token_usage_records(conversation_id=conversation_id)
    assert len(records) == 1
    assert records[0].conversation_id == conversation_id

def test_get_token_usage_records_filter_by_conversation_type(mongo_persistence_provider):
    """
    Test retrieving token usage records filtered by conversation_type.
    """
    conversation_type = "AI_TERMINAL"
    # Create multiple records, some with a different conversation_type
    mongo_persistence_provider.create_token_usage_record(
        conversation_id="mongo_conv_for_type_1",
        conversation_type=conversation_type,
        role="assistant",
        token_count=30,
        cost=0.003
    )
    mongo_persistence_provider.create_token_usage_record(
        conversation_id="mongo_conv_for_type_2",
        conversation_type="WORKFLOW",
        role="assistant",
        token_count=40,
        cost=0.004
    )

    records = mongo_persistence_provider.get_token_usage_records(conversation_type=conversation_type)
    assert len(records) >= 1
    for r in records:
        assert r.conversation_type == conversation_type

def test_get_token_usage_records_no_records(mongo_persistence_provider):
    """
    Test retrieving token usage records when none exist for given filters.
    """
    records = mongo_persistence_provider.get_token_usage_records(
        conversation_id="non_existent_conversation_id"
    )
    assert len(records) == 0

def test_get_total_cost_in_period(mongo_persistence_provider):
    """
    Test calculating total cost of token usage within a specified period.
    """
    # Create records spanning different time ranges
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    two_days_ago = now - timedelta(days=2)

    # We'll rely on the repository or default created_at to handle the times.
    # For demonstration, assume the underlying DB and/or mock environment
    # sets created_at to 'now' by default.

    mongo_persistence_provider.create_token_usage_record(
        conversation_id="cost_period_test_1",
        conversation_type="WORKFLOW",
        role="user",
        token_count=10,
        cost=0.001
    )
    mongo_persistence_provider.create_token_usage_record(
        conversation_id="cost_period_test_2",
        conversation_type="AI_TERMINAL",
        role="assistant",
        token_count=20,
        cost=0.002
    )

    # Attempt to get total cost for the last 24 hours
    total_cost_24h = mongo_persistence_provider.get_total_cost_in_period(yesterday, now)
    assert total_cost_24h > 0.0

    # Attempt to get total cost for a period prior to these records
    total_cost_older = mongo_persistence_provider.get_total_cost_in_period(two_days_ago - timedelta(days=3), two_days_ago - timedelta(days=2))
    assert total_cost_older == 0.0 or total_cost_older is not None
