
import pytest
from datetime import datetime, timedelta
from autobyteus_server.token_usage.repositories.sql.token_usage_record_repository import TokenUsageRecordRepository
from autobyteus_server.token_usage.models.sql.token_usage_record import TokenUsageRecord

pytestmark = pytest.mark.integration

@pytest.fixture(scope="function")
def token_usage_repo():
    """
    Provides the TokenUsageRecordRepository instance for testing.
    """
    return TokenUsageRecordRepository()

@pytest.fixture
def sample_token_usage_data():
    """
    Provides sample token usage data for testing.
    """
    return {
        "conversation_id": "test-conversation-id",
        "conversation_type": "agent",
        "role": "user",
        "token_count": 100,
        "cost": 0.002
    }

def test_create_usage_record(token_usage_repo, sample_token_usage_data):
    """Test creation of a new usage record."""
    # Act
    record = token_usage_repo.create_usage_record(
        conversation_id=sample_token_usage_data["conversation_id"],
        conversation_type=sample_token_usage_data["conversation_type"],
        role=sample_token_usage_data["role"],
        token_count=sample_token_usage_data["token_count"],
        cost=sample_token_usage_data["cost"]
    )

    # Assert
    assert record is not None
    assert isinstance(record, TokenUsageRecord)
    assert record.conversation_id == sample_token_usage_data["conversation_id"]
    assert record.conversation_type == sample_token_usage_data["conversation_type"]
    assert record.role == sample_token_usage_data["role"]
    assert record.token_count == sample_token_usage_data["token_count"]
    assert record.cost == sample_token_usage_data["cost"]
    assert isinstance(record.created_at, datetime)

def test_get_usage_records_by_conversation_id(token_usage_repo, sample_token_usage_data):
    """Test retrieval of usage records by conversation ID."""
    # Arrange
    record = token_usage_repo.create_usage_record(
        conversation_id=sample_token_usage_data["conversation_id"],
        conversation_type=sample_token_usage_data["conversation_type"],
        role=sample_token_usage_data["role"],
        token_count=sample_token_usage_data["token_count"],
        cost=sample_token_usage_data["cost"]
    )

    # Act
    records = token_usage_repo.get_usage_records_by_conversation_id(
        conversation_id=sample_token_usage_data["conversation_id"]
    )

    # Assert
    assert len(records) == 1
    assert records[0].conversation_id == sample_token_usage_data["conversation_id"]
    assert records[0].conversation_type == sample_token_usage_data["conversation_type"]
    assert records[0].role == sample_token_usage_data["role"]
    assert records[0].token_count == sample_token_usage_data["token_count"]
    assert records[0].cost == sample_token_usage_data["cost"]

def test_get_total_cost_in_period(token_usage_repo):
    """Test calculation of total cost within a specified time period."""
    # Arrange
    base_time = datetime.utcnow()
    records_data = [
        {
            "conversation_id": "conv-1",
            "conversation_type": "agent",
            "role": "user",
            "token_count": 100,
            "cost": 0.002
        },
        {
            "conversation_id": "conv-2",
            "conversation_type": "agent",
            "role": "assistant",
            "token_count": 150,
            "cost": 0.003
        },
        {
            "conversation_id": "conv-3",
            "conversation_type": "agent",
            "role": "user",
            "token_count": 200,
            "cost": 0.004
        }
    ]

    for data in records_data:
        token_usage_repo.create_usage_record(
            conversation_id=data["conversation_id"],
            conversation_type=data["conversation_type"],
            role=data["role"],
            token_count=data["token_count"],
            cost=data["cost"]
        )

    # Act
    start_date = base_time - timedelta(days=1)
    end_date = base_time + timedelta(days=1)
    total_cost = token_usage_repo.get_total_cost_in_period(start_date, end_date)

    # Assert
    expected_total = sum(record["cost"] for record in records_data)
    assert total_cost == expected_total

def test_get_usage_records_empty_conversation(token_usage_repo):
    """Test retrieval of usage records for a conversation with no records."""
    # Act
    records = token_usage_repo.get_usage_records_by_conversation_id("nonexistent-id")

    # Assert
    assert len(records) == 0

def test_get_total_cost_empty_period(token_usage_repo):
    """Test calculation of total cost for a period with no records."""
    # Arrange
    start_date = datetime.utcnow() - timedelta(days=1)
    end_date = datetime.utcnow()

    # Act
    total_cost = token_usage_repo.get_total_cost_in_period(start_date, end_date)

    # Assert
    assert total_cost == 0

def test_multiple_records_same_conversation(token_usage_repo, sample_token_usage_data):
    """Test creation and retrieval of multiple records for the same conversation."""
    # Arrange
    conversation_id = "test-multi-conv-id"
    records_data = [
        {
            "conversation_id": conversation_id,
            "conversation_type": "agent",
            "role": "user",
            "token_count": 100,
            "cost": 0.002
        },
        {
            "conversation_id": conversation_id,
            "conversation_type": "agent",
            "role": "assistant",
            "token_count": 150,
            "cost": 0.003
        },
        {
            "conversation_id": conversation_id,
            "conversation_type": "agent",
            "role": "user",
            "token_count": 200,
            "cost": 0.004
        }
    ]

    # Create multiple records
    created_records = []
    for data in records_data:
        record = token_usage_repo.create_usage_record(
            conversation_id=data["conversation_id"],
            conversation_type=data["conversation_type"],
            role=data["role"],
            token_count=data["token_count"],
            cost=data["cost"]
        )
        created_records.append(record)

    # Act
    retrieved_records = token_usage_repo.get_usage_records_by_conversation_id(conversation_id)

    # Assert
    assert len(retrieved_records) == len(records_data)
    
    # Verify records are returned in order of creation
    for i, record in enumerate(retrieved_records):
        assert record.conversation_id == conversation_id
        assert record.conversation_type == records_data[i]["conversation_type"]
        assert record.role == records_data[i]["role"]
        assert record.token_count == records_data[i]["token_count"]
        assert record.cost == records_data[i]["cost"]
        
    # Verify total cost
    total_cost = sum(record.cost for record in retrieved_records)
    expected_total = sum(data["cost"] for data in records_data)
    assert total_cost == expected_total
