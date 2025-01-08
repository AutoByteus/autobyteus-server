
import pytest
from autobyteus_server.workflow.persistence.conversation.provider.sql_persistence_provider import SqlPersistenceProvider
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
    step_name = sample_conversation.step_name
    role = "user"
    message = "Hello, SQL Database!"
    token_count = 100
    cost = 0.002

    conversation_id = sample_conversation.step_conversation_id
    updated_conversation = sql_persistence_provider.store_message(
        step_name=step_name,
        role=role,
        message=message,
        token_count=token_count,
        cost=cost,
        conversation_id=conversation_id
    )

    assert isinstance(updated_conversation, StepConversation)
    assert len(updated_conversation.messages) == 1
    assert updated_conversation.messages[-1].message == message
    assert updated_conversation.messages[-1].role == role
    assert updated_conversation.messages[-1].token_count == token_count
    assert updated_conversation.messages[-1].cost == cost
    assert isinstance(updated_conversation.messages[-1].timestamp, datetime)

def test_store_message_with_conversation_id(sql_persistence_provider, sample_conversation):
    """Test storing a message with a specified conversation_id in SQL-based persistence."""
    step_name = sample_conversation.step_name
    role = "assistant"
    message = "Hi there!"
    token_count = 50
    cost = 0.001

    conversation_id = sample_conversation.step_conversation_id
    updated_conversation = sql_persistence_provider.store_message(
        step_name=step_name,
        role=role,
        message=message,
        token_count=token_count,
        cost=cost,
        conversation_id=conversation_id
    )

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
    assert msg.token_count == token_count
    assert msg.cost == cost
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
            token_count=10 * (i + 1),
            cost=0.0001 * (i + 1),
            conversation_id=step_conversation_id
        )
    
    page = 2
    page_size = 5
    history = sql_persistence_provider.get_conversation_history(step_name, page, page_size)
    
    assert history.total_conversations == total_conversations
    assert history.total_pages == 3
    assert history.current_page == page
    assert len(history.conversations) == page_size
    for conv in history.conversations:
        assert conv.step_name == step_name
        assert len(conv.messages) >= 1

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
        token_count=25,
        cost=0.0005,
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
    token_count = 75
    cost = 0.0015

    conversation_id = sample_conversation.step_conversation_id
    updated_conversation = sql_persistence_provider.store_message(
        step_name=step_name,
        role=role,
        message=message,
        token_count=token_count,
        cost=cost,
        conversation_id=conversation_id
    )

    history = sql_persistence_provider.get_conversation_history(step_name, page=1, page_size=10)
    assert history.total_conversations >= 1
    assert len(history.conversations) >= 1
    conv = history.conversations[0]
    assert len(conv.messages) >= 1
    msg = conv.messages[-1]
    assert msg.role == role
    assert msg.message == message
    assert msg.token_count == token_count
    assert msg.cost == cost
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
    token_count1 = 30
    cost1 = 0.0006

    role2 = "assistant"
    message2 = "Second message"
    original_message2 = "Original second message"
    context_paths2 = ["/path/to/context3"]
    token_count2 = 45
    cost2 = 0.0009

    conversation_id = sample_conversation.step_conversation_id
    sql_persistence_provider.store_message(
        step_name=step_name,
        role=role1,
        message=message1,
        token_count=token_count1,
        cost=cost1,
        original_message=original_message1,
        context_paths=context_paths1,
        conversation_id=conversation_id
    )

    sql_persistence_provider.store_message(
        step_name=step_name,
        role=role2,
        message=message2,
        token_count=token_count2,
        cost=cost2,
        original_message=original_message2,
        context_paths=context_paths2,
        conversation_id=conversation_id
    )

    history = sql_persistence_provider.get_conversation_history(step_name, page=1, page_size=10)
    assert history.total_conversations >= 1
    assert len(history.conversations) >= 1
    conv = history.conversations[0]
    assert len(conv.messages) >= 2

    msg1 = conv.messages[-2]
    assert msg1.role == role1
    assert msg1.message == message1
    assert msg1.token_count == token_count1
    assert msg1.cost == cost1
    assert msg1.original_message == original_message1
    assert msg1.context_paths == context_paths1

    msg2 = conv.messages[-1]
    assert msg2.role == role2
    assert msg2.message == message2
    assert msg2.token_count == token_count2
    assert msg2.cost == cost2
    assert msg2.original_message == original_message2
    assert msg2.context_paths == context_paths2

