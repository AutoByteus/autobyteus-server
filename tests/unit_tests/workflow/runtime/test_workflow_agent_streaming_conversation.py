
import pytest
import asyncio
from typing import Optional, List, AsyncGenerator
from unittest.mock import Mock, patch, AsyncMock
from queue import Empty
from autobyteus.agent.async_agent import AsyncAgent
from autobyteus.conversation.user_message import UserMessage
from autobyteus.llm.base_llm import BaseLLM
from autobyteus.llm.models import LLMModel
from autobyteus.llm.utils.token_usage import TokenUsage
from autobyteus.llm.utils.response_types import CompleteResponse, ChunkResponse
from autobyteus.events.event_types import EventType
import pytest_asyncio
from autobyteus_server.workflow.runtime.workflow_agent_streaming_conversation import WorkflowAgentStreamingConversation
from autobyteus_server.agent_runtime.exceptions import StreamClosedError
from autobyteus_server.agent_runtime.agent_response import AgentResponseData

class MockLLM(BaseLLM):
    def __init__(self, model: LLMModel):
        super().__init__(model=model)
        
    async def _send_user_message_to_llm(self, user_message: str, file_paths: Optional[List[str]] = None, **kwargs) -> CompleteResponse:
        # Add user message to conversation history
        self.add_user_message(user_message)
        
        # Generate mock response
        response_content = "Mock response"
        
        # Add assistant response to conversation history
        self.add_assistant_message(response_content)
        
        # Mock token usage for testing
        token_usage = TokenUsage(
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15
        )
        
        return CompleteResponse(
            content=response_content,
            usage=token_usage
        )

    async def _stream_user_message_to_llm(self, user_message: str, file_paths: Optional[List[str]] = None, **kwargs) -> AsyncGenerator[ChunkResponse, None]:
        # Add user message at the start of streaming
        self.add_user_message(user_message)
        
        chunks = ["Mock", "response", "streaming"]
        complete_response = ""
        
        for i, chunk in enumerate(chunks):
            is_last = i == len(chunks) - 1
            complete_response += chunk
            
            usage = None
            if is_last:
                # Add complete assistant response to history before final chunk
                self.add_assistant_message(complete_response)
                usage = TokenUsage(
                    prompt_tokens=10,
                    completion_tokens=5,
                    total_tokens=15
                )
                
            yield ChunkResponse(
                content=chunk,
                is_complete=is_last,
                usage=usage
            )

async def wait_for_response(conversation: WorkflowAgentStreamingConversation) -> Optional[AgentResponseData]:
    """Helper function to wait for a response
    
    Args:
        conversation: The conversation to wait for response from
    
    Returns:
        Optional[StepResponseData]: The response when received
    """
    while True:
        response = conversation.get_response()
        if response is not None:
            return response
        await asyncio.sleep(0.1)

@pytest.fixture
def mock_llm():
    return MockLLM(model=LLMModel.CLAUDE_3_HAIKU_API)

@pytest_asyncio.fixture
async def agent_streaming_conversation(mock_llm):
    conversation = WorkflowAgentStreamingConversation(
        workspace_id="test_workspace",
        step_id="test_step",
        step_name="test_step_name",
        llm=mock_llm,
        initial_message=UserMessage(
            content="initial message",
            file_paths=None,
            original_requirement="original message",
            context_file_paths=["test_path"]
        ),
        tools=[]
    )
    await conversation.start()
    
    try:
        yield conversation
    finally:
        await conversation.stop()
        conversation.close()

@pytest.mark.asyncio
async def test_initialization(agent_streaming_conversation):
    """Test proper initialization of WorkflowAgentStreamingConversation"""
    assert agent_streaming_conversation.workspace_id == "test_workspace"
    assert agent_streaming_conversation.step_id == "test_step"
    assert agent_streaming_conversation.is_active
    assert agent_streaming_conversation._agent is not None

@pytest.mark.asyncio
async def test_response_streaming():
    """Test streaming responses from the conversation"""
    conversation = WorkflowAgentStreamingConversation(
        workspace_id="test",
        step_id="test",
        step_name="test",
        llm=MockLLM(model=LLMModel.CLAUDE_3_HAIKU_API),
        initial_message=UserMessage(
            content="test",
            file_paths=None,
            original_requirement="test",
            context_file_paths=["test"]
        ),
        tools=[],
    )
    
    try:
        await conversation.start()
        
        await conversation.send_message(UserMessage(
            content="Test input",
            file_paths=None,
            original_requirement="test",
            context_file_paths=[]
        ))
        
        # Collect all streaming responses
        responses = []
        async for response in conversation:
            responses.append(response)
            if len(responses) == 3:  # We expect 3 chunks from MockLLM
                break
                
        # Verify each chunk
        assert len(responses) == 3
        assert responses[0].message == "Mock"
        assert responses[1].message == "response" 
        assert responses[2].message == "streaming"
        
    finally:
        await conversation.stop()
        conversation.close()

