import pytest
from autobyteus_server.workflow.persistence.conversation.persistence.postgresql_persistence_provider import PostgresqlPersistenceProvider
from autobyteus_server.workflow.persistence.conversation.domain.models import StepConversation, ConversationHistory, Message
from datetime import datetime
import uuid
from autobyteus_server.workflow.persistence.conversation.repositories.postgres.step_conversation_repository import StepConversationRepository
import json

@pytest.fixture
def postgres_persistence_provider():
    """Provides the singleton PostgresqlPersistenceProvider instance for testing."""
    return PostgresqlPersistenceProvider()

@pytest.fixture
def sample_conversation(postgres_persistence_provider):
    """Creates a sample conversation for testing."""
    step_name = "postgres_sample_step"
    conversation = postgres_persistence_provider.create_conversation(step_name)
    return conversation

def test_create_conversation(postgres_persistence_provider, sample_conversation):
    """Test creating a new conversation in PostgreSQL."""
    step_name = "postgres_test_step"
    conversation = postgres_persistence_provider.create_conversation(step_name)

    assert isinstance(conversation, StepConversation)
    assert conversation.step_name == step_name
    assert isinstance(conversation.created_at, datetime)
    assert isinstance(uuid.UUID(conversation.step_conversation_id), uuid.UUID)
    assert len(conversation.messages) == 0

def test_store_message(postgres_persistence_provider, sample_conversation):
    """Test storing a message in a PostgreSQL conversation."""
    # Use the step_name from the sample_conversation to ensure the current_conversation is used
    step_name = "postgres_sample_step"
    role = "user"
    message = "Hello, PostgreSQL!"
    
    # Store message with conversation_id
    conversation_id = sample_conversation.step_conversation_id  # Fixed attribute access
    updated_conversation = postgres_persistence_provider.store_message(
        step_name=step_name,
        role=role,
        message=message,
        conversation_id=conversation_id
    )
    
    assert updated_conversation.messages[-1].content == message
    assert updated_conversation.messages[-1].role == role
    assert updated_conversation.messages[-1].timestamp <= datetime.utcnow()

def test_store_message_with_conversation_id(postgres_persistence_provider, sample_conversation):
    """Test storing a message with a specified conversation_id in PostgreSQL."""
    step_name = "postgres_sample_step"  # Changed to match sample_conversation's step_name
    role = "assistant"
    message = "Hi PostgreSQL!"

    # Store a message with the given conversation_id
    conversation_id = sample_conversation.step_conversation_id  # Fixed attribute access
    updated_conversation = postgres_persistence_provider.store_message(
        step_name=step_name,
        role=role,
        message=message,
        conversation_id=conversation_id
    )

    # Verify the message is stored in the correct conversation
    history = postgres_persistence_provider.get_conversation_history(step_name, page=1, page_size=10)
    assert history.total_conversations >= 1
    assert len(history.conversations) >= 1
    conv = history.conversations[0]
    assert conv.step_conversation_id == sample_conversation.step_conversation_id
    assert len(conv.messages) >= 1
    assert conv.messages[-1].role == role
    assert conv.messages[-1].content == message
    assert isinstance(conv.messages[-1].timestamp, datetime)

def test_get_conversation_history(postgres_persistence_provider, sample_conversation):
    """Test retrieving conversation history with pagination in PostgreSQL."""
    step_name = "postgres_pagination_step"
    total_conversations = 15
    for i in range(total_conversations):
        conv = postgres_persistence_provider.create_conversation(step_name)
        postgres_persistence_provider.store_message(
            step_name=step_name, 
            role="user", 
            message=f"Message {i+1}", 
            conversation_id=conv.step_conversation_id  # Fixed attribute access
        )

    # Retrieve paginated history
    page = 2
    page_size = 5
    history = postgres_persistence_provider.get_conversation_history(step_name, page, page_size)

    assert history.total_conversations == total_conversations
    assert history.total_pages == 3
    assert history.current_page == page
    assert len(history.conversations) == page_size
    for conv in history.conversations:
        assert conv.step_name == step_name
        assert len(conv.messages) >= 1  # Each conversation has at least one message

def test_get_conversation_history_no_conversations(postgres_persistence_provider):
    """Test retrieving conversation history when no conversations exist in PostgreSQL."""
    step_name = "postgres_nonexistent_step"

    history = postgres_persistence_provider.get_conversation_history(step_name, page=1, page_size=10)
    assert history.total_conversations == 0
    assert history.total_pages == 0
    assert history.current_page == 1
    assert len(history.conversations) == 0

def test_pagination_beyond_available_pages(postgres_persistence_provider):
    """Test pagination when requesting a page beyond available data in PostgreSQL."""
    step_name = "postgres_edge_case_step"
    conv = postgres_persistence_provider.create_conversation(step_name)
    postgres_persistence_provider.store_message(
        step_name=step_name, 
        role="user", 
        message="Edge case message", 
        conversation_id=conv.step_conversation_id  # Fixed attribute access
    )

    history = postgres_persistence_provider.get_conversation_history(step_name, page=999, page_size=10)
    assert history.total_conversations >= 1
    assert history.total_pages >= 1
    assert history.current_page == 999
    assert len(history.conversations) == 0

