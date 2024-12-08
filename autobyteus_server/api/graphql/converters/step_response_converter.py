from autobyteus_server.workflow.types.step_response import StepResponseData
from autobyteus_server.api.graphql.types.step_response import StepResponse

def to_graphql_step_response(conversation_id: str, response_data: StepResponseData) -> StepResponse:
    """
    Convert a StepResponseData instance to a GraphQL StepResponse.
    
    Args:
        conversation_id (str): The ID of the conversation
        response_data (StepResponseData): The step response data to convert
        
    Returns:
        StepResponse: The converted GraphQL response
    """
    return StepResponse(
        conversation_id=conversation_id,
        message_chunk=response_data.message,
        is_complete=response_data.is_complete
    )