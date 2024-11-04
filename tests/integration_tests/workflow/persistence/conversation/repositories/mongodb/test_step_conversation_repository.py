import pytest
from bson import ObjectId
from datetime import datetime
from autobyteus_server.workflow.persistence.conversation.models.mongodb.conversation import StepConversation, Message
from autobyteus_server.workflow.persistence.conversation.repositories.mongodb.step_conversation_repository import StepConversationRepository
from repository_mongodb.transaction_management import transaction
import json

pytestmark = pytest.mark.integration

@pytest.fixture(scope="function")
def conversation_repo():
    """
    Provides the singleton StepConversationRepository instance for testing.
    Ensures a clean state before each test.
    
    Returns:
        StepConversationRepository: Repository instance for testing.
    """
    repo = StepConversationRepository()
    # Clean the collection before each test
    repo.collection.delete_many({})
    return repo

@pytest.fixture
def sample_conversations(conversation_repo):
    """
    Fixture to create sample conversations for testing.
    
    Args:
        conversation_repo (StepConversationRepository): The repository instance.
    
    Returns:
        List[StepConversation]: A list of created StepConversation instances.
    """
    step_names = ["conversation1", "conversation2", "conversation3"]
    conversations = []
    for name in step_names:
        conv = conversation_repo.create_conversation(name)
        conversations.append(conv)
    return conversations

def test_create_empty_conversation(conversation_repo):
    """Test creation of an empty conversation without messages."""
    # Arrange
    step_name = "empty_conversation"

    # Act
    conversation = conversation_repo.create_conversation(step_name)

    # Assert
    assert conversation is not None
    assert conversation.step_name == step_name
    assert isinstance(conversation.created_at, datetime)
    assert isinstance(conversation.step_conversation_id, ObjectId)
    assert len(conversation.messages) == 0

def test_create_conversation_without_messages(conversation_repo):
    """Test successful creation of a new conversation."""
    # Arrange
    step_name = "test_conversation"

    # Act
    conversation = conversation_repo.create_conversation(step_name)

    # Assert
    assert conversation is not None
    assert conversation.step_name == step_name
    assert isinstance(conversation.created_at, datetime)
    assert isinstance(conversation.step_conversation_id, ObjectId)
    assert len(conversation.messages) == 0

def test_get_all_conversations(conversation_repo, sample_conversations):
    """Test retrieval of all conversations."""
    # Act
    conversations = conversation_repo.get_all_conversations()

    # Assert
    assert len(conversations) == len(sample_conversations)
    retrieved_names = [conv.step_name for conv in conversations]
    for conv in sample_conversations:
        assert conv.step_name in retrieved_names

def test_get_conversation_by_id(conversation_repo, sample_conversations):
    """Test retrieval of a conversation by its ID."""
    # Arrange
    conversation = sample_conversations[0]
    conversation_id = conversation.step_conversation_id

    # Act
    retrieved_conversation = conversation_repo.get_conversation_by_id(conversation_id)

    # Assert
    assert retrieved_conversation is not None
    assert retrieved_conversation.step_conversation_id == conversation_id
    assert retrieved_conversation.step_name == conversation.step_name

def test_get_conversations_by_step_name_with_pagination(conversation_repo):
    """Test retrieval of conversations by step name with pagination."""
    # Arrange
    step_name = "pagination_test_conversation"
    total_conversations = 15
    for _ in range(total_conversations):
        conversation_repo.create_conversation(step_name)

    page = 2
    page_size = 5

    # Act
    result = conversation_repo.get_conversations_by_step_name(step_name, page, page_size)

    # Assert
    assert result["total_conversations"] == total_conversations
    assert result["total_pages"] == 3
    assert result["current_page"] == page
    assert len(result["conversations"]) == page_size
    for conv in result["conversations"]:
        assert conv.step_name == step_name

def test_get_conversations_by_nonexistent_step_name(conversation_repo):
    """Test retrieval behavior with a non-existent step name."""
    # Act
    result = conversation_repo.get_conversations_by_step_name("nonexistent_conversation", 1, 10)

    # Assert
    assert result["total_conversations"] == 0
    assert result["total_pages"] == 0
    assert result["current_page"] == 1
    assert len(result["conversations"]) == 0

