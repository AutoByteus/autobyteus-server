import pytest
import asyncio
from typing import Optional, List, AsyncGenerator
from unittest.mock import Mock, patch, AsyncMock
from queue import Empty
from autobyteus.agent.async_agent import AsyncAgent
from autobyteus.conversation.user_message import UserMessage
from autobyteus.llm.base_llm import BaseLLM
from autobyteus_server.workflow.runtime.streaming_conversation import StreamingConversation
from autobyteus_server.workflow.runtime.exceptions import StreamClosedError
from autobyteus_server.workflow.types.step_response import StepResponseData

class MockLLM(BaseLLM):
    async def _send_user_message_to_llm(self, user_message: str, file_paths: Optional[List[str]] = None, **kwargs) -> str:
        return "Mock response"

    async def _stream_user_message_to_llm(self, user_message: str, file_paths: Optional[List[str]] = None, **kwargs) -> AsyncGenerator[str, None]:
        yield "Mock"
        yield "response"
        yield "streaming"

@pytest.fixture
def mock_llm():
    return MockLLM("gpt-4")  # Providing a model name as required by BaseLLM

@pytest.fixture
def mock_agent():
    agent = AsyncMock(spec=AsyncAgent)
    agent.agent_id = "test_agent"
    return agent

@pytest.fixture
async def streaming_conversation(mock_llm):
    conversation = StreamingConversation(
        workspace_id="test_workspace",
        step_id="test_step",
        conversation_id="test_conversation",
        step_name="test_step_name",
        llm=mock_llm,
        initial_message=UserMessage(content="initial message"),
        tools=[]
    )
    yield conversation
    await conversation.stop()
    conversation.close()

@pytest.mark.asyncio
async def test_initialization(streaming_conversation):
    """Test proper initialization of StreamingConversation"""
    assert streaming_conversation.workspace_id == "test_workspace"
    assert streaming_conversation.step_id == "test_step"
    assert streaming_conversation.conversation_id == "test_conversation"
    assert streaming_conversation.is_active
    assert streaming_conversation._agent is not None

@pytest.mark.asyncio
async def test_message_handling(streaming_conversation):
    """Test sending messages to the conversation"""
    test_message = "test message"
    await streaming_conversation.send_message(test_message)
    # Verify message was processed by checking the response queue
    response = streaming_conversation.get_response()
    assert response is not None

@pytest.mark.asyncio
async def test_response_streaming():
    """Test streaming responses from the conversation"""
    with patch('autobyteus.agent.async_agent.AsyncAgent') as MockAgent:
        # Setup mock agent to emit a response
        agent_instance = AsyncMock()
        MockAgent.return_value = agent_instance
        
        conversation = StreamingConversation(
            workspace_id="test",
            step_id="test",
            conversation_id="test",
            step_name="test",
            llm=MockLLM("gpt-4"),
            initial_message=UserMessage(content="test"),
            tools=[]
        )
        
        # Simulate agent response
        test_response = "Test response"
        conversation._on_assistant_response(response=test_response, is_complete=True)
        
        # Verify response in queue
        response_data = conversation.get_response()
        assert isinstance(response_data, StepResponseData)
        assert response_data.message == test_response
        assert response_data.is_complete
        
        await conversation.stop()
        conversation.close()

@pytest.mark.asyncio
async def test_conversation_lifecycle(streaming_conversation):
    """Test conversation start, stop, and close operations"""
    await streaming_conversation.start()
    assert streaming_conversation.is_active
    
    await streaming_conversation.stop()
    streaming_conversation.close()
    assert not streaming_conversation.is_active
    
    # Verify queue is closed
    with pytest.raises(Empty):
        streaming_conversation.get_response()

@pytest.mark.asyncio
async def test_async_iteration():
    """Test async iteration over conversation responses"""
    conversation = StreamingConversation(
        workspace_id="test",
        step_id="test",
        conversation_id="test",
        step_name="test",
        llm=MockLLM("gpt-4"),
        initial_message=UserMessage(content="test"),
        tools=[]
    )
    
    # Queue some test responses
    conversation.put_response(StepResponseData(message="Response 1", is_complete=False))
    conversation.put_response(StepResponseData(message="Response 2", is_complete=True))
    
    responses = []
    async for response in conversation:
        responses.append(response)
        if response.is_complete:
            break
    
    assert len(responses) == 2
    assert responses[0].message == "Response 1"
    assert responses[1].message == "Response 2"
    assert responses[1].is_complete
    
    await conversation.stop()
    conversation.close()

@pytest.mark.asyncio
async def test_closed_stream_iteration():
    """Test behavior when iterating over a closed stream"""
    conversation = StreamingConversation(
        workspace_id="test",
        step_id="test",
        conversation_id="test",
        step_name="test",
        llm=MockLLM("gpt-4"),
        initial_message=UserMessage(content="test"),
        tools=[]
    )
    
    conversation.close()
    
    with pytest.raises(StreamClosedError):
        async for _ in conversation:
            pass

@pytest.mark.asyncio
async def test_error_handling(streaming_conversation):
    """Test error handling during message processing"""
    # Simulate error in agent processing
    with patch.object(streaming_conversation._agent, 'receive_user_message', 
                     side_effect=Exception("Test error")):
        with pytest.raises(Exception):
            await streaming_conversation.send_message("test message")

@pytest.mark.asyncio
async def test_queue_management(streaming_conversation):
    """Test queue management functionality"""
    # Test putting responses
    response_data = StepResponseData(message="test", is_complete=False)
    streaming_conversation.put_response(response_data)
    
    # Test getting responses
    retrieved = streaming_conversation.get_response()
    assert retrieved == response_data
    
    # Test empty queue behavior
    assert streaming_conversation.get_response() is None

@pytest.mark.asyncio
async def test_agent_event_subscription(streaming_conversation):
    """Test agent event subscription and handling"""
    test_response = "Test response"
    streaming_conversation._on_assistant_response(response=test_response, is_complete=True)
    
    response = streaming_conversation.get_response()
    assert response.message == test_response
    assert response.is_complete