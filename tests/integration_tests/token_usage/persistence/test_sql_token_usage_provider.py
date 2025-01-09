import pytest
from autobyteus_server.token_usage.provider.sql_persistence_provider import SqlPersistenceProvider
from autobyteus_server.token_usage.domain.token_usage_record import TokenUsageRecord
from datetime import datetime, timedelta
import uuid

@pytest.fixture
def sql_persistence_provider():
    """
    Provides the singleton SqlPersistenceProvider instance for testing.
    """
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
    llm_model = "sql_test_model"

    record = sql_persistence_provider.create_token_usage_record(
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
    assert isinstance(record.created_at, datetime)
    assert record.llm_model == llm_model
    if record.token_usage_record_id:
        assert uuid.UUID(record.token_usage_record_id)  # Validate UUID format
    else:
        pytest.fail("token_usage_record_id should not be None after creation")

def test_get_usage_records_in_period_no_filters(sql_persistence_provider):
    """
    Test retrieving usage records within a wide date range, without filtering by LLM model.
    """
    now = datetime.utcnow()
    past = now - timedelta(days=1)
    future = now + timedelta(days=1)

    # Create multiple records
    record1 = sql_persistence_provider.create_token_usage_record(
        conversation_id="sql_conversation_1",
        conversation_type="AI_TERMINAL",
        role="user",
        token_count=10,
        cost=0.001
    )
    record2 = sql_persistence_provider.create_token_usage_record(
        conversation_id="sql_conversation_2",
        conversation_type="WORKFLOW",
        role="assistant",
        token_count=20,
        cost=0.002
    )

    records = sql_persistence_provider.get_usage_records_in_period(start_date=past, end_date=future)
    found_ids = {r.conversation_id for r in records}
    assert record1.conversation_id in found_ids
    assert record2.conversation_id in found_ids

def test_get_usage_records_in_period_filter_by_llm_model(sql_persistence_provider):
    """
    Test retrieving usage records filtered by LLM model within a date range.
    """
    now = datetime.utcnow()
    past = now - timedelta(days=1)
    future = now + timedelta(days=1)

    # Create records with different models
    record_a = sql_persistence_provider.create_token_usage_record(
        conversation_id="sql_conv_a",
        conversation_type="WORKFLOW",
        role="user",
        token_count=30,
        cost=0.003,
        llm_model="modelSQLA"
    )
    record_b = sql_persistence_provider.create_token_usage_record(
        conversation_id="sql_conv_b",
        conversation_type="AI_TERMINAL",
        role="assistant",
        token_count=40,
        cost=0.004,
        llm_model="modelSQLB"
    )

    # Retrieve only the records for modelSQLA
    filtered_records = sql_persistence_provider.get_usage_records_in_period(
        start_date=past,
        end_date=future,
        llm_model="modelSQLA"
    )
    assert len(filtered_records) == 1
    assert filtered_records[0].llm_model == "modelSQLA"
    assert filtered_records[0].conversation_id == record_a.conversation_id

def test_get_usage_records_in_period_no_records(sql_persistence_provider):
    """
    Test retrieving usage records for a period with no matches.
    """
    # Create a record now
    sql_persistence_provider.create_token_usage_record(
        conversation_id="sql_no_record_test",
        conversation_type="WORKFLOW",
        role="assistant",
        token_count=50,
        cost=0.005,
        llm_model="modelSQLX"
    )

    # Query a date range entirely in the past
    now = datetime.utcnow()
    older_start = now - timedelta(days=10)
    older_end = now - timedelta(days=9)
    records = sql_persistence_provider.get_usage_records_in_period(
        start_date=older_start,
        end_date=older_end
    )
    assert len(records) == 0

def test_get_total_cost_in_period(sql_persistence_provider):
    """
    Test retrieving the total cost of token usage within a specified time period.
    """
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    tomorrow = now + timedelta(days=1)

    # Create records spanning the relevant time
    sql_persistence_provider.create_token_usage_record(
        conversation_id="sql_cost_test_1",
        conversation_type="WORKFLOW",
        role="user",
        token_count=10,
        cost=0.001,
        llm_model="modelSQL7"
    )
    sql_persistence_provider.create_token_usage_record(
        conversation_id="sql_cost_test_2",
        conversation_type="AI_TERMINAL",
        role="assistant",
        token_count=20,
        cost=0.002,
        llm_model="modelSQL8"
    )

    # Calculate total cost in a time range that should capture these records
    total_cost = sql_persistence_provider.get_total_cost_in_period(yesterday, tomorrow)
    assert total_cost > 0.0

    # Calculate total cost in a time range that excludes these records
    old_start = now - timedelta(days=10)
    old_end = now - timedelta(days=9)
    total_cost_older = sql_persistence_provider.get_total_cost_in_period(old_start, old_end)
    assert total_cost_older == 0.0
