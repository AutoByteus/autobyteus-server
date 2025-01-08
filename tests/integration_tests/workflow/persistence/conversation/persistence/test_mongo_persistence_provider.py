
import pytest
from autobyteus_server.workflow.persistence.conversation.provider.mongo_persistence_provider import MongoPersistenceProvider
from autobyteus_server.workflow.persistence.conversation.domain.models import StepConversation, Message
from datetime import datetime

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
    assert isinstance(conversation.step_conversation_id, str)  # Changed to string
    assert len(conversation.messages) == 0

def test_store_message(mongo_persistence_provider, sample_conversation):
    """Test storing a message in a MongoDB conversation."""
    # Corrected step_name to match the sample_conversation's step_name
    step_name = sample_conversation.step_name  # Changed from "mongo_store_message_step" to "mongo_sample_step"
    role = "user"
    message = "Hello, MongoDB!"
    original_message = "Original user message"
    context_paths = ["/path/to/context1", "/path/to/context2"]

    # Store message with step_conversation_id
    step_conversation_id = sample_conversation.step_conversation_id
    mongo_persistence_provider.store_message(
        step_name,
        role,
        message,
        original_message=original_message,
        context_paths=context_paths,
        step_conversation_id=step_conversation_id  # Updated parameter name
    )

    # Retrieve the latest conversation
    history = mongo_persistence_provider.get_conversation_history(step_name, page=1, page_size=1)
    assert history.total_conversations == 1
    assert len(history.conversations) == 1
    conv = history.conversations[0]
    assert len(conv.messages) == 1
    msg = conv.messages[0]
    assert msg.role == role
    assert msg.message == message
    assert msg.original_message == original_message
    assert msg.context_paths == context_paths
    assert isinstance(msg.timestamp, datetime)

def test_store_message_with_conversation_id(mongo_persistence_provider, sample_conversation):
    """Test storing a message with a specified step_conversation_id."""
    step_name = sample_conversation.step_name  # Changed from "mongo_store_message_step" to "mongo_sample_step"
    role = "assistant"
    message = "Hi there!"
    original_message = "Original assistant message"
    context_paths = ["/path/to/context3"]

    # Store a message with the given step_conversation_id
    step_conversation_id = sample_conversation.step_conversation_id
    mongo_persistence_provider.store_message(
        step_name,
        role,
        message,
        original_message=original_message,
        context_paths=context_paths,
        step_conversation_id=step_conversation_id  # Updated parameter name
    )

    # Verify the message is stored in the correct conversation
    history = mongo_persistence_provider.get_conversation_history(step_name, page=1, page_size=10)
    assert history.total_conversations == 1
    assert len(history.conversations) == 1
    conv = history.conversations[0]
    assert conv.step_conversation_id == step_conversation_id
    assert len(conv.messages) == 1
    msg = conv.messages[0]
    assert msg.role == role
    assert msg.message == message
    assert msg.original_message == original_message
    assert msg.context_paths == context_paths
    assert isinstance(msg.timestamp, datetime)

def test_get_conversation_history(mongo_persistence_provider, sample_conversation):
    """Test retrieving conversation history with pagination in MongoDB."""
    step_name = "mongo_pagination_step"
    total_conversations = 15
    for i in range(total_conversations):
        conv = mongo_persistence_provider.create_conversation(step_name)
        step_conversation_id = conv.step_conversation_id
        mongo_persistence_provider.store_message(
            step_name,
            "user",
            f"Message {i+1}",
            original_message=f"Original message {i+1}",
            context_paths=[f"/path/to/context{i+1}"],
            step_conversation_id=step_conversation_id  # Updated parameter name
        )

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
        msg = conv.messages[0]
        assert isinstance(msg, Message)
        assert isinstance(msg.timestamp, datetime)

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
    step_conversation_id = conv.step_conversation_id
    mongo_persistence_provider.store_message(
        step_name,
        "user",
        "Edge case message",
        original_message="Original edge case message",
        context_paths=["/path/to/edge_case"],
        step_conversation_id=step_conversation_id  # Updated parameter name
    )

    history = mongo_persistence_provider.get_conversation_history(step_name, page=999, page_size=10)
    assert history.total_conversations == 1
    assert history.total_pages == 1
    assert history.current_page == 999
    assert len(history.conversations) == 0

def test_store_message_without_optional_fields(mongo_persistence_provider, sample_conversation):
    """Test storing a message without original_message and context_paths."""
    step_name = sample_conversation.step_name
    role = "user"
    message = "Message without optional fields"

    # Store message without original_message and context_paths
    step_conversation_id = sample_conversation.step_conversation_id
    mongo_persistence_provider.store_message(
        step_name,
        role,
        message,
        step_conversation_id=step_conversation_id  # Updated parameter name
    )

    # Retrieve the conversation
    history = mongo_persistence_provider.get_conversation_history(step_name, page=1, page_size=1)
    assert history.total_conversations == 1
    assert len(history.conversations) == 1
    conv = history.conversations[0]
    assert len(conv.messages) == 1
    msg = conv.messages[0]
    assert msg.role == role
    assert msg.message == message
    assert msg.original_message is None
    assert msg.context_paths == []
    assert isinstance(msg.timestamp, datetime)

