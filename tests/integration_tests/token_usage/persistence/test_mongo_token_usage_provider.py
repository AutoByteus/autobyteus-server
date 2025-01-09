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
    llm_model = "test_model"

    record = mongo_persistence_provider.create_token_usage_record(
        conversation_id=conversation_id,
        conversation_type=conversation_type,
        role=role,
        token_count=token_count,
        cost=cost,
        llm_model=llm_model
    )

    assert isinstance(record, TokenUsageRecord)
    assert record.conversation_id == conversation_id
    assert record.conversation_type == conversation_type
    assert record.role == role
    assert record.token_count == token_count
    assert record.cost == cost
    assert record.created_at is not None
    assert record.llm_model == llm_model

def test_get_usage_records_in_period_no_filters(mongo_persistence_provider):
    """
    Test retrieving all token usage records within a wide date range, without filtering by LLM model.
    """
    # Create a couple of records
    record1 = mongo_persistence_provider.create_token_usage_record(
        conversation_id="mongo_conversation_1",
        conversation_type="AI_TERMINAL",
        role="user",
        token_count=10,
        cost=0.001,
        llm_model="model1"
    )
    record2 = mongo_persistence_provider.create_token_usage_record(
        conversation_id="mongo_conversation_2",
        conversation_type="WORKFLOW",
        role="assistant",
        token_count=20,
        cost=0.002,
        llm_model="model2"
    )

    # Use a date range that definitely includes our newly-created records
    now = datetime.utcnow()
    past = now - timedelta(days=1)
    future = now + timedelta(days=1)

    records = mongo_persistence_provider.get_usage_records_in_period(start_date=past, end_date=future)
    # We expect at least these two
    found_ids = {r.conversation_id for r in records}
    assert record1.conversation_id in found_ids
    assert record2.conversation_id in found_ids

def test_get_usage_records_in_period_filter_by_llm_model(mongo_persistence_provider):
    """
    Test retrieving token usage records within a date range, filtered by LLM model.
    """
    now = datetime.utcnow()
    past = now - timedelta(days=1)
    future = now + timedelta(days=1)

    # Create multiple records with different LLM models
    record_a = mongo_persistence_provider.create_token_usage_record(
        conversation_id="mongo_conv_a",
        conversation_type="WORKFLOW",
        role="user",
        token_count=50,
        cost=0.005,
        llm_model="modelA"
    )
    record_b = mongo_persistence_provider.create_token_usage_record(
        conversation_id="mongo_conv_b",
        conversation_type="AI_TERMINAL",
        role="assistant",
        token_count=60,
        cost=0.006,
        llm_model="modelB"
    )

    # Retrieve only records with llm_model="modelA"
    filtered_records = mongo_persistence_provider.get_usage_records_in_period(
        start_date=past,
        end_date=future,
        llm_model="modelA"
    )
    assert len(filtered_records) == 1
    assert filtered_records[0].llm_model == "modelA"
    assert filtered_records[0].conversation_id == record_a.conversation_id

def test_get_usage_records_in_period_no_records(mongo_persistence_provider):
    """
    Test retrieving token usage records for a date range that should match none.
    """
    # Create a record now
    mongo_persistence_provider.create_token_usage_record(
        conversation_id="mongo_no_record_test",
        conversation_type="WORKFLOW",
        role="assistant",
        token_count=30,
        cost=0.003,
        llm_model="modelX"
    )

    # Query a date range entirely in the past
    now = datetime.utcnow()
    older_start = now - timedelta(days=10)
    older_end = now - timedelta(days=9)
    records = mongo_persistence_provider.get_usage_records_in_period(
        start_date=older_start,
        end_date=older_end
    )
    assert len(records) == 0

def test_get_total_cost_in_period(mongo_persistence_provider):
    """
    Test calculating total cost of token usage within a specified period.
    """
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    tomorrow = now + timedelta(days=1)

    # Create records spanning the relevant time
    mongo_persistence_provider.create_token_usage_record(
        conversation_id="cost_period_test_1",
        conversation_type="WORKFLOW",
        role="user",
        token_count=10,
        cost=0.001,
        llm_model="model7"
    )
    mongo_persistence_provider.create_token_usage_record(
        conversation_id="cost_period_test_2",
        conversation_type="AI_TERMINAL",
        role="assistant",
        token_count=20,
        cost=0.002,
        llm_model="model8"
    )

    # Calculate total cost for the last 24 hours
    total_cost = mongo_persistence_provider.get_total_cost_in_period(yesterday, tomorrow)
    assert total_cost > 0.0

    # Calculate total cost outside this period (far in the past)
    old_start = now - timedelta(days=10)
    old_end = now - timedelta(days=9)
    total_cost_older = mongo_persistence_provider.get_total_cost_in_period(old_start, old_end)
    # Should be 0.0 if no records fall in that range
    assert total_cost_older == 0.0
