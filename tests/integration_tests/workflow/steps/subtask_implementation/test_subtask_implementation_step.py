import pytest
import asyncio
import os
from autobyteus_server.workflow.steps.subtask_implementation.subtask_implementation_step import SubtaskImplementationStep
from autobyteus.llm.models import LLMModel
from autobyteus.workflow.workflow import Workflow

@pytest.fixture
def workflow():
    return Workflow()

@pytest.fixture
def context_file(tmp_path):
    file_content = """
def greet(name):
    return f"Hello, {name}!"

def main():
    print(greet("World"))

if __name__ == "__main__":
    main()
    """
    file_path = tmp_path / "greetings.py"
    file_path.write_text(file_content)
    return str(file_path)

@pytest.fixture
async def step(workflow):
    step = SubtaskImplementationStep(workflow)
    yield step
    # Cleanup: Close any remaining conversations
    conversation_manager = step.streaming_conversation_manager
    for conversation_id in list(conversation_manager._conversations.keys()):
        conversation_manager.close_conversation(conversation_id)

@pytest.mark.asyncio
async def test_subtask_implementation_step_without_context(step):
    # Arrange
    requirement = "Implement a function to calculate the factorial of a number"
    llm_model = LLMModel.MISTRAL_LARGE_API

    # Act
    conversation_id = await step.process_requirement(requirement, [], llm_model)

    # Assert
    conversation = step.streaming_conversation_manager.get_conversation(conversation_id)
    assert conversation is not None
    
    response = await asyncio.wait_for(step.get_latest_response(conversation_id), timeout=60.0)
    assert response is not None
    assert "def factorial" in response

@pytest.mark.asyncio
async def test_subtask_implementation_step_with_context(step, context_file):
    # Arrange
    requirement = "Modify the greet function to include a time of day greeting"
    llm_model = LLMModel.CLAUDE_3_5_SONNET_API

    # Act
    conversation_id = await step.process_requirement(
        requirement, 
        [{'path': context_file, 'type': 'text'}], 
        llm_model
    )

    # Assert
    conversation = step.streaming_conversation_manager.get_conversation(conversation_id)
    assert conversation is not None
    
    response = await asyncio.wait_for(step.get_latest_response(conversation_id), timeout=60.0)
    assert response is not None
    assert "def greet" in response

@pytest.mark.asyncio
async def test_subtask_implementation_step_continuation(step):
    # Arrange
    initial_requirement = "Implement a function to calculate the factorial of a number"
    llm_model = LLMModel.MISTRAL_LARGE_API

    # Act - Initial conversation
    conversation_id = await step.process_requirement(initial_requirement, [], llm_model)
    initial_response = await asyncio.wait_for(step.get_latest_response(conversation_id), timeout=60.0)
    
    # Assert initial response
    assert initial_response is not None
    assert "def factorial" in initial_response

    # Act - Continue conversation
    continuation_requirement = "Optimize the factorial function using memoization."
    await step.process_requirement(continuation_requirement, [], llm_model, conversation_id=conversation_id)
    
    # Assert continuation
    continuation_response = await asyncio.wait_for(step.get_latest_response(conversation_id), timeout=60.0)
    assert continuation_response is not None
    assert "memoization" in continuation_response

@pytest.mark.asyncio
async def test_subtask_implementation_multiple_conversations(step, context_file):
    # Arrange
    requirement1 = "Implement a function to calculate the factorial of a number"
    requirement2 = "Modify the greet function to include a time of day greeting"
    llm_model1 = LLMModel.MISTRAL_LARGE_API
    llm_model2 = LLMModel.CLAUDE_3_5_SONNET_API

    # Act - First conversation
    conversation_id1 = await step.process_requirement(requirement1, [], llm_model1)
    response1 = await asyncio.wait_for(step.get_latest_response(conversation_id1), timeout=60.0)

    # Act - Second conversation
    conversation_id2 = await step.process_requirement(
        requirement2, 
        [{'path': context_file, 'type': 'text'}], 
        llm_model2
    )
    response2 = await asyncio.wait_for(step.get_latest_response(conversation_id2), timeout=60.0)
    
    # Assert
    assert response1 is not None and "def factorial" in response1
    assert response2 is not None and "def greet" in response2
    
    # Verify both conversations exist
    assert step.streaming_conversation_manager.get_conversation(conversation_id1) is not None
    assert step.streaming_conversation_manager.get_conversation(conversation_id2) is not None