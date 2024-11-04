import pytest
from bson import ObjectId
from datetime import datetime
from autobyteus_server.workflow.persistence.conversation.models.mongodb.conversation import StepConversation
from autobyteus_server.workflow.persistence.conversation.repositories.mongodb.step_conversation_repository import StepConversationRepository
from repository_mongodb.transaction_management import transaction
import json

pytestmark = pytest.mark.integration

@pytest.fixture
def conversation_repo():
    """
    Provides the singleton StepConversationRepository instance for testing.

    Returns:
        StepConversationRepository: Repository instance for testing.
    """
    return StepConversationRepository()

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

def test_get_all_conversations(conversation_repo):
    """Test retrieval of all conversations."""
    # Arrange
    step_names = ["conversation1", "conversation2", "conversation3"]
    for name in step_names:
        conversation_repo.create_conversation(name)

    # Act
    conversations = conversation_repo.get_all_conversations()

    # Assert
    assert len(conversations) >= len(step_names)
    retrieved_names = [conv.step_name for conv in conversations]
    for name in step_names:
        assert name in retrieved_names

def test_get_conversation_by_id(conversation_repo):
    """Test retrieval of a conversation by its ID."""
    # Arrange
    step_name = "unique_conversation"
    conversation = conversation_repo.create_conversation(step_name)
    conversation_id = conversation.step_conversation_id

    # Act
    retrieved_conversation = conversation_repo.get_conversation_by_id(conversation_id)

    # Assert
    assert retrieved_conversation is not None
    assert retrieved_conversation.step_conversation_id == conversation_id
    assert retrieved_conversation.step_name == step_name

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