from dataclasses import dataclass
from typing import Optional

@dataclass
class AgentResponseData:
    """
    Data class representing the agent response with streaming state and token usage.
    
    Attributes:
        message (str): The response message content
        is_complete (bool): Indicates if this is the final complete response (True) 
                          or a streaming chunk (False)
        prompt_tokens (Optional[int]): Number of tokens in the prompt
        completion_tokens (Optional[int]): Number of tokens in the completion
        total_tokens (Optional[int]): Total number of tokens used
        prompt_cost (Optional[float]): Cost of prompt tokens
        completion_cost (Optional[float]): Cost of completion tokens
        total_cost (Optional[float]): Total cost of the response
    """
    message: str
    is_complete: bool
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    prompt_cost: Optional[float] = None
    completion_cost: Optional[float] = None
    total_cost: Optional[float] = None
