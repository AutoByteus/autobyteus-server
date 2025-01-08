
import pytest
import os
from datetime import datetime
from unittest.mock import patch
from autobyteus_server.ai_terminal.persistence.providers.mongo_ai_terminal_provider import MongoAiTerminalProvider
from autobyteus_server.ai_terminal.persistence.domain.models import AiTerminalConversation, AiTerminalMessage, ConversationHistory
from autobyteus_server.ai_terminal.persistence.repositories.mongodb.ai_terminal_conversation_repository import ConversationNotFoundError

@pytest.fixture
def mongo_provider():
    """
    Provides an instance of MongoAiTerminalProvider for testing.
    """
    return MongoAiTerminalProvider()

def test_create_conversation(mongo_provider):
    """
    Test creating a new conversation in MongoDB through MongoAiTerminalProvider.
    """
    conv = mongo_provider.create_conversation()
    assert isinstance(conv, AiTerminalConversation)
    assert isinstance(conv.conversation_id, str)
    assert isinstance(conv.created_at, datetime)
    assert conv.messages == []

def test_store_message(mongo_provider):
    """
    Test storing a message in a MongoDB conversation.
    """
    # Create conversation first
    conv = mongo_provider.create_conversation()
    conversation_id = conv.conversation_id

    updated_conv = mongo_provider.store_message(
        conversation_id=conversation_id,
        role="user",
        message="Hello, AI Terminal from Mongo!"
    )

    assert len(updated_conv.messages) == 1
    msg = updated_conv.messages[0]
    assert msg.role == "user"
    assert msg.message == "Hello, AI Terminal from Mongo!"
    assert isinstance(msg.timestamp, datetime)

def test_store_message_nonexistent_conversation(mongo_provider):
    """
    Test storing a message in a non-existent MongoDB conversation.
    """
    with pytest.raises(ConversationNotFoundError):
        mongo_provider.store_message(
            conversation_id="nonexistent-id",
            role="user",
            message="Should fail"
        )

def test_get_conversation_history(mongo_provider):
    """
    Test retrieving the history of an existing MongoDB conversation.
    """
    conv = mongo_provider.create_conversation()
    conversation_id = conv.conversation_id

    # Store a couple of messages
    mongo_provider.store_message(conversation_id, "user", "Hello!")
    mongo_provider.store_message(conversation_id, "assistant", "Hi, how can I help?")

    retrieved_conv = mongo_provider.get_conversation_history(conversation_id)
    assert retrieved_conv.conversation_id == conversation_id
    assert len(retrieved_conv.messages) == 2
    assert retrieved_conv.messages[0].role == "user"
    assert retrieved_conv.messages[1].role == "assistant"

def test_list_conversations(mongo_provider):
    """
    Test listing conversations with pagination in MongoDB.
    """
    # Create multiple conversations
    for _ in range(5):
        conv = mongo_provider.create_conversation()
        mongo_provider.store_message(conv.conversation_id, "user", "Message")

    history: ConversationHistory = mongo_provider.list_conversations(page=1, page_size=2)
    assert history.total_conversations >= 5
    assert len(history.conversations) == 2
    assert history.current_page == 1

    # Fetch the second page
    history_page_2: ConversationHistory = mongo_provider.list_conversations(page=2, page_size=2)
    assert len(history_page_2.conversations) == 2
    assert history_page_2.current_page == 2

def test_store_message_with_cost_and_token_count(mongo_provider):
    """
    Test storing a message with token_count and cost in a MongoDB conversation.
    """
    conv = mongo_provider.create_conversation()
    conversation_id = conv.conversation_id

    updated_conv = mongo_provider.store_message(
        conversation_id=conversation_id,
        role="assistant",
        message="This message has usage data",
        token_count=30,
        cost=0.10
    )
    msg = updated_conv.messages[-1]
    assert msg.token_count == 30
    assert msg.cost == 0.10
