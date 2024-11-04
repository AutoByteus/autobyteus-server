import pytest
from autobyteus_server.workflow.persistence.conversation.persistence.mongo_persistence_provider import MongoPersistenceProvider
from autobyteus_server.workflow.persistence.conversation.domain.models import StepConversation
from bson import ObjectId
from datetime import datetime
import json

@pytest.fixture
def mongo_persistence_provider():
    """Provides the singleton MongoPersistenceProvider instance for testing."""
    return MongoPersistenceProvider()

@pytest.fixture
def sample_conversation(mongo_persistence_provider):
    """Creates a sample conversation for testing."""
    step_name = "mongo_sample_step"
    conversation = mongo_persistence_provider.create_conversation(step_name)
    return conversation

def test_create_conversation(mongo_persistence_provider, sample_conversation):
    """Test creating a new conversation in MongoDB."""
    step_name = "mongo_test_step"
    conversation = mongo_persistence_provider.create_conversation(step_name)

    assert isinstance(conversation, StepConversation)
    assert conversation.step_name == step_name
    assert isinstance(conversation.created_at, datetime)
    assert isinstance(conversation.step_conversation_id, ObjectId)
    assert len(conversation.messages) == 0

def test_store_message(mongo_persistence_provider, sample_conversation):
    """Test storing a message in a MongoDB conversation."""
    step_name = "mongo_store_message_step"
    role = "user"
    message = "Hello, MongoDB!"

    # Store message with conversation_id
    conversation_id = str(sample_conversation.step_conversation_id)
    mongo_persistence_provider.store_message(step_name, role, message, conversation_id=conversation_id)

    # Retrieve the latest conversation
    history = mongo_persistence_provider.get_conversation_history(step_name, page=1, page_size=1)
    assert history.total_conversations == 1
    assert len(history.conversations) == 1
    conv = history.conversations[0]
    assert len(conv.messages) == 1
    assert conv.messages[0].role == role
    assert conv.messages[0].content == message
    assert isinstance(conv.messages[0].timestamp, datetime)

def test_store_message_with_conversation_id(mongo_persistence_provider, sample_conversation):
    """Test storing a message with a specified conversation_id."""
    step_name = "mongo_store_specific_id_step"
    role = "assistant"
    message = "Hi there!"

    # Store a message with the given conversation_id
    conversation_id = str(sample_conversation.step_conversation_id)
    mongo_persistence_provider.store_message(step_name, role, message, conversation_id=conversation_id)

    # Verify the message is stored in the correct conversation
    history = mongo_persistence_provider.get_conversation_history(step_name, page=1, page_size=10)
    assert history.total_conversations == 1
    assert len(history.conversations) == 1
    conv = history.conversations[0]
    assert conv.step_conversation_id == ObjectId(conversation_id)
    assert len(conv.messages) == 1
    assert conv.messages[0].role == role
    assert conv.messages[0].content == message
    assert isinstance(conv.messages[0].timestamp, datetime)

def test_get_conversation_history(mongo_persistence_provider, sample_conversation):
    """Test retrieving conversation history with pagination in MongoDB."""
    step_name = "mongo_pagination_step"
    total_conversations = 15
    for i in range(total_conversations):
        conv = mongo_persistence_provider.create_conversation(step_name)
        conversation_id = str(conv.step_conversation_id)
        mongo_persistence_provider.store_message(step_name, "user", f"Message {i+1}", conversation_id=conversation_id)

    # Retrieve paginated history
    page = 2
    page_size = 5
    history = mongo_persistence_provider.get_conversation_history(step_name, page, page_size)

    assert history.total_conversations == total_conversations
    assert history.total_pages == 3
    assert history.current_page == page
    assert len(history.conversations) == page_size
    for conv in history.conversations:
        assert conv.step_name == step_name
        assert len(conv.messages) == 1  # Each conversation has one message

def test_get_conversation_history_no_conversations(mongo_persistence_provider):
    """Test retrieving conversation history when no conversations exist in MongoDB."""
    step_name = "mongo_nonexistent_step"

    history = mongo_persistence_provider.get_conversation_history(step_name, page=1, page_size=10)
    assert history.total_conversations == 0
    assert history.total_pages == 0
    assert history.current_page == 1
    assert len(history.conversations) == 0

def test_pagination_beyond_available_pages(mongo_persistence_provider):
    """Test pagination when requesting a page beyond available data in MongoDB."""
    step_name = "mongo_edge_case_step"
    conv = mongo_persistence_provider.create_conversation(step_name)
    conversation_id = str(conv.step_conversation_id)
    mongo_persistence_provider.store_message(step_name, "user", "Edge case message", conversation_id=conversation_id)

    history = mongo_persistence_provider.get_conversation_history(step_name, page=999, page_size=10)
    assert history.total_conversations == 1
    assert history.total_pages == 1
    assert history.current_page == 999
    assert len(history.conversations) == 0