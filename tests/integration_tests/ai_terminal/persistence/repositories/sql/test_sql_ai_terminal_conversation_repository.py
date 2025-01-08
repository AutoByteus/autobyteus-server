
import pytest
import uuid
from datetime import datetime
from autobyteus_server.ai_terminal.persistence.models.sql.conversation import AiTerminalConversation
from autobyteus_server.ai_terminal.persistence.repositories.sql.ai_terminal_conversation_repository import (
    AiTerminalConversationRepository
)

pytestmark = pytest.mark.integration

@pytest.fixture(scope="function")
def sql_conversation_repo():
    """
    Provides an instance of AiTerminalConversationRepository for SQL.
    Since we assume a fresh test database or a transaction rollback mechanism,
    no explicit cleanup is done here. Adjust as needed for your environment.
    """
    return AiTerminalConversationRepository()

def test_create_conversation(sql_conversation_repo):
    """
    Test creating a new conversation in SQL.
    """
    conv = sql_conversation_repo.create_conversation()
    assert isinstance(conv, AiTerminalConversation)
    assert isinstance(conv.id, int)
    uuid_obj = uuid.UUID(conv.conversation_id)
    assert str(uuid_obj) == conv.conversation_id
    assert isinstance(conv.created_at, datetime)
    assert conv.messages == []

def test_find_by_conversation_id_success(sql_conversation_repo):
    """
    Test successful find by conversation UUID.
    """
    conv = sql_conversation_repo.create_conversation()
    found = sql_conversation_repo.find_by_conversation_id(conv.conversation_id)
    assert found is not None
    assert found.id == conv.id

def test_find_by_conversation_id_nonexistent(sql_conversation_repo):
    """
    Test find by conversation UUID for a non-existent conversation returns None.
    """
    found = sql_conversation_repo.find_by_conversation_id(str(uuid.uuid4()))
    assert found is None

def test_list_conversations_pagination(sql_conversation_repo):
    """
    Test conversation listing with pagination in SQL.
    """
    # Create multiple conversations
    total_conversations = 5
    for _ in range(total_conversations):
        sql_conversation_repo.create_conversation()

    result_page_1 = sql_conversation_repo.list_conversations(skip=0, limit=2)
    assert len(result_page_1["conversations"]) == 2
    assert result_page_1["total"] == total_conversations
    assert result_page_1["total_pages"] == (total_conversations + 2 - 1) // 2
    assert result_page_1["current_page"] == 1

    result_page_2 = sql_conversation_repo.list_conversations(skip=2, limit=2)
    assert len(result_page_2["conversations"]) == 2
    assert result_page_2["current_page"] == 2

def test_list_conversations_no_data(sql_conversation_repo):
    """
    Test listing conversations when none exist in SQL.
    """
    result = sql_conversation_repo.list_conversations(skip=0, limit=10)
    assert len(result["conversations"]) == 0
    assert result["total"] == 0
    assert result["total_pages"] == 0
    assert result["current_page"] == 1