def test_store_message_with_zero_values(sql_persistence_provider, sample_conversation):
    """Test storing a message with zero token count and cost."""
    step_name = sample_conversation.step_name
    role = "user"
    message = "Zero values message"
    token_count = 0
    cost = 0.0

    conversation_id = sample_conversation.step_conversation_id
    updated_conversation = sql_persistence_provider.store_message(
        step_name=step_name,
        role=role,
        message=message,
        token_count=token_count,
        cost=cost,
        conversation_id=conversation_id
    )

    assert len(updated_conversation.messages) >= 1
    msg = updated_conversation.messages[-1]
    assert msg.token_count == token_count
    assert msg.cost == cost

def test_update_last_user_message_usage_success(sql_persistence_provider, sample_conversation):
    """Test successfully updating the token count and cost for the last user message."""
    step_name = sample_conversation.step_name
    role = "user"
    message = "User message to update"
    token_count = 10
    cost = 0.01

    # Store initial message
    sql_persistence_provider.store_message(
        step_name=step_name,
        role=role,
        message=message,
        token_count=token_count,
        cost=cost,
        conversation_id=sample_conversation.step_conversation_id
    )

    # Update the last user message
    new_token_count = 20
    new_cost = 0.02
    updated_conversation = sql_persistence_provider.update_last_user_message_usage(
        step_conversation_id=sample_conversation.step_conversation_id,
        token_count=new_token_count,
        cost=new_cost
    )

    # Verify the update
    assert len(updated_conversation.messages) == 1
    msg = updated_conversation.messages[0]
    assert msg.token_count == new_token_count
    assert msg.cost == new_cost

def test_update_last_user_message_usage_no_user_message(sql_persistence_provider):
    """Test updating token usage when there are no user messages."""
    step_name = "sql_no_user_message_step"
    conv = sql_persistence_provider.create_conversation(step_name)
    step_conversation_id = conv.step_conversation_id

    # Store a message with role 'assistant'
    sql_persistence_provider.store_message(
        step_name=step_name,
        role="assistant",
        message="Assistant message",
        conversation_id=step_conversation_id
    )

    # Attempt to update the last user message, which does not exist
    with pytest.raises(ValueError) as exc_info:
        sql_persistence_provider.update_last_user_message_usage(
            step_conversation_id=step_conversation_id,
            token_count=15,
            cost=0.015
        )
    assert "No user message found in the conversation to update token usage." in str(exc_info.value)

def test_update_last_user_message_usage_negative_values(sql_persistence_provider, sample_conversation):
    """Test updating token usage with negative token count and cost."""
    step_name = sample_conversation.step_name
    role = "user"
    message = "User message with negative values"

    # Store initial message
    sql_persistence_provider.store_message(
        step_name=step_name,
        role=role,
        message=message,
        conversation_id=sample_conversation.step_conversation_id
    )

    # Attempt to update with negative token_count
    with pytest.raises(ValueError) as exc_info:
        sql_persistence_provider.update_last_user_message_usage(
            step_conversation_id=sample_conversation.step_conversation_id,
            token_count=-5,
            cost=0.01
        )
    assert "token_count cannot be negative" in str(exc_info.value)

    # Attempt to update with negative cost
    with pytest.raises(ValueError) as exc_info:
        sql_persistence_provider.update_last_user_message_usage(
            step_conversation_id=sample_conversation.step_conversation_id,
            token_count=10,
            cost=-0.01
        )
    assert "cost cannot be negative" in str(exc_info.value)

def test_update_last_user_message_usage_invalid_conversation_id(sql_persistence_provider):
    """Test updating token usage with an invalid conversation ID format."""
    invalid_conversation_id = "invalid-uuid"

    with pytest.raises(ValueError) as exc_info:
        sql_persistence_provider.update_last_user_message_usage(
            step_conversation_id=invalid_conversation_id,
            token_count=10,
            cost=0.01
        )
    assert f"Invalid step_conversation_id format: {invalid_conversation_id}" in str(exc_info.value)

def test_update_last_user_message_usage_nonexistent_conversation(sql_persistence_provider):
    """Test updating token usage for a non-existent conversation."""
    nonexistent_conversation_id = str(uuid.uuid4())  # Generate a random UUID

    with pytest.raises(ValueError) as exc_info:
        sql_persistence_provider.update_last_user_message_usage(
            step_conversation_id=nonexistent_conversation_id,
            token_count=10,
            cost=0.01
        )
    assert f"Conversation with ID {nonexistent_conversation_id} does not exist." in str(exc_info.value)
