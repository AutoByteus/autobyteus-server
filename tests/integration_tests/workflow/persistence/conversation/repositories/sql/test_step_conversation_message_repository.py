
import pytest
from datetime import datetime
from autobyteus_server.workflow.persistence.conversation.repositories.sql.step_conversation_message_repository import (
    StepConversationMessageRepository
)
from autobyteus_server.workflow.persistence.conversation.repositories.sql.step_conversation_repository import StepConversationRepository

pytestmark = pytest.mark.integration

@pytest.fixture
def message_repo():
    """
    Provides the singleton StepConversationMessageRepository instance for testing.
    
    Returns:
        StepConversationMessageRepository: Repository instance for testing
    """
    return StepConversationMessageRepository()

@pytest.fixture
def sample_message_data(message_repo):
    """
    Provides sample message data for testing.
    
    Args:
        message_repo: The message repository fixture.
    
    Returns:
        dict: Sample message data.
    """
    # Create a sample conversation to associate messages with
    conversation_repo = StepConversationRepository()
    step_name = "sample_step_sql"
    conversation = conversation_repo.create_step_conversation(step_name)
    return {
        "step_conversation_id": conversation.id,
        "role": "user",
        "message": "Sample message",
        "token_count": 100,
        "cost": 0.05
    }

def test_should_create_message_successfully(message_repo, sample_message_data):
    """Test successful creation of a new message with token count and cost."""
    # Act
    result = message_repo.create_message(
        step_conversation_id=sample_message_data["step_conversation_id"],
        role=sample_message_data["role"],
        message=sample_message_data["message"],
        token_count=sample_message_data["token_count"],
        cost=sample_message_data["cost"]
    )

    # Assert
    assert result is not None
    assert result.step_conversation_id == sample_message_data["step_conversation_id"]
    assert result.role == sample_message_data["role"]
    assert result.message == sample_message_data["message"]
    assert result.token_count == sample_message_data["token_count"]
    assert result.cost == sample_message_data["cost"]
    assert isinstance(result.timestamp, datetime)

def test_should_retrieve_messages_from_empty_conversation(message_repo, sample_message_data):
    """Test retrieval of messages from an empty conversation."""
    # Act
    messages = message_repo.get_messages_by_step_conversation_id(
        step_conversation_id=sample_message_data["step_conversation_id"]
    )

    # Assert
    assert len(messages) == 0

def test_should_retrieve_all_messages_for_conversation(message_repo, sample_message_data):
    """Test retrieval of all messages for a specific conversation, including token count and cost."""
    # Arrange
    message_repo.create_message(
        step_conversation_id=sample_message_data["step_conversation_id"],
        role=sample_message_data["role"],
        message=sample_message_data["message"],
        token_count=sample_message_data["token_count"],
        cost=sample_message_data["cost"]
    )

    # Act
    messages = message_repo.get_messages_by_step_conversation_id(
        step_conversation_id=sample_message_data["step_conversation_id"]
    )

    # Assert
    assert len(messages) == 1
    assert messages[0].step_conversation_id == sample_message_data["step_conversation_id"]
    assert messages[0].role == sample_message_data["role"]
    assert messages[0].message == sample_message_data["message"]
    assert messages[0].token_count == sample_message_data["token_count"]
    assert messages[0].cost == sample_message_data["cost"]

def test_should_update_message_successfully(message_repo, sample_message_data):
    """Test successful update of an existing message, including token count and cost."""
    # Arrange
    message = message_repo.create_message(
        step_conversation_id=sample_message_data["step_conversation_id"],
        role=sample_message_data["role"],
        message=sample_message_data["message"],
        token_count=sample_message_data["token_count"],
        cost=sample_message_data["cost"]
    )
    new_content = "Updated message"
    new_token_count = 150
    new_cost = 0.075

    # Act
    updated_message = message_repo.update_message(message.id, new_content, token_count=new_token_count, cost=new_cost)

    # Assert
    assert updated_message is not None
    assert updated_message.message == new_content
    assert updated_message.token_count == new_token_count
    assert updated_message.cost == new_cost
    assert updated_message.step_conversation_id == sample_message_data["step_conversation_id"]
    assert updated_message.role == sample_message_data["role"]

def test_should_handle_update_of_nonexistent_message(message_repo):
    """Test update behavior with non-existent message ID."""
    # Act
    result = message_repo.update_message(999, "New content")

    # Assert
    assert result is None

