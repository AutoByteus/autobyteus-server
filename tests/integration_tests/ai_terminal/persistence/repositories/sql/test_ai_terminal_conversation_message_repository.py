
import pytest
from datetime import datetime
from autobyteus_server.ai_terminal.persistence.models.sql.conversation_message import AiTerminalConversationMessage
from autobyteus_server.ai_terminal.persistence.models.sql.conversation import AiTerminalConversation
from autobyteus_server.ai_terminal.persistence.repositories.sql.ai_terminal_conversation_message_repository import (
    AiTerminalConversationMessageRepository
)
from autobyteus_server.ai_terminal.persistence.repositories.sql.ai_terminal_conversation_repository import (
    AiTerminalConversationRepository
)

pytestmark = pytest.mark.integration

@pytest.fixture(scope="function")
def conversation_message_repo():
    """
    Provides an instance of AiTerminalConversationMessageRepository for SQL.
    """
    return AiTerminalConversationMessageRepository()

@pytest.fixture(scope="function")
def conversation_repo():
    """
    Provides an instance of AiTerminalConversationRepository for SQL.
    """
    return AiTerminalConversationRepository()

@pytest.fixture
def sample_sql_conversation(conversation_repo):
    """
    Creates a sample conversation for message tests.
    """
    return conversation_repo.create_conversation()

def test_create_message(conversation_message_repo, sample_sql_conversation):
    """
    Test creating a conversation message.
    """
    new_msg = conversation_message_repo.create_message(
        conversation_id=sample_sql_conversation.id,
        role="user",
        message="Hello from SQL message repo!",
        token_count=10,
        cost=0.05
    )
    assert isinstance(new_msg, AiTerminalConversationMessage)
    assert new_msg.conversation_id == sample_sql_conversation.id
    assert new_msg.role == "user"
    assert new_msg.message == "Hello from SQL message repo!"
    assert new_msg.token_count == 10
    assert new_msg.cost == 0.05

def test_get_messages_by_conversation_id(conversation_message_repo, sample_sql_conversation):
    """
    Test retrieving messages by conversation ID.
    """
    # Create multiple messages
    for i in range(3):
        conversation_message_repo.create_message(
            conversation_id=sample_sql_conversation.id,
            role="user" if i % 2 == 0 else "assistant",
            message=f"Message {i}",
            token_count=5 * i,
            cost=0.01 * i
        )

    messages = conversation_message_repo.get_messages_by_conversation_id(sample_sql_conversation.id)
    assert len(messages) == 3
    for idx, msg in enumerate(messages):
        assert msg.message == f"Message {idx}"
        if idx % 2 == 0:
            assert msg.role == "user"
        else:
            assert msg.role == "assistant"

def test_update_message(conversation_message_repo, sample_sql_conversation):
    """
    Test updating message content.
    """
    msg = conversation_message_repo.create_message(
        conversation_id=sample_sql_conversation.id,
        role="assistant",
        message="Initial content"
    )
    updated = conversation_message_repo.update_message(msg.id, "Updated content")
    assert updated is not None
    assert updated.message == "Updated content"

def test_update_message_nonexistent(conversation_message_repo):
    """
    Test updating a nonexistent message returns None.
    """
    updated = conversation_message_repo.update_message(999999, "Should not exist")
    assert updated is None

def test_delete_message(conversation_message_repo, sample_sql_conversation):
    """
    Test deleting a message from the conversation.
    """
    msg = conversation_message_repo.create_message(
        conversation_id=sample_sql_conversation.id,
        role="assistant",
        message="Message to delete"
    )
    conversation_message_repo.delete(msg)
    remaining = conversation_message_repo.get_messages_by_conversation_id(sample_sql_conversation.id)
    assert len(remaining) == 0

def test_delete_nonexistent_message(conversation_message_repo):
    """
    Test deleting a nonexistent message returns False.
    """
    class DummyMessage:
        id = 999999

    dummy = DummyMessage()
    # Attempt to delete a message that does not exist in the repository.
    result = conversation_message_repo.delete(dummy)
    assert result is False

def test_update_token_usage(conversation_message_repo, sample_sql_conversation):
    """
    Test updating token_count and cost for a message.
    """
    msg = conversation_message_repo.create_message(
        conversation_id=sample_sql_conversation.id,
        role="user",
        message="Message with usage"
    )
    updated_msg = conversation_message_repo.update_token_usage(msg.id, token_count=50, cost=0.2)
    assert updated_msg is not None
    assert updated_msg.token_count == 50
    assert updated_msg.cost == 0.2

def test_update_token_usage_nonexistent(conversation_message_repo):
    """
    Test updating token usage on a nonexistent message returns None.
    """
    updated = conversation_message_repo.update_token_usage(999999, token_count=10, cost=0.05)
    assert updated is None