def test_multiple_messages_in_conversation(mongo_persistence_provider, sample_conversation):
    """Test storing multiple messages in a single conversation."""
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
    step_conversation_id = sample_conversation.step_conversation_id
    mongo_persistence_provider.store_message(
        step_name,
        role1,
        message1,
        original_message=original_message1,
        context_paths=context_paths1,
        step_conversation_id=step_conversation_id  # Updated parameter name
    )

    # Store second message
    mongo_persistence_provider.store_message(
        step_name,
        role2,
        message2,
        original_message=original_message2,
        context_paths=context_paths2,
        step_conversation_id=step_conversation_id  # Updated parameter name
    )

    # Retrieve the conversation
    history = mongo_persistence_provider.get_conversation_history(step_name, page=1, page_size=1)
    assert history.total_conversations == 1
    assert len(history.conversations) == 1
    conv = history.conversations[0]
    assert len(conv.messages) == 2

    msg1 = conv.messages[0]
    assert msg1.role == role1
    assert msg1.message == message1
    assert msg1.original_message == original_message1
    assert msg1.context_paths == context_paths1
    assert isinstance(msg1.timestamp, datetime)

    msg2 = conv.messages[1]
    assert msg2.role == role2
    assert msg2.message == message2
    assert msg2.original_message == original_message2
    assert msg2.context_paths == context_paths2
    assert isinstance(msg2.timestamp, datetime)

def test_update_last_user_message_usage_success(mongo_persistence_provider, sample_conversation):
    """Test successfully updating the token count and cost for the last user message."""
    step_name = sample_conversation.step_name
    role = "user"
    message = "User message to update"
    token_count = 10
    cost = 0.01

    # Store initial message
    mongo_persistence_provider.store_message(
        step_name,
        role,
        message,
        token_count=token_count,
        cost=cost,
        step_conversation_id=sample_conversation.step_conversation_id
    )

    # Update the last user message
    new_token_count = 20
    new_cost = 0.02
    updated_conversation = mongo_persistence_provider.update_last_user_message_usage(
        step_conversation_id=sample_conversation.step_conversation_id,
        token_count=new_token_count,
        cost=new_cost
    )

    # Verify the update
    assert len(updated_conversation.messages) == 1
    msg = updated_conversation.messages[0]
    assert msg.token_count == new_token_count
    assert msg.cost == new_cost

def test_update_last_user_message_usage_no_user_message(mongo_persistence_provider):
    """Test updating token usage when there are no user messages."""
    step_name = "mongo_no_user_message_step"
    conv = mongo_persistence_provider.create_conversation(step_name)
    step_conversation_id = conv.step_conversation_id

    # Store a message with role 'assistant'
    mongo_persistence_provider.store_message(
        step_name,
        "assistant",
        "Assistant message",
        step_conversation_id=step_conversation_id
    )

    # Attempt to update the last user message, which does not exist
    with pytest.raises(ValueError) as exc_info:
        mongo_persistence_provider.update_last_user_message_usage(
            step_conversation_id=step_conversation_id,
            token_count=15,
            cost=0.015
        )
    assert "No user message found in the conversation to update token usage." in str(exc_info.value)

def test_update_last_user_message_usage_negative_values(mongo_persistence_provider, sample_conversation):
    """Test updating token usage with negative token count and cost."""
    step_name = sample_conversation.step_name
    role = "user"
    message = "User message with negative values"

    # Store initial message
    mongo_persistence_provider.store_message(
        step_name,
        role,
        message,
        step_conversation_id=sample_conversation.step_conversation_id
    )

    # Attempt to update with negative token_count
    with pytest.raises(ValueError) as exc_info:
        mongo_persistence_provider.update_last_user_message_usage(
            step_conversation_id=sample_conversation.step_conversation_id,
            token_count=-5,
            cost=0.01
        )
    assert "token_count cannot be negative" in str(exc_info.value)

    # Attempt to update with negative cost
    with pytest.raises(ValueError) as exc_info:
        mongo_persistence_provider.update_last_user_message_usage(
            step_conversation_id=sample_conversation.step_conversation_id,
            token_count=10,
            cost=-0.01
        )
    assert "cost cannot be negative" in str(exc_info.value)

def test_update_last_user_message_usage_invalid_conversation_id(mongo_persistence_provider):
    """Test updating token usage with an invalid conversation ID format."""
    invalid_conversation_id = "invalid_id"

    with pytest.raises(ValueError) as exc_info:
        mongo_persistence_provider.update_last_user_message_usage(
            step_conversation_id=invalid_conversation_id,
            token_count=10,
            cost=0.01
        )
    assert f"Invalid step_conversation_id format: {invalid_conversation_id}" in str(exc_info.value)

def test_update_last_user_message_usage_nonexistent_conversation(mongo_persistence_provider):
    """Test updating token usage for a non-existent conversation."""
    nonexistent_conversation_id = "507f1f77bcf86cd799439011"  # Example ObjectId

    with pytest.raises(ConversationNotFoundError) as exc_info:
        mongo_persistence_provider.update_last_user_message_usage(
            step_conversation_id=nonexistent_conversation_id,
            token_count=10,
            cost=0.01
        )
    assert f"Conversation with ID {nonexistent_conversation_id} not found" in str(exc_info.value)
