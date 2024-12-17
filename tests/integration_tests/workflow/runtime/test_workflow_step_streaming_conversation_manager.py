from typing import List
import pytest
import asyncio
from unittest.mock import MagicMock
from autobyteus.llm.models import LLMModel
from autobyteus.conversation.user_message import UserMessage
from autobyteus_server.workflow.runtime.workflow_step_streaming_conversation_manager import WorkflowStepStreamingConversationManager
from autobyteus_server.workflow.types.step_response import StepResponseData

@pytest.fixture
def conversation_manager():
    manager = WorkflowStepStreamingConversationManager()
    yield manager
    # Cleanup
    manager.shutdown()

@pytest.fixture
def mock_message():
    return UserMessage(content="write a fibonacchi series in python")

@pytest.mark.asyncio
async def test_create_conversation(conversation_manager, mock_message):
    # Arrange
    conversation_id = "test-conv-1"
    step_name = "test-step"
    workspace_id = "test-workspace"
    step_id = "test-step-id"
    llm_model = LLMModel.MISTRAL_LARGE_API.name
    
    # Act
    conversation = conversation_manager.create_conversation(
        conversation_id=conversation_id,
        step_name=step_name,
        workspace_id=workspace_id,
        step_id=step_id,
        llm_model=llm_model,
        initial_message=mock_message
    )
    
    # Wait for complete response
    responses: List[StepResponseData] = []
    async for response in conversation:
        responses.append(response)
        if response.is_complete:
            break

    # Assert
    assert conversation is not None
    assert conversation_manager.get_conversation(conversation_id) is not None
    assert len(responses) > 0
    assert any(r.is_complete for r in responses), "No complete response received"
    
    # Optional: Print out the responses for debugging
    for i, r in enumerate(responses):
        print(f"Response {i}: {r.message} (complete: {r.is_complete})")


@pytest.mark.asyncio
async def test_send_message(conversation_manager, mock_message):
    # Arrange
    conversation_id = "test-conv-2"
    conversation = conversation_manager.create_conversation(
        conversation_id=conversation_id,
        step_name="test-step",
        workspace_id="test-workspace",
        step_id="test-step-id",
        llm_model=LLMModel.MISTRAL_LARGE_API,
        initial_message=mock_message
    )

    # Act
    await conversation_manager.send_message(conversation_id, "Test follow-up message")

    # Assert
    assert conversation_manager.get_conversation(conversation_id) is not None

@pytest.mark.asyncio
async def test_close_conversation(conversation_manager, mock_message):
    # Arrange
    conversation_id = "test-conv-3"
    conversation_manager.create_conversation(
        conversation_id=conversation_id,
        step_name="test-step",
        workspace_id="test-workspace",
        step_id="test-step-id",
        llm_model=LLMModel.MISTRAL_LARGE_API,
        initial_message=mock_message
    )

    # Act
    conversation_manager.close_conversation(conversation_id)

    # Assert
    assert conversation_manager.get_conversation(conversation_id) is None

@pytest.mark.asyncio
async def test_multiple_conversations(conversation_manager, mock_message):
    # Arrange
    conversation_ids = ["test-conv-4", "test-conv-5"]
    
    # Act
    for conv_id in conversation_ids:
        conversation_manager.create_conversation(
            conversation_id=conv_id,
            step_name="test-step",
            workspace_id="test-workspace",
            step_id="test-step-id",
            llm_model=LLMModel.MISTRAL_LARGE_API,
            initial_message=mock_message
        )

    # Assert
    for conv_id in conversation_ids:
        assert conversation_manager.get_conversation(conv_id) is not None

    # Test shutdown
    conversation_manager.shutdown()
    for conv_id in conversation_ids:
        assert conversation_manager.get_conversation(conv_id) is None

@pytest.mark.asyncio
async def test_conversation_error_handling(conversation_manager, mock_message):
    # Arrange
    conversation_id = "test-conv-6"
    
    # Act & Assert - Invalid LLM model
    with pytest.raises(RuntimeError):
        conversation_manager.create_conversation(
            conversation_id=conversation_id,
            step_name="test-step",
            workspace_id="test-workspace",
            step_id="test-step-id",
            llm_model="invalid_model",
            initial_message=mock_message
        )

    # Act & Assert - Invalid conversation ID
    with pytest.raises(RuntimeError):
        await conversation_manager.send_message("invalid_id", "test message")