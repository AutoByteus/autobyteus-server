import pytest
from autobyteus_server.workflow.persistence.conversation.persistence.sql_persistence_provider import SqlPersistenceProvider
from autobyteus_server.workflow.persistence.conversation.domain.models import StepConversation, ConversationHistory, Message
from datetime import datetime
import uuid
from autobyteus_server.workflow.persistence.conversation.repositories.sql.step_conversation_repository import StepConversationRepository
import json

@pytest.fixture
def sql_persistence_provider():
    """Provides the singleton SqlPersistenceProvider instance for testing."""
    return SqlPersistenceProvider()

@pytest.fixture
def sample_conversation(sql_persistence_provider):
    """Creates a sample conversation for testing."""
    step_name = "sql_sample_step"
    conversation = sql_persistence_provider.create_conversation(step_name)
    return conversation

def test_create_conversation(sql_persistence_provider, sample_conversation):
    """Test creating a new conversation in SQL-based persistence."""
    step_name = "sql_test_step"
    conversation = sql_persistence_provider.create_conversation(step_name)

    assert isinstance(conversation, StepConversation)
    assert conversation.step_name == step_name
    assert isinstance(conversation.created_at, datetime)
    # Validate UUID format
    uuid_obj = uuid.UUID(conversation.step_conversation_id)
    assert str(uuid_obj) == conversation.step_conversation_id
    assert len(conversation.messages) == 0

def test_store_message(sql_persistence_provider, sample_conversation):
    """Test storing a message in a SQL-based conversation."""
    # Use the step_name from the sample_conversation to ensure the current_conversation is used
    step_name = sample_conversation.step_name
    role = "user"
    message = "Hello, SQL Database!"
    
    # Store message with conversation_id
    conversation_id = sample_conversation.step_conversation_id
    updated_conversation = sql_persistence_provider.store_message(
        step_name=step_name,
        role=role,
        message=message,
        conversation_id=conversation_id
    )
    
    assert isinstance(updated_conversation, StepConversation)
    assert len(updated_conversation.messages) == 1
    assert updated_conversation.messages[-1].message == message
    assert updated_conversation.messages[-1].role == role
    assert isinstance(updated_conversation.messages[-1].timestamp, datetime)

def test_store_message_with_conversation_id(sql_persistence_provider, sample_conversation):
    """Test storing a message with a specified conversation_id in SQL-based persistence."""
    step_name = sample_conversation.step_name
    role = "assistant"
    message = "Hi there!"
    
    # Store a message with the given conversation_id
    conversation_id = sample_conversation.step_conversation_id
    updated_conversation = sql_persistence_provider.store_message(
        step_name=step_name,
        role=role,
        message=message,
        conversation_id=conversation_id
    )
    
    # Verify the message is stored in the correct conversation
    history = sql_persistence_provider.get_conversation_history(step_name, page=1, page_size=10)
    assert history.total_conversations >= 1
    assert history.total_pages >= 1
    assert history.current_page == 1
    assert len(history.conversations) >= 1
    conv = history.conversations[0]
    assert conv.step_conversation_id == conversation_id
    assert len(conv.messages) >= 1
    msg = conv.messages[-1]
    assert msg.role == role
    assert msg.message == message
    assert isinstance(msg.timestamp, datetime)

def test_get_conversation_history(sql_persistence_provider, sample_conversation):
    """Test retrieving conversation history with pagination in SQL-based persistence."""
    step_name = "sql_pagination_step"
    total_conversations = 15
    for i in range(total_conversations):
        conv = sql_persistence_provider.create_conversation(step_name)
        step_conversation_id = conv.step_conversation_id
        sql_persistence_provider.store_message(
            step_name=step_name,
            role="user",
            message=f"Message {i+1}",
            conversation_id=step_conversation_id
        )
    
    # Retrieve paginated history
    page = 2
    page_size = 5
    history = sql_persistence_provider.get_conversation_history(step_name, page, page_size)
    
    assert history.total_conversations == total_conversations
    assert history.total_pages == 3
    assert history.current_page == page
    assert len(history.conversations) == page_size
    for conv in history.conversations:
        assert conv.step_name == step_name
        assert len(conv.messages) >= 1  # Each conversation has at least one message

