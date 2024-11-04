import pytest
import os
import shutil
import glob
import json
from autobyteus_server.workflow.persistence.conversation.persistence.file_based_persistence_provider import FileBasedPersistenceProvider
from autobyteus_server.workflow.persistence.conversation.domain.models import StepConversation, ConversationHistory, Message
from datetime import datetime

@pytest.fixture(scope="function")
def cleanup_conversations():
    """Fixture to clean up the conversations directory after tests."""
    yield
    if os.path.exists("conversations"):
        shutil.rmtree("conversations")

def test_create_conversation(cleanup_conversations):
    """Test creating a new conversation."""
    provider = FileBasedPersistenceProvider()
    step_name = "test_step"
    conversation = provider.create_conversation(step_name)

    assert isinstance(conversation, StepConversation)
    assert conversation.step_name == step_name
    assert isinstance(conversation.created_at, datetime)
    assert conversation.step_conversation_id.startswith("conversations/test_step_")
    assert os.path.exists(conversation.step_conversation_id)
    assert os.path.isfile(conversation.step_conversation_id)
    assert len(conversation.messages) == 0

def test_store_message(cleanup_conversations):
    """Test storing a message in a conversation."""
    provider = FileBasedPersistenceProvider()
    step_name = "test_step"
    role = "user"
    message = "Hello, World!"

    # First, create a conversation
    conversation = provider.create_conversation(step_name)
    conversation_id = conversation.step_conversation_id

    provider.store_message(step_name, role, message, conversation_id=conversation_id)

    # Verify that the file exists
    safe_name = ''.join(c if c.isalnum() else '_' for c in step_name)
    pattern = f"conversations/{safe_name}_*.txt"
    files = list(glob.glob(pattern))
    assert len(files) == 1

    # Verify the content
    with open(files[0], "r") as f:
        lines = f.readlines()
        assert len(lines) == 1
        data = json.loads(lines[0].strip())
        assert data["role"] == role
        assert data["message"] == message
        datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S")  # Should not raise

def test_store_message_with_conversation_id(cleanup_conversations):
    """Test storing a message with a specified conversation_id."""
    provider = FileBasedPersistenceProvider()
    step_name = "test_step_specific_id"
    role = "assistant"
    message = "Hi there!"

    # Create a conversation
    conversation = provider.create_conversation(step_name)
    conversation_id = conversation.step_conversation_id

    # Store a message with conversation_id
    provider.store_message(step_name, role, message, conversation_id=conversation_id)

    # Verify the message is stored in the correct conversation
    history = provider.get_conversation_history(step_name, page=1, page_size=10)
    assert history.total_conversations == 1
    assert history.total_pages == 1
    assert history.current_page == 1
    assert len(history.conversations) == 1
    assert len(history.conversations[0].messages) == 1
    assert history.conversations[0].messages[0].role == role
    assert history.conversations[0].messages[0].content == message
    assert isinstance(history.conversations[0].messages[0].timestamp, datetime)

def test_get_conversation_history(cleanup_conversations):
    """Test retrieving conversation history with pagination."""
    provider = FileBasedPersistenceProvider()
    step_name = "test_step_pagination"
    total_messages = 25
    conversation = provider.create_conversation(step_name)
    conversation_id = conversation.step_conversation_id
    for i in range(total_messages):
        provider.store_message(step_name, "user", f"Message {i+1}", conversation_id=conversation_id)

    # Retrieve first page
    history_page_1 = provider.get_conversation_history(step_name, page=1, page_size=10)
    assert history_page_1.total_conversations == 1
    assert history_page_1.total_pages == 1
    assert history_page_1.current_page == 1
    assert len(history_page_1.conversations) == 1
    assert len(history_page_1.conversations[0].messages) == total_messages

def test_get_conversation_history_no_conversations(cleanup_conversations):
    """Test retrieving conversation history when no conversations exist."""
    provider = FileBasedPersistenceProvider()
    step_name = "nonexistent_step"

    history = provider.get_conversation_history(step_name, page=1, page_size=10)
    assert history.total_conversations == 0
    assert history.total_pages == 0
    assert history.current_page == 1
    assert len(history.conversations) == 0

def test_pagination_beyond_available_pages(cleanup_conversations):
    """Test pagination when requesting a page beyond available data."""
    provider = FileBasedPersistenceProvider()
    step_name = "test_step_pagination_beyond"
    conversation = provider.create_conversation(step_name)
    conversation_id = conversation.step_conversation_id
    for i in range(5):
        provider.store_message(step_name, "user", f"Message {i+1}", conversation_id=conversation_id)

    history = provider.get_conversation_history(step_name, page=2, page_size=10)
    assert history.total_conversations == 1
    assert history.total_pages == 1
    assert history.current_page == 2
    assert len(history.conversations) == 0