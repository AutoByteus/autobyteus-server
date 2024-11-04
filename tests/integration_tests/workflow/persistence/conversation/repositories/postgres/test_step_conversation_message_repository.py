import pytest
from datetime import datetime
from autobyteus_server.workflow.persistence.conversation.repositories.postgres.step_conversation_message_repository import (
    StepConversationMessageRepository
)
from autobyteus_server.workflow.persistence.conversation.repositories.postgres.step_conversation_repository import StepConversationRepository

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
    step_name = "sample_step"
    conversation = conversation_repo.create_step_conversation(step_name)
    return {
        "step_conversation_id": conversation.id,
        "role": "user",
        "message": "Sample message"
    }

def test_should_create_message_successfully(message_repo, sample_message_data):
    """Test successful creation of a new message."""
    # Act
    result = message_repo.create_message(
        step_conversation_id=sample_message_data["step_conversation_id"],
        role=sample_message_data["role"],
        message=sample_message_data["message"]
    )

    # Assert
    assert result is not None
    assert result.step_conversation_id == sample_message_data["step_conversation_id"]
    assert result.role == sample_message_data["role"]
    assert result.message == sample_message_data["message"]
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
    """Test retrieval of all messages for a specific conversation."""
    # Arrange
    message_repo.create_message(
        step_conversation_id=sample_message_data["step_conversation_id"],
        role=sample_message_data["role"],
        message=sample_message_data["message"]
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

def test_should_update_message_successfully(message_repo, sample_message_data):
    """Test successful update of an existing message."""
    # Arrange
    message = message_repo.create_message(
        step_conversation_id=sample_message_data["step_conversation_id"],
        role=sample_message_data["role"],
        message=sample_message_data["message"]
    )
    new_content = "Updated message"

    # Act
    updated_message = message_repo.update_message(message.id, new_content)

    # Assert
    assert updated_message is not None
    assert updated_message.message == new_content
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
        message=sample_message_data["message"]
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
    """Test creating and retrieving multiple messages in a conversation."""
    # Arrange
    messages_data = [
        {"role": "user", "message": "First message"},
        {"role": "assistant", "message": "Second message"},
        {"role": "user", "message": "Third message"}
    ]
    
    # Act
    for msg_data in messages_data:
        message_repo.create_message(
            step_conversation_id=sample_message_data["step_conversation_id"],
            role=msg_data["role"],
            message=msg_data["message"]
        )
    
    # Assert
    messages = message_repo.get_messages_by_step_conversation_id(
        step_conversation_id=sample_message_data["step_conversation_id"]
    )
    assert len(messages) == len(messages_data)
    for i, msg in enumerate(messages):
        assert msg.role == messages_data[i]["role"]
        assert msg.message == messages_data[i]["message"]

def test_should_maintain_message_order(message_repo, sample_message_data):
    """Test that messages are retrieved in the order they were created."""
    # Arrange
    messages_data = [
        {"role": "user", "message": "First"},
        {"role": "assistant", "message": "Second"},
        {"role": "user", "message": "Third"}
    ]
    
    for msg_data in messages_data:
        message_repo.create_message(
            step_conversation_id=sample_message_data["step_conversation_id"],
            role=msg_data["role"],
            message=msg_data["message"]
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