def test_get_conversation_history_no_conversations(sql_persistence_provider):
    """Test retrieving conversation history when no conversations exist in SQL-based persistence."""
    step_name = "sql_nonexistent_step"
    
    history = sql_persistence_provider.get_conversation_history(step_name, page=1, page_size=10)
    assert history.total_conversations == 0
    assert history.total_pages == 0
    assert history.current_page == 1
    assert len(history.conversations) == 0

def test_pagination_beyond_available_pages(sql_persistence_provider):
    """Test pagination when requesting a page beyond available data in SQL-based persistence."""
    step_name = "sql_edge_case_step"
    conv = sql_persistence_provider.create_conversation(step_name)
    sql_persistence_provider.store_message(
        step_name=step_name,
        role="user",
        message="Edge case message",
        conversation_id=conv.step_conversation_id
    )
    
    history = sql_persistence_provider.get_conversation_history(step_name, page=999, page_size=10)
    assert history.total_conversations >= 1
    assert history.total_pages >= 1
    assert history.current_page == 999
    assert len(history.conversations) == 0

def test_store_message_without_optional_fields(sql_persistence_provider, sample_conversation):
    """Test storing a message without original_message and context_paths in SQL-based persistence."""
    step_name = sample_conversation.step_name
    role = "user"
    message = "Message without optional fields"
    
    # Store message without original_message and context_paths
    conversation_id = sample_conversation.step_conversation_id
    updated_conversation = sql_persistence_provider.store_message(
        step_name=step_name,
        role=role,
        message=message,
        conversation_id=conversation_id
    )
    
    # Retrieve the conversation
    history = sql_persistence_provider.get_conversation_history(step_name, page=1, page_size=10)
    assert history.total_conversations >= 1
    assert len(history.conversations) >= 1
    conv = history.conversations[0]
    assert len(conv.messages) >= 1
    msg = conv.messages[-1]
    assert msg.role == role
    assert msg.message == message
    assert msg.original_message is None
    assert msg.context_paths == []
    assert isinstance(msg.timestamp, datetime)

def test_multiple_messages_in_conversation(sql_persistence_provider, sample_conversation):
    """Test storing multiple messages in a single conversation in SQL-based persistence."""
    step_name = sample_conversation.step_name 
    role1 = "user"
    message1 = "First message"
    original_message1 = "Original first message"
    context_paths1 = ["/path/to/context1", "/path/to/context2"]
    
    role2 = "assistant"
    message2 = "Second message"
    original_message2 = "Original second message"
    context_paths2 = ["/path/to/context3"]
    
    # Store first message
    conversation_id = sample_conversation.step_conversation_id
    sql_persistence_provider.store_message(
        step_name=step_name,
        role=role1,
        message=message1,
        original_message=original_message1,
        context_paths=context_paths1,
        conversation_id=conversation_id
    )
    
    # Store second message
    sql_persistence_provider.store_message(
        step_name=step_name,
        role=role2,
        message=message2,
        original_message=original_message2,
        context_paths=context_paths2,
        conversation_id=conversation_id
    )
    
    # Retrieve the conversation
    history = sql_persistence_provider.get_conversation_history(step_name, page=1, page_size=10)
    assert history.total_conversations >= 1
    assert len(history.conversations) >= 1
    conv = history.conversations[0]
    assert len(conv.messages) >= 2
    
    msg1 = conv.messages[-2]
    assert msg1.role == role1
    assert msg1.message == message1
    assert msg1.original_message == original_message1
    assert msg1.context_paths == context_paths1
    
    msg2 = conv.messages[-1]
    assert msg2.role == role2
    assert msg2.message == message2
    assert msg2.original_message == original_message2
    assert msg2.context_paths == context_paths2