def test_should_delete_message_successfully(message_repo, sample_message_data):
    """Test successful deletion of an existing message."""
    # Arrange
    message = message_repo.create_message(
        step_conversation_id=sample_message_data["step_conversation_id"],
        role=sample_message_data["role"],
        message=sample_message_data["message"],
        token_count=sample_message_data["token_count"],
        cost=sample_message_data["cost"]
    )

    # Act
    result = message_repo.delete_message(message.id)

    # Assert
    assert result is True
    messages = message_repo.get_messages_by_step_conversation_id(
        step_conversation_id=sample_message_data["step_conversation_id"]
    )
    assert len(messages) == 0

def test_should_handle_deletion_of_nonexistent_message(message_repo):
    """Test deletion behavior with non-existent message ID."""
    # Act
    result = message_repo.delete_message(999)

    # Assert
    assert result is False

def test_should_create_multiple_messages_in_conversation(message_repo, sample_message_data):
    """Test creating and retrieving multiple messages in a conversation, including token count and cost."""
    # Arrange
    messages_data = [
        {"role": "user", "message": "First message", "token_count": 50, "cost": 0.025},
        {"role": "assistant", "message": "Second message", "token_count": 75, "cost": 0.0375},
        {"role": "user", "message": "Third message", "token_count": 100, "cost": 0.05}
    ]
    
    # Act
    for msg_data in messages_data:
        message_repo.create_message(
            step_conversation_id=sample_message_data["step_conversation_id"],
            role=msg_data["role"],
            message=msg_data["message"],
            token_count=msg_data["token_count"],
            cost=msg_data["cost"]
        )
    
    # Assert
    messages = message_repo.get_messages_by_step_conversation_id(
        step_conversation_id=sample_message_data["step_conversation_id"]
    )
    assert len(messages) == len(messages_data)
    for i, msg in enumerate(messages):
        assert msg.role == messages_data[i]["role"]
        assert msg.message == messages_data[i]["message"]
        assert msg.token_count == messages_data[i]["token_count"]
        assert msg.cost == messages_data[i]["cost"]

def test_should_maintain_message_order(message_repo, sample_message_data):
    """Test that messages are retrieved in the order they were created, including token count and cost."""
    # Arrange
    messages_data = [
        {"role": "user", "message": "First", "token_count": 30, "cost": 0.015},
        {"role": "assistant", "message": "Second", "token_count": 45, "cost": 0.0225},
        {"role": "user", "message": "Third", "token_count": 60, "cost": 0.03}
    ]
    
    for msg_data in messages_data:
        message_repo.create_message(
            step_conversation_id=sample_message_data["step_conversation_id"],
            role=msg_data["role"],
            message=msg_data["message"],
            token_count=msg_data["token_count"],
            cost=msg_data["cost"]
        )
    
    # Act
    messages = message_repo.get_messages_by_step_conversation_id(
        step_conversation_id=sample_message_data["step_conversation_id"]
    )
    
    # Assert
    assert len(messages) == len(messages_data)
    for i, msg in enumerate(messages):
        assert msg.message == messages_data[i]["message"]
        assert msg.role == messages_data[i]["role"]
        assert msg.token_count == messages_data[i]["token_count"]
        assert msg.cost == messages_data[i]["cost"]

def test_should_update_token_usage_successfully(message_repo, sample_message_data):
    """Test successful update of token usage using update_token_usage method."""
    # Arrange
    message = message_repo.create_message(
        step_conversation_id=sample_message_data["step_conversation_id"],
        role=sample_message_data["role"],
        message=sample_message_data["message"],
        token_count=sample_message_data["token_count"],
        cost=sample_message_data["cost"]
    )
    new_token_count = 200
    new_cost = 0.10

    # Act
    updated_message = message_repo.update_token_usage(
        message_id=message.id,
        token_count=new_token_count,
        cost=new_cost
    )

    # Assert
    assert updated_message is not None
    assert updated_message.token_count == new_token_count
    assert updated_message.cost == new_cost

def test_should_handle_update_token_usage_for_nonexistent_message(message_repo):
    """Test update_token_usage behavior with non-existent message ID."""
    # Act
    updated_message = message_repo.update_token_usage(
        message_id=999,
        token_count=100,
        cost=0.05
    )

    # Assert
    assert updated_message is None