def test_pagination_beyond_available_pages(conversation_repo):
    """Test pagination behavior when requesting a page beyond available data."""
    # Arrange
    step_name = "edge_case_conversation"
    conversation_repo.create_conversation(step_name)

    # Act
    result = conversation_repo.get_conversations_by_step_name(step_name, page=999, page_size=10)

    # Assert
    assert len(result["conversations"]) == 0
    assert result["current_page"] == 999

def test_add_message_to_conversation(conversation_repo):
    """Test adding a message to an existing conversation."""
    # Arrange
    step_name = "message_test_conversation"
    conversation = conversation_repo.create_conversation(step_name)
    conversation_id = conversation.step_conversation_id
    role = "user"
    message_content = "Hello, this is a test message."
    original_message = "Original test message."
    context_paths = ["path/to/context1", "path/to/context2"]

    # Act
    updated_conversation = conversation_repo.add_message(
        step_conversation_id=conversation_id,
        role=role,
        message=message_content,
        original_message=original_message,
        context_paths=context_paths
    )

    # Assert
    assert updated_conversation is not None
    assert len(updated_conversation.messages) == 1
    last_message = updated_conversation.messages[-1]
    assert last_message["role"] == role
    assert last_message["message"] == message_content
    assert last_message["original_message"] == original_message
    assert last_message["context_paths"] == context_paths
    assert isinstance(last_message["timestamp"], datetime)

def test_add_message_to_nonexistent_conversation(conversation_repo):
    """Test adding a message to a conversation that does not exist."""
    # Arrange
    nonexistent_id = ObjectId()
    role = "user"
    message_content = "This message should not be added."

    # Act
    result = conversation_repo.add_message(
        step_conversation_id=nonexistent_id,
        role=role,
        message=message_content
    )

    # Assert
    assert result is None

def test_get_conversation_with_pagination(conversation_repo):
    """Test retrieving a conversation with message pagination."""
    # Arrange
    step_name = "pagination_message_conversation"
    conversation = conversation_repo.create_conversation(step_name)
    conversation_id = conversation.step_conversation_id

    # Add multiple messages
    total_messages = 10
    for i in range(total_messages):
        conversation_repo.add_message(
            step_conversation_id=conversation_id,
            role="user",
            message=f"Message {i+1}"
        )

    # Act
    retrieved_conversation = conversation_repo.get_conversation_by_id(conversation_id, skip_messages=5, limit_messages=3)

    # Assert
    assert retrieved_conversation is not None
    assert len(retrieved_conversation.messages) == 3
    expected_messages = [f"Message 6", f"Message 7", f"Message 8"]
    actual_messages = [msg["message"] for msg in retrieved_conversation.messages]
    assert actual_messages == expected_messages

