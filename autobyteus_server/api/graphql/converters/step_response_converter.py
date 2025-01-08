
from autobyteus_server.agent_runtime.agent_response import AgentResponseData
from autobyteus_server.api.graphql.types.step_response import StepResponse

def to_graphql_step_response(conversation_id: str, response_data: AgentResponseData) -> StepResponse:
    """
    Convert a StepResponseData instance to a GraphQL StepResponse.
    
    Args:
        conversation_id (str): The ID of the conversation
        response_data (StepResponseData): The step response data to convert
        
    Returns:
        StepResponse: The converted GraphQL response with token usage information
                     when the response is complete
    """
    return StepResponse(
        conversation_id=conversation_id,
        message_chunk=response_data.message,
        is_complete=response_data.is_complete,
        prompt_tokens=response_data.prompt_tokens if response_data.is_complete else None,
        completion_tokens=response_data.completion_tokens if response_data.is_complete else None,
        total_tokens=response_data.total_tokens if response_data.is_complete else None,
        prompt_cost=response_data.prompt_cost if response_data.is_complete else None,
        completion_cost=response_data.completion_cost if response_data.is_complete else None,
        total_cost=response_data.total_cost if response_data.is_complete else None
    )