def test_store_message_invalid_conversation_id(postgres_persistence_provider):
    """Test storing a message with an invalid conversation_id, expecting a ValueError."""
    step_name = "postgres_sample_step"  # Changed to match any existing conversation's step_name if needed
    role = "user"
    message = "This should fail."
    invalid_conversation_id = "invalid-uuid"

    with pytest.raises(ValueError) as exc_info:
        postgres_persistence_provider.store_message(
            step_name=step_name,
            role=role,
            message=message,
            conversation_id=invalid_conversation_id
        )

    assert f"Conversation with ID {invalid_conversation_id} does not exist." in str(exc_info.value)

def test_store_multiple_messages(postgres_persistence_provider, sample_conversation):
    """Test storing multiple messages in a single conversation."""
    step_name = "postgres_multiple_messages_step"
    role_user = "user"
    role_assistant = "assistant"
    messages = ["First message", "Second message", "Third message"]

    conversation_id = sample_conversation.step_conversation_id
    for msg in messages:
        postgres_persistence_provider.store_message(
            step_name=step_name,
            role=role_user if msg.startswith("First") else role_assistant,
            message=msg,
            conversation_id=conversation_id
        )

    history = postgres_persistence_provider.get_conversation_history(step_name, page=1, page_size=10)
    if history.conversations:
        updated_conversation = history.conversations[0]
        assert len(updated_conversation.messages) == len(messages)
        assert updated_conversation.messages[0].content == "First message"
        assert updated_conversation.messages[0].role == "user"
        assert updated_conversation.messages[1].content == "Second message"
        assert updated_conversation.messages[1].role == "assistant"
        assert updated_conversation.messages[2].content == "Third message"
        assert updated_conversation.messages[2].role == "assistant"
    else:
        pytest.fail("No conversations found in history.")

def test_create_duplicate_conversation(postgres_persistence_provider):
    """Test creating conversations with the same step_name to ensure uniqueness of step_conversation_id."""
    step_name = "duplicate_conversation_step"
    conversation1 = postgres_persistence_provider.create_conversation(step_name)
    conversation2 = postgres_persistence_provider.create_conversation(step_name)

    assert conversation1.step_conversation_id != conversation2.step_conversation_id
    assert conversation1.step_name == conversation2.step_name

def test_store_message_with_context_paths(postgres_persistence_provider, sample_conversation):
    """Test storing a message with context_paths."""
    step_name = "postgres_context_paths_step"
    role = "user"
    message = "Message with context."
    context_paths = ["/path/to/context1", "/path/to/context2"]

    conversation_id = sample_conversation.step_conversation_id
    updated_conversation = postgres_persistence_provider.store_message(
        step_name=step_name,
        role=role,
        message=message,
        context_paths=context_paths,
        conversation_id=conversation_id
    )

    # Verify that the message is correctly stored
    history = postgres_persistence_provider.get_conversation_history(step_name, page=1, page_size=10)
    if history.conversations:
        conv = history.conversations[0]
        assert len(conv.messages) == 1
        assert conv.messages[0].content == message
        assert conv.messages[0].context_paths == context_paths
    else:
        pytest.fail("No conversations found in history.")

def test_store_message_with_original_message(postgres_persistence_provider, sample_conversation):
    """Test storing a message with an original_message."""
    step_name = "postgres_original_message_step"
    role = "user"
    message = "This is a reply."
    original_message = "This is the original message."

    conversation_id = sample_conversation.step_conversation_id
    updated_conversation = postgres_persistence_provider.store_message(
        step_name=step_name,
        role=role,
        message=message,
        original_message=original_message,
        conversation_id=conversation_id
    )

    # Verify that the message is correctly stored with the original_message
    history = postgres_persistence_provider.get_conversation_history(step_name, page=1, page_size=10)
    if history.conversations:
        conv = history.conversations[0]
        assert len(conv.messages) == 1
        assert conv.messages[0].content == message
        assert conv.messages[0].original_message == original_message
    else:
        pytest.fail("No conversations found in history.")

def test_store_message_with_invalid_step_name(postgres_persistence_provider, sample_conversation):
    """Test storing a message with a step_name that does not match the conversation's step_name."""
    step_name = "mismatched_step_name"
    role = "user"
    message = "Mismatched step name message."

    conversation_id = sample_conversation.step_conversation_id
    with pytest.raises(ValueError) as exc_info:
        postgres_persistence_provider.store_message(
            step_name=step_name,
            role=role,
            message=message,
            conversation_id=conversation_id
        )

    assert f"Conversation with ID {conversation_id} does not exist." in str(exc_info.value)