
from typing import List
import pytest
import asyncio
from unittest.mock import MagicMock
from autobyteus.llm.models import LLMModel
from autobyteus.conversation.user_message import UserMessage
from autobyteus_server.workflow.runtime.workflow_agent_conversation_manager import WorkflowAgentConversationManager
from autobyteus_server.agent_runtime.agent_response import AgentResponseData

@pytest.fixture
def conversation_manager():
    manager = WorkflowAgentConversationManager()
    yield manager
    manager.shutdown()

@pytest.fixture
def mock_message():
    return UserMessage(
        content="write a fibonacci series in python",
        file_paths=None,
        original_requirement="write a fibonacci series in python",
        context_file_paths=[]
    )

@pytest.mark.asyncio
async def test_create_conversation(conversation_manager, mock_message):
    # Arrange
    step_name = "test-step"
    workspace_id = "test-workspace"
    step_id = "test-step-id"
    llm_model = LLMModel.MISTRAL_LARGE_API.name
    
    # Act
    conversation = conversation_manager.create_conversation(
        step_name=step_name,
        workspace_id=workspace_id,
        step_id=step_id,
        llm_model=llm_model,
        initial_message=mock_message
    )
    
    # Wait for complete response
    responses: List[AgentResponseData] = []
    async for response in conversation:
        responses.append(response)
        if response.is_complete:
            break

    # Assert
    assert conversation is not None
    assert conversation_manager.get_conversation(conversation.conversation_id) is not None
    assert len(responses) > 0
    assert any(r.is_complete for r in responses)

@pytest.mark.asyncio
async def test_send_message(conversation_manager, mock_message):
    # Arrange
    conversation = conversation_manager.create_conversation(
        step_name="test-step",
        workspace_id="test-workspace",
        step_id="test-step-id",
        llm_model=LLMModel.MISTRAL_LARGE_API.name,
        initial_message=mock_message
    )

    follow_up_message = UserMessage(
        content="Test follow-up message",
        file_paths=None,
        original_requirement="Test follow-up message",
        context_file_paths=[]
    )

    # Act
    await conversation_manager.send_message(conversation.conversation_id, follow_up_message)

    # Assert
    assert conversation_manager.get_conversation(conversation.conversation_id) is not None

@pytest.mark.asyncio
async def test_close_conversation(conversation_manager, mock_message):
    # Arrange
    conversation = conversation_manager.create_conversation(
        step_name="test-step",
        workspace_id="test-workspace",
        step_id="test-step-id",
        llm_model=LLMModel.MISTRAL_LARGE_API.name,
        initial_message=mock_message
    )

    # Act
    conversation_manager.close_conversation(conversation.conversation_id)

    # Assert
    assert conversation_manager.get_conversation(conversation.conversation_id) is None

@pytest.mark.asyncio
async def test_multiple_conversations(conversation_manager, mock_message):
    # Arrange & Act
    conversations = []
    for i in range(2):
        conversation = conversation_manager.create_conversation(
            step_name=f"test-step-{i}",
            workspace_id="test-workspace",
            step_id=f"test-step-id-{i}",
            llm_model=LLMModel.MISTRAL_LARGE_API.name,
            initial_message=mock_message
        )
        conversations.append(conversation)

    # Assert
    for conversation in conversations:
        assert conversation_manager.get_conversation(conversation.conversation_id) is not None

    # Test shutdown
    conversation_manager.shutdown()
    for conversation in conversations:
        assert conversation_manager.get_conversation(conversation.conversation_id) is None

@pytest.mark.asyncio
async def test_conversation_error_handling(conversation_manager, mock_message):
    # Act & Assert - Invalid LLM model
    with pytest.raises(RuntimeError):
        conversation_manager.create_conversation(
            step_name="test-step",
            workspace_id="test-workspace",
            step_id="test-step-id",
            llm_model="invalid_model",
            initial_message=mock_message
        )

    # Act & Assert - Invalid conversation ID
    with pytest.raises(RuntimeError):
        await conversation_manager.send_message("invalid_id", mock_message)
