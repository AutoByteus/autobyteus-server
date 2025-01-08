
import pytest
from datetime import datetime
from bson import ObjectId

from autobyteus_server.ai_terminal.persistence.models.mongodb.conversation import AiTerminalConversation
from autobyteus_server.ai_terminal.persistence.repositories.mongodb.ai_terminal_conversation_repository import (
    AiTerminalConversationRepository,
    ConversationNotFoundError
)

pytestmark = pytest.mark.integration

@pytest.fixture(scope="function")
def mongo_conversation_repo():
    """
    Provides an instance of AiTerminalConversationRepository for MongoDB.
    Cleans the collection before each test to ensure a fresh state.
    """
    repo = AiTerminalConversationRepository()
    repo.collection.delete_many({})
    return repo

def test_create_conversation(mongo_conversation_repo):
    """
    Test creating a new conversation document in MongoDB.
    """
    conversation_id = "test_mongo_conversation"
    conversation = mongo_conversation_repo.create_conversation(conversation_id)
    assert isinstance(conversation, AiTerminalConversation)
    assert conversation.conversation_id == conversation_id
    assert conversation._id is not None
    assert isinstance(conversation.created_at, datetime)
    assert conversation.messages == []

def test_find_by_conversation_id_success(mongo_conversation_repo):
    """
    Test successful retrieval of a conversation by conversation_id.
    """
    conversation_id = "test_find_mongo"
    created = mongo_conversation_repo.create_conversation(conversation_id)
    found = mongo_conversation_repo.find_by_conversation_id(conversation_id)
    assert found is not None
    assert found.conversation_id == created.conversation_id
    assert str(found._id) == str(created._id)

def test_find_by_conversation_id_nonexistent(mongo_conversation_repo):
    """
    Test finding a non-existent conversation returns None.
    """
    found = mongo_conversation_repo.find_by_conversation_id("nonexistent_id")
    assert found is None

def test_add_message_success(mongo_conversation_repo):
    """
    Test adding a message to a conversation in MongoDB.
    """
    conversation_id = "test_add_message_mongo"
    conv = mongo_conversation_repo.create_conversation(conversation_id)
    updated_conv = mongo_conversation_repo.add_message(
        conversation_id=conversation_id,
        role="user",
        message="Hello, from test_add_message!",
        token_count=10,
        cost=0.02
    )
    assert updated_conv is not None
    assert len(updated_conv.messages) == 1
    last_msg = updated_conv.messages[-1]
    assert last_msg["role"] == "user"
    assert last_msg["message"] == "Hello, from test_add_message!"
    assert last_msg["token_count"] == 10
    assert last_msg["cost"] == 0.02

def test_add_message_nonexistent_conversation(mongo_conversation_repo):
    """
    Test adding a message to a conversation that doesn't exist should return None.
    """
    updated = mongo_conversation_repo.add_message(
        conversation_id="does_not_exist",
        role="user",
        message="This won't be added"
    )
    assert updated is None

def test_list_conversations_pagination(mongo_conversation_repo):
    """
    Test listing conversations with pagination in MongoDB repository.
    """
    # Create multiple conversations
    total_conversations = 5
    for i in range(total_conversations):
        mongo_conversation_repo.create_conversation(f"conv_{i}")

    result_page_1 = mongo_conversation_repo.list_conversations(skip=0, limit=2)
    assert len(result_page_1["conversations"]) == 2
    assert result_page_1["total_conversations"] == total_conversations
    assert result_page_1["total_pages"] == (total_conversations + 2 - 1) // 2
    assert result_page_1["current_page"] == 1

    result_page_2 = mongo_conversation_repo.list_conversations(skip=2, limit=2)
    assert len(result_page_2["conversations"]) == 2
    assert result_page_2["current_page"] == 2

def test_list_conversations_no_data(mongo_conversation_repo):
    """
    Test listing conversations when none exist.
    """
    result = mongo_conversation_repo.list_conversations(skip=0, limit=10)
    assert result["total_conversations"] == 0
    assert result["total_pages"] == 0
    assert result["current_page"] == 1
    assert len(result["conversations"]) == 0
