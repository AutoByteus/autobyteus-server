
import pytest
import uuid
from datetime import datetime
from autobyteus_server.ai_terminal.persistence.providers.sql_ai_terminal_provider import SqlAiTerminalProvider
from autobyteus_server.ai_terminal.persistence.domain.models import AiTerminalConversation, AiTerminalMessage, ConversationHistory

@pytest.fixture
def sql_provider():
    """
    Provides an instance of SqlAiTerminalProvider for testing.
    """
    return SqlAiTerminalProvider()

def test_create_conversation(sql_provider):
    """
    Test creating a new conversation in SQL-based database.
    """
    conv = sql_provider.create_conversation()
    assert isinstance(conv, AiTerminalConversation)
    assert isinstance(conv.conversation_id, str)
    # Validate UUID format
    uuid_obj = uuid.UUID(conv.conversation_id)
    assert str(uuid_obj) == conv.conversation_id
    assert isinstance(conv.created_at, datetime)
    assert conv.messages == []

def test_store_message(sql_provider):
    """
    Test storing a message in a SQL-based conversation.
    """
    conv = sql_provider.create_conversation()
    conversation_id = conv.conversation_id

    updated_conv = sql_provider.store_message(
        conversation_id=conversation_id,
        role="user",
        message="Hello from SQL provider!"
    )

    assert len(updated_conv.messages) == 1
    msg = updated_conv.messages[0]
    assert msg.role == "user"
    assert msg.message == "Hello from SQL provider!"

def test_store_message_nonexistent_conversation(sql_provider):
    """
    Test storing a message in a non-existent SQL conversation should fail.
    """
    with pytest.raises(ValueError) as exc_info:
        sql_provider.store_message(
            conversation_id="nonexistent-uuid",
            role="assistant",
            message="Should fail in SQL"
        )
    assert "does not exist" in str(exc_info.value)

def test_list_conversations(sql_provider):
    """
    Test listing conversations with pagination in SQL-based database.
    """
    # Create multiple conversations
    for _ in range(3):
        conv = sql_provider.create_conversation()
        sql_provider.store_message(conversation_id=conv.conversation_id, role="user", message="Test message")

    history: ConversationHistory = sql_provider.list_conversations(page=1, page_size=2)
    assert history.total_conversations >= 3
    assert len(history.conversations) == 2
    assert history.current_page == 1

    # Next page
    history_page_2: ConversationHistory = sql_provider.list_conversations(page=2, page_size=2)
    assert history_page_2.current_page == 2

def test_store_message_with_token_and_cost(sql_provider):
    """
    Test storing a message with a specified token_count and cost in SQL-based conversation.
    """
    conv = sql_provider.create_conversation()
    conversation_id = conv.conversation_id

    updated_conv = sql_provider.store_message(
        conversation_id=conversation_id,
        role="assistant",
        message="Message with usage data in SQL",
        token_count=15,
        cost=0.05
    )
    msg = updated_conv.messages[-1]
    assert msg.token_count == 15
    assert msg.cost == 0.05
