
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from autobyteus_server.ai_terminal.persistence.providers.sql_ai_terminal_provider import SqlAiTerminalProvider
from autobyteus_server.ai_terminal.persistence.domain.models import AiTerminalConversation

pytestmark = pytest.mark.integration

@pytest.fixture
def sql_ai_terminal_provider():
    """
    Provides a SqlAiTerminalProvider instance for testing AI Terminal persistence in SQL databases.
    """
    return SqlAiTerminalProvider()

def test_create_conversation(sql_ai_terminal_provider):
    """
    Test creating a new conversation in a SQL database via SqlAiTerminalProvider.
    """
    conversation = sql_ai_terminal_provider.create_conversation()
    assert isinstance(conversation, AiTerminalConversation)
    assert conversation.conversation_id is not None
    assert conversation.created_at is not None
    assert len(conversation.messages) == 0

def test_store_message(sql_ai_terminal_provider):
    """
    Test storing a new message in an existing conversation via SqlAiTerminalProvider.
    """
    conversation = sql_ai_terminal_provider.create_conversation()
    updated_conversation = sql_ai_terminal_provider.store_message(
        conversation_id=conversation.conversation_id,
        role="assistant",
        message="Hello from SQLAI Terminal tests",
        token_count=10,
        cost=0.002
    )
    assert len(updated_conversation.messages) == 1
    message = updated_conversation.messages[0]
    assert message.role == "assistant"
    assert message.message == "Hello from SQLAI Terminal tests"
    assert message.token_count == 10
    assert message.cost == 0.002

def test_store_message_nonexistent_conversation(sql_ai_terminal_provider):
    """
    Test storing a message in a nonexistent conversation should raise an error.
    """
    with pytest.raises(ValueError):
        sql_ai_terminal_provider.store_message(
            conversation_id="nonexistent-id",
            role="assistant",
            message="This does not exist"
        )

def test_get_conversation_history(sql_ai_terminal_provider):
    """
    In SQLAiTerminalProvider, get_conversation_history is implemented differently.
    For the scope of this integration test, we'll assume listing all conversations (and messages)
    is performed via get_conversation_history with pagination or a direct approach.
    This example will demonstrate retrieving multiple conversation pages.
    """
    # Create multiple conversations to populate the DB
    for _ in range(2):
        conv = sql_ai_terminal_provider.create_conversation()
        sql_ai_terminal_provider.store_message(
            conversation_id=conv.conversation_id,
            role="user",
            message=f"Message for conversation {conv.conversation_id}"
        )

    # The provider's get_conversation_history is actually returning paginated results of all conversations,
    # so let's attempt to call it and see if we get multiple.
    history_page = sql_ai_terminal_provider.get_conversation_history(page=1, page_size=2)
    assert history_page.current_page == 1
    assert len(history_page.conversations) <= 2
    assert history_page.total_conversations >= 2

def test_get_conversation_history_empty(sql_ai_terminal_provider):
    """
    Test retrieving conversation history when no conversations have been created.
    This should return an empty or zero-based paginated response.
    """
    history_page = sql_ai_terminal_provider.get_conversation_history(page=1, page_size=5)
    assert len(history_page.conversations) == 0
    assert history_page.total_conversations == 0
    assert history_page.current_page == 1
