import pytest
from datetime import datetime
import uuid
from autobyteus_server.workflow.persistence.conversation.repositories.postgres.step_conversation_repository import (
    StepConversation,
    StepConversationRepository
)

pytestmark = pytest.mark.integration

@pytest.fixture
def conversation_repo():
    """
    Provides the singleton StepConversationRepository instance for testing.
    
    Returns:
        StepConversationRepository: Repository instance for testing
    """
    return StepConversationRepository()

def test_create_empty_conversation(conversation_repo):
    """Test creation of an empty conversation."""
    # Arrange
    step_name = "empty_conversation_postgres"

    # Act
    conversation = conversation_repo.create_step_conversation(step_name)

    # Assert
    assert conversation is not None
    assert conversation.step_name == step_name
    assert isinstance(conversation.created_at, datetime)
    assert isinstance(conversation.id, int)
    assert uuid.UUID(conversation.step_conversation_id)
    assert len(conversation.messages) == 0

def test_create_conversation_successfully(conversation_repo):
    """Test successful creation of a new conversation."""
    # Arrange
    step_name = "test_conversation_postgres"

    # Act
    conversation = conversation_repo.create_step_conversation(step_name)

    # Assert
    assert conversation is not None
    assert conversation.step_name == step_name
    assert isinstance(conversation.created_at, datetime)
    assert isinstance(conversation.id, int)
    assert uuid.UUID(conversation.step_conversation_id)

def test_get_by_id_successful(conversation_repo):
    """Test successful retrieval of a conversation using internal ID."""
    # Arrange
    step_name = "internal_id_test"
    conversation = conversation_repo.create_step_conversation(step_name)
    internal_id = conversation.id

    # Act
    retrieved_conversation = conversation_repo.get_by_id(internal_id)

    # Assert
    assert retrieved_conversation is not None
    assert retrieved_conversation.id == internal_id
    assert retrieved_conversation.step_name == step_name
    assert uuid.UUID(retrieved_conversation.step_conversation_id)

def test_get_by_id_nonexistent(conversation_repo):
    """Test retrieval behavior with non-existent internal ID."""
    # Act & Assert
    assert conversation_repo.get_by_id(999999) is None

def test_get_by_step_conversation_id_successful(conversation_repo):
    """Test successful retrieval of a conversation using UUID step_conversation_id."""
    # Arrange
    step_name = "uuid_test"
    conversation = conversation_repo.create_step_conversation(step_name)
    conversation_uuid = conversation.step_conversation_id

    # Act
    retrieved_conversation = conversation_repo.get_step_conversation_by_uuid(conversation_uuid)

    # Assert
    assert retrieved_conversation is not None
    assert retrieved_conversation.step_conversation_id == conversation_uuid
    assert retrieved_conversation.step_name == step_name

def test_get_by_step_conversation_id_nonexistent(conversation_repo):
    """Test retrieval behavior with non-existent UUID step_conversation_id."""
    # Act & Assert
    assert conversation_repo.get_step_conversation_by_uuid(str(uuid.uuid4())) is None

def test_get_all_conversations(conversation_repo):
    """Test retrieval of all conversations."""
    # Arrange
    step_names = ["conversation_pg1", "conversation_pg2", "conversation_pg3"]
    created_uuids = []
    for name in step_names:
        conversation = conversation_repo.create_step_conversation(name)
        created_uuids.append(conversation.step_conversation_id)

    # Act
    conversations = conversation_repo.get_step_conversations()

    # Assert
    assert len(conversations) >= len(step_names)
    retrieved_uuids = [conv.step_conversation_id for conv in conversations]
    for uuid_str in created_uuids:
        assert uuid_str in retrieved_uuids

def test_get_conversations_by_step_name_with_pagination(conversation_repo):
    """Test retrieval of conversations by step name with pagination."""
    # Arrange
    step_name = "pagination_test_conversation_pg"
    total_conversations = 15
    created_uuids = []
    for _ in range(total_conversations):
        conversation = conversation_repo.create_step_conversation(step_name)
        created_uuids.append(conversation.step_conversation_id)

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
        assert uuid.UUID(conv.step_conversation_id)

def test_get_conversations_by_nonexistent_step_name(conversation_repo):
    """Test retrieval behavior with a non-existent step name."""
    # Act
    result = conversation_repo.get_conversations_by_step_name("nonexistent_conversation_pg", 1, 10)

    # Assert
    assert result["total_conversations"] == 0
    assert result["total_pages"] == 0
    assert result["current_page"] == 1
    assert len(result["conversations"]) == 0

def test_pagination_beyond_available_pages(conversation_repo):
    """Test pagination behavior when requesting a page beyond available data."""
    # Arrange
    step_name = "edge_case_conversation_pg"
    conversation = conversation_repo.create_step_conversation(step_name)
    assert uuid.UUID(conversation.step_conversation_id)

    # Act
    result = conversation_repo.get_conversations_by_step_name(step_name, page=999, page_size=10)

    # Assert
    assert result["total_conversations"] == 1
    assert result["total_pages"] == 1
    assert result["current_page"] == 999
    assert len(result["conversations"]) == 0