def test_concurrent_conversation_creation(conversation_repo):
    """Test creating multiple conversations concurrently."""
    # This test assumes that the repository can handle concurrent operations.
    # Depending on the implementation, additional setup might be required.
    import threading

    step_name = "concurrent_conversation"
    num_threads = 5
    created_conversations = []
    lock = threading.Lock()

    def create_conv():
        conv = conversation_repo.create_conversation(step_name)
        with lock:
            created_conversations.append(conv)

    threads = [threading.Thread(target=create_conv) for _ in range(num_threads)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # Assert
    assert len(created_conversations) == num_threads
    conversations = conversation_repo.get_all_conversations()
    assert len(conversations) == num_threads
    for conv in conversations:
        assert conv.step_name == step_name

def test_delete_conversation(conversation_repo):
    """Test deleting a conversation from the repository."""
    # Arrange
    step_name = "delete_test_conversation"
    conversation = conversation_repo.create_conversation(step_name)
    conversation_id = conversation.step_conversation_id

    # Act
    result = conversation_repo.collection.delete_one({"step_conversation_id": conversation_id})

    # Assert
    assert result.deleted_count == 1
    retrieved = conversation_repo.get_conversation_by_id(conversation_id)
    assert retrieved is None

def test_update_conversation_step_name(conversation_repo):
    """Test updating the step name of an existing conversation."""
    # Arrange
    original_step_name = "original_step"
    new_step_name = "updated_step"
    conversation = conversation_repo.create_conversation(original_step_name)
    conversation_id = conversation.step_conversation_id

    # Act
    conversation.step_name = new_step_name
    conversation_repo.collection.replace_one(
        {"step_conversation_id": conversation_id},
        conversation.to_dict(),
        session=conversation_repo.session
    )
    updated_conversation = conversation_repo.get_conversation_by_id(conversation_id)

    # Assert
    assert updated_conversation is not None
    assert updated_conversation.step_name == new_step_name

def test_add_multiple_messages(conversation_repo):
    """Test adding multiple messages to a conversation."""
    # Arrange
    step_name = "multiple_messages_conversation"
    conversation = conversation_repo.create_conversation(step_name)
    conversation_id = conversation.step_conversation_id
    messages = [
        {"role": "user", "message": "First message"},
        {"role": "assistant", "message": "Second message"},
        {"role": "user", "message": "Third message"}
    ]

    # Act
    for msg in messages:
        conversation_repo.add_message(
            step_conversation_id=conversation_id,
            role=msg["role"],
            message=msg["message"]
        )
    retrieved_conversation = conversation_repo.get_conversation_by_id(conversation_id)

    # Assert
    assert retrieved_conversation is not None
    assert len(retrieved_conversation.messages) == len(messages)
    for i, msg in enumerate(messages):
        retrieved_msg = retrieved_conversation.messages[i]
        assert retrieved_msg["role"] == msg["role"]
        assert retrieved_msg["message"] == msg["message"]

def test_message_timestamp(conversation_repo):
    """Test that message timestamps are correctly recorded."""
    # Arrange
    step_name = "timestamp_test_conversation"
    conversation = conversation_repo.create_conversation(step_name)
    conversation_id = conversation.step_conversation_id

    # Act
    before_time = datetime.utcnow()
    conversation_repo.add_message(
        step_conversation_id=conversation_id,
        role="user",
        message="Timestamp test message"
    )
    after_time = datetime.utcnow()
    retrieved_conversation = conversation_repo.get_conversation_by_id(conversation_id)
    message = retrieved_conversation.messages[-1]

    # Assert
    assert retrieved_conversation is not None
    assert len(retrieved_conversation.messages) == 1
    assert "timestamp" in message
    assert isinstance(message["timestamp"], datetime), f"Expected timestamp to be datetime, got {type(message['timestamp'])}"
    assert before_time <= message["timestamp"] <= after_time, f"Timestamp {message['timestamp']} not within {before_time} and {after_time}"
    
def test_context_paths_in_message(conversation_repo):
    """Test that context paths are correctly stored in messages."""
    # Arrange
    step_name = "context_paths_conversation"
    conversation = conversation_repo.create_conversation(step_name)
    conversation_id = conversation.step_conversation_id
    context_paths = ["path/to/context1", "path/to/context2"]

    # Act
    conversation_repo.add_message(
        step_conversation_id=conversation_id,
        role="user",
        message="Message with context paths",
        context_paths=context_paths
    )
    retrieved_conversation = conversation_repo.get_conversation_by_id(conversation_id)
    message = retrieved_conversation.messages[-1]

    # Assert
    assert message["context_paths"] == context_paths

def test_original_message_field(conversation_repo):
    """Test that the original_message field is correctly stored."""
    # Arrange
    step_name = "original_message_conversation"
    conversation = conversation_repo.create_conversation(step_name)
    conversation_id = conversation.step_conversation_id
    original_message = "This is the original message."

    # Act
    conversation_repo.add_message(
        step_conversation_id=conversation_id,
        role="user",
        message="Reply to original message.",
        original_message=original_message
    )
    retrieved_conversation = conversation_repo.get_conversation_by_id(conversation_id)
    message = retrieved_conversation.messages[-1]

    # Assert
    assert message["original_message"] == original_message