@pytest.mark.asyncio
async def test_message_handling(agent_streaming_conversation):
    """Test sending messages to the conversation"""
    test_message = UserMessage(
        content="test message",
        file_paths=None,
        original_requirement="test message",
        context_file_paths=[]
    )
    await agent_streaming_conversation.send_message(test_message)
    
    # Collect all streaming responses
    responses = []
    async for response in agent_streaming_conversation:
        responses.append(response)
        if len(responses) == 3:  # We expect 3 chunks from MockLLM
            break
            
    # Verify each chunk
    assert len(responses) == 3
    assert responses[0].message == "Mock"
    assert responses[1].message == "response"
    assert responses[2].message == "streaming"

@pytest.mark.asyncio
async def test_conversation_lifecycle(agent_streaming_conversation):
    """Test conversation start, stop, and close operations"""
    assert agent_streaming_conversation.is_active
    
    await agent_streaming_conversation.stop()
    agent_streaming_conversation.close()
    assert not agent_streaming_conversation.is_active
    
    with pytest.raises(Empty):
        agent_streaming_conversation.get_response()

@pytest.mark.asyncio
async def test_async_iteration():
    """Test async iteration over conversation responses"""
    conversation = WorkflowAgentStreamingConversation(
        workspace_id="test",
        step_id="test",
        step_name="test",
        llm=MockLLM(model=LLMModel.CLAUDE_3_HAIKU_API),
        initial_message=UserMessage(
            content="test",
            file_paths=None,
            original_requirement="test",
            context_file_paths=[]
        ),
        tools=[]
    )
    
    try:
        await conversation.start()
        
        await conversation.send_message(UserMessage(
            content="Test input",
            file_paths=None,
            original_requirement="test",
            context_file_paths=[]
        ))
        
        responses = []
        async for response in conversation:
            responses.append(response)
            if len(responses) == 3:  # We expect three chunks from mock LLM
                break
        
        assert len(responses) == 3
        assert responses[0].message == "Mock"
        assert responses[1].message == "response"
        assert responses[2].message == "streaming"
    finally:
        await conversation.stop()
        conversation.close()

@pytest.mark.asyncio
async def test_closed_stream_iteration():
    """Test behavior when iterating over a closed stream"""
    conversation = WorkflowAgentStreamingConversation(
        workspace_id="test",
        step_id="test",
        step_name="test",
        llm=MockLLM(model=LLMModel.CLAUDE_3_HAIKU_API),
        initial_message=UserMessage(
            content="test",
            file_paths=None,
            original_requirement="test",
            context_file_paths=[]
        ),
        tools=[]
    )
    
    try:
        await conversation.start()
        conversation.close()
        
        with pytest.raises(StreamClosedError):
            async for _ in conversation:
                pass
    finally:
        await conversation.stop()
        conversation.close()

@pytest.mark.asyncio
async def test_error_handling(agent_streaming_conversation):
    """Test error handling during message processing"""
    with patch.object(agent_streaming_conversation._agent, 'receive_user_message', 
                     side_effect=Exception("Test error")):
        test_message = UserMessage(
            content="test message",
            file_paths=None,
            original_requirement="test message",
            context_file_paths=[]
        )
        with pytest.raises(Exception):
            await agent_streaming_conversation.send_message(test_message)

@pytest.mark.asyncio
async def test_queue_management(agent_streaming_conversation):
    """Test queue management functionality"""
    await agent_streaming_conversation.send_message(UserMessage(
        content="Test input",
        file_paths=None,
        original_requirement="test",
        context_file_paths=[]
    ))
    
    # Collect all streaming responses
    responses = []
    async for response in agent_streaming_conversation:
        responses.append(response)
        if len(responses) == 3:  # We expect 3 chunks from MockLLM
            break
            
    # Verify each chunk
    assert len(responses) == 3
    assert responses[0].message == "Mock"
    assert responses[1].message == "response"
    assert responses[2].message == "streaming"
