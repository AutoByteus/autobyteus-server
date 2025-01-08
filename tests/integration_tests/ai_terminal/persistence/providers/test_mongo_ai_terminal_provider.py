
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from autobyteus_server.ai_terminal.persistence.providers.mongo_ai_terminal_provider import MongoAiTerminalProvider
from autobyteus_server.ai_terminal.persistence.domain.models import AiTerminalConversation

pytestmark = pytest.mark.integration

@pytest.fixture
def mongo_ai_terminal_provider():
    """
    Provides a MongoAiTerminalProvider instance for testing AI Terminal persistence in MongoDB.
    """
    return MongoAiTerminalProvider()

def test_create_conversation(mongo_ai_terminal_provider):
    """
    Test creating a new conversation in MongoDB via MongoAiTerminalProvider.
    """
    conversation = mongo_ai_terminal_provider.create_conversation()
    assert isinstance(conversation, AiTerminalConversation)
    assert conversation.conversation_id is not None
    assert conversation.created_at is not None
    assert len(conversation.messages) == 0

def test_store_message(mongo_ai_terminal_provider):
    """
    Test storing a new message in an existing conversation via MongoAiTerminalProvider.
    """
    conversation = mongo_ai_terminal_provider.create_conversation()
    updated_conversation = mongo_ai_terminal_provider.store_message(
        conversation_id=conversation.conversation_id,
        role="user",
        message="Hello from MongoAI Terminal tests",
        token_count=5,
        cost=0.001
    )
    assert len(updated_conversation.messages) == 1
    message = updated_conversation.messages[0]
    assert message.role == "user"
    assert message.message == "Hello from MongoAI Terminal tests"
    assert message.token_count == 5
    assert message.cost == 0.001

def test_get_conversation_history(mongo_ai_terminal_provider):
    """
    Test retrieving conversation history from MongoDB via MongoAiTerminalProvider.
    """
    conversation = mongo_ai_terminal_provider.create_conversation()
    mongo_ai_terminal_provider.store_message(
        conversation_id=conversation.conversation_id,
        role="assistant",
        message="Hi, how can I help?",
        token_count=10,
        cost=0.002
    )
    retrieved_conversation = mongo_ai_terminal_provider.get_conversation_history(conversation.conversation_id)
    assert retrieved_conversation.conversation_id == conversation.conversation_id
    assert len(retrieved_conversation.messages) == 1
    assert retrieved_conversation.messages[0].role == "assistant"

def test_list_conversations(mongo_ai_terminal_provider):
    """
    Test listing conversations with pagination via MongoAiTerminalProvider.
    """
    # Create multiple conversations
    for _ in range(3):
        mongo_ai_terminal_provider.create_conversation()

    history_page = mongo_ai_terminal_provider.list_conversations(page=1, page_size=2)
    assert len(history_page.conversations) <= 2
    assert history_page.current_page == 1
    assert history_page.total_conversations >= 3

    if history_page.total_conversations > 2:
        # Check the second page
        history_page_2 = mongo_ai_terminal_provider.list_conversations(page=2, page_size=2)
        assert history_page_2.current_page == 2
        # We don't strictly know how many will be on page 2, but it should be > 0 if total_conversations > 2

def test_store_message_nonexistent_conversation(mongo_ai_terminal_provider):
    """
    Test storing a message in a nonexistent conversation should raise an error.
    """
    with pytest.raises(Exception):
        mongo_ai_terminal_provider.store_message(
            conversation_id="nonexistent-id",
            role="user",
            message="This conversation does not exist"
        )

def test_get_conversation_history_nonexistent(mongo_ai_terminal_provider):
    """
    Test retrieving conversation history for a nonexistent conversation should raise an error.
    """
    with pytest.raises(Exception):
        mongo_ai_terminal_provider.get_conversation_history("nonexistent